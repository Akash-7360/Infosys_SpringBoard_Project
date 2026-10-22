import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.models.bug_submission import (
    BugSubmission,
    BugSubmissionResponse,
    HistoricalBugItem,
    ResolveBugRequest,
    ResolveBugResponse,
    KnowledgeBaseStatsResponse
)
from app.agents.orchestrator import run_defect_analysis_pipeline
from app.services.vector_store import vector_store_service

router = APIRouter()


@router.post("/submit", response_model=BugSubmissionResponse)
@limiter.limit(settings.SUBMISSION_RATE_LIMIT)
async def submit_bug_report(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    stack_trace: Optional[str] = Form(None),
    environment_details: Optional[str] = Form(None),
    repository: Optional[str] = Form("Mozilla/Apache/Eclipse"),
    component: Optional[str] = Form("General"),
    log_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new software defect for autonomous analysis & triage.
    Supports direct text input and multipart log file uploads (.log, .txt, .json).
    """
    bug_id = f"BUG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    file_content = ""
    file_name = None

    if log_file:
        file_name = log_file.filename
        content_bytes = await log_file.read()
        try:
            file_content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            file_content = content_bytes.decode("latin-1", errors="ignore")

    # Combine text trace with log file content if present
    combined_log = file_content if file_content else (stack_trace or "")

    # Execute Multi-Agent LangGraph Pipeline
    pipeline_result = await run_defect_analysis_pipeline(
        bug_id=bug_id,
        title=title,
        description=description or "",
        stack_trace=stack_trace or "",
        raw_log_content=combined_log,
        environment_details=environment_details or "",
        repository=repository or "General",
        component=component or "General"
    )

    triage = pipeline_result.get("triage_info", {})
    dup = pipeline_result.get("duplicate_info", {})
    rc = pipeline_result.get("root_cause_info", {})
    rem = pipeline_result.get("remediation_info", {})
    parsed_log = pipeline_result.get("parsed_log", {})
    retrieved = pipeline_result.get("retrieved_docs", [])
    steps = pipeline_result.get("workflow_steps", [])

    # Format remediation steps as string
    steps_list = rem.get("step_by_step_mitigation", [])
    mitigation_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_list)])

    # Persist to database
    db_bug = BugSubmission(
        id=bug_id,
        title=title,
        description=description,
        stack_trace=stack_trace,
        environment_details=environment_details,
        log_file_name=file_name,
        repository=repository,
        component=triage.get("component") or component,
        severity=triage.get("severity", "Major"),
        priority=triage.get("priority", "P3"),
        is_duplicate=dup.get("is_duplicate", False),
        duplicate_of_id=dup.get("duplicate_bug_id"),
        root_cause=rc.get("detailed_explanation") or rc.get("root_cause_summary"),
        suggested_fix=rem.get("suggested_patch_diff"),
        remediation_steps=mitigation_str,
        parsed_log_json=json.dumps(parsed_log),
        agent_logs_json=json.dumps(steps),
        root_cause_json=json.dumps(rc),
        duplicate_json=json.dumps(dup),
        remediation_json=json.dumps(rem),
        similar_bugs_json=json.dumps(retrieved),
        status="COMPLETED"
    )

    db.add(db_bug)
    await db.commit()
    await db.refresh(db_bug)

    # Format response
    similar_items = [
        HistoricalBugItem(
            bug_id=b.get("bug_id", ""),
            repository=b.get("repository", ""),
            component=b.get("component", ""),
            title=b.get("title", ""),
            description=b.get("description", ""),
            stack_trace=b.get("stack_trace", ""),
            resolution=b.get("resolution", ""),
            similarity_score=b.get("similarity_score", 0.0),
            root_cause=b.get("root_cause"),
            offending_function=b.get("offending_function")
        )
        for b in retrieved
    ]

    return BugSubmissionResponse(
        id=db_bug.id,
        title=db_bug.title,
        description=db_bug.description,
        stack_trace=db_bug.stack_trace,
        environment_details=db_bug.environment_details,
        log_file_name=db_bug.log_file_name,
        repository=db_bug.repository,
        component=db_bug.component,
        severity=db_bug.severity,
        priority=db_bug.priority,
        triage_reasoning=triage.get("triage_reasoning"),
        is_duplicate=db_bug.is_duplicate,
        duplicate_of_id=db_bug.duplicate_of_id,
        root_cause=db_bug.root_cause,
        confidence_score=db_bug.confidence_score,
        suggested_fix=db_bug.suggested_fix,
        remediation_steps=db_bug.remediation_steps,
        status=db_bug.status,
        created_at=db_bug.created_at,
        parsed_log=parsed_log,
        similar_bugs=similar_items,
        workflow_steps=steps,
        root_cause_info=rc,
        duplicate_info=dup,
        remediation_info=rem,
        resolved_at=db_bug.resolved_at,
        verified_resolution=db_bug.verified_resolution,
        is_ingested_to_kb=db_bug.is_ingested_to_kb or False,
        kb_chunk_ids=db_bug.kb_chunk_ids
    )


def _deserialize_similar_bugs(db_bug: BugSubmission, dup_info: Optional[dict]) -> List[HistoricalBugItem]:
    """Helper to reconstruct similar_bugs list from JSON column or duplicate_info candidates."""
    if db_bug.similar_bugs_json:
        try:
            raw = json.loads(db_bug.similar_bugs_json)
            return [
                HistoricalBugItem(
                    bug_id=b.get("bug_id", ""),
                    repository=b.get("repository", ""),
                    component=b.get("component", ""),
                    title=b.get("title", ""),
                    description=b.get("description", ""),
                    stack_trace=b.get("stack_trace", ""),
                    resolution=b.get("resolution", ""),
                    similarity_score=b.get("similarity_score", 0.0),
                    root_cause=b.get("root_cause"),
                    offending_function=b.get("offending_function")
                )
                for b in raw
            ]
        except Exception:
            pass
    if dup_info and dup_info.get("potential_matches"):
        return [
            HistoricalBugItem(
                bug_id=m.get("bug_id", ""),
                repository=m.get("repository", ""),
                component=m.get("component", ""),
                title=m.get("title", ""),
                description="",
                stack_trace=m.get("stack_trace", ""),
                resolution=m.get("resolution", ""),
                similarity_score=m.get("similarity_score", 0.0),
                root_cause=m.get("root_cause"),
                offending_function=None
            )
            for m in dup_info.get("potential_matches", [])
        ]
    return []


@router.get("/submissions", response_model=List[BugSubmissionResponse])
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def list_bug_submissions(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List all submitted defect analysis reports stored in the database.
    """
    result = await db.execute(
        select(BugSubmission).order_by(BugSubmission.created_at.desc()).offset(skip).limit(limit)
    )
    bugs = result.scalars().all()

    response = []
    for db_bug in bugs:
        parsed_log = json.loads(db_bug.parsed_log_json) if db_bug.parsed_log_json else None
        steps = json.loads(db_bug.agent_logs_json) if db_bug.agent_logs_json else []
        rc_info = json.loads(db_bug.root_cause_json) if db_bug.root_cause_json else None
        dup_info = json.loads(db_bug.duplicate_json) if db_bug.duplicate_json else None
        rem_info = json.loads(db_bug.remediation_json) if db_bug.remediation_json else None
        similar_items = _deserialize_similar_bugs(db_bug, dup_info)

        response.append(
            BugSubmissionResponse(
                id=db_bug.id,
                title=db_bug.title,
                description=db_bug.description,
                stack_trace=db_bug.stack_trace,
                environment_details=db_bug.environment_details,
                log_file_name=db_bug.log_file_name,
                repository=db_bug.repository,
                component=db_bug.component,
                severity=db_bug.severity,
                priority=db_bug.priority,
                is_duplicate=db_bug.is_duplicate,
                duplicate_of_id=db_bug.duplicate_of_id,
                root_cause=db_bug.root_cause,
                confidence_score=db_bug.confidence_score,
                suggested_fix=db_bug.suggested_fix,
                remediation_steps=db_bug.remediation_steps,
                status=db_bug.status,
                created_at=db_bug.created_at,
                parsed_log=parsed_log,
                workflow_steps=steps,
                similar_bugs=similar_items,
                root_cause_info=rc_info,
                duplicate_info=dup_info,
                remediation_info=rem_info,
                resolved_at=db_bug.resolved_at,
                verified_resolution=db_bug.verified_resolution,
                is_ingested_to_kb=db_bug.is_ingested_to_kb or False,
                kb_chunk_ids=db_bug.kb_chunk_ids
            )
        )
    return response


@router.get("/submissions/{bug_id}", response_model=BugSubmissionResponse)
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_bug_submission(
    request: Request,
    bug_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analysis report for a single bug submission.
    """
    result = await db.execute(select(BugSubmission).where(BugSubmission.id == bug_id))
    db_bug = result.scalars().first()

    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug submission not found")

    parsed_log = json.loads(db_bug.parsed_log_json) if db_bug.parsed_log_json else None
    steps = json.loads(db_bug.agent_logs_json) if db_bug.agent_logs_json else []
    rc_info = json.loads(db_bug.root_cause_json) if db_bug.root_cause_json else None
    dup_info = json.loads(db_bug.duplicate_json) if db_bug.duplicate_json else None
    rem_info = json.loads(db_bug.remediation_json) if db_bug.remediation_json else None
    similar_items = _deserialize_similar_bugs(db_bug, dup_info)

    return BugSubmissionResponse(
        id=db_bug.id,
        title=db_bug.title,
        description=db_bug.description,
        stack_trace=db_bug.stack_trace,
        environment_details=db_bug.environment_details,
        log_file_name=db_bug.log_file_name,
        repository=db_bug.repository,
        component=db_bug.component,
        severity=db_bug.severity,
        priority=db_bug.priority,
        is_duplicate=db_bug.is_duplicate,
        duplicate_of_id=db_bug.duplicate_of_id,
        root_cause=db_bug.root_cause,
        confidence_score=db_bug.confidence_score,
        suggested_fix=db_bug.suggested_fix,
        remediation_steps=db_bug.remediation_steps,
        status=db_bug.status,
        created_at=db_bug.created_at,
        parsed_log=parsed_log,
        workflow_steps=steps,
        similar_bugs=similar_items,
        root_cause_info=rc_info,
        duplicate_info=dup_info,
        remediation_info=rem_info,
        resolved_at=db_bug.resolved_at,
        verified_resolution=db_bug.verified_resolution,
        is_ingested_to_kb=db_bug.is_ingested_to_kb or False,
        kb_chunk_ids=db_bug.kb_chunk_ids
    )


# Milestone 4: Knowledge Base Growth Endpoints
@router.post("/submissions/{bug_id}/resolve", response_model=ResolveBugResponse)
@limiter.limit("20/minute")
async def resolve_and_ingest_bug(
    request: Request,
    bug_id: str,
    payload: ResolveBugRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Milestone 4: Confirms resolution for a defect and ingests verified root cause
    and fix back into ChromaDB using the 3-Chunk Ingestion Strategy.
    This dynamically grows the Knowledge Base, improving future recommendations.
    """
    result = await db.execute(select(BugSubmission).where(BugSubmission.id == bug_id))
    db_bug = result.scalars().first()

    if not db_bug:
        raise HTTPException(status_code=404, detail=f"Defect with ID {bug_id} not found")

    # Update database record status
    db_bug.status = "RESOLVED"
    db_bug.resolved_at = datetime.now(timezone.utc)
    db_bug.verified_resolution = payload.confirmed_resolution
    db_bug.root_cause = payload.verified_root_cause

    # Determine offending function
    offending_func = payload.offending_function or "N/A"
    if offending_func == "N/A" and db_bug.parsed_log_json:
        try:
            parsed = json.loads(db_bug.parsed_log_json)
            failure_point = parsed.get("failure_point") or {}
            method_name = failure_point.get("method_name")
            if method_name:
                offending_func = method_name
        except Exception:
            pass

    # Build defect payload for ChromaDB ingestion
    defect_record = {
        "bug_id": db_bug.id,
        "repository": db_bug.repository or "Production",
        "component": db_bug.component or "General",
        "title": db_bug.title,
        "description": f"{db_bug.description or ''}\n\nConfirmed Resolution: {payload.confirmed_resolution}".strip(),
        "stack_trace": db_bug.stack_trace or "",
        "offending_function": offending_func,
        "root_cause": payload.verified_root_cause,
        "resolution": payload.confirmed_resolution
    }

    # Ingest 3 dense vector chunks into ChromaDB
    chunks_indexed = vector_store_service.add_defects([defect_record])
    
    chunk_ids = [
        f"{db_bug.id}_chunk1_overview",
        f"{db_bug.id}_chunk2_trace",
        f"{db_bug.id}_chunk3_resolution"
    ]
    
    db_bug.is_ingested_to_kb = True
    db_bug.kb_chunk_ids = json.dumps(chunk_ids)

    await db.commit()
    await db.refresh(db_bug)

    total_count = vector_store_service.collection.count()

    return ResolveBugResponse(
        bug_id=db_bug.id,
        status="RESOLVED",
        is_ingested_to_kb=True,
        indexed_chunks=chunk_ids,
        total_knowledge_base_items=total_count,
        message=f"Defect {bug_id} successfully marked RESOLVED and indexed into ChromaDB ({chunks_indexed} new chunks). Future recommendations will now retrieve this verified fix."
    )


@router.get("/knowledge-base/stats", response_model=KnowledgeBaseStatsResponse)
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
async def get_knowledge_base_stats(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Milestone 4: Returns current status and growth statistics of the Knowledge Base.
    """
    total_chunks = vector_store_service.collection.count()
    
    # Query database for resolved bugs
    result = await db.execute(select(BugSubmission).where(BugSubmission.is_ingested_to_kb == True))
    resolved_bugs = result.scalars().all()

    recent_ingested = []
    for b in resolved_bugs[-10:]:
        recent_ingested.append({
            "bug_id": b.id,
            "title": b.title,
            "component": b.component,
            "resolved_at": b.resolved_at.isoformat() if b.resolved_at else None,
            "verified_resolution": b.verified_resolution[:120] + "..." if b.verified_resolution and len(b.verified_resolution) > 120 else b.verified_resolution
        })

    user_count = len(resolved_bugs)
    # 3 chunks per defect
    total_unique_docs = max(10, total_chunks // 3)
    baseline_count = max(0, total_unique_docs - user_count)

    return KnowledgeBaseStatsResponse(
        total_documents=total_unique_docs,
        total_chunks=total_chunks,
        baseline_defects_count=baseline_count,
        user_resolved_defects_count=user_count,
        recent_ingested_bugs=recent_ingested
    )

