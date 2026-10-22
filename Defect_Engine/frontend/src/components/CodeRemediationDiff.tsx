'use client';

import React, { useState } from 'react';
import { GitCommit, Copy, Check, ShieldCheck, Wrench } from 'lucide-react';
import { BugSubmissionResponse } from '@/lib/api';

interface CodeRemediationDiffProps {
  report: BugSubmissionResponse;
}

export const CodeRemediationDiff: React.FC<CodeRemediationDiffProps> = ({ report }) => {
  const [copied, setCopied] = useState(false);

  const diffText = report.suggested_fix || '--- a/app/service.py\n+++ b/app/service.py\n@@ -10,3 +10,5 @@\n-    result = process()\n+    if process is not None:\n+        result = process()\n';

  const handleCopy = () => {
    navigator.clipboard.writeText(diffText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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

  return (
    <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-xl border border-indigo-500/20">
            <GitCommit className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Automated Code Remediation Patch
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Generated Unified Diff (`git diff`) Patch & Fix Advice</p>
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-xl bg-white dark:bg-surface border border-slate-200 dark:border-surface-border hover:border-indigo-500 hover:text-slate-900 dark:hover:text-white transition-all text-slate-700 dark:text-slate-300 shadow-2xs"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Patch</span>
            </>
          )}
        </button>
      </div>

      {/* Unified Diff View */}
      <div className="rounded-xl border border-surface-border bg-slate-950/95 overflow-x-auto py-3 shadow-inner">
        {parseDiffLines(diffText)}
      </div>

      {/* Step-by-Step Mitigation Checklist */}
      {report.remediation_steps && (
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-surface/50 border border-slate-200 dark:border-surface-border space-y-2 shadow-2xs">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider mb-2">
            <Wrench className="w-4 h-4" />
            <span>Recommended Mitigation Steps</span>
          </div>

          <div className="text-xs text-slate-700 dark:text-slate-300 font-sans space-y-1.5 whitespace-pre-line leading-relaxed">
            {report.remediation_steps}
          </div>
        </div>
      )}
    </div>
  );
};
