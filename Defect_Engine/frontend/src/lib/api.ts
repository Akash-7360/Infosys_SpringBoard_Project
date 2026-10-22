import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface LogFrameInfo {
  frame_number: number;
  raw_line: string;
  file_path?: string;
  line_number?: number;
  function_name?: string;
  class_name?: string;
  method_name?: string;
  is_app_code: boolean;
}

export interface LogFailurePoint {
  file_name?: string;
  class_name?: string;
  method_name?: string;
  line_number?: number;
  raw_frame?: string;
}

export interface ParsedLog {
  exception_type: string;
  exception_message: string;
  sanitized_trace: string;
  top_offending_frame?: LogFrameInfo;
  failure_point?: LogFailurePoint;
  code_path?: string[];
  log_format?: string;
  confidence_score?: number;
  application_frames: LogFrameInfo[];
  stdlib_frames: LogFrameInfo[];
  noise_lines_removed: number;
}

export interface HistoricalBugItem {
  bug_id: string;
  repository: string;
  component: string;
  title: string;
  description: string;
  stack_trace: string;
  resolution: string;
  similarity_score: number;
  root_cause?: string;
  offending_function?: string;
}

export interface WorkflowStep {
  agent: string;
  timestamp: string;
  summary: string;
}

// -------------------------------------------------------------
// Milestone 3.2: Duplicate Detection Schema
// -------------------------------------------------------------
export interface DuplicateMatchItem {
  bug_id: string;
  title: string;
  repository: string;
  component: string;
  similarity_score: number;
  similarity_category: 'Duplicate Match' | 'Related Issue' | 'Weak Match';
  match_reason: string;
  root_cause?: string;
  resolution?: string;
  stack_trace?: string;
}

export interface DuplicateInfo {
  duplicate_status: 'Duplicate' | 'Related Issue' | 'New / Unmatched Issue';
  is_duplicate: boolean;
  duplicate_bug_id?: string;
  highest_similarity_score: number;
  match_summary: string;
  potential_matches: DuplicateMatchItem[];
  related_bug_ids?: string[];
}

// -------------------------------------------------------------
// Milestone 3.1: Root Cause Analysis Schema
// -------------------------------------------------------------
export interface RootCauseEvidenceItem {
  bug_id: string;
  title: string;
  repository: string;
  component: string;
  similarity_score: number;
  root_cause: string;
  resolution: string;
  relevance_explanation: string;
}

export interface RootCauseInfo {
  primary_hypothesis: string;
  secondary_hypotheses: string[];
  confidence_score: number;
  agent_reasoning: string;
  primary_failure_mechanism: string;
  evidence_status: 'Sufficient Evidence' | 'Insufficient Evidence' | 'Direct Match Evidence';
  supporting_evidence: RootCauseEvidenceItem[];
  root_cause_summary?: string;
  detailed_explanation?: string;
}

// -------------------------------------------------------------
// Milestone 3.3: Remediation Schema
// -------------------------------------------------------------
export interface RemediationApproach {
  title: string;
  approach_type: 'Primary Recommended Fix' | 'Alternative Mitigation' | 'Defensive Fallback';
  description: string;
  confidence_score: number;
  grounding_type: 'Historical Defect Evidence' | 'Best Practice Guideline' | 'Agent Heuristic';
  supporting_historical_bug_id?: string;
  supporting_evidence_summary?: string;
}

export interface TechnicalRecommendations {
  target_module: string;
  code_modifications: string[];
  configuration_changes: string[];
  validation_steps: string[];
  error_handling_improvements: string[];
}

export interface RemediationInfo {
  recommended_fixes: RemediationApproach[];
  suggested_patch_diff: string;
  technical_recommendations?: TechnicalRecommendations;
  step_by_step_mitigation: string[];
  verification_testing_advice: string;
  confidence_score: number;
  evidence_status: 'Sufficient Evidence' | 'Insufficient Evidence' | 'Heuristic Guideline';
  is_speculative: boolean;
}

// -------------------------------------------------------------
// Comprehensive Bug Submission Response
// -------------------------------------------------------------
export interface BugSubmissionResponse {
  id: string;
  title: string;
  description?: string;
  stack_trace?: string;
  environment_details?: string;
  log_file_name?: string;
  repository?: string;
  component?: string;
  severity?: string;
  priority?: string;
  triage_reasoning?: string;
  is_duplicate: boolean;
  duplicate_of_id?: string;
  root_cause?: string;
  confidence_score: number;
  suggested_fix?: string;
  remediation_steps?: string;
  status: string;
  created_at: string;
  parsed_log?: ParsedLog;
  similar_bugs?: HistoricalBugItem[];
  workflow_steps?: WorkflowStep[];

  // Milestone 3 Structured Findings
  root_cause_info?: RootCauseInfo;
  duplicate_info?: DuplicateInfo;
  remediation_info?: RemediationInfo;

  // Milestone 4 Knowledge Base Growth & Resolution Tracking
  resolved_at?: string;
  verified_resolution?: string;
  is_ingested_to_kb?: boolean;
  kb_chunk_ids?: string;
}

// -------------------------------------------------------------
// Milestone 4: Knowledge Base Growth Models
// -------------------------------------------------------------
export interface ResolveBugRequest {
  verified_root_cause: string;
  confirmed_resolution: string;
  offending_function?: string;
  notes?: string;
}

export interface ResolveBugResponse {
  bug_id: string;
  status: string;
  is_ingested_to_kb: boolean;
  indexed_chunks: string[];
  total_knowledge_base_items: number;
  message: string;
}

export interface KnowledgeBaseStatsResponse {
  total_documents: number;
  total_chunks: number;
  baseline_defects_count: number;
  user_resolved_defects_count: number;
  recent_ingested_bugs: Array<{
    bug_id: string;
    title: string;
    component: string;
    resolved_at: string;
    verified_resolution: string;
  }>;
}

// -------------------------------------------------------------
// Milestone 4: Defect Pattern Analytics Models
// -------------------------------------------------------------
export interface ComponentFrequencyItem {
  component: string;
  count: number;
  percentage: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
}

export interface RecurringThemeItem {
  theme_id: string;
  theme_name: string;
  description: string;
  count: number;
  percentage: number;
  impact_level: string;
  sample_exception_types: string[];
  sample_bug_ids: string[];
  representative_failure_mechanism: string;
}

export interface SystemicHotspotItem {
  target: string;
  target_type: string;
  occurrence_count: number;
  associated_components: string[];
  associated_severities: string[];
  primary_failure_pattern: string;
}

export interface ArchitecturalRecommendation {
  theme: string;
  target_components: string;
  actionable_recommendation: string;
  priority: string;
}

export interface SystemicPatternAnalytics {
  total_bugs_analyzed: number;
  total_resolved_bugs: number;
  duplicate_rate_percentage: number;
  systemic_health_score: number;
  health_grade: string;
  summary_insight: string;
  component_frequencies: ComponentFrequencyItem[];
  recurring_themes: RecurringThemeItem[];
  systemic_hotspots: SystemicHotspotItem[];
  architectural_recommendations: ArchitecturalRecommendation[];
}

export interface SimilarBugSearchRequest {
  query_text: string;
  repository?: string;
  component?: string;
  top_k?: number;
}

export interface SimilarBugResponse {
  query: string;
  total_found: number;
  results: HistoricalBugItem[];
}

export const submitBugReport = async (formData: FormData): Promise<BugSubmissionResponse> => {
  const response = await axios.post<BugSubmissionResponse>(`${API_BASE_URL}/bugs/submit`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const searchSimilarBugs = async (req: SimilarBugSearchRequest): Promise<SimilarBugResponse> => {
  const response = await axios.post<SimilarBugResponse>(`${API_BASE_URL}/bugs/search-similar`, req);
  return response.data;
};

export const getSubmissionsList = async (): Promise<BugSubmissionResponse[]> => {
  const response = await axios.get<BugSubmissionResponse[]>(`${API_BASE_URL}/bugs/submissions`);
  return response.data;
};

export const getSubmissionById = async (id: string): Promise<BugSubmissionResponse> => {
  const response = await axios.get<BugSubmissionResponse>(`${API_BASE_URL}/bugs/submissions/${id}`);
  return response.data;
};

export const resolveAndIngestBug = async (
  bugId: string,
  req: ResolveBugRequest
): Promise<ResolveBugResponse> => {
  const response = await axios.post<ResolveBugResponse>(
    `${API_BASE_URL}/bugs/submissions/${bugId}/resolve`,
    req
  );
  return response.data;
};

export const getKnowledgeBaseStats = async (): Promise<KnowledgeBaseStatsResponse> => {
  const response = await axios.get<KnowledgeBaseStatsResponse>(`${API_BASE_URL}/bugs/knowledge-base/stats`);
  return response.data;
};

export const getPatternAnalytics = async (): Promise<SystemicPatternAnalytics> => {
  const response = await axios.get<SystemicPatternAnalytics>(`${API_BASE_URL}/bugs/analytics/patterns`);
  return response.data;
};

