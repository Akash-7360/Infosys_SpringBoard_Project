from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Float, Boolean
from pydantic import BaseModel, Field, ConfigDict
from app.core.database import Base


class BugSubmission(Base):
    __tablename__ = "bug_submissions"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    environment_details = Column(Text, nullable=True)
    log_file_name = Column(String(255), nullable=True)
    repository = Column(String(100), nullable=True, default="Mozilla/Apache/Eclipse")
    
    # Analysis & Triage Results
    component = Column(String(100), nullable=True, index=True)
    severity = Column(String(50), nullable=True, default="Unclassified")
    priority = Column(String(50), nullable=True, default="P3")
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(String(100), nullable=True)
    
    # Root cause & patch
    root_cause = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True, default=0.0)
    suggested_fix = Column(Text, nullable=True)
    remediation_steps = Column(Text, nullable=True)
    
    # Serialization of complex structures
    parsed_log_json = Column(Text, nullable=True)
    agent_logs_json = Column(Text, nullable=True)
    root_cause_json = Column(Text, nullable=True)
    duplicate_json = Column(Text, nullable=True)
    remediation_json = Column(Text, nullable=True)
    similar_bugs_json = Column(Text, nullable=True)
    
    # Milestone 4: Knowledge Base Growth & Resolution Tracking
    status = Column(String(50), default="PENDING", index=True)
    resolved_at = Column(DateTime, nullable=True)
    verified_resolution = Column(Text, nullable=True)
    is_ingested_to_kb = Column(Boolean, default=False)
    kb_chunk_ids = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# Pydantic Schemas
class BugSubmissionCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "NullPointer Exception in Kafka RecordAccumulator during flush"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Application crashed when high throughput batch flush occurs under memory pressure."})
    stack_trace: Optional[str] = Field(None, json_schema_extra={"example": "java.lang.NullPointerException\n\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:234)"})
    environment_details: Optional[str] = Field(None, json_schema_extra={"example": "Linux 5.15 x86_64, OpenJDK 17.0.2, Kafka 3.4.0"})
    repository: Optional[str] = Field("Apache", json_schema_extra={"example": "Apache"})
    component: Optional[str] = Field("Core", json_schema_extra={"example": "Core"})


class HistoricalBugItem(BaseModel):
    bug_id: str
    repository: str
    component: str
    title: str
    description: str
    stack_trace: str
    resolution: str
    similarity_score: float
    root_cause: Optional[str] = None
    offending_function: Optional[str] = None


class SimilarBugSearchRequest(BaseModel):
    query_text: str
    repository: Optional[str] = None
    component: Optional[str] = None
    top_k: int = 5


class SimilarBugResponse(BaseModel):
    query: str
    total_found: int
    results: List[HistoricalBugItem]


class BugSubmissionResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    stack_trace: Optional[str] = None
    environment_details: Optional[str] = None
    log_file_name: Optional[str] = None
    repository: Optional[str] = None
    component: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    triage_reasoning: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of_id: Optional[str] = None
    root_cause: Optional[str] = None
    confidence_score: float = 0.0
    suggested_fix: Optional[str] = None
    remediation_steps: Optional[str] = None
    status: str
    created_at: datetime
    parsed_log: Optional[Dict[str, Any]] = None
    similar_bugs: Optional[List[HistoricalBugItem]] = None
    workflow_steps: Optional[List[Dict[str, Any]]] = None

    # M3 Structured Agent Outputs
    root_cause_info: Optional[Dict[str, Any]] = None
    duplicate_info: Optional[Dict[str, Any]] = None
    remediation_info: Optional[Dict[str, Any]] = None

    # M4 Knowledge Base Growth Status
    resolved_at: Optional[datetime] = None
    verified_resolution: Optional[str] = None
    is_ingested_to_kb: bool = False
    kb_chunk_ids: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Milestone 4: Knowledge Base Growth Models
class ResolveBugRequest(BaseModel):
    verified_root_cause: str = Field(..., description="Confirmed root cause explanation from engineer")
    confirmed_resolution: str = Field(..., description="Confirmed code patch, configuration fix, or solution")
    offending_function: Optional[str] = Field(None, description="Offending function/method isolated during fix")
    notes: Optional[str] = Field(None, description="Additional triage or postmortem notes")


class ResolveBugResponse(BaseModel):
    bug_id: str
    status: str
    is_ingested_to_kb: bool
    indexed_chunks: List[str]
    total_knowledge_base_items: int
    message: str


class KnowledgeBaseStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    baseline_defects_count: int
    user_resolved_defects_count: int
    recent_ingested_bugs: List[Dict[str, Any]]


# Milestone 4: Defect Pattern Analytics Models
class ComponentFrequencyItem(BaseModel):
    component: str
    count: int
    percentage: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    risk_score: float
    risk_level: str  # "CRITICAL", "HIGH", "MODERATE", "LOW"


class RecurringThemeItem(BaseModel):
    theme_id: str
    theme_name: str
    description: str
    count: int
    percentage: float
    impact_level: str
    sample_exception_types: List[str]
    sample_bug_ids: List[str]
    representative_failure_mechanism: str


class SystemicHotspotItem(BaseModel):
    target: str  # e.g., "RecordAccumulator.java:234" or "org.apache.kafka.clients.producer"
    target_type: str  # "file", "method", "package"
    occurrence_count: int
    associated_components: List[str]
    associated_severities: List[str]
    primary_failure_pattern: str


class SystemicPatternAnalytics(BaseModel):
    total_bugs_analyzed: int
    total_resolved_bugs: int
    duplicate_rate_percentage: float
    systemic_health_score: float  # 0 to 100
    health_grade: str  # "A", "B", "C", "D", "F"
    summary_insight: str
    component_frequencies: List[ComponentFrequencyItem]
    recurring_themes: List[RecurringThemeItem]
    systemic_hotspots: List[SystemicHotspotItem]
    architectural_recommendations: List[Dict[str, str]]


