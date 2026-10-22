from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.state import DefectAnalysisState
from app.services.rag_pipeline import rag_pipeline_service
from app.core.config import settings

DUPLICATE_SIMILARITY_THRESHOLD = 0.88
RELATED_SIMILARITY_THRESHOLD = 0.75


def generate_match_reason(
    query_title: str,
    query_exc: str,
    query_comp: str,
    match_bug: Dict[str, Any],
    score: float
) -> str:
    """
    Generates a clear explanation of why a retrieved historical bug was ranked and matched.
    """
    m_id = match_bug.get("bug_id", "Unknown")
    m_comp = match_bug.get("component", "General")
    m_title = match_bug.get("title", "")
    m_rc = match_bug.get("root_cause", "")
    pct = int(score * 100)

    if score >= DUPLICATE_SIMILARITY_THRESHOLD:
        reason = (
            f"Strong duplicate candidate ({pct}% match) to {m_id}. "
            f"Shares matching failure context in '{m_comp}' component with nearly identical error manifestation"
        )
        if query_exc and query_exc.lower() in (m_title + " " + m_rc).lower():
            reason += f" and consistent {query_exc} exception pattern."
        else:
            reason += "."
        return reason
    elif score >= RELATED_SIMILARITY_THRESHOLD:
        return (
            f"Related defect ({pct}% match) in '{m_comp}' module. "
            f"Exhibits correlated error symptoms or subsystem behavior with historical ticket {m_id}, "
            f"though specific call paths or trigger conditions may differ."
        )
    else:
        return (
            f"Partial semantic relevance ({pct}% match) within '{m_comp}'. "
            f"Shares technical keywords with {m_id} but lacks sufficient similarity for duplicate classification."
        )


async def duplicate_agent_node(state: DefectAnalysisState) -> Dict[str, Any]:
    """
    Milestone 3.2 Duplicate Detection Agent Node:
    Performs dense vector semantic search against historical bug repository in ChromaDB,
    ranks candidate matches, computes similarity scores, classifies duplicate status,
    and generates detailed per-match duplicate explanations and resolution summaries.
    """
    title = state.get("raw_title", "")
    desc = state.get("raw_description", "")
    trace = state.get("raw_stack_trace", "")
    repo = state.get("repository", "")
    comp = state.get("component", "")
    parsed_log = state.get("parsed_log", {})
    exc_type = parsed_log.get("exception_type", "")

    # 1. Retrieve top matching historical defect records
    similar_bugs = rag_pipeline_service.retrieve_similar_defects(
        title=title,
        description=desc,
        stack_trace=trace,
        repository=repo,
        component=comp,
        top_k=5
    )

    # 2. Analyze matches and compute similarity thresholds
    max_score = 0.0
    top_match = None
    if similar_bugs:
        top_match = similar_bugs[0]
        max_score = float(top_match.get("similarity_score", 0.0))

    # Determine Duplicate Status
    if max_score >= DUPLICATE_SIMILARITY_THRESHOLD:
        duplicate_status = "Duplicate"
        is_dup = True
        dup_id = top_match.get("bug_id") if top_match else None
    elif max_score >= RELATED_SIMILARITY_THRESHOLD:
        duplicate_status = "Related Issue"
        is_dup = False
        dup_id = None
    else:
        duplicate_status = "New / Unmatched Issue"
        is_dup = False
        dup_id = None

    # 3. Format structured potential matches with per-match reasoning
    potential_matches: List[Dict[str, Any]] = []
    related_bug_ids: List[str] = []

    for bug in similar_bugs:
        score = float(bug.get("similarity_score", 0.0))
        b_id = bug.get("bug_id", "")
        related_bug_ids.append(b_id)

        if score >= DUPLICATE_SIMILARITY_THRESHOLD:
            category = "Duplicate Match"
        elif score >= RELATED_SIMILARITY_THRESHOLD:
            category = "Related Issue"
        else:
            category = "Weak Match"

        reason = generate_match_reason(
            query_title=title,
            query_exc=exc_type,
            query_comp=comp,
            match_bug=bug,
            score=score
        )

        potential_matches.append({
            "bug_id": b_id,
            "title": bug.get("title", ""),
            "repository": bug.get("repository", "General"),
            "component": bug.get("component", "General"),
            "similarity_score": round(score, 4),
            "similarity_category": category,
            "match_reason": reason,
            "root_cause": bug.get("root_cause", ""),
            "resolution": bug.get("resolution", ""),
            "stack_trace": bug.get("stack_trace", "")
        })

    # Summary text
    if duplicate_status == "Duplicate":
        match_summary = (
            f"Detected DUPLICATE bug report matching historical defect {dup_id} "
            f"with {int(max_score * 100)}% similarity. Root cause and verified fix are readily available in knowledge base."
        )
    elif duplicate_status == "Related Issue":
        match_summary = (
            f"Identified {len(potential_matches)} RELATED historical defect(s). "
            f"Top match {top_match.get('bug_id') if top_match else 'N/A'} has {int(max_score * 100)}% similarity. "
            f"Not a direct duplicate, but historical resolutions provide relevant context."
        )
    else:
        match_summary = (
            f"No direct duplicate detected (highest similarity: {int(max_score * 100)}% < threshold {int(DUPLICATE_SIMILARITY_THRESHOLD * 100)}%). "
            f"This appears to be a NEW or unmatched defect requiring novel investigation."
        )

    # 4. Optional LLM Refinement if API key is configured
    if settings.OPENAI_API_KEY and potential_matches:
        try:
            import json
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate
            llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            prompt = PromptTemplate.from_template(
                "You are an expert bug duplicate detection agent.\n"
                "New Defect: {title} | Exception: {exc_type}\n"
                "Top Matches: {matches}\n"
                "Return JSON with keys: duplicate_status (Duplicate / Related Issue / New / Unmatched Issue), match_summary."
            )
            chain = prompt | llm
            res = chain.invoke({
                "title": title,
                "exc_type": exc_type,
                "matches": json.dumps(potential_matches[:3])
            })
            data = json.loads(res.content)
            if data.get("duplicate_status"):
                duplicate_status = data["duplicate_status"]
                is_dup = duplicate_status == "Duplicate"
            if data.get("match_summary"):
                match_summary = data["match_summary"]
        except Exception:
            pass

    dup_info = {
        "duplicate_status": duplicate_status,
        "is_duplicate": is_dup,
        "duplicate_bug_id": dup_id,
        "highest_similarity_score": round(max_score, 4),
        "match_summary": match_summary,
        "potential_matches": potential_matches,
        "related_bug_ids": related_bug_ids,
        "related_bugs": similar_bugs  # backwards compatibility
    }

    step_log = {
        "agent": "DuplicateAgent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": (
            f"Duplicate Detection: Status='{duplicate_status}' (Highest Match: {int(max_score * 100)}%). "
            f"{'Flagged as duplicate of ' + str(dup_id) if is_dup else 'Surfaced ' + str(len(potential_matches)) + ' candidate defect(s)'}."
        )
    }

    steps = list(state.get("workflow_steps", []))
    steps.append(step_log)

    return {
        "duplicate_info": dup_info,
        "retrieved_docs": similar_bugs,
        "workflow_steps": steps
    }

