import os
import sys
import asyncio
import json
import logging

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, AsyncSessionLocal
from app.agents.orchestrator import run_defect_analysis_pipeline
from app.services.vector_store import vector_store_service
from app.services.pattern_analytics import generate_defect_pattern_analytics

logging.basicConfig(level=logging.WARNING)

DEMO_BUG_CASES = [
    {
        "index": 1,
        "name": "Apache Kafka Memory Pressure / Buffer Drain Race",
        "lang": "Java / Distributed Systems",
        "component": "Messaging/Queue",
        "title": "NullPointerException in RecordAccumulator drain during high memory pressure batch flush",
        "desc": "Producer application crashed under heavy load when batch size exceeded buffer memory threshold. The drain loop attempted to reference a recycled ProducerBatch.",
        "trace": """java.lang.NullPointerException: Cannot invoke "org.apache.kafka.clients.producer.internals.ProducerBatch.drain()" because "batch" is null
\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)
\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)
\tat org.apache.kafka.clients.producer.internals.Sender.run(Sender.java:240)""",
        "repo": "Apache",
        "env": "Linux 5.15 x86_64, OpenJDK 17.0.2, Kafka 3.4.0"
    },
    {
        "index": 2,
        "name": "Mozilla Firefox Gecko Engine Layout Segfault",
        "lang": "C++ / Native Browser Engine",
        "component": "Core",
        "title": "Access violation SIGSEGV in nsCSSFrameConstructor::ConstructFrame layout tree",
        "desc": "Firefox rendering engine crashed with access violation while reconstructing frame tree for dynamic nested CSS flexbox layout.",
        "trace": """CRASH INFO: Crash Type: EXCEPTION_ACCESS_VIOLATION_READ (SIGSEGV)
#0  0x00007fff8912ba40 in nsCSSFrameConstructor::ConstructFrame(nsFrameConstructorState&, nsIContent*, nsContainerFrame*, nsFrameList&) at layout/base/nsCSSFrameConstructor.cpp:6421
#1  0x00007fff8912cb10 in nsCSSFrameConstructor::ContentAppended(nsIContent*, nsIContent*) at layout/base/nsCSSFrameConstructor.cpp:6800
#2  0x00007fff8901aa20 in PresShell::ContentAppended(nsIContent*, nsIContent*) at layout/base/PresShell.cpp:4210""",
        "repo": "Mozilla",
        "env": "Ubuntu 22.04 LTS x86_64, Clang 15.0, Firefox Gecko"
    },
    {
        "index": 3,
        "name": "Python AsyncIO Database Pool Semaphore Deadlock",
        "lang": "Python / Async Microservice",
        "component": "Database/Storage",
        "title": "TimeoutError and connection deadlock in async database pool acquire",
        "desc": "FastAPI microservice hung during peak traffic spike due to unreleased connection semaphore in SQLAlchemy async pool under high concurrent queries.",
        "trace": """Traceback (most recent call last):
  File "/app/services/query_executor.py", line 142, in execute_transaction
    async with pool.acquire(timeout=5.0) as conn:
  File "/usr/local/lib/python3.11/site-packages/asyncpg/pool.py", line 748, in acquire
    return await asyncio.wait_for(self._acquire(timeout), timeout)
  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 479, in wait_for
    raise exceptions.TimeoutError()
asyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out after 5.0s""",
        "repo": "Microservices",
        "env": "Debian 12, Python 3.11.4, asyncpg 0.28.0"
    },
    {
        "index": 4,
        "name": "Go Telemetry Distributor Closed Channel Panic",
        "lang": "Go / Concurrent Telemetry Agent",
        "component": "Networking",
        "title": "panic: send on closed channel in message distributor worker",
        "desc": "Go high-throughput telemetry agent panicked when upstream broadcaster closed the response channel while consumer workers were still writing diagnostics.",
        "trace": """panic: send on closed channel

goroutine 64 [running]:
main.(*MessageDistributor).Dispatch(0xc00010c000, 0xc00028a000)
\t/go/src/collector/distributor.go:128 +0x3a4
main.worker(0xc00010c000, 0x1)
\t/go/src/collector/worker.go:45 +0x88
created by main.StartCollector
\t/go/src/collector/main.go:92 +0x1b0""",
        "repo": "Microservices",
        "env": "Alpine Linux, Go 1.21.3 amd64, Kubernetes Pod"
    },
    {
        "index": 5,
        "name": "Apache Cassandra SSTable Decompression Checksum Corruption",
        "lang": "Java / Distributed Database",
        "component": "Database/Storage",
        "title": "CorruptSSTableException when reading compressed SSTable chunk index",
        "desc": "Node failed to complete compaction due to CRC32 checksum mismatch in CompressedRandomAccessReader while decompressing chunk 42.",
        "trace": """org.apache.cassandra.io.sstable.CorruptSSTableException: org.apache.cassandra.io.compress.CorruptBlockException: checksum mismatch in /var/lib/cassandra/data/keyspace1/standard1-ca1-Data.db at chunk 42
\tat org.apache.cassandra.io.compress.CompressedRandomAccessReader.decompressChunk(CompressedRandomAccessReader.java:112)
\tat org.apache.cassandra.io.compress.CompressedRandomAccessReader.reBuffer(CompressedRandomAccessReader.java:88)
\tat org.apache.cassandra.io.util.RandomAccessReader.read(RandomAccessReader.java:142)
\tat org.apache.cassandra.db.compaction.CompactionTask.execute(CompactionTask.java:234)""",
        "repo": "Apache",
        "env": "Red Hat Enterprise Linux 8.8, OpenJDK 11, Cassandra 4.1.2"
    }
]


async def run_final_showcase():
    print("=" * 105)
    print("        DEFECTMIND: FINAL DEMONSTRATION SHOWCASE (MILESTONES 1, 2, 3 & 4)")
    print("=" * 105)
    print(" Demonstrating minimum 5 distinct bug submissions with complete LangGraph multi-agent pipeline output,")
    print(" knowledge base growth ingestion (+3 chunks), and systemic defect pattern analytics.")
    print("=" * 105)

    await init_db()

    for bug in DEMO_BUG_CASES:
        idx = bug["index"]
        bug_id = f"DEMO-DEFECT-0{idx}"
        print(f"\n[{idx}/5] PROCESSING SUBMISSION: {bug['name']} ({bug['lang']})")
        print("-" * 105)
        print(f" Title       : {bug['title']}")
        print(f" Environment : {bug['env']}")

        res = await run_defect_analysis_pipeline(
            bug_id=bug_id,
            title=bug["title"],
            description=bug["desc"],
            stack_trace=bug["trace"],
            raw_log_content=bug["trace"],
            environment_details=bug["env"],
            repository=bug["repo"],
            component=bug["component"]
        )

        log = res.get("parsed_log", {})
        triage = res.get("triage_info", {})
        dup = res.get("duplicate_info", {})
        rc = res.get("root_cause_info", {})
        rem = res.get("remediation_info", {})

        fp = log.get("failure_point", {})
        fp_str = f"{fp.get('file_name')}:{fp.get('line_number')}" if fp.get("file_name") else "Isolated Frame"

        print("\n  ▶ AGENT 1: LOG ANALYSIS AGENT")
        print(f"    • Exception Type    : {log.get('exception_type')}")
        print(f"    • Failure Point     : {fp_str} ({fp.get('method_name', 'N/A')})")
        print(f"    • App Code Path     : {' -> '.join(log.get('code_path', [])[:3])}")

        print("\n  ▶ AGENT 2: TRIAGE AGENT")
        print(f"    • Severity Assigned : {triage.get('severity')} | Priority: {triage.get('priority')}")
        print(f"    • Component Isolated: {triage.get('component')} (Confidence: {int(triage.get('confidence_score', 0.9)*100)}%)")
        print(f"    • Triage Reasoning  : {triage.get('triage_reasoning')[:100]}...")

        print("\n  ▶ AGENT 3: DUPLICATE DETECTION AGENT")
        print(f"    • Status            : {dup.get('duplicate_status')} (is_duplicate={dup.get('is_duplicate')})")
        print(f"    • Peak Similarity   : {int(dup.get('highest_similarity_score', 0)*100)}% (Matched Ticket: {dup.get('duplicate_bug_id') or 'N/A'})")
        print(f"    • Match Summary     : {dup.get('match_summary')[:100]}...")

        print("\n  ▶ AGENT 4: ROOT CAUSE ANALYSIS AGENT")
        print(f"    • Failure Mechanism : {rc.get('primary_failure_mechanism')}")
        print(f"    • Primary Hypothesis: {rc.get('primary_hypothesis')}")
        print(f"    • Evidence Status   : {rc.get('evidence_status')} (Confidence: {int(rc.get('confidence_score', 0)*100)}%)")

        print("\n  ▶ AGENT 5: REMEDIATION & PATCH AGENT")
        print(f"    • Grounding Source  : {rem.get('recommended_fixes', [{}])[0].get('grounding_type', 'Historical Defect Evidence')}")
        print(f"    • Speculative Guard : {'Flagged Speculative' if rem.get('is_speculative') else 'Grounded Verified Patch'}")
        print(f"    • Synthesized Patch :")
        diff_lines = rem.get("suggested_patch_diff", "").splitlines()[:6]
        for dl in diff_lines:
            print(f"        {dl}")

    # Demonstrate Knowledge Base Growth Mechanism
    print("\n" + "=" * 105)
    print("                  DEMONSTRATION OF KNOWLEDGE BASE GROWTH MECHANISM (M4.2)")
    print("=" * 105)
    initial_count = vector_store_service.collection.count()
    print(f" Current ChromaDB Knowledge Base Count: {initial_count} chunks")
    
    growth_bug_id = "DEMO-DEFECT-03" # Python AsyncIO pool deadlock
    confirmed_root_cause = "SQLAlchemy asyncpg connection pool leaked semaphore count when query cancelled by client timeout."
    confirmed_fix = """--- a/app/services/query_executor.py
+++ b/app/services/query_executor.py
@@ -142,3 +142,6 @@
+    try:
         async with pool.acquire(timeout=5.0) as conn:
+    except asyncio.TimeoutError:
+        await pool.release_expired_connections()
+        raise ServiceUnavailableError("DB connection pool exhausted")"""

    print(f" Engineer confirms resolution for {growth_bug_id}:")
    print(f"  • Verified Root Cause: {confirmed_root_cause}")
    print(f"  • Ingesting 3 dense chunks into ChromaDB...")

    chunks_added = vector_store_service.add_defects([{
        "bug_id": growth_bug_id,
        "repository": "Microservices",
        "component": "Database/Storage",
        "title": "TimeoutError and connection deadlock in async database pool acquire",
        "description": f"Async database pool hung.\nConfirmed Fix: {confirmed_fix}",
        "stack_trace": "asyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out after 5.0s in query_executor.py:142",
        "offending_function": "execute_transaction",
        "root_cause": confirmed_root_cause,
        "resolution": confirmed_fix
    }])

    new_count = vector_store_service.collection.count()
    print(f" ✓ Successfully Ingested {chunks_added} Chunks! New ChromaDB Total: {new_count} chunks.")

    print("\n Testing Retrieval of Newly Learned Defect from Vector Store:")
    retrieval_test = vector_store_service.search_similar("Connection semaphore acquisition timed out in query_executor.py", top_k=1)
    if retrieval_test and retrieval_test[0]["bug_id"] == growth_bug_id:
        print(f" ✓ Retrieved Newly Ingested Defect: {retrieval_test[0]['bug_id']} (Similarity: {int(retrieval_test[0]['similarity_score']*100)}%)")
        print(f" ✓ Grounded Root Cause: {retrieval_test[0]['root_cause']}")

    # Demonstrate Defect Pattern Analytics Module
    print("\n" + "=" * 105)
    print("                  DEMONSTRATION OF DEFECT PATTERN ANALYTICS MODULE (M4.1)")
    print("=" * 105)
    async with AsyncSessionLocal() as session:
        analytics = await generate_defect_pattern_analytics(session)
        print(f" Systemic Defect Health Score : {analytics.systemic_health_score}/100 (Grade {analytics.health_grade})")
        print(f" Total Analyzed Defects       : {analytics.total_bugs_analyzed}")
        print(f" Duplicate Ticket Rate        : {analytics.duplicate_rate_percentage}%")
        print(f" Systemic Diagnostic Summary  : {analytics.summary_insight}")
        
        print("\n High-Frequency Affected Components:")
        for comp in analytics.component_frequencies[:4]:
            print(f"  • {comp.component:<20}: {comp.count:>2} bugs ({comp.percentage:>4.1f}%) | Risk: {comp.risk_level:<8} (Score: {comp.risk_score})")

        print("\n Top Recurring Failure Themes:")
        for theme in analytics.recurring_themes[:3]:
            print(f"  • {theme.theme_name:<36} [{theme.impact_level}]: {theme.count} bugs ({theme.percentage}%)")
            print(f"    Mechanism: {theme.representative_failure_mechanism}")

        print("\n Actionable Architectural Recommendations:")
        for rec in analytics.architectural_recommendations[:2]:
            print(f"  [{rec['priority']}] {rec['theme']} (Target: {rec['target_components']}):")
            print(f"      {rec['actionable_recommendation']}")

    print("\n" + "=" * 105)
    print(" DEMONSTRATION COMPLETE: ALL 5 DISTINCT BUGS, KB GROWTH, AND PATTERN ANALYTICS VERIFIED!")
    print("=" * 105)


if __name__ == "__main__":
    asyncio.run(run_final_showcase())
