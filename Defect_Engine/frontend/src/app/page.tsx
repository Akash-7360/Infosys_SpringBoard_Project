'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Terminal,
  Activity,
  Layers,
  Sparkles,
  History,
  CheckCircle2,
  RefreshCw,
  BarChart3,
  Database,
  PlusCircle,
  FileCode2,
  ChevronRight,
  Search,
  ExternalLink,
  Cpu,
  Wrench
} from 'lucide-react';
import { BugSubmissionForm } from '@/components/BugSubmissionForm';
import { DiagnosisView } from '@/components/DiagnosisView';
import { SimilarBugsList } from '@/components/SimilarBugsList';
import { CodeRemediationDiff } from '@/components/CodeRemediationDiff';
import { PatternAnalyticsView } from '@/components/PatternAnalyticsView';
import { ThemeToggle } from '@/components/ThemeToggle';
import { BugSubmissionResponse, getSubmissionsList, getSubmissionById } from '@/lib/api';

export default function Home() {
  const [currentReport, setCurrentReport] = useState<BugSubmissionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [historyList, setHistoryList] = useState<BugSubmissionResponse[]>([]);
  const [searchFilter, setSearchFilter] = useState('');
  
  // Navigation State
  const [primaryMode, setPrimaryMode] = useState<'workspace' | 'analytics'>('workspace');
  const [leftTab, setLeftTab] = useState<'submit' | 'history'>('submit');
  const [workspaceTab, setWorkspaceTab] = useState<'diagnosis' | 'remediation' | 'similar'>('diagnosis');

  const fetchHistory = async () => {
    try {
      const data = await getSubmissionsList();
      setHistoryList(data);
    } catch (e) {
      console.log('No prior history found or backend offline');
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSubmissionSuccess = (report: BugSubmissionResponse) => {
    setCurrentReport(report);
    setWorkspaceTab('diagnosis');
    fetchHistory();
  };

  const handleSelectHistoricalBug = async (item: BugSubmissionResponse) => {
    setCurrentReport(item);
    setWorkspaceTab('diagnosis');
    try {
      const full = await getSubmissionById(item.id);
      if (full) {
        setCurrentReport(full);
      }
    } catch (e) {
      // Fallback to cached item
    }
  };

  const filteredHistory = historyList.filter(item => 
    item.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
    item.id.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (item.component && item.component.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  return (
    <main className="min-h-screen bg-background text-slate-900 dark:text-slate-100 p-3 sm:p-6 lg:p-8 font-sans selection:bg-indigo-500 selection:text-white transition-colors duration-250">
      {/* Top Header Bar */}
      <header className="max-w-7xl mx-auto mb-6 pb-4 border-b border-surface-border space-y-3.5">
        {/* Top Tier: Branding on Left, Primary Navigation & Theme Toggle on Right */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Branding & Milestone Badge */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-violet-700 flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0">
              <Terminal className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">DefectMind</h1>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                  Milestone 4
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Autonomous Defect Analysis &amp; Multi-Agent Triage Engine
              </p>
            </div>
          </div>

          {/* Right: Primary Mode Switcher + Theme Toggle */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-between sm:justify-end shrink-0">
            {/* Global Primary Mode Switcher */}
            <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-200/80 dark:bg-surface/90 border border-slate-300 dark:border-surface-border shadow-inner">
              <button
                onClick={() => setPrimaryMode('workspace')}
                className={`py-1.5 px-3.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                  primaryMode === 'workspace'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Triage Workspace</span>
              </button>

              <button
                onClick={() => setPrimaryMode('analytics')}
                className={`py-1.5 px-3.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                  primaryMode === 'analytics'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <BarChart3 className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                <span>Pattern Analytics</span>
              </button>
            </div>

            {/* Theme Toggle Button */}
            <div className="flex items-center gap-1.5 pl-2 border-l border-slate-200 dark:border-surface-border shrink-0">
              <ThemeToggle />
            </div>
          </div>
        </div>

        {/* Bottom Tier: Live Telemetry & Status Badges Strip */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60 dark:border-surface-border/40 text-[11px] font-mono">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/80 dark:bg-surface/60 border border-slate-200 dark:border-surface-border shadow-2xs">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" />
              <span className="text-slate-600 dark:text-slate-300">FastAPI: <strong className="text-emerald-600 dark:text-emerald-400 font-semibold">Online</strong></span>
            </div>

            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/80 dark:bg-surface/60 border border-slate-200 dark:border-surface-border shadow-2xs">
              <Database className="w-3 h-3 text-cyan-600 dark:text-cyan-400" />
              <span className="text-slate-600 dark:text-slate-300">Database: <strong className="text-cyan-600 dark:text-cyan-400 font-semibold">{historyList.length} Stored</strong></span>
            </div>

            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/80 dark:bg-surface/60 border border-slate-200 dark:border-surface-border shadow-2xs">
              <Database className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
              <span className="text-slate-600 dark:text-slate-300">ChromaDB: <strong className="text-emerald-600 dark:text-emerald-400 font-semibold">3-Chunk RAG</strong></span>
            </div>

            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/80 dark:bg-surface/60 border border-slate-200 dark:border-surface-border shadow-2xs">
              <Layers className="w-3 h-3 text-purple-600 dark:text-purple-400" />
              <span className="text-slate-600 dark:text-slate-300">LangGraph: <strong className="text-purple-600 dark:text-purple-400 font-semibold">5 Active Agents</strong></span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-2 text-[10.5px] text-slate-500 dark:text-slate-400">
            <span>Cosine Threshold &ge; 88%</span>
            <span>&bull;</span>
            <span className="text-indigo-600 dark:text-indigo-400 font-semibold">MTTR Reduction Engine</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto">
        {primaryMode === 'analytics' ? (
          /* Full-Width Expansive Pattern Analytics View */
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setPrimaryMode('workspace')}
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 flex items-center gap-1 font-semibold"
              >
                &larr; Back to Triage Workspace
              </button>
            </div>
            <PatternAnalyticsView />
          </div>
        ) : (
          /* Dual-Panel Triage Workspace */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* Left Column: Defect Intake & History Drawer (5 cols) */}
            <div className="lg:col-span-5 space-y-4">
              {/* Left Panel Segment Switcher */}
              <div className="flex items-center gap-2 p-1 rounded-xl bg-slate-200/80 dark:bg-surface/80 border border-slate-300/80 dark:border-surface-border shadow-inner">
                <button
                  onClick={() => setLeftTab('submit')}
                  className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                    leftTab === 'submit'
                      ? 'bg-white dark:bg-surface text-slate-900 dark:text-white shadow-sm border border-slate-300 dark:border-surface-border'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <PlusCircle className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                  <span>Submit Defect</span>
                </button>

                <button
                  onClick={() => setLeftTab('history')}
                  className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                    leftTab === 'history'
                      ? 'bg-white dark:bg-surface text-slate-900 dark:text-white shadow-sm border border-slate-300 dark:border-surface-border'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  <History className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                  <span>Defect History ({historyList.length})</span>
                </button>
              </div>

              {leftTab === 'submit' ? (
                <BugSubmissionForm
                  onSubmissionSuccess={handleSubmissionSuccess}
                  isSubmitting={isSubmitting}
                  setIsSubmitting={setIsSubmitting}
                />
              ) : (
                /* History Drawer */
                <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-surface-border">
                    <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                      Recent Submissions
                    </span>
                    <button
                      onClick={fetchHistory}
                      className="p-1 rounded text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-all"
                      title="Refresh List"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Filter Search */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      value={searchFilter}
                      onChange={(e) => setSearchFilter(e.target.value)}
                      placeholder="Filter by title, ID, or component..."
                      className="w-full bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 shadow-xs"
                    />
                  </div>

                  {/* List of submissions */}
                  <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                    {filteredHistory.length === 0 ? (
                      <div className="text-center py-8 text-xs text-slate-500">
                        No matching defect submissions found.
                      </div>
                    ) : (
                      filteredHistory.map((item) => (
                        <div
                          key={item.id}
                          onClick={() => handleSelectHistoricalBug(item)}
                          className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                            currentReport?.id === item.id
                              ? 'bg-indigo-50 dark:bg-indigo-600/15 border-indigo-400 dark:border-indigo-500 text-slate-900 dark:text-white shadow-xs'
                              : 'bg-white/80 dark:bg-surface/40 border-slate-200 dark:border-surface-border hover:border-slate-400 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1 font-mono text-[10px]">
                            <span className="text-indigo-600 dark:text-indigo-400 font-bold">{item.id}</span>
                            <span className="text-slate-500 dark:text-slate-400">{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                          <div className="font-semibold truncate text-slate-900 dark:text-white">{item.title}</div>
                          <div className="flex items-center gap-1.5 mt-2">
                            <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] text-slate-700 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                              {item.severity}
                            </span>
                            <span className="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-900/50 text-[10px] text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                              {item.priority}
                            </span>
                            {item.status === 'RESOLVED' ? (
                              <span className="px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/80 text-[10px] text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/80">
                                Resolved & Ingested
                              </span>
                            ) : item.is_ingested_to_kb ? (
                              <span className="px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/80 text-[10px] text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/80">
                                KB Ingested
                              </span>
                            ) : (
                              <span className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-900/60 text-[10px] text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/60">
                                Analyzed
                              </span>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Interactive Diagnosis & Analysis Results (7 cols) */}
            <div className="lg:col-span-7 space-y-4">
              {currentReport ? (
                <div className="space-y-4">
                  {/* Tab Navigation */}
                  <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-200/80 dark:bg-surface/80 border border-slate-300/80 dark:border-surface-border shadow-inner">
                    <button
                      onClick={() => setWorkspaceTab('diagnosis')}
                      className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                        workspaceTab === 'diagnosis'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      <Activity className="w-3.5 h-3.5" />
                      <span>Diagnosis Report</span>
                    </button>

                    <button
                      onClick={() => setWorkspaceTab('remediation')}
                      className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                        workspaceTab === 'remediation'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Code Patch Diff</span>
                    </button>

                    <button
                      onClick={() => setWorkspaceTab('similar')}
                      className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                        workspaceTab === 'similar'
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      <Layers className="w-3.5 h-3.5" />
                      <span>Vector Matches ({currentReport.similar_bugs?.length || 0})</span>
                    </button>
                  </div>

                  {/* Tab Contents */}
                  {workspaceTab === 'diagnosis' && (
                    <DiagnosisView
                      report={currentReport}
                      onResolved={(updated) => {
                        setCurrentReport(updated);
                        fetchHistory();
                      }}
                    />
                  )}
                  {workspaceTab === 'remediation' && <CodeRemediationDiff report={currentReport} />}
                  {workspaceTab === 'similar' && <SimilarBugsList similarBugs={currentReport.similar_bugs} />}
                </div>
              ) : (
                /* Empty State: 5-Agent Pipeline Architecture Guide */
                <div className="glass-panel rounded-2xl p-6 sm:p-7 border border-surface-border text-center space-y-6 shadow-sm">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mx-auto shadow-inner">
                    <Sparkles className="w-6 h-6" />
                  </div>

                  <div className="max-w-lg mx-auto space-y-1.5">
                    <h3 className="text-base sm:text-lg font-black text-slate-900 dark:text-white tracking-tight">
                      Autonomous 5-Agent Diagnostic Architecture
                    </h3>
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      Select any showcase preset on the left (e.g. <strong>Kafka OOM Buffer</strong>) or upload a raw log to watch the 5 autonomous agents diagnose the incident in sequence:
                    </p>
                  </div>

                  {/* 5-Agent Explainer Flow Grid */}
                  <div className="grid grid-cols-1 gap-2.5 text-left pt-2">
                    {/* Agent 1 */}
                    <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-start gap-3 shadow-2xs">
                      <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
                        <Terminal className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">1. Log Analysis Agent</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 font-semibold">Frame Isolator</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                          Strips noise & runtime frames from Java, Python, C++, Go, or syslogs to isolate the exact developer crash line (file & line) and call sequence.
                        </p>
                      </div>
                    </div>

                    {/* Agent 2 */}
                    <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-start gap-3 shadow-2xs">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                        <ShieldAlert className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">2. Triage Agent</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-semibold">Operational Urgency</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                          Evaluates production blast radius to assign Severity (Critical/High/Medium/Low), Priority (P1–P4), and subsystem routing with deductive justification.
                        </p>
                      </div>
                    </div>

                    {/* Agent 3 */}
                    <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-start gap-3 shadow-2xs">
                      <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0 mt-0.5">
                        <Search className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">3. Duplicate Detection Agent</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 font-semibold">ChromaDB RAG</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                          Runs dense vector cosine queries across historical defect memory (≥88% threshold) to flag duplicate tickets and recall verified past fixes.
                        </p>
                      </div>
                    </div>

                    {/* Agent 4 */}
                    <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-start gap-3 shadow-2xs">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                        <Cpu className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">4. Root Cause Agent</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 font-semibold">Deductive Engine</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                          Deduces physical failure mechanisms (e.g. buffer de-allocation race condition, deadlock). Keeps agent deduction clearly separated from retrieved facts.
                        </p>
                      </div>
                    </div>

                    {/* Agent 5 */}
                    <div className="p-3 rounded-xl bg-white/80 dark:bg-surface/50 border border-slate-200 dark:border-surface-border flex items-start gap-3 shadow-2xs">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                        <Wrench className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900 dark:text-white">5. Remediation Agent</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold">Unified Diff</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5 leading-relaxed">
                          Synthesizes a syntactically valid unified git diff patch targeting the failing line and provides concrete 4-part architectural fix guidance.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-1 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400 border-t border-surface-border">
                    <span className="text-[11px]">💡 Click <strong>"Kafka OOM Buffer"</strong> on the left to test live!</span>
                    <button
                      onClick={() => setPrimaryMode('analytics')}
                      className="inline-flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold text-xs"
                    >
                      <BarChart3 className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                      <span>Explore Defect Pattern Analytics &rarr;</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

          </div>
        )}
      </div>
    </main>
  );
}
