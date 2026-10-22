"""
Unit & Integration Tests for Milestone 2: Triage Agent, Log Analysis Agent, and Multi-Agent Orchestration.
"""

from app.services.log_parser import parse_and_sanitize_logs, extract_exception_info, parse_stack_frames

from app.agents.log_analysis_agent import log_analysis_agent_node
from app.agents.triage_agent import triage_agent_node
from app.agents.orchestrator import run_defect_analysis_pipeline
from app.agents.state import DefectAnalysisState


async def test_java_log_parser_and_failure_point():
    raw_trace = (
        "java.lang.NullPointerException: Cannot invoke ProducerBatch.drain() because batch is null\n"
        "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)\n"
        "\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)"
    )
    result = parse_and_sanitize_logs("", raw_trace)
    
    assert result.exception_type == "NullPointerException"
    assert result.log_format == "Java"
    assert result.confidence_score >= 0.90
    assert result.failure_point is not None
    assert result.failure_point.file_name == "RecordAccumulator.java"
    assert result.failure_point.line_number == 248
    assert result.failure_point.method_name == "drain"
    assert len(result.code_path) >= 2


async def test_python_log_parser_and_failure_point():
    raw_trace = (
        'Traceback (most recent call last):\n'
        '  File "app/services/metrics.py", line 87, in aggregate_scores\n'
        '    total += item["score"]\n'
        'TypeError: unsupported operand type(s) for +: "int" and "str"'
    )
    result = parse_and_sanitize_logs("", raw_trace)
    
    assert result.exception_type == "TypeError"
    assert result.log_format == "Python"
    assert result.failure_point is not None
    assert result.failure_point.file_name == "metrics.py"
    assert result.failure_point.line_number == 87
    assert result.failure_point.method_name == "aggregate_scores"


async def test_triage_agent_critical_classification():
    state: DefectAnalysisState = {
        "bug_id": "TEST-CRITICAL-01",
        "raw_title": "OutOfMemoryError in TaskMemoryManager during shuffle join",
        "raw_description": "Executor crashed with OOM",
        "raw_stack_trace": "java.lang.OutOfMemoryError: Java heap space",
        "raw_log_content": "",
        "environment_details": "Production",
        "repository": "Apache",
        "component": "General",
        "parsed_log": {"exception_type": "OutOfMemoryError"},
        "triage_info": {},
        "duplicate_info": {},
        "root_cause_info": {},
        "remediation_info": {},
        "retrieved_docs": [],
        "status": "PROCESSING",
        "workflow_steps": []
    }
    
    res = await triage_agent_node(state)
    triage_info = res["triage_info"]
    
    assert triage_info["severity"] == "Critical"
    assert triage_info["priority"] == "P1"
    assert triage_info["confidence_score"] >= 0.90
    assert len(triage_info["triage_reasoning"]) > 0


async def test_multi_agent_orchestrator_pipeline_resilience():
    # Test execution with messy log input
    state_result = await run_defect_analysis_pipeline(
        bug_id="TEST-ORCH-01",
        title="Unexpected service shutdown under memory load",
        description="Daemon process stopped responding",
        stack_trace="",
        raw_log_content="[14002.41] kernel: Out of memory: Kill process 1892 (python3)",
        environment_details="Linux 5.15 x86_64",
        repository="Core",
        component="Core"
    )
    
    assert state_result["status"] in ["COMPLETED", "PROCESSING"]
    assert "triage_info" in state_result
    assert "parsed_log" in state_result
    assert state_result["triage_info"]["severity"] in ["Critical", "High", "Medium", "Low"]
