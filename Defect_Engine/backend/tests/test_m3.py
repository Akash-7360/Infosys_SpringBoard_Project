"""
Unit and Integration Tests for Milestone 3 Agents:
- M3.1 Root Cause Agent
- M3.2 Duplicate Detection Agent
- M3.3 Remediation Agent
"""

from app.agents.root_cause_agent import root_cause_agent_node
from app.agents.duplicate_agent import duplicate_agent_node
from app.agents.remediation_agent import remediation_agent_node
from app.agents.orchestrator import run_defect_analysis_pipeline
from app.agents.state import DefectAnalysisState


async def test_m3_duplicate_detection_agent():
    state: DefectAnalysisState = {
        "bug_id": "TEST-DUP-01",
        "raw_title": "NullPointerException in RecordAccumulator drain during high memory batch flush",
        "raw_description": "Kafka Producer crashes when draining batch under buffer exhaustion.",
        "raw_stack_trace": (
            "java.lang.NullPointerException: Cannot invoke 'ProducerBatch.drain()' because 'batch' is null\n"
            "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)"
        ),
        "raw_log_content": "",
        "environment_details": "Kafka 3.4.0",
        "repository": "Apache",
        "component": "Messaging/Queue",
        "parsed_log": {"exception_type": "NullPointerException"},
        "triage_info": {"severity": "High", "priority": "P2", "component": "Messaging/Queue"},
        "duplicate_info": {},
        "root_cause_info": {},
        "remediation_info": {},
        "retrieved_docs": [],
        "status": "PROCESSING",
        "workflow_steps": []
    }

    res = await duplicate_agent_node(state)
    dup_info = res["duplicate_info"]

    assert dup_info["is_duplicate"] is True
    assert dup_info["duplicate_status"] == "Duplicate"
    assert dup_info["duplicate_bug_id"] == "APACHE-KAFKA-10294"
    assert dup_info["highest_similarity_score"] >= 0.88
    assert len(dup_info["potential_matches"]) > 0
    assert len(dup_info["potential_matches"][0]["match_reason"]) > 10


async def test_m3_root_cause_agent():
    state: DefectAnalysisState = {
        "bug_id": "TEST-RC-01",
        "raw_title": "OutOfMemoryError in TaskMemoryManager during shuffle join",
        "raw_description": "Executor crashes with OOM heap space error during shuffle.",
        "raw_stack_trace": (
            "java.lang.OutOfMemoryError: Java heap space\n"
            "\tat org.apache.spark.memory.TaskMemoryManager.allocatePage(TaskMemoryManager.java:298)"
        ),
        "raw_log_content": "",
        "environment_details": "Spark 3.3",
        "repository": "Apache",
        "component": "Core",
        "parsed_log": {
            "exception_type": "OutOfMemoryError",
            "failure_point": {
                "file_name": "TaskMemoryManager.java",
                "method_name": "allocatePage",
                "line_number": 298
            },
            "code_path": ["TaskMemoryManager.allocatePage:298"]
        },
        "triage_info": {"severity": "Critical", "priority": "P1", "component": "Core"},
        "duplicate_info": {},
        "root_cause_info": {},
        "remediation_info": {},
        "retrieved_docs": [],
        "status": "PROCESSING",
        "workflow_steps": []
    }

    res = await root_cause_agent_node(state)
    rc_info = res["root_cause_info"]

    assert "primary_hypothesis" in rc_info
    assert "Heap" in rc_info["primary_failure_mechanism"] or "Exhaustion" in rc_info["primary_failure_mechanism"]
    assert rc_info["confidence_score"] >= 0.80
    assert len(rc_info["agent_reasoning"]) > 20
    assert rc_info["evidence_status"] in ["Direct Match Evidence", "Sufficient Evidence"]


async def test_m3_remediation_agent():
    state: DefectAnalysisState = {
        "bug_id": "TEST-REM-01",
        "raw_title": "NullPointerException in RecordAccumulator drain",
        "raw_description": "Batch is null in drain loop",
        "raw_stack_trace": "",
        "raw_log_content": "",
        "environment_details": "Linux",
        "repository": "Apache",
        "component": "Messaging/Queue",
        "parsed_log": {
            "exception_type": "NullPointerException",
            "failure_point": {
                "file_name": "RecordAccumulator.java",
                "method_name": "drain",
                "line_number": 248
            }
        },
        "triage_info": {"severity": "High", "priority": "P2"},
        "duplicate_info": {
            "is_duplicate": True,
            "duplicate_bug_id": "APACHE-KAFKA-10294"
        },
        "root_cause_info": {
            "primary_hypothesis": "Null Pointer Dereference during batch drain",
            "primary_failure_mechanism": "Null Pointer Dereference & Object De-allocation Race Condition",
            "evidence_status": "Direct Match Evidence"
        },
        "remediation_info": {},
        "retrieved_docs": [{
            "bug_id": "APACHE-KAFKA-10294",
            "similarity_score": 0.95,
            "resolution": "Added explicit null check and synchronized barrier prior to dequeuing ProducerBatch instances during buffer pool eviction."
        }],
        "status": "PROCESSING",
        "workflow_steps": []
    }

    res = await remediation_agent_node(state)
    rem_info = res["remediation_info"]

    assert "suggested_patch_diff" in rem_info
    assert "--- a/RecordAccumulator.java" in rem_info["suggested_patch_diff"]
    assert "+++ b/RecordAccumulator.java" in rem_info["suggested_patch_diff"]
    assert len(rem_info["recommended_fixes"]) >= 1
    assert rem_info["recommended_fixes"][0]["grounding_type"] == "Historical Defect Evidence"
    assert rem_info["is_speculative"] is False
    assert rem_info["technical_recommendations"]["target_module"] == "RecordAccumulator.java:248"


async def test_m3_end_to_end_pipeline():
    result = await run_defect_analysis_pipeline(
        bug_id="TEST-E2E-M3",
        title="NullPointerException in RecordAccumulator drain during flush",
        description="Application crashes under memory pressure",
        stack_trace=(
            "java.lang.NullPointerException: Cannot invoke ProducerBatch.drain() because batch is null\n"
            "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)"
        ),
        raw_log_content="",
        environment_details="Linux OpenJDK 17",
        repository="Apache",
        component="Messaging/Queue"
    )

    assert result["status"] in ["COMPLETED", "PROCESSING"]
    assert "duplicate_info" in result
    assert "root_cause_info" in result
    assert "remediation_info" in result
    assert result["duplicate_info"]["duplicate_status"] == "Duplicate"
    assert "RecordAccumulator" in result["remediation_info"]["suggested_patch_diff"]
