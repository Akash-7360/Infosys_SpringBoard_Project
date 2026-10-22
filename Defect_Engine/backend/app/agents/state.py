from typing import TypedDict, List, Dict, Any, Optional


class DefectAnalysisState(TypedDict):
    bug_id: str
    raw_title: str
    raw_description: str
    raw_stack_trace: str
    raw_log_content: str
    environment_details: str
    repository: str
    component: str

    # Agent step outputs
    parsed_log: Dict[str, Any]
    triage_info: Dict[str, Any]
    duplicate_info: Dict[str, Any]
    root_cause_info: Dict[str, Any]
    remediation_info: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]

    # Process execution metadata
    status: str
    workflow_steps: List[Dict[str, Any]]
