'use client';

import React, { useState } from 'react';
import { Database, Search, ChevronRight, ExternalLink, GitPullRequest } from 'lucide-react';
import { HistoricalBugItem } from '@/lib/api';

interface SimilarBugsListProps {
  similarBugs?: HistoricalBugItem[];
}

export const SimilarBugsList: React.FC<SimilarBugsListProps> = ({ similarBugs = [] }) => {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(0);

  if (!similarBugs || similarBugs.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-surface-border text-center text-slate-500 dark:text-slate-400">
        <Database className="w-8 h-8 text-slate-400 dark:text-slate-600 mx-auto mb-2" />
        <p className="text-sm">No historical vector matches retrieved yet.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-6 border border-surface-border">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-surface-border">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl border border-emerald-500/20">
            <Database className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Top-{similarBugs.length} Historical Vector Matches
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Retrieved from Mozilla, Apache & Eclipse ChromaDB collection</p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20 font-medium">
          RAG Pipeline Active
        </span>
      </div>

      <div className="space-y-3">
        {similarBugs.map((bug, idx) => {
          const matchPct = Math.round(bug.similarity_score * 100);
          const isExpanded = expandedIdx === idx;

          return (
            <div
              key={idx}
              className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                isExpanded
                  ? 'bg-white dark:bg-surface/80 border-indigo-400 dark:border-indigo-500/40 shadow-md'
                  : 'bg-slate-50/70 dark:bg-surface/30 border-slate-200 dark:border-surface-border hover:border-slate-400 dark:hover:border-slate-600'
              }`}
            >
              {/* Card Header */}
              <div
                onClick={() => setExpandedIdx(isExpanded ? null : idx)}
                className="p-4 cursor-pointer flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 shrink-0">
                    {bug.bug_id}
                  </span>

                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-surface border border-slate-200 dark:border-surface-border text-slate-700 dark:text-slate-300 shrink-0">
                    {bug.repository} / {bug.component}
                  </span>

                  <h4 className="text-sm font-medium text-slate-900 dark:text-slate-200 truncate">
                    {bug.title}
                  </h4>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {/* Similarity Badge */}
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                      matchPct >= 80
                        ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30'
                        : matchPct >= 65
                        ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30'
                        : 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border-indigo-500/30'
                    }`}
                  >
                    {matchPct}% Match
                  </span>

                  <ChevronRight
                    className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${
                      isExpanded ? 'rotate-90' : ''
                    }`}
                  />
                </div>
              </div>

              {/* Expanded Resolution Details */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-2 border-t border-slate-200 dark:border-surface-border/50 text-xs space-y-3 bg-slate-50/90 dark:bg-slate-950/40">
                  <div>
                    <div className="text-slate-500 dark:text-slate-400 font-semibold mb-1 uppercase tracking-wider text-[10px]">
                      Historical Functional Description:
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 font-sans leading-relaxed">
                      {bug.description}
                    </p>
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-semibold mb-1 uppercase tracking-wider text-[10px]">
                      <GitPullRequest className="w-3.5 h-3.5" />
                      <span>Verified Historical Resolution & Patch:</span>
                    </div>
                    <div className="p-3 rounded-lg bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-500/20 font-mono text-slate-800 dark:text-slate-200 leading-relaxed shadow-2xs">
                      {bug.resolution}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
