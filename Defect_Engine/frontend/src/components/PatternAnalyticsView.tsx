'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  RefreshCw,
  Cpu,
  Layers,
  Zap,
  ArrowRight,
  Code2,
  Database,
  Globe,
  Radio,
  Lock,
  Flame
} from 'lucide-react';
import {
  SystemicPatternAnalytics,
  getPatternAnalytics,
  KnowledgeBaseStatsResponse,
  getKnowledgeBaseStats
} from '@/lib/api';

export const PatternAnalyticsView: React.FC = () => {
  const [analytics, setAnalytics] = useState<SystemicPatternAnalytics | null>(null);
  const [kbStats, setKbStats] = useState<KnowledgeBaseStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [analyticsData, kbData] = await Promise.all([
        getPatternAnalytics(),
        getKnowledgeBaseStats().catch(() => null)
      ]);
      setAnalytics(analyticsData);
      setKbStats(kbData);
    } catch (err: any) {
      console.error('Failed to load pattern analytics:', err);
      setError('Could not retrieve analytics. Ensure the backend engine is running.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20';
      case 'MODERATE':
        return 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border-indigo-500/20';
      default:
        return 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20';
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'B':
        return 'text-indigo-600 dark:text-indigo-400 border-indigo-500/30 bg-indigo-500/10';
      case 'C':
        return 'text-amber-600 dark:text-amber-400 border-amber-500/30 bg-amber-500/10';
      default:
        return 'text-red-600 dark:text-red-400 border-red-500/30 bg-red-500/10';
    }
  };

  const getComponentIcon = (name: string) => {
    const lower = name.toLowerCase();
    if (lower.includes('core')) return <Cpu className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />;
    if (lower.includes('storage') || lower.includes('database')) return <Database className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
    if (lower.includes('network')) return <Globe className="w-4 h-4 text-sky-600 dark:text-sky-400" />;
    if (lower.includes('message') || lower.includes('queue')) return <Radio className="w-4 h-4 text-purple-600 dark:text-purple-400" />;
    if (lower.includes('security') || lower.includes('auth')) return <Lock className="w-4 h-4 text-rose-600 dark:text-rose-400" />;
    return <Layers className="w-4 h-4 text-slate-500 dark:text-slate-400" />;
  };

  if (isLoading) {
    return (
      <div className="glass-panel rounded-2xl p-12 border border-surface-border flex flex-col items-center justify-center space-y-4 text-center">
        <RefreshCw className="w-8 h-8 text-indigo-600 dark:text-indigo-400 animate-spin" />
        <div className="text-sm font-semibold text-slate-800 dark:text-slate-300">Synthesizing Systemic Defect Patterns...</div>
        <p className="text-xs text-slate-500 max-w-sm">
          Analyzing recurring bug themes, calculating component risk indexes, and isolating failure hotspots.
        </p>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-red-500/20 text-center space-y-4">
        <AlertTriangle className="w-8 h-8 text-red-500 dark:text-red-400 mx-auto" />
        <div className="text-sm font-semibold text-red-600 dark:text-red-300">{error || 'No analytics data available.'}</div>
        <button
          onClick={fetchData}
          className="px-4 py-2 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-surface-border text-xs font-semibold text-slate-700 dark:text-slate-200 hover:text-slate-900 dark:hover:text-white"
        >
          Retry Analytics Sync
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Control Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel rounded-2xl p-5 border border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
              <BarChart3 className="w-4 h-4" />
            </span>
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white tracking-tight">
              Defect Pattern Analytics Module
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-500/30">
              M4.1 Active
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Autonomous aggregation of recurring bug themes, high-frequency components, and systemic health
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={isLoading}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-surface-border text-xs font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:border-indigo-500 transition-all shadow-2xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Health Score */}
        <div className="glass-panel rounded-2xl p-4 border border-surface-border relative overflow-hidden shadow-xs">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">
            Systemic Health Score
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 dark:text-white">{analytics.systemic_health_score}</span>
            <span className="text-xs font-bold text-slate-500">/ 100</span>
          </div>
          <div className="mt-2 flex items-center gap-1.5">
            <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getGradeColor(analytics.health_grade)}`}>
              Grade {analytics.health_grade}
            </span>
            <span className="text-[10px] text-slate-500 dark:text-slate-400">System Rating</span>
          </div>
        </div>

        {/* Analyzed Defects */}
        <div className="glass-panel rounded-2xl p-4 border border-surface-border shadow-xs">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">
            Defects In Scope
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 dark:text-white">{analytics.total_bugs_analyzed}</span>
            <span className="text-xs font-bold text-slate-500">tickets</span>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
            <span>Cross-Repository Corpus</span>
          </div>
        </div>

        {/* Knowledge Base Growth & Resolved */}
        <div className="glass-panel rounded-2xl p-4 border border-surface-border shadow-xs">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">
            KB Growth (Resolved)
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
              {kbStats?.user_resolved_defects_count ?? analytics.total_resolved_bugs}
            </span>
            <span className="text-xs font-bold text-slate-500">learned</span>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
            <span>{kbStats?.total_chunks ?? 30} Total Chunks Ingested</span>
          </div>
        </div>

        {/* Duplicate Rate */}
        <div className="glass-panel rounded-2xl p-4 border border-surface-border shadow-xs">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">
            Duplicate Ticket Rate
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-purple-600 dark:text-purple-400">{analytics.duplicate_rate_percentage}%</span>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <Layers className="w-3 h-3 text-purple-600 dark:text-purple-400" />
            <span>Vector Match Threshold &ge; 88%</span>
          </div>
        </div>
      </div>

      {/* Summary Narrative Banner */}
      <div className="p-4 rounded-2xl bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-500/20 flex items-start gap-3 shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-800 dark:text-slate-300 leading-relaxed">
          <strong className="text-indigo-700 dark:text-indigo-300 font-semibold">Systemic Diagnostic Summary: </strong>
          {analytics.summary_insight}
        </div>
      </div>

      {/* High-Frequency Affected Components */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
              High-Frequency Affected Components & Risk Distribution
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500">Sorted by Defect Volume</span>
        </div>

        <div className="space-y-3">
          {analytics.component_frequencies.map((comp) => (
            <div
              key={comp.component}
              className="p-3.5 rounded-xl bg-white/80 dark:bg-surface/40 border border-slate-200 dark:border-surface-border/70 hover:border-slate-400 dark:hover:border-slate-600 transition-all space-y-2.5 shadow-2xs"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-1 rounded-lg bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
                    {getComponentIcon(comp.component)}
                  </div>
                  <div>
                    <span className="text-xs font-bold text-slate-900 dark:text-white">{comp.component}</span>
                    <span className="ml-2 text-[11px] font-mono text-slate-500 dark:text-slate-400">
                      ({comp.count} defects &bull; {comp.percentage}%)
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getRiskBadge(comp.risk_level)}`}>
                    {comp.risk_level} RISK ({comp.risk_score})
                  </span>
                </div>
              </div>

              {/* Progress and Severity Breakdown Bar */}
              <div className="space-y-1">
                <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                  {comp.critical_count > 0 && (
                    <div
                      style={{ width: `${(comp.critical_count / comp.count) * 100}%` }}
                      className="bg-red-500 h-full"
                      title={`Critical: ${comp.critical_count}`}
                    />
                  )}
                  {comp.high_count > 0 && (
                    <div
                      style={{ width: `${(comp.high_count / comp.count) * 100}%` }}
                      className="bg-amber-500 h-full"
                      title={`High: ${comp.high_count}`}
                    />
                  )}
                  {comp.medium_count > 0 && (
                    <div
                      style={{ width: `${(comp.medium_count / comp.count) * 100}%` }}
                      className="bg-indigo-500 h-full"
                      title={`Medium: ${comp.medium_count}`}
                    />
                  )}
                  {comp.low_count > 0 && (
                    <div
                      style={{ width: `${(comp.low_count / comp.count) * 100}%` }}
                      className="bg-slate-400 dark:bg-slate-500 h-full"
                      title={`Low: ${comp.low_count}`}
                    />
                  )}
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 dark:text-slate-400 pt-0.5">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                      Critical: {comp.critical_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                      High: {comp.high_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                      Medium: {comp.medium_count}
                    </span>
                  </div>
                  <span>{comp.percentage}% share</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recurring Bug Themes & Systemic Patterns */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-amber-500 dark:text-amber-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
              Recurring Bug Themes & Systemic Failure Mechanisms
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500">{analytics.recurring_themes.length} Active Themes</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analytics.recurring_themes.map((theme) => (
            <div
              key={theme.theme_id}
              className="p-4 rounded-xl bg-white/80 dark:bg-surface/40 border border-slate-200 dark:border-surface-border hover:border-slate-400 dark:hover:border-slate-600 transition-all flex flex-col justify-between space-y-3 shadow-2xs"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-slate-900 dark:text-white">{theme.theme_name}</span>
                  <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${getRiskBadge(theme.impact_level)}`}>
                    {theme.impact_level}
                  </span>
                </div>

                <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mb-2.5">
                  {theme.description}
                </p>

                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-surface-border/30 border border-slate-200 dark:border-surface-border/50 text-[10px] space-y-1">
                  <div className="text-slate-600 dark:text-slate-400">
                    <strong className="text-slate-800 dark:text-slate-300">Failure Mechanism: </strong>
                    {theme.representative_failure_mechanism}
                  </div>
                  {theme.sample_exception_types.length > 0 && (
                    <div className="text-slate-600 dark:text-slate-400">
                      <strong className="text-slate-800 dark:text-slate-300">Observed Exceptions: </strong>
                      <span className="font-mono text-indigo-600 dark:text-indigo-300">{theme.sample_exception_types.join(', ')}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-200 dark:border-surface-border/40 flex items-center justify-between text-[10px] font-mono text-slate-500 dark:text-slate-400">
                <span>Associated: {theme.sample_bug_ids.join(', ')}</span>
                <span className="font-bold text-slate-900 dark:text-white">{theme.count} tickets ({theme.percentage}%)</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Systemic Hotspots & Failure Points */}
      {analytics.systemic_hotspots.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
                Systemic Code Hotspots & Crash Location Hotspots
              </h3>
            </div>
            <span className="text-[10px] font-mono text-slate-500">Isolated across Stack Traces</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {analytics.systemic_hotspots.map((spot, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-white/80 dark:bg-surface/30 border border-slate-200 dark:border-surface-border space-y-2 font-mono text-xs shadow-2xs"
              >
                <div className="flex items-center justify-between">
                  <span className="text-indigo-600 dark:text-indigo-400 font-bold truncate max-w-[180px]" title={spot.target}>
                    {spot.target}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    {spot.occurrence_count}x crash
                  </span>
                </div>
                <div className="text-[10px] text-slate-600 dark:text-slate-400 font-sans leading-snug line-clamp-2">
                  {spot.primary_failure_pattern}
                </div>
                <div className="flex items-center gap-1.5 text-[9px] text-slate-500">
                  <span>In: {spot.associated_components.join(', ')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Automated Architectural Recommendations */}
      {analytics.architectural_recommendations.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
                Automated Architectural Remediation Recommendations
              </h3>
            </div>
            <span className="text-[10px] font-mono text-purple-600 dark:text-purple-400">Engineering Action Plan</span>
          </div>

          <div className="space-y-3">
            {analytics.architectural_recommendations.map((rec, i) => (
              <div
                key={i}
                className="p-4 rounded-xl bg-purple-50/70 dark:bg-purple-950/10 border border-purple-200 dark:border-purple-500/20 flex items-start gap-3 text-xs shadow-2xs"
              >
                <div className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-700 dark:text-purple-300 font-mono font-bold text-[10px] border border-purple-500/30 shrink-0 mt-0.5">
                  {rec.priority}
                </div>
                <div className="space-y-1">
                  <div className="text-slate-900 dark:text-white font-semibold">
                    {rec.theme} &bull; Target: <span className="text-indigo-600 dark:text-indigo-300 font-mono">{rec.target_components}</span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                    {rec.actionable_recommendation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
