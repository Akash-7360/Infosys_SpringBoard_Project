'use client';

import React, { useState, useRef } from 'react';
import {
  Upload,
  FileText,
  Sparkles,
  AlertCircle,
  Play,
  CheckCircle2,
  X,
  FileCode2,
  Terminal,
  Layers
} from 'lucide-react';
import { submitBugReport, BugSubmissionResponse } from '@/lib/api';

interface BugSubmissionFormProps {
  onSubmissionSuccess: (result: BugSubmissionResponse) => void;
  isSubmitting: boolean;
  setIsSubmitting: (state: boolean) => void;
}

const PRESET_SAMPLE_CRASHES = [
  {
    id: 'kafka',
    badge: 'Java',
    badgeColor: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    label: 'Kafka OOM Buffer',
    title: 'NullPointerException in RecordAccumulator drain during high memory pressure batch flush',
    desc: 'Producer application crashed under heavy load when batch size exceeded buffer memory threshold. The drain loop attempted to reference a recycled ProducerBatch.',
    trace: `java.lang.NullPointerException: Cannot invoke "org.apache.kafka.clients.producer.internals.ProducerBatch.drain()" because "batch" is null\n\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)\n\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)\n\tat org.apache.kafka.clients.producer.internals.Sender.run(Sender.java:240)`,
    repo: 'Apache',
    component: 'Messaging/Queue',
    env: 'Linux 5.15 x86_64, OpenJDK 17.0.2, Kafka 3.4.0'
  },
  {
    id: 'gecko',
    badge: 'C++',
    badgeColor: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
    label: 'Gecko Segfault',
    title: 'Access violation SIGSEGV in nsCSSFrameConstructor::ConstructFrame layout tree',
    desc: 'Firefox rendering engine crashed with access violation while reconstructing frame tree for dynamic nested CSS flexbox layout.',
    trace: `CRASH INFO: Crash Type: EXCEPTION_ACCESS_VIOLATION_READ (SIGSEGV)\n#0  0x00007fff8912ba40 in nsCSSFrameConstructor::ConstructFrame(nsFrameConstructorState&, nsIContent*, nsContainerFrame*, nsFrameList&) at layout/base/nsCSSFrameConstructor.cpp:6421\n#1  0x00007fff8912cb10 in nsCSSFrameConstructor::ContentAppended(nsIContent*, nsIContent*) at layout/base/nsCSSFrameConstructor.cpp:6800\n#2  0x00007fff8901aa20 in PresShell::ContentAppended(nsIContent*, nsIContent*) at layout/base/PresShell.cpp:4210`,
    repo: 'Mozilla',
    component: 'Core',
    env: 'Ubuntu 22.04 LTS x86_64, Clang 15.0, Firefox Gecko'
  },
  {
    id: 'asyncio',
    badge: 'Python',
    badgeColor: 'text-sky-400 bg-sky-400/10 border-sky-400/20',
    label: 'AsyncIO Deadlock',
    title: 'TimeoutError and connection deadlock in async database pool acquire',
    desc: 'FastAPI microservice hung during peak traffic spike due to unreleased connection semaphore in SQLAlchemy async pool under high concurrent queries.',
    trace: `Traceback (most recent call last):\n  File "/app/services/query_executor.py", line 142, in execute_transaction\n    async with pool.acquire(timeout=5.0) as conn:\n  File "/usr/local/lib/python3.11/site-packages/asyncpg/pool.py", line 748, in acquire\n    return await asyncio.wait_for(self._acquire(timeout), timeout)\n  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 479, in wait_for\n    raise exceptions.TimeoutError()\nasyncio.exceptions.TimeoutError: Connection semaphore acquisition timed out after 5.0s`,
    repo: 'Microservices',
    component: 'Database/Storage',
    env: 'Debian 12, Python 3.11.4, asyncpg 0.28.0'
  },
  {
    id: 'go',
    badge: 'Go',
    badgeColor: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
    label: 'Go Channel Panic',
    title: 'panic: send on closed channel in message distributor worker',
    desc: 'Go high-throughput telemetry agent panicked when upstream broadcaster closed the response channel while consumer workers were still writing diagnostics.',
    trace: `panic: send on closed channel\n\ngoroutine 64 [running]:\nmain.(*MessageDistributor).Dispatch(0xc00010c000, 0xc00028a000)\n\t/go/src/collector/distributor.go:128 +0x3a4\nmain.worker(0xc00010c000, 0x1)\n\t/go/src/collector/worker.go:45 +0x88\ncreated by main.StartCollector\n\t/go/src/collector/main.go:92 +0x1b0`,
    repo: 'Microservices',
    component: 'Networking',
    env: 'Alpine Linux, Go 1.21.3 amd64, Kubernetes Pod'
  },
  {
    id: 'cassandra',
    badge: 'Java',
    badgeColor: 'text-rose-400 bg-rose-400/10 border-rose-400/20',
    label: 'SSTable Checksum',
    title: 'CorruptSSTableException when reading compressed SSTable chunk index',
    desc: 'Node failed to complete compaction due to CRC32 checksum mismatch in CompressedRandomAccessReader while decompressing chunk 42.',
    trace: `org.apache.cassandra.io.sstable.CorruptSSTableException: org.apache.cassandra.io.compress.CorruptBlockException: checksum mismatch in /var/lib/cassandra/data/keyspace1/standard1-ca1-Data.db at chunk 42\n\tat org.apache.cassandra.io.compress.CompressedRandomAccessReader.decompressChunk(CompressedRandomAccessReader.java:112)\n\tat org.apache.cassandra.io.compress.CompressedRandomAccessReader.reBuffer(CompressedRandomAccessReader.java:88)\n\tat org.apache.cassandra.io.util.RandomAccessReader.read(RandomAccessReader.java:142)\n\tat org.apache.cassandra.db.compaction.CompactionTask.execute(CompactionTask.java:234)`,
    repo: 'Apache',
    component: 'Database/Storage',
    env: 'Red Hat Enterprise Linux 8.8, OpenJDK 11, Cassandra 4.1.2'
  }
];

export const BugSubmissionForm: React.FC<BugSubmissionFormProps> = ({
  onSubmissionSuccess,
  isSubmitting,
  setIsSubmitting
}) => {
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [environmentDetails, setEnvironmentDetails] = useState('');
  const [repository, setRepository] = useState('Apache');
  const [component, setComponent] = useState('Messaging/Queue');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const loadPreset = (preset: typeof PRESET_SAMPLE_CRASHES[0]) => {
    setActivePreset(preset.id);
    setTitle(preset.title);
    setDescription(preset.desc);
    setStackTrace(preset.trace);
    setRepository(preset.repo);
    setComponent(preset.component);
    setEnvironmentDetails(preset.env);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg('Please enter a defect title or summary.');
      return;
    }
    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('title', title);
      if (description) formData.append('description', description);
      if (stackTrace) formData.append('stack_trace', stackTrace);
      if (environmentDetails) formData.append('environment_details', environmentDetails);
      formData.append('repository', repository);
      formData.append('component', component);
      if (selectedFile) formData.append('log_file', selectedFile);

      const result = await submitBugReport(formData);
      onSubmissionSuccess(result);
    } catch (err: any) {
      console.error('Submission error:', err);
      if (err.response?.status === 429) {
        const retrySec = err.response?.data?.retry_after_seconds || 60;
        setErrorMsg(err.response?.data?.message || `Rate limit exceeded. Please wait ${retrySec} seconds before submitting again.`);
      } else {
        setErrorMsg(err.response?.data?.message || err.response?.data?.detail || err.message || 'Failed to submit bug report for analysis.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearForm = () => {
    setActivePreset(null);
    setTitle('');
    setDescription('');
    setStackTrace('');
    setEnvironmentDetails('');
    setSelectedFile(null);
    setErrorMsg(null);
  };

  return (
    <div className="glass-panel rounded-2xl p-5 sm:p-6 border border-surface-border text-slate-800 dark:text-slate-200">
      {/* Header & Reset */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-surface-border/80">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">Defect Intake & Triage</h2>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Autonomous 5-agent pipeline</p>
          </div>
        </div>

        {(title || stackTrace || selectedFile) && (
          <button
            type="button"
            onClick={clearForm}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            Clear Form
          </button>
        )}
      </div>

      {/* Preset Showcase Selector */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Showcase Presets:
          </span>
          <span className="text-[10px] text-slate-400 dark:text-slate-500">1-click test load</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
          {PRESET_SAMPLE_CRASHES.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => loadPreset(preset)}
              className={`p-2 rounded-xl text-left border transition-all text-xs flex items-center justify-between gap-1.5 ${
                activePreset === preset.id
                  ? 'bg-indigo-50 dark:bg-indigo-600/15 border-indigo-500 text-slate-900 dark:text-white shadow-xs'
                  : 'bg-white/90 dark:bg-surface/50 border-slate-200 dark:border-surface-border/70 hover:border-slate-400 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
              }`}
            >
              <span className="truncate font-medium text-[11px]">{preset.label}</span>
              <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded border shrink-0 ${preset.badgeColor}`}>
                {preset.badge}
              </span>
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3.5">
        {/* Defect Title */}
        <div>
          <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
            Defect Title or Summary <span className="text-rose-500 dark:text-rose-400">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setActivePreset(null);
            }}
            placeholder="e.g. NullPointerException in RecordAccumulator during batch drain"
            className="w-full bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-sans shadow-2xs"
            required
          />
        </div>

        {/* Repository & Component Selectors */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
              Repository
            </label>
            <select
              value={repository}
              onChange={(e) => setRepository(e.target.value)}
              className="w-full bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border rounded-xl px-3 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 shadow-2xs"
            >
              <option value="Apache">Apache</option>
              <option value="Mozilla">Mozilla</option>
              <option value="Eclipse">Eclipse</option>
              <option value="Microservices">Microservices</option>
              <option value="General">General / Custom</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
              Component
            </label>
            <select
              value={component}
              onChange={(e) => setComponent(e.target.value)}
              className="w-full bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border rounded-xl px-3 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 shadow-2xs"
            >
              <option value="Core">Core</option>
              <option value="Messaging/Queue">Messaging/Queue</option>
              <option value="Database/Storage">Database/Storage</option>
              <option value="Networking">Networking</option>
              <option value="Security/Auth">Security/Auth</option>
              <option value="Frontend/UI">Frontend/UI</option>
            </select>
          </div>
        </div>

        {/* Stack Trace */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-medium text-slate-700 dark:text-slate-300">
              Stack Trace or Error Log
            </label>
            <span className="text-[10px] text-slate-400 dark:text-slate-500">Java, Python, C++, Go, Node</span>
          </div>
          <textarea
            value={stackTrace}
            onChange={(e) => setStackTrace(e.target.value)}
            rows={4}
            placeholder="Paste crash traceback, GDB backtrace, or panic dump..."
            className="w-full bg-white dark:bg-surface/60 border border-slate-200 dark:border-surface-border rounded-xl p-3 text-xs font-mono text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all shadow-2xs"
          />
        </div>

        {/* Drag and Drop File Upload Zone */}
        <div>
          <label className="block text-[11px] font-medium text-slate-700 dark:text-slate-300 mb-1">
            Attach Crash Log File <span className="text-slate-400 dark:text-slate-500 font-normal">(.log, .txt, .json)</span>
          </label>

          {selectedFile ? (
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-white dark:bg-surface/60 border border-indigo-400 dark:border-indigo-500/40 text-xs shadow-xs">
              <div className="flex items-center gap-2 truncate">
                <FileCode2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
                <span className="text-slate-900 dark:text-white truncate font-mono text-[11px]">{selectedFile.name}</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 shrink-0">
                  ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="p-1 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border border-dashed rounded-xl p-3 text-center cursor-pointer transition-all ${
                dragActive
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10'
                  : 'border-slate-300 dark:border-surface-border hover:border-slate-400 dark:hover:border-slate-500 bg-slate-50/60 dark:bg-surface/20'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".log,.txt,.json"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex items-center justify-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <Upload className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                <span>Drop crash log here or <strong className="text-indigo-600 dark:text-indigo-400">browse</strong></span>
              </div>
            </div>
          )}
        </div>

        {/* Submit Action Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Orchestrating Multi-Agent Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Analyze Defect with Agents</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
