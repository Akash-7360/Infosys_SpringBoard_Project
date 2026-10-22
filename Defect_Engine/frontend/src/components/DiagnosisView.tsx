'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Cpu,
  Layers,
  CheckCircle2,
  FileCode2,
  AlertTriangle,
  AlertCircle,
  Activity,
  Award,
  Copy,
  Check,
  GitCommit,
  GitPullRequest,
  Download,
  Terminal,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Info,
  Wrench,
  Search,
  Database,
  BookOpen,
  ArrowUpRight,
  CheckCheck,
  RefreshCw,
  SlidersHorizontal,
  FolderGit2,
  HelpCircle,
  Code2
} from 'lucide-react';
import { BugSubmissionResponse, resolveAndIngestBug } from '@/lib/api';

interface DiagnosisViewProps {
  report: BugSubmissionResponse;
  onResolved?: (updatedReport: BugSubmissionResponse) => void;
}

export type SectionKey =
  | 'all'
  | 'log_analysis'
  | 'triage'
  | 'duplicates'
  | 'root_cause'
  | 'remediation'
  | 'kb_growth'
  | 'timeline';

interface AgentMeta {
  id: SectionKey;
  stepNum: number;
  name: string;
  shortRole: string;
  plainExplanation: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
  badgeBg: string;
}

const AGENTS: AgentMeta[] = [
  {
    id: 'log_analysis',
    stepNum: 1,
    name: 'Log Analysis Agent',
    shortRole: 'Log Sanitizer & Frame Isolator',
    plainExplanation:
      'Removes timestamps and framework runtime noise to pinpoint the exact application file, line number, and execution sequence leading to the crash.',
    icon: Terminal,
    accentColor: 'text-cyan-600 dark:text-cyan-400',
    badgeBg: 'bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 border-cyan-500/30'
  },
  {
    id: 'triage',
    stepNum: 2,
    name: 'Triage Agent',
    shortRole: 'Severity & Priority Evaluator',
    plainExplanation:
      'Evaluates operational blast radius to classify Severity (Critical/High/Medium/Low), Priority (P1–P4), and the affected subsystem.',
    icon: ShieldAlert,
    accentColor: 'text-amber-600 dark:text-amber-400',
    badgeBg: 'bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/30'
  },
  {
    id: 'duplicates',
    stepNum: 3,
    name: 'Duplicate Detection Agent',
    shortRole: 'ChromaDB Dense Vector RAG',
    plainExplanation:
      'Compares the crash against historical defect memory using vector cosine similarity. Any ticket with ≥88% similarity is flagged as a duplicate to save hours of investigation.',
    icon: Search,
    accentColor: 'text-purple-600 dark:text-purple-400',
    badgeBg: 'bg-purple-500/10 text-purple-700 dark:text-purple-300 border-purple-500/30'
  },
  {
    id: 'root_cause',
    stepNum: 4,
    name: 'Root Cause Agent',
    shortRole: 'Deductive Diagnostic Engine',
    plainExplanation:
      'Deduces the exact physical failure mechanism (e.g., race condition, heap exhaustion). Separates deductive hypotheses from retrieved facts to eliminate hallucinations.',
    icon: Cpu,
    accentColor: 'text-indigo-600 dark:text-indigo-400',
    badgeBg: 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/30'
  },
  {
    id: 'remediation',
    stepNum: 5,
    name: 'Remediation Agent',
    shortRole: 'Code Patch & Fix Architect',
    plainExplanation:
      'Synthesizes a production-ready unified git diff patch targeting the exact failing line and provides concrete 4-pillar architectural fix guidance.',
    icon: Wrench,
    accentColor: 'text-emerald-600 dark:text-emerald-400',
    badgeBg: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
  }
];

export const DiagnosisView: React.FC<DiagnosisViewProps> = ({ report, onResolved }) => {
  const [copiedPatch, setCopiedPatch] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionKey>('all');
  const [showAgentGuide, setShowAgentGuide] = useState(false);

  // Section collapsed state for fine-grained toggling
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const toggleSection = (id: string) => {
    setCollapsed(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Milestone 4: Knowledge Base Growth state
  const [isIngested, setIsIngested] = useState(report.is_ingested_to_kb || report.status === 'RESOLVED');
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestSuccessMessage, setIngestSuccessMessage] = useState<string | null>(null);
  const [ingestErrorMessage, setIngestErrorMessage] = useState<string | null>(null);
  const [customRootCause, setCustomRootCause] = useState(
    report.root_cause_info?.primary_hypothesis || report.root_cause || ''
  );
  const [customResolution, setCustomResolution] = useState(
    report.remediation_info?.suggested_patch_diff || report.suggested_fix || ''
  );

  useEffect(() => {
    setIsIngested(report.is_ingested_to_kb || report.status === 'RESOLVED');
    setCustomRootCause(report.root_cause_info?.primary_hypothesis || report.root_cause || '');
    setCustomResolution(report.remediation_info?.suggested_patch_diff || report.suggested_fix || '');
    setIngestSuccessMessage(null);
    setIngestErrorMessage(null);
  }, [report]);

  const handleIngestKnowledgeBase = async () => {
    if (!customRootCause.trim() || !customResolution.trim()) return;
    setIsIngesting(true);
    try {
      const res = await resolveAndIngestBug(report.id, {
        verified_root_cause: customRootCause,
        confirmed_resolution: customResolution,
        offending_function: report.parsed_log?.failure_point?.method_name || 'N/A',
        notes: `Confirmed resolution ingested into ChromaDB via DefectMind diagnosis panel.`
      });
      setIsIngested(true);
      setIngestSuccessMessage(res.message);
      setIngestErrorMessage(null);
      if (onResolved) {
        onResolved({
          ...report,
          status: 'RESOLVED',
          is_ingested_to_kb: true,
          verified_resolution: customResolution,
          resolved_at: new Date().toISOString()
        });
      }
    } catch (err: any) {
      console.error('Failed to ingest defect into knowledge base:', err);
      if (err.response?.status === 429) {
        const retrySec = err.response?.data?.retry_after_seconds || 60;
        setIngestErrorMessage(err.response?.data?.message || `Rate limit exceeded. Please wait ${retrySec} seconds before retrying.`);
      } else {
        setIngestErrorMessage(err.response?.data?.message || err.response?.data?.detail || 'Failed to ingest defect into knowledge base.');
      }
    } finally {
      setIsIngesting(false);
    }
  };

  const rc = report.root_cause_info;
  const dup = report.duplicate_info;
  const rem = report.remediation_info;
  const log = report.parsed_log;
  const confidencePct = Math.round((rc?.confidence_score ?? report.confidence_score ?? 0.85) * 100);

  const getSeverityBadgeClass = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'blocker':
        return 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/30';
      case 'high':
      case 'major':
        return 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30';
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/30';
      case 'low':
      case 'minor':
        return 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-500/10 text-slate-700 dark:text-slate-400 border-slate-500/30';
    }
  };

  const getPriorityBadgeClass = (priority?: string) => {
    switch (priority?.toUpperCase()) {
      case 'P1':
        return 'bg-rose-500/10 text-rose-700 dark:text-rose-300 border-rose-500/30 font-bold';
      case 'P2':
        return 'bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/30 font-bold';
      case 'P3':
        return 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-300 border-yellow-500/30 font-bold';
      default:
        return 'bg-slate-500/10 text-slate-700 dark:text-slate-300 border-slate-500/30 font-bold';
    }
  };

  const handleCopyPatch = () => {
    const patch = rem?.suggested_patch_diff || report.suggested_fix || '';
    navigator.clipboard.writeText(patch);
    setCopiedPatch(true);
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  const generateMarkdownReport = () => {
    const lines = [
      `# Defect Diagnosis Report: ${report.id}`,
      `**Title**: ${report.title}`,
      `**Repository**: ${report.repository || 'General'} | **Component**: ${report.component || 'General'}`,
      `**Severity**: ${report.severity || 'High'} | **Priority**: ${report.priority || 'P2'} | **Confidence**: ${confidencePct}%`,
      `**Submission Date**: ${new Date(report.created_at).toLocaleString()}`,
      '',
      `## 1. Description & Environment Details`,
      `**Description**: ${report.description || 'N/A'}`,
      `**Environment**: ${report.environment_details || 'N/A'}`,
      report.log_file_name ? `**Uploaded Log File**: ${report.log_file_name}` : '',
      '',
      `## 2. Agent 1: Log Analysis Findings`,
      `- **Exception Type**: ${log?.exception_type || 'Unknown'}`,
      `- **Exception Message**: ${log?.exception_message || 'N/A'}`,
      `- **Failure Point**: ${log?.failure_point?.file_name || 'N/A'}:${log?.failure_point?.line_number || '?'}, method: ${log?.failure_point?.method_name || 'N/A'}()`,
      `- **Log Format**: ${log?.log_format || 'Unstructured'}`,
      `- **Code Path Sequence**: ${log?.code_path?.join(' -> ') || 'N/A'}`,
      '',
      `## 3. Agent 2: Triage Assessment`,
      `- **Severity**: ${report.severity || 'High'}`,
      `- **Priority**: ${report.priority || 'P2'}`,
      `- **Component**: ${report.component || 'General'}`,
      `- **Triage Reasoning**: ${report.triage_reasoning || 'N/A'}`,
      '',
      `## 4. Agent 3: Duplicate Detection (Milestone 3.2)`,
      `**Duplicate Status**: ${dup?.duplicate_status || (report.is_duplicate ? 'Duplicate' : 'New / Unmatched Issue')}`,
      `**Highest Similarity**: ${Math.round((dup?.highest_similarity_score || 0) * 100)}%`,
      `**Summary**: ${dup?.match_summary || 'N/A'}`,
      dup?.potential_matches && dup.potential_matches.length > 0
        ? dup.potential_matches.map(m => `- **${m.bug_id}** (${Math.round(m.similarity_score * 100)}% - ${m.similarity_category}): ${m.match_reason}`).join('\n')
        : '',
      '',
      `## 5. Agent 4: Root Cause Analysis (Milestone 3.1)`,
      `**Primary Hypothesis**: ${rc?.primary_hypothesis || report.root_cause}`,
      `**Failure Mechanism**: ${rc?.primary_failure_mechanism || 'N/A'}`,
      `**Evidence Status**: ${rc?.evidence_status || 'Sufficient Evidence'}`,
      '',
      `### Agent Deductive Reasoning`,
      `${rc?.agent_reasoning || 'N/A'}`,
      '',
      `### Supporting Historical Defect Evidence`,
      rc?.supporting_evidence && rc.supporting_evidence.length > 0
        ? rc.supporting_evidence.map((e, idx) => `- **Match #${idx + 1} [${e.bug_id}]** (${Math.round(e.similarity_score * 100)}% match): ${e.root_cause}\n  *Verified Resolution*: ${e.resolution}`).join('\n')
        : 'No direct historical defect evidence retrieved.',
      '',
      `## 6. Agent 5: Remediation & Action Plan (Milestone 3.3)`,
      `**Grounding Type**: ${rem?.recommended_fixes?.[0]?.grounding_type || 'Historical Defect Evidence'}`,
      `**Speculative Warning**: ${rem?.is_speculative ? 'YES - Incomplete diagnostic evidence; proceed with manual validation.' : 'NO - Grounded fix.'}`,
      '',
      `### Recommended Technical Modifications`,
      rem?.technical_recommendations?.code_modifications?.map(c => `- ${c}`).join('\n') || '',
      '',
      `### Suggested Unified Diff Patch`,
      '```diff',
      rem?.suggested_patch_diff || report.suggested_fix || '',
      '```',
      '',
      `### Verification Testing Advice`,
      rem?.verification_testing_advice || report.remediation_steps || ''
    ];

    return lines.filter(Boolean).join('\n');
  };

  const handleExportReport = () => {
    const reportText = generateMarkdownReport();
    const blob = new Blob([reportText], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${report.id}_diagnosis_report.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyReport = () => {
    const reportText = generateMarkdownReport();
    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  const diffText = rem?.suggested_patch_diff || report.suggested_fix || '';

  const parseDiffLines = (diff: string) => {
    return diff.split('\n').map((line, idx) => {
      let lineStyle = 'text-slate-300 bg-transparent';
      if (line.startsWith('+') && !line.startsWith('+++')) {
        lineStyle = 'text-emerald-400 bg-emerald-500/10 font-semibold';
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        lineStyle = 'text-rose-400 bg-rose-500/10 font-semibold';
      } else if (line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++')) {
        lineStyle = 'text-indigo-300 font-bold bg-indigo-500/10';
      }
      return (
        <div key={idx} className={`px-4 py-0.5 whitespace-pre font-mono text-xs ${lineStyle}`}>
          {line}
        </div>
      );
    });
  };

  const shouldShow = (sec: SectionKey) => {
    return activeSection === 'all' || activeSection === sec;
  };

  return (
    <div className="space-y-4">
      {/* 1. Header Card: Bug Submission Overview & Clean Metrics Strip */}
      <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4 shadow-sm">
        {/* Top row: ID, Badges, and Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-surface-border/70">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-lg bg-white dark:bg-surface border border-slate-200 dark:border-surface-border text-indigo-600 dark:text-indigo-400 shadow-2xs">
              {report.id}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-lg bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20">
              {report.repository || 'General'}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-lg bg-purple-500/10 text-purple-700 dark:text-purple-300 border border-purple-500/20">
              {report.component || 'General'}
            </span>
            {report.log_file_name && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                📁 {report.log_file_name}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAgentGuide(!showAgentGuide)}
              className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 transition-all shadow-2xs"
              title="Explain what each of the 5 agents do"
            >
              <HelpCircle className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>{showAgentGuide ? 'Hide Agent Guide' : 'What do the 5 Agents do?'}</span>
            </button>

            <button
              onClick={handleCopyReport}
              className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-surface-border hover:border-indigo-500 hover:text-slate-900 dark:hover:text-white transition-all text-slate-700 dark:text-slate-300 shadow-2xs"
              title="Copy Full Diagnosis Report"
            >
              {copiedReport ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>

            <button
              onClick={handleExportReport}
              className="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all"
              title="Download Full Markdown Report"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .md</span>
            </button>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight leading-snug">
          {report.title}
        </h2>

        {/* Executive Quick Stats Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
          <div className="p-2.5 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-center justify-between shadow-2xs">
            <span className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400">Severity</span>
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${getSeverityBadgeClass(report.severity)}`}>
              {report.severity || 'High'}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-center justify-between shadow-2xs">
            <span className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400">Priority</span>
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${getPriorityBadgeClass(report.priority)}`}>
              {report.priority || 'P2'}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-center justify-between shadow-2xs">
            <span className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400">Confidence</span>
            <span className="text-[11px] font-mono font-extrabold text-emerald-600 dark:text-emerald-400">
              {confidencePct}%
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-center justify-between shadow-2xs">
            <span className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400">KB Growth</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
              isIngested
                ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30'
                : 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/20'
            }`}>
              {isIngested ? 'Active Ingest' : 'Pending'}
            </span>
          </div>
        </div>

        {/* Brief description & environment */}
        <div className="text-xs text-slate-700 dark:text-slate-300 bg-white/70 dark:bg-surface/30 p-3 rounded-xl border border-slate-200 dark:border-surface-border leading-relaxed font-sans shadow-2xs">
          <p>{report.description || 'No detailed functional description provided.'}</p>
          {report.environment_details && (
            <div className="mt-2 pt-2 border-t border-slate-200 dark:border-surface-border/50 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
              Env: <span className="text-slate-700 dark:text-slate-300">{report.environment_details}</span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Interactive 5-Agent Visual Pipeline Header */}
      <div className="glass-panel rounded-2xl p-4 border border-surface-border space-y-3 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
              <Layers className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                5-Agent LangGraph Diagnostic Pipeline
              </h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Click any agent below to isolate its findings and understand its exact role.
              </p>
            </div>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            All 5 Finished
          </span>
        </div>

        {/* 5 Agent Interactive Pipeline Step Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 pt-1">
          {AGENTS.map((agent) => {
            const Icon = agent.icon;
            const isSelected = activeSection === agent.id;
            return (
              <button
                key={agent.id}
                onClick={() => setActiveSection(isSelected ? 'all' : agent.id)}
                className={`p-2.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-600/25 ring-2 ring-indigo-400/30'
                    : 'bg-white/80 dark:bg-surface/50 border-slate-200 dark:border-surface-border hover:border-indigo-400 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/20'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      isSelected
                        ? 'bg-white/20 text-white'
                        : agent.badgeBg
                    }`}>
                      Step {agent.stepNum}
                    </span>
                    <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : agent.accentColor}`} />
                  </div>
                  <div className={`text-xs font-bold truncate ${isSelected ? 'text-white' : 'text-slate-900 dark:text-white'}`}>
                    {agent.name.replace(' Agent', '')}
                  </div>
                  <div className={`text-[10.5px] leading-tight mt-1 line-clamp-2 ${isSelected ? 'text-indigo-100' : 'text-slate-500 dark:text-slate-400'}`}>
                    {agent.shortRole}
                  </div>
                </div>

                <div className={`text-[9.5px] font-semibold mt-2 pt-1.5 border-t ${
                  isSelected
                    ? 'border-white/20 text-indigo-100'
                    : 'border-slate-100 dark:border-surface-border text-indigo-600 dark:text-indigo-400'
                }`}>
                  {isSelected ? 'Viewing Agent &rarr;' : 'Click to inspect &rarr;'}
                </div>
              </button>
            );
          })}
        </div>

        {/* Collapsible Educational Guide on the 5 Agents */}
        {showAgentGuide && (
          <div className="mt-3 p-4 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/60 space-y-3 text-xs animate-in fade-in duration-200">
            <div className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>How the 5 Agents Collaborate in Sequence (Plain-English Guide):</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] leading-relaxed text-slate-700 dark:text-slate-300">
              {AGENTS.map((a) => (
                <div key={a.id} className="p-2.5 rounded-lg bg-white dark:bg-surface/70 border border-indigo-100 dark:border-indigo-900/50 shadow-2xs">
                  <div className="font-bold text-indigo-700 dark:text-indigo-300 mb-0.5">
                    Step {a.stepNum}: {a.name}
                  </div>
                  <p>{a.plainExplanation}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. Section Filter Pill Bar for Easy Switching */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 p-1 rounded-xl bg-slate-200/80 dark:bg-surface/80 border border-slate-300/80 dark:border-surface-border scrollbar-none text-xs font-semibold shadow-inner">
        <button
          onClick={() => setActiveSection('all')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'all'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <SlidersHorizontal className="w-3 h-3" />
          <span>Show All 5 Agents</span>
        </button>

        <button
          onClick={() => setActiveSection('log_analysis')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'log_analysis'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Terminal className="w-3 h-3 text-cyan-600 dark:text-cyan-400" />
          <span>1. Log Analysis</span>
        </button>

        <button
          onClick={() => setActiveSection('triage')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'triage'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <ShieldAlert className="w-3 h-3 text-amber-500 dark:text-amber-400" />
          <span>2. Triage</span>
        </button>

        <button
          onClick={() => setActiveSection('duplicates')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'duplicates'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Search className="w-3 h-3 text-purple-600 dark:text-purple-400" />
          <span>3. Duplicate Detection</span>
        </button>

        <button
          onClick={() => setActiveSection('root_cause')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'root_cause'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Cpu className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
          <span>4. Root Cause</span>
        </button>

        <button
          onClick={() => setActiveSection('remediation')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'remediation'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Wrench className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
          <span>5. Remediation Patch</span>
        </button>

        <button
          onClick={() => setActiveSection('kb_growth')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'kb_growth'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Database className="w-3 h-3 text-teal-600 dark:text-teal-400" />
          <span>KB Feedback Loop</span>
        </button>

        <button
          onClick={() => setActiveSection('timeline')}
          className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeSection === 'timeline'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          <Activity className="w-3 h-3 text-violet-600 dark:text-violet-400" />
          <span>Agent Timeline</span>
        </button>
      </div>

      {/* ============================================================== */}
      {/* AGENT 1: LOG ANALYSIS & FRAME ISOLATION                        */}
      {/* ============================================================== */}
      {shouldShow('log_analysis') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('log_analysis')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Terminal className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <span>Agent 1: Log Analysis & Failure Point Isolation</span>
            </div>
            {collapsed['log_analysis'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['log_analysis'] && (
            <div className="space-y-4">
              {/* Agent 1 Plain-English Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 text-[10px] shrink-0 uppercase">
                  Agent 1 Role
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this agent does:</strong> Takes noisy production crash traces, strips timestamps and runtime framework junk (e.g. JVM internal frames, stdlib), and isolates the exact developer application file, line number, and execution call sequence.
                </p>
              </div>

              {log && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-surface-border shadow-2xs">
                    <div className="text-slate-500 dark:text-slate-400 text-[10px] uppercase mb-1 font-semibold">
                      Extracted Exception Type:
                    </div>
                    <div className="text-rose-600 dark:text-rose-400 font-bold text-xs">{log.exception_type}</div>
                    <div className="text-slate-700 dark:text-slate-300 mt-1 line-clamp-2 text-[11px]">
                      {log.exception_message || 'No explicit error message string in call frame.'}
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-surface-border shadow-2xs">
                    <div className="text-slate-500 dark:text-slate-400 text-[10px] uppercase mb-1 font-semibold">
                      Identified Application Failure Point:
                    </div>
                    {log.failure_point ? (
                      <div>
                        <div className="text-emerald-600 dark:text-emerald-400 font-bold text-xs">
                          {log.failure_point.method_name || 'unknown_method'}()
                        </div>
                        <div className="text-slate-700 dark:text-slate-300 mt-1 text-[11px]">
                          File: <span className="text-cyan-600 dark:text-cyan-300 font-bold">{log.failure_point.file_name || 'N/A'}</span> : Line{' '}
                          <span className="text-amber-600 dark:text-amber-400 font-bold">{log.failure_point.line_number || '?'}</span>
                        </div>
                      </div>
                    ) : log.top_offending_frame ? (
                      <div>
                        <div className="text-emerald-600 dark:text-emerald-400 font-bold">
                          {log.top_offending_frame.function_name}
                        </div>
                        <div className="text-slate-700 dark:text-slate-300 mt-1 text-[11px]">
                          {log.top_offending_frame.file_path}:
                          <span className="text-amber-600 dark:text-amber-400 font-bold">
                            {log.top_offending_frame.line_number}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="text-slate-500 italic text-[11px]">Unstructured log context</div>
                    )}
                  </div>
                </div>
              )}

              {log?.code_path && log.code_path.length > 0 && (
                <div className="p-3.5 rounded-xl bg-slate-950/90 border border-surface-border text-xs font-mono">
                  <div className="text-slate-400 mb-2 font-semibold flex items-center gap-1.5 text-[11px]">
                    <Layers className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Probable Affected Code Path Sequence (Top to Bottom):</span>
                  </div>
                  <div className="space-y-1 pl-2 border-l-2 border-cyan-500/40 text-[11px]">
                    {log.code_path.map((frameStr: string, fIdx: number) => (
                      <div key={fIdx} className="text-slate-300 hover:text-white transition-colors">
                        <span className="text-slate-500 mr-2">{fIdx + 1}.</span>
                        {frameStr}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* AGENT 2: TRIAGE AGENT                                          */}
      {/* ============================================================== */}
      {shouldShow('triage') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('triage')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <ShieldAlert className="w-4 h-4 text-amber-500 dark:text-amber-400" />
              <span>Agent 2: Autonomous Triage Assessment</span>
            </div>
            {collapsed['triage'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['triage'] && (
            <div className="space-y-4">
              {/* Agent 2 Plain-English Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-amber-500/20 text-amber-700 dark:text-amber-300 text-[10px] shrink-0 uppercase">
                  Agent 2 Role
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this agent does:</strong> Evaluates the incident's operational blast radius to classify Severity (Critical/High/Medium/Low), Priority (P1–P4), and the affected Subsystem so engineers know how urgently this must be resolved.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border shadow-2xs">
                  <div className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400 mb-1">Assigned Severity</div>
                  <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-bold border ${getSeverityBadgeClass(report.severity)}`}>
                    {report.severity || 'High'}
                  </div>
                  <p className="text-[10.5px] text-slate-500 dark:text-slate-400 mt-2">
                    {report.severity === 'Critical' ? 'System outage or fatal crash halting operations.' : 'Functional regression affecting service flow.'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border shadow-2xs">
                  <div className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400 mb-1">Assigned Priority</div>
                  <div className={`inline-block px-2.5 py-1 rounded-md text-xs font-bold border ${getPriorityBadgeClass(report.priority)}`}>
                    {report.priority || 'P2'}
                  </div>
                  <p className="text-[10.5px] text-slate-500 dark:text-slate-400 mt-2">
                    {report.priority === 'P1' ? 'Requires immediate on-call response.' : 'Scheduled for prioritized sprint remediation.'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border shadow-2xs">
                  <div className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400 mb-1">Target Component</div>
                  <div className="text-xs font-bold text-slate-900 dark:text-white py-1">
                    {report.component || 'General / Core'}
                  </div>
                  <p className="text-[10.5px] text-slate-500 dark:text-slate-400 mt-2">
                    Routes defect report to the owning subsystem team.
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-surface/30 border border-slate-200 dark:border-surface-border text-xs">
                <div className="text-[10px] uppercase font-mono text-slate-500 dark:text-slate-400 mb-1 font-semibold">
                  Agent Deductive Triage Rationale:
                </div>
                <p className="text-slate-700 dark:text-slate-300 font-sans leading-relaxed text-[11.5px]">
                  {report.triage_reasoning ||
                    (report.severity === 'Critical'
                      ? `Critical severity assigned due to fatal crash exception (${log?.exception_type || 'system crash'}) directly interrupting runtime operations and requiring immediate P1 triage response.`
                      : `Assigned ${report.severity || 'High'} severity and ${report.priority || 'P2'} priority for ${report.component || 'Core'} subsystem based on isolated application failure frame.`)}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* AGENT 3: DUPLICATE DETECTION AGENT                             */}
      {/* ============================================================== */}
      {shouldShow('duplicates') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('duplicates')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Search className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>Agent 3: Duplicate Detection & Historical RAG</span>
            </div>
            {collapsed['duplicates'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['duplicates'] && (
            <div className="space-y-4">
              {/* Agent 3 Plain-English Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-purple-500/20 text-purple-700 dark:text-purple-300 text-[10px] shrink-0 uppercase">
                  Agent 3 Role
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this agent does:</strong> Converts the crash into dense vector embeddings and searches ChromaDB defect memory. Uses calibrated thresholds (≥88% = Duplicate, 75%–87% = Related, &lt;75% = New) so teams don't solve the same bug twice.
                </p>
              </div>

              {/* Duplicate Status Banner */}
              <div className={`p-3.5 rounded-xl border flex items-center justify-between ${
                dup?.is_duplicate || (dup?.highest_similarity_score || 0) >= 0.88
                  ? 'bg-rose-50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-500/30 text-rose-900 dark:text-rose-200'
                  : (dup?.highest_similarity_score || 0) >= 0.75
                  ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-500/30 text-amber-900 dark:text-amber-200'
                  : 'bg-indigo-50 dark:bg-indigo-950/20 border-indigo-200 dark:border-indigo-500/30 text-indigo-900 dark:text-indigo-200'
              }`}>
                <div>
                  <div className="text-[10px] uppercase font-mono font-bold tracking-wider opacity-80">
                    Classification Status
                  </div>
                  <div className="text-sm font-black mt-0.5">
                    {dup?.duplicate_status || (report.is_duplicate ? 'DUPLICATE TICKET' : 'NEW / UNMATCHED ISSUE')}
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className="text-[10px] uppercase opacity-80">Highest Match</div>
                  <div className="text-sm font-black">
                    {Math.round((dup?.highest_similarity_score || 0) * 100)}% Similarity
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 dark:bg-surface/40 border border-slate-200 dark:border-surface-border text-xs text-slate-700 dark:text-slate-300 leading-relaxed shadow-2xs">
                {dup?.match_summary || 'Evaluated vector similarity against historical Mozilla, Apache, and Eclipse defect records.'}
              </div>

              {dup?.potential_matches && dup.potential_matches.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    Candidate Matches from Historical Vector Database:
                  </div>
                  {dup.potential_matches.map((item, mIdx) => (
                    <div key={mIdx} className="p-3 rounded-xl bg-white dark:bg-surface/30 border border-slate-200 dark:border-surface-border text-xs space-y-1.5 shadow-2xs">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{item.bug_id}</span>
                          <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-surface border border-slate-200 dark:border-surface-border text-slate-600 dark:text-slate-400 text-[10px]">
                            {item.repository} / {item.component}
                          </span>
                        </div>

                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                          item.similarity_score >= 0.88
                            ? 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/30'
                            : item.similarity_score >= 0.75
                            ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30'
                            : 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/30'
                        }`}>
                          {Math.round(item.similarity_score * 100)}% Similarity ({item.similarity_category})
                        </span>
                      </div>

                      <p className="text-slate-700 dark:text-slate-300 font-sans text-[11px] leading-relaxed">
                        <strong>Match Reasoning:</strong> {item.match_reason}
                      </p>

                      {item.resolution && (
                        <div className="text-[11px] text-emerald-700 dark:text-emerald-400 font-sans pl-2 border-l-2 border-emerald-500/30">
                          <strong>Historical Resolution:</strong> {item.resolution}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* AGENT 4: ROOT CAUSE AGENT                                      */}
      {/* ============================================================== */}
      {shouldShow('root_cause') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('root_cause')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Cpu className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Agent 4: Grounded Root Cause Deduction</span>
            </div>
            {collapsed['root_cause'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['root_cause'] && (
            <div className="space-y-4">
              {/* Agent 4 Plain-English Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 text-[10px] shrink-0 uppercase">
                  Agent 4 Role
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this agent does:</strong> Deduces why the crash happened (e.g., race condition, heap exhaustion). Crucially, it separates the agent's deductive reasoning from retrieved historical evidence to eliminate hallucinations.
                </p>
              </div>

              {/* Primary Hypothesis Banner */}
              <div className="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-500/30 text-slate-900 dark:text-slate-100 shadow-2xs">
                <div className="text-[10px] uppercase font-bold tracking-wider text-indigo-700 dark:text-indigo-300 mb-1 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                  <span>Primary Root Cause Hypothesis</span>
                </div>
                <p className="text-xs sm:text-sm font-semibold leading-relaxed">
                  {rc?.primary_hypothesis || report.root_cause || 'Analyzing root cause hypothesis...'}
                </p>

                {rc?.primary_failure_mechanism && (
                  <div className="mt-2 text-xs font-mono text-indigo-700 dark:text-indigo-300">
                    Physical Failure Mechanism: <strong className="text-slate-900 dark:text-white">{rc.primary_failure_mechanism}</strong>
                  </div>
                )}
              </div>

              {/* Deductive Reasoning & Historical KB Evidence Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-surface-border space-y-1.5 shadow-2xs">
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-cyan-700 dark:text-cyan-400 uppercase tracking-wider">
                    <Terminal className="w-3.5 h-3.5" />
                    <span>Agent Deductive Reasoning</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                    {rc?.agent_reasoning || 'Reasoning synthesized from call stack frames and component failure profiles.'}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-surface-border space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                      <GitPullRequest className="w-3.5 h-3.5" />
                      <span>Retrieved Knowledge Base Evidence</span>
                    </div>
                    {rc?.supporting_evidence && (
                      <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">
                        {rc.supporting_evidence.length} Record(s)
                      </span>
                    )}
                  </div>

                  {rc?.supporting_evidence && rc.supporting_evidence.length > 0 ? (
                    <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
                      {rc.supporting_evidence.map((evidence, eIdx) => (
                        <div key={eIdx} className="p-2 rounded-lg bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border text-xs space-y-0.5 shadow-2xs">
                          <div className="flex items-center justify-between font-mono text-[10px]">
                            <span className="font-bold text-indigo-600 dark:text-indigo-400">{evidence.bug_id}</span>
                            <span className="text-emerald-600 dark:text-emerald-400 font-bold">{Math.round(evidence.similarity_score * 100)}% Match</span>
                          </div>
                          <div className="text-slate-700 dark:text-slate-300 font-sans text-[11px] line-clamp-2">{evidence.root_cause}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">
                      No historical defect records directly correlated to this profile in the vector index.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* AGENT 5: REMEDIATION AGENT                                     */}
      {/* ============================================================== */}
      {shouldShow('remediation') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('remediation')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Wrench className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Agent 5: Code Remediation & Unified Diff Patch</span>
            </div>
            {collapsed['remediation'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['remediation'] && (
            <div className="space-y-4">
              {/* Agent 5 Plain-English Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 text-[10px] shrink-0 uppercase">
                  Agent 5 Role
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this agent does:</strong> Synthesizes a valid unified git diff patch targeting the exact failing file and line, alongside actionable architectural advice (Code, Config, Validation, Error Handling).
                </p>
              </div>

              {/* Copy patch toolbar & warning */}
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-slate-600 dark:text-slate-400">
                  Grounded in: <strong className="text-indigo-600 dark:text-indigo-400">{rem?.recommended_fixes?.[0]?.grounding_type || 'Historical Defect Evidence'}</strong>
                </span>

                <button
                  onClick={handleCopyPatch}
                  className="flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-surface-border hover:border-indigo-500 hover:text-slate-900 dark:hover:text-white transition-all text-slate-700 dark:text-slate-300 shadow-2xs"
                >
                  {copiedPatch ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Patch</span>
                    </>
                  )}
                </button>
              </div>

              {/* Unified Diff */}
              {diffText && (
                <div className="rounded-xl border border-surface-border bg-slate-950/95 overflow-x-auto py-2.5">
                  {parseDiffLines(diffText)}
                </div>
              )}

              {/* Technical Recommendations Grid */}
              {rem?.technical_recommendations && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-sans">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-surface/30 border border-slate-200 dark:border-surface-border space-y-1.5 shadow-2xs">
                    <div className="font-bold text-indigo-700 dark:text-indigo-300 uppercase text-[10px]">
                      1. Code Modifications:
                    </div>
                    <ul className="space-y-1 text-slate-700 dark:text-slate-300 list-disc list-inside text-[11px]">
                      {rem.technical_recommendations.code_modifications.map((item, idx) => (
                        <li key={idx} className="leading-relaxed">{item}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-surface/30 border border-slate-200 dark:border-surface-border space-y-1.5 shadow-2xs">
                    <div className="font-bold text-emerald-700 dark:text-emerald-400 uppercase text-[10px]">
                      2. Validation & Testing Steps:
                    </div>
                    <ul className="space-y-1 text-slate-700 dark:text-slate-300 list-disc list-inside text-[11px]">
                      {rem.technical_recommendations.validation_steps.map((item, idx) => (
                        <li key={idx} className="leading-relaxed">{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* MILESTONE 4.2: KNOWLEDGE BASE GROWTH MECHANISM                 */}
      {/* ============================================================== */}
      {shouldShow('kb_growth') && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-4">
          <div
            onClick={() => toggleSection('kb_growth')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Database className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Knowledge Base Growth: Confirmed Resolution Ingestion</span>
            </div>
            {collapsed['kb_growth'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['kb_growth'] && (
            <div className="space-y-4">
              {/* Explainer Banner */}
              <div className="flex items-start gap-2.5 p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 text-xs">
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-teal-500/20 text-teal-700 dark:text-teal-300 text-[10px] shrink-0 uppercase">
                  Continuous Learning
                </span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">
                  <strong>What this does:</strong> When an engineer applies and verifies this patch, they click confirm. DefectMind embeds the verified fix into ChromaDB using the <strong>3-Chunk Strategy</strong> (Overview, Stack Trace, Resolution) so future crashes auto-retrieve this fix.
                </p>
              </div>

              {ingestSuccessMessage && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-500/30 text-xs text-emerald-700 dark:text-emerald-300 flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-white">Ingestion Successful!</div>
                    <div className="text-[11px] text-emerald-700/90 dark:text-emerald-300/90">{ingestSuccessMessage}</div>
                  </div>
                </div>
              )}

              {ingestErrorMessage && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-500/30 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-white">Ingestion Rate Limited / Error</div>
                    <div className="text-[11px] text-rose-700/90 dark:text-rose-300/90">{ingestErrorMessage}</div>
                  </div>
                </div>
              )}

              {isIngested ? (
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-surface/30 border border-slate-200 dark:border-surface-border space-y-2 text-xs shadow-2xs">
                  <div>
                    <div className="text-[10px] font-mono uppercase text-slate-500 dark:text-slate-400">Verified Root Cause:</div>
                    <div className="text-slate-800 dark:text-slate-200 mt-0.5 font-sans">{report.root_cause || customRootCause}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono uppercase text-slate-500 dark:text-slate-400">Confirmed Resolution:</div>
                    <pre className="mt-0.5 p-2 rounded-lg bg-white dark:bg-surface font-mono text-[11px] text-emerald-700 dark:text-emerald-300 overflow-x-auto whitespace-pre-wrap border border-slate-200 dark:border-surface-border">
                      {report.verified_resolution || report.suggested_fix || customResolution}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">
                      Verified Root Cause:
                    </label>
                    <textarea
                      value={customRootCause}
                      onChange={(e) => setCustomRootCause(e.target.value)}
                      rows={2}
                      className="w-full rounded-xl bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-none focus:border-indigo-500 font-sans shadow-2xs"
                      placeholder="Confirm root cause..."
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">
                      Confirmed Resolution / Code Patch:
                    </label>
                    <textarea
                      value={customResolution}
                      onChange={(e) => setCustomResolution(e.target.value)}
                      rows={3}
                      className="w-full rounded-xl bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border px-3 py-2 font-mono text-[11px] text-slate-900 dark:text-slate-200 focus:outline-none focus:border-indigo-500 shadow-2xs"
                      placeholder="Confirm code patch..."
                    />
                  </div>

                  <div className="flex items-center justify-end">
                    <button
                      onClick={handleIngestKnowledgeBase}
                      disabled={isIngesting || !customRootCause.trim() || !customResolution.trim()}
                      className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md shadow-emerald-600/20"
                    >
                      {isIngesting ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Indexing into ChromaDB...</span>
                        </>
                      ) : (
                        <>
                          <Database className="w-3.5 h-3.5" />
                          <span>Confirm Fix & Ingest into Knowledge Base</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* AGENT TIMELINE                                                 */}
      {/* ============================================================== */}
      {shouldShow('timeline') && report.workflow_steps && report.workflow_steps.length > 0 && (
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-3">
          <div
            onClick={() => toggleSection('timeline')}
            className="flex items-center justify-between cursor-pointer select-none pb-2 border-b border-surface-border/70"
          >
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200 uppercase tracking-wider">
              <Activity className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>Multi-Agent Orchestration Log ({report.workflow_steps.length} Steps)</span>
            </div>
            {collapsed['timeline'] ? <ChevronRight className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </div>

          {!collapsed['timeline'] && (
            <div className="space-y-2">
              {report.workflow_steps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-2.5 rounded-xl bg-slate-50 dark:bg-surface/40 border border-slate-200 dark:border-surface-border text-xs shadow-2xs">
                  <div className="p-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 mt-0.5">
                    <CheckCircle2 className="w-3 h-3" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between font-mono mb-0.5 text-[11px]">
                      <span className="font-bold text-indigo-700 dark:text-indigo-300">{step.agent}</span>
                      <span className="text-[10px] text-slate-500">
                        {new Date(step.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 font-sans text-[11px]">{step.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
