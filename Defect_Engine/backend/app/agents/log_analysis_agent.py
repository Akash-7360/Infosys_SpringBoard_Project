from datetime import datetime, timezone
from typing import Dict, Any
from app.agents.state import DefectAnalysisState
from app.services.log_parser import parse_and_sanitize_logs


async def log_analysis_agent_node(state: DefectAnalysisState) -> Dict[str, Any]:
    """
    Log Analysis Agent Node:
    De-noises raw logs, extracts exception type, failure point (file, class, method, line),
    code path call stack sequence, format detection, and confidence score.
    """
    raw_log = state.get("raw_log_content", "")
    raw_trace = state.get("raw_stack_trace", "")
    
    parsed = parse_and_sanitize_logs(raw_log, raw_trace)
    parsed_dict = parsed.model_dump()

    failure_loc = "Unknown Location"
    if parsed.failure_point:
        fp = parsed.failure_point
        failure_loc = f"{fp.file_name or 'UnknownFile'}:{fp.line_number or '?'}"

    step_log = {
        "agent": "LogAnalysisAgent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": (
            f"Extracted '{parsed.exception_type}' ({parsed.log_format} format). "
            f"Failure Point: {failure_loc} ({parsed.failure_point.method_name if parsed.failure_point else 'N/A'}). "
            f"Confidence: {int(parsed.confidence_score * 100)}%."
        )
    }

    steps = list(state.get("workflow_steps", []))
    steps.append(step_log)

    return {
        "parsed_log": parsed_dict,
        "workflow_steps": steps
    }

