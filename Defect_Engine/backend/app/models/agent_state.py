from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class LogFrameInfo(BaseModel):
    frame_number: int
    raw_line: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    is_app_code: bool = True


class LogFailurePoint(BaseModel):
    file_name: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    line_number: Optional[int] = None
    raw_frame: str = ""


class ParsedLogResult(BaseModel):
    exception_type: str = "UnknownException"
    exception_message: str = ""
    sanitized_trace: str = ""
    top_offending_frame: Optional[LogFrameInfo] = None
    failure_point: Optional[LogFailurePoint] = None
    code_path: List[str] = []
    log_format: str = "Unstructured"
    confidence_score: float = 0.5
    application_frames: List[LogFrameInfo] = []
    stdlib_frames: List[LogFrameInfo] = []
    noise_lines_removed: int = 0


class TriageAgentOutput(BaseModel):
    severity: Literal["Critical", "High", "Medium", "Low"] = Field("High", description="Critical, High, Medium, or Low")
    priority: Literal["P1", "P2", "P3", "P4"] = Field("P2", description="P1 (Urgent) to P4 (Low)")
    component: str = Field("General", description="System component or module name")
    confidence_score: float = Field(0.85, description="Confidence score between 0.0 and 1.0")
    triage_reasoning: str = ""


# -------------------------------------------------------------
# Milestone 3.2: Duplicate Detection Schemas
# -------------------------------------------------------------
class DuplicateMatchItem(BaseModel):
    bug_id: str
    title: str
    repository: str = "General"
    component: str = "General"
    similarity_score: float = 0.0
    similarity_category: Literal["Duplicate Match", "Related Issue", "Weak Match"] = "Related Issue"
    match_reason: str = ""
    root_cause: str = ""
    resolution: str = ""
    stack_trace: str = ""


class DuplicateAgentOutput(BaseModel):
    duplicate_status: Literal["Duplicate", "Related Issue", "New / Unmatched Issue"] = "New / Unmatched Issue"
    is_duplicate: bool = False
    duplicate_bug_id: Optional[str] = None
    highest_similarity_score: float = 0.0
    match_summary: str = ""
    potential_matches: List[DuplicateMatchItem] = []
    related_bug_ids: List[str] = []


# -------------------------------------------------------------
# Milestone 3.1: Root Cause Analysis Schemas
# -------------------------------------------------------------
class RootCauseEvidenceItem(BaseModel):
    bug_id: str
    title: str
    repository: str = "General"
    component: str = "General"
    similarity_score: float = 0.0
    root_cause: str = ""
    resolution: str = ""
    relevance_explanation: str = ""


class RootCauseAgentOutput(BaseModel):
    primary_hypothesis: str = ""
    secondary_hypotheses: List[str] = []
    confidence_score: float = 0.0
    agent_reasoning: str = ""
    primary_failure_mechanism: str = ""
    evidence_status: Literal["Sufficient Evidence", "Insufficient Evidence", "Direct Match Evidence"] = "Sufficient Evidence"
    supporting_evidence: List[RootCauseEvidenceItem] = []
    root_cause_summary: str = ""  # backwards compatibility
    detailed_explanation: str = ""  # backwards compatibility


# -------------------------------------------------------------
# Milestone 3.3: Remediation Schemas
# -------------------------------------------------------------
class RemediationApproach(BaseModel):
    title: str
    approach_type: Literal["Primary Recommended Fix", "Alternative Mitigation", "Defensive Fallback"] = "Primary Recommended Fix"
    description: str
    confidence_score: float = 0.85
    grounding_type: Literal["Historical Defect Evidence", "Best Practice Guideline", "Agent Heuristic"] = "Historical Defect Evidence"
    supporting_historical_bug_id: Optional[str] = None
    supporting_evidence_summary: Optional[str] = None


class TechnicalRecommendations(BaseModel):
    target_module: str = ""
    code_modifications: List[str] = []
    configuration_changes: List[str] = []
    validation_steps: List[str] = []
    error_handling_improvements: List[str] = []


class RemediationAgentOutput(BaseModel):
    recommended_fixes: List[RemediationApproach] = []
    suggested_patch_diff: str = ""
    technical_recommendations: Optional[TechnicalRecommendations] = None
    step_by_step_mitigation: List[str] = []
    verification_testing_advice: str = ""
    confidence_score: float = 0.85
    evidence_status: Literal["Sufficient Evidence", "Insufficient Evidence", "Heuristic Guideline"] = "Sufficient Evidence"
    is_speculative: bool = False


