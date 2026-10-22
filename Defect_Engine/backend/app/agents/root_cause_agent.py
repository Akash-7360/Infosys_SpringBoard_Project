from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.state import DefectAnalysisState
from app.services.rag_pipeline import rag_pipeline_service
from app.core.config import settings


def deduce_failure_mechanism(exc_type: str, title: str, desc: str, offending_func: str) -> str:
    """
    Identifies the underlying failure mechanism based on exception type and technical context.
    """
    text = f"{exc_type} {title} {desc} {offending_func}".lower()

    if any(k in text for k in ["outofmemory", "heap space", "heap", "memoryerror", "taskmemorymanager"]):
        return "Heap Space Exhaustion & Inadequate Spill Registration"
    elif any(k in text for k in ["nullpointer", "null_pointer", "null reference", "recordaccumulator", "producerbatch"]):
        return "Null Pointer Dereference & Object De-allocation Race Condition"
    elif any(k in text for k in ["sigsegv", "segmentation fault", "dangling pointer", "use-after-free", "access_violation"]):
        return "Dangling Pointer Dereference & Memory Safety Violation"
    elif any(k in text for k in ["deadlock", "blocked", "typesystem", "permit", "mutex", "lock"]):
        return "Lock Ordering Discrepancy & Concurrent Thread Deadlock"
    elif any(k in text for k in ["corruptsstable", "checksum mismatch", "crc", "unflushed"]):
        return "Unflushed Disk Buffer Truncation & Checksum Desynchronization"
    elif any(k in text for k in ["buffer overflow", "sec_error", "secitem", "integer overflow"]):
        return "Integer Arithmetic Overflow in Buffer Bounds Validation"
    elif any(k in text for k in ["bundleexception", "equinox", "osgi", "wiring", "stale wire"]):
        return "Stale Module Wiring Reference in Dynamic Container Graph"
    elif any(k in text for k in ["no more handles", "swterror", "cairo", "leak", "gdk", "gtk"]):
        return "Native GUI Handle Leak & Undisposed Context Handles"
    elif any(k in text for k in ["connectionrefused", "timeout", "econnrefused", "socket"]):
        return "Network Socket Connection Refusal & Inadequate Retry Backoff"
    elif any(k in text for k in ["typeerror", "referenceerror", "attributeerror"]):
        return "Unchecked Dynamic Type Property Access on Undefined Reference"
    else:
        return "Unhandled Component Execution Exception in Core Pipeline"


async def root_cause_agent_node(state: DefectAnalysisState) -> Dict[str, Any]:
    """
    Milestone 3.1 Root Cause Agent Node:
    Synthesizes outputs from Triage Agent and Log Analysis Agent,
    retrieves historical defects and verified resolutions via RAG,
    formulates primary and secondary root cause hypotheses,
    computes confidence score, categorizes failure mechanism,
    and clearly distinguishes between Agent Reasoning and Retrieved Evidence.
    """
    title = state.get("raw_title", "")
    desc = state.get("raw_description", "")
    trace = state.get("raw_stack_trace", "")
    component = state.get("component") or "General"
    
    triage_info = state.get("triage_info", {})
    severity = triage_info.get("severity", "High")
    priority = triage_info.get("priority", "P2")

    parsed_log = state.get("parsed_log", {})
    exc_type = parsed_log.get("exception_type", "UnknownException")
    exc_msg = parsed_log.get("exception_message", "")
    code_path = parsed_log.get("code_path", [])
    log_format = parsed_log.get("log_format", "Unstructured")
    
    failure_point = parsed_log.get("failure_point") or {}
    top_frame = parsed_log.get("top_offending_frame") or {}
    
    offending_file = failure_point.get("file_name") or top_frame.get("file_path") or "Unknown File"
    offending_func = failure_point.get("method_name") or top_frame.get("function_name") or "Unknown Function"
    offending_line = failure_point.get("line_number") or top_frame.get("line_number") or 0

    # 1. RAG Historical Evidence
    retrieved_docs = state.get("retrieved_docs", [])
    if not retrieved_docs:
        retrieved_docs = rag_pipeline_service.retrieve_similar_defects(
            title=title,
            description=desc,
            stack_trace=trace,
            repository=state.get("repository"),
            component=component,
            top_k=4
        )

    # 2. Format Supporting Evidence Items
    supporting_evidence: List[Dict[str, Any]] = []
    top_rag_match = retrieved_docs[0] if retrieved_docs else None
    top_score = float(top_rag_match.get("similarity_score", 0.0)) if top_rag_match else 0.0

    for doc in retrieved_docs:
        b_id = doc.get("bug_id", "")
        score = float(doc.get("similarity_score", 0.0))
        rc_text = doc.get("root_cause") or "Historical defect with verified fix in knowledge base."
        res_text = doc.get("resolution") or ""
        
        relevance = (
            f"Matches {int(score * 100)}% with historical bug {b_id} in {doc.get('component')}. "
            f"Historical root cause was '{rc_text}'. Verified fix: '{res_text}'."
        )
        supporting_evidence.append({
            "bug_id": b_id,
            "title": doc.get("title", ""),
            "repository": doc.get("repository", "General"),
            "component": doc.get("component", "General"),
            "similarity_score": round(score, 4),
            "root_cause": rc_text,
            "resolution": res_text,
            "relevance_explanation": relevance
        })

    # 3. Determine Failure Mechanism & Evidence Status
    failure_mech = deduce_failure_mechanism(exc_type, title, desc, offending_func)
    has_diagnostic_frames = (offending_file != "Unknown File" and offending_line > 0)
    has_meaningful_exc = exc_type not in ["UnknownException", "Unknown", "ApplicationDefect"]

    if top_score >= 0.88 and has_diagnostic_frames:
        evidence_status = "Direct Match Evidence"
        confidence = min(0.96, 0.88 + (top_score * 0.08))
    elif has_diagnostic_frames:
        evidence_status = "Sufficient Evidence"
        confidence = 0.85
    elif top_score >= 0.75 and has_meaningful_exc:
        evidence_status = "Sufficient Evidence"
        confidence = 0.78
    else:
        evidence_status = "Insufficient Evidence"
        confidence = 0.42

    # 4. Synthesize Hypotheses & Agent Reasoning
    if evidence_status == "Insufficient Evidence":
        primary_hypothesis = (
            f"Insufficient diagnostic evidence to conclusively isolate root cause. "
            f"Submission lacks explicit stack trace frames or recognized exception identifiers."
        )
        secondary_hypotheses = [
            f"Potential non-fatal configuration divergence or transient environmental timeout.",
            f"Unlogged exception swallowed upstream before diagnostic capture."
        ]
        agent_reasoning = (
            f"Agent evaluated submission '{title}' triaged as {severity} ({priority}) in component '{component}'. "
            f"The provided log content does not contain structured stack frames or identifiable failure points. "
            f"No direct matches found in RAG knowledge base (highest match: {int(top_score * 100)}%). "
            f"Conclusion marked as Insufficient Evidence to prevent speculative claims."
        )
    else:
        if top_score >= 0.78 and top_rag_match and top_rag_match.get("root_cause"):
            primary_hypothesis = (
                f"{failure_mech}: Grounded by historical defect {top_rag_match['bug_id']}, "
                f"where {top_rag_match['root_cause'].lower().rstrip('.')} occurred during `{offending_func}` "
                f"at {offending_file}:{offending_line}."
            )
        elif has_diagnostic_frames:
            primary_hypothesis = (
                f"{failure_mech} triggered during invocation of `{offending_func}` at `{offending_file}:{offending_line}` "
                f"when `{exc_type}` ({exc_msg or 'unhandled state'}) was raised."
            )
        else:
            primary_hypothesis = (
                f"{failure_mech} within the '{component}' subsystem associated with `{exc_type}`: '{exc_msg or title}'."
            )

        secondary_hypotheses = [
            f"Race condition or un-synchronized access under high concurrent workload causing state desynchronization.",
            f"Missing defensive precondition check or null guard in `{offending_func}` prior to object dereference."
        ]

        agent_reasoning = (
            f"The agent synthesized the defect profile in component '{component}' triaged at {severity} severity ({priority} priority). "
            f"Log analysis extracted exception `{exc_type}` in {log_format} format with failure point localized to `{offending_func}` "
            f"({offending_file}:{offending_line}). Call sequence shows {len(code_path)} active frames leading to the exception. "
            f"Cross-referencing historical RAG defect records ({len(supporting_evidence)} candidates) reveals consistent failure pattern '{failure_mech}'."
        )

    # 5. Optional LLM Refinement if API Key is configured
    if settings.OPENAI_API_KEY and evidence_status != "Insufficient Evidence":
        try:
            import json
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate
            llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            prompt = PromptTemplate.from_template(
                "You are an expert Root Cause Analysis agent.\n"
                "Defect: {title} | Component: {component} | Severity: {severity}\n"
                "Exception: {exc_type} - {exc_msg}\n"
                "Failure Point: {offending_func} in {offending_file}:{offending_line}\n"
                "Top RAG Evidence: {rag_evidence}\n"
                "Return JSON with exact keys: primary_hypothesis, secondary_hypotheses (list), agent_reasoning, confidence_score (0.0-1.0)."
            )
            chain = prompt | llm
            res = chain.invoke({
                "title": title,
                "component": component,
                "severity": severity,
                "exc_type": exc_type,
                "exc_msg": exc_msg,
                "offending_func": offending_func,
                "offending_file": offending_file,
                "offending_line": offending_line,
                "rag_evidence": str(supporting_evidence[:2])
            })
            data = json.loads(res.content)
            if data.get("primary_hypothesis"):
                primary_hypothesis = data["primary_hypothesis"]
            if data.get("secondary_hypotheses"):
                secondary_hypotheses = data["secondary_hypotheses"]
            if data.get("agent_reasoning"):
                agent_reasoning = data["agent_reasoning"]
            if data.get("confidence_score"):
                confidence = float(data["confidence_score"])
        except Exception:
            pass

    # Backwards compatibility strings
    root_cause_summary = primary_hypothesis
    detailed_explanation = (
        f"{primary_hypothesis}\n\n"
        f"**Agent Deductive Reasoning**:\n{agent_reasoning}\n\n"
        f"**Failure Mechanism**: {failure_mech}\n\n"
        f"**Supporting Knowledge Base Evidence**:\n" +
        ("\n".join([f"- [{e['bug_id']}] ({int(e['similarity_score']*100)}%): {e['root_cause']}" for e in supporting_evidence[:3]]) if supporting_evidence else "No historical defect evidence available.")
    )

    root_cause_output = {
        "primary_hypothesis": primary_hypothesis,
        "secondary_hypotheses": secondary_hypotheses,
        "confidence_score": round(confidence, 2),
        "agent_reasoning": agent_reasoning,
        "primary_failure_mechanism": failure_mech,
        "evidence_status": evidence_status,
        "supporting_evidence": supporting_evidence,
        "root_cause_summary": root_cause_summary,
        "detailed_explanation": detailed_explanation
    }

    step_log = {
        "agent": "RootCauseAgent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": (
            f"Delineated Root Cause: '{primary_hypothesis[:80]}...' "
            f"(Status: {evidence_status}, Confidence: {int(confidence * 100)}%)."
        )
    }

    steps = list(state.get("workflow_steps", []))
    steps.append(step_log)

    return {
        "root_cause_info": root_cause_output,
        "workflow_steps": steps
    }

