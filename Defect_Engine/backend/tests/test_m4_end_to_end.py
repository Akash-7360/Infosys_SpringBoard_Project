import asyncio
import json
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal, init_db
from app.models.bug_submission import (
    BugSubmission,
    ResolveBugRequest
)
from app.services.vector_store import vector_store_service
from app.services.pattern_analytics import generate_defect_pattern_analytics
from app.agents.orchestrator import run_defect_analysis_pipeline


async def test_m4_defect_pattern_analytics():
    """
    Validates Defect Pattern Analytics Module (M4.1):
    Verifies component distribution, theme classification, systemic hotspots,
    health score, and architectural recommendations.
    """
    await init_db()
    async with AsyncSessionLocal() as session:
        analytics = await generate_defect_pattern_analytics(session)

        assert analytics.total_bugs_analyzed > 0
        assert len(analytics.component_frequencies) > 0
        assert len(analytics.recurring_themes) > 0
        assert 0.0 <= analytics.systemic_health_score <= 100.0
        assert analytics.health_grade in ["A", "B", "C", "D", "F"]
        assert len(analytics.architectural_recommendations) > 0

        # Validate component frequencies structure
        top_comp = analytics.component_frequencies[0]
        assert top_comp.component is not None
        assert top_comp.count > 0
        assert top_comp.risk_level in ["CRITICAL", "HIGH", "MODERATE", "LOW"]

        # Validate recurring theme structure
        top_theme = analytics.recurring_themes[0]
        assert top_theme.theme_id is not None
        assert top_theme.count > 0
        assert top_theme.impact_level in ["CRITICAL", "HIGH", "MODERATE"]


async def test_m4_knowledge_base_growth_and_feedback_loop():
    """
    Validates Knowledge Base Growth Mechanism (M4.2):
    Submits a new defect, resolves it with a verified fix, ingests into ChromaDB,
    and verifies that a subsequent similar defect retrieves this newly learned fix.
    """
    await init_db()
    
    unique_sig = f"TEST-FIX-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    initial_chunks = vector_store_service.collection.count()

    # 1. Run pipeline for a new custom defect
    bug_id = f"BUG-GROWTH-{unique_sig}"
    pipeline_result = await run_defect_analysis_pipeline(
        bug_id=bug_id,
        title=f"Custom connection pool exhaustion in {unique_sig}",
        description="Async connection pool hangs when acquire timeout is exceeded during microservice load.",
        stack_trace="""Traceback (most recent call last):
  File "/app/db/pool.py", line 88, in acquire_connection
    conn = await self._semaphore.acquire(timeout=2.0)
asyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out""",
        raw_log_content="asyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out in pool.py:88",
        environment_details="Python 3.11, asyncpg 0.28.0",
        repository="Microservices",
        component="Database/Storage"
    )

    # 2. Simulate resolving the bug and ingesting into ChromaDB
    confirmed_root_cause = f"Semaphore deadlock due to missing finally release block in pool.py ({unique_sig})"
    confirmed_fix = f"""--- a/app/db/pool.py
+++ b/app/db/pool.py
@@ -88,4 +88,7 @@
+    try:
         conn = await self._semaphore.acquire(timeout=2.0)
+    finally:
+        self._semaphore.release()"""

    defect_record = {
        "bug_id": bug_id,
        "repository": "Microservices",
        "component": "Database/Storage",
        "title": f"Custom connection pool exhaustion in {unique_sig}",
        "description": f"Async connection pool hangs when acquire timeout is exceeded.\nConfirmed Fix: {confirmed_fix}",
        "stack_trace": f"asyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out in pool.py:88 ({unique_sig})",
        "offending_function": "acquire_connection",
        "root_cause": confirmed_root_cause,
        "resolution": confirmed_fix
    }

    try:
        # Ingest 3 chunks into ChromaDB
        chunks_added = vector_store_service.add_defects([defect_record])
        assert chunks_added == 3

        new_total_chunks = vector_store_service.collection.count()
        assert new_total_chunks == initial_chunks + 3

        # 3. Test Retrieval of the Newly Learned Defect
        similar = vector_store_service.search_similar(
            query_text=f"Connection semaphore acquisition timed out in pool.py {unique_sig}",
            top_k=3
        )

        assert len(similar) > 0
        top_match = similar[0]
        assert top_match["bug_id"] == bug_id
        assert top_match["root_cause"] == confirmed_root_cause
        assert top_match["resolution"] == confirmed_fix
        assert top_match["similarity_score"] >= 0.85
    finally:
        # Clean up test chunks to keep test runs idempotent
        try:
            vector_store_service.collection.delete(
                ids=[f"{bug_id}_chunk1_overview", f"{bug_id}_chunk2_trace", f"{bug_id}_chunk3_resolution"]
            )
        except Exception:
            pass


async def test_m4_multi_language_pipeline_coverage():
    """
    Validates end-to-end multi-agent pipeline across varied bug types and stack trace formats (M4.3):
    1. Java Stack Trace
    2. Python Traceback
    3. C++ GDB Backtrace
    4. Go Panic Trace
    """
    test_cases = [
        {
            "lang": "Java",
            "title": "NullPointerException in Kafka batch accumulator",
            "trace": "java.lang.NullPointerException\n\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:234)",
            "expected_sev": "Critical",
            "expected_comp": "Messaging/Queue"
        },
        {
            "lang": "Python",
            "title": "AttributeError in Python AST indexer",
            "trace": "Traceback (most recent call last):\n  File \"/app/indexer.py\", line 45, in parse\n    node.attr.strip()\nAttributeError: 'NoneType' object has no attribute 'strip'",
            "expected_sev": "High",
            "expected_comp": "Core"
        },
        {
            "lang": "C++",
            "title": "GDB Segfault in Gecko frame constructor",
            "trace": "#0  0x00007fff8912ba40 in nsCSSFrameConstructor::ConstructFrame at layout/base/nsCSSFrameConstructor.cpp:6421",
            "expected_sev": "Critical",
            "expected_comp": "Core"
        },
        {
            "lang": "Go",
            "title": "Go goroutine channel panic",
            "trace": "panic: send on closed channel\n\ngoroutine 14 [running]:\nmain.(*Distributor).Dispatch(0xc00010c000)\n\t/app/distributor.go:88 +0x42",
            "expected_sev": "Critical",
            "expected_comp": "Networking"
        }
    ]

    for tc in test_cases:
        res = await run_defect_analysis_pipeline(
            bug_id=f"TEST-{tc['lang']}",
            title=tc["title"],
            description="Testing language parser resilience",
            stack_trace=tc["trace"],
            raw_log_content=tc["trace"],
            environment_details="Unit test env",
            repository="Mozilla/Apache/Eclipse",
            component="General"
        )

        assert res.get("parsed_log") is not None
        assert res.get("triage_info") is not None
        assert res.get("root_cause_info") is not None
        assert res.get("duplicate_info") is not None
        assert res.get("remediation_info") is not None

        # Verify unified diff patch was synthesized
        rem = res["remediation_info"]
        assert "suggested_patch_diff" in rem
        assert "--- a/" in rem["suggested_patch_diff"]
        assert "+++ b/" in rem["suggested_patch_diff"]
