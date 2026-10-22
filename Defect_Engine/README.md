# Autonomous Software Defect Analysis & Multi-Agent Triage Engine (DefectMind)

### Complete Architecture — Milestones 1, 2, 3 & 4

An end-to-end production-grade platform for autonomous log de-noising, vector-based historical bug retrieval (RAG), multi-agent state orchestration (LangGraph), root cause deduction, duplicate detection, unified diff code patch generation, structured findings reporting, **continuous knowledge base growth**, and **systemic defect pattern analytics**.

> For the comprehensive final report and case studies, see **[PROJECT_REPORT_FINAL.md](PROJECT_REPORT_FINAL.md)**.
> For the complete changelog across all milestones, see **[MILESTONES_SUMMARY.md](MILESTONES_SUMMARY.md)**.

---

## Key Features

1. **Bug Submission & Log Sanitizer Module (FastAPI)**
   - Accepts title, functional description, stack trace, and environment details.
   - Multipart file upload support for `.log`, `.txt`, and `.json` crash files.
   - Multi-format log parser covering Java, Python, C/C++ GDB, Go panic dumps, Node.js V8 traces, and production syslogs.
   - Isolates developer application frames from framework/stdlib runtime noise.

2. **Historical Defect RAG Knowledge Base (ChromaDB)**
   - Dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with cosine HNSW indexing.
   - **3-Chunk Ingestion Strategy**:
     - **Chunk 1**: Bug Title + Functional Description (Overview)
     - **Chunk 2**: Error Trace + Offending Function Call (Stack Trace)
     - **Chunk 3**: Verified Root Cause + Resolution Patch (Resolution)
   - Seeded with Apache, Mozilla, and Eclipse defect records.

3. **LangGraph Multi-Agent Orchestration Engine**
   - **Log Analysis Agent**: Isolates top offending frame, class, line, and method sequence.
   - **Triage Agent**: Classifies Severity (`Critical`, `High`, `Medium`, `Low`), Priority (`P1`-`P4`), and Component.
   - **Duplicate Detection Agent**: Semantic similarity ranking, calibrated thresholding (Duplicate $\ge 88\%$, Related $\ge 75\%$, Unmatched $< 75\%$), and per-match reasoning.
   - **Root Cause Agent**: Identifies specific failure mechanisms (heap exhaustion, race condition, deadlock, SSTable corruption) and separates agent deductive reasoning from retrieved evidence.
   - **Remediation Agent**: Synthesizes unified diff code patches (`--- a/... +++ b/...`) and technical recommendations (code, config, validation, error handling).

4. **Defect Pattern Analytics Module (Milestone 4.1)**
   - **High-Frequency Affected Components**: Distribution, counts, percentages, and weighted risk scores.
   - **Recurring Defect Themes**: Clusters crashes into 6 failure categories (Memory Exhaustion, Null State Inconsistency, Concurrency Deadlocks, Network Failures, Storage Corruption, Security/Auth).
   - **Systemic Hotspots**: Tracks top recurring offending files and methods across all submitted defect traces.
   - **Systemic Health Score**: Executive 0-100 rating and letter grade (`A` to `F`).
   - **Architectural Action Plans**: Tailored engineering guidance based on systemic failure clusters.

5. **Knowledge Base Growth Mechanism (Milestone 4.2)**
   - When an engineer confirms a resolution, the verified root cause and fix are ingested into ChromaDB using the 3-Chunk Ingestion Strategy.
   - Subsequent vector queries immediately retrieve this newly learned ticket, grounding future recommendations in verified fixes.

6. **Modern Next.js 14 Glassmorphism Dashboard**
   - Interactive dual-panel layout with real-time agent status tracker and exportable Markdown report.
   - **Pattern Analytics View**: Systemic health scorecard, component risk breakdown, recurring theme cards, and architectural recommendations.
   - **Knowledge Base Growth Card**: 1-click confirmation and vector store ingestion.
   - **5 Distinct Demonstration Presets**: 1-click sample presets covering Kafka, Mozilla Gecko, Python AsyncIO, Go panic, and Cassandra SSTable.

---

## Quick Start & Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 1. Install Backend Dependencies & Seed Vector Store
```bash
cd backend

# Install python dependencies
pip3 install -r requirements.txt

# Seed ChromaDB vector database with historical defect datasets
python3 scripts/seed_historical_data.py
```

### 2. Start FastAPI Backend Server
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Install & Start Frontend Dashboard
```bash
cd frontend

# Install node dependencies
npm install

# Start Next.js development server
npm run dev
```
- Dashboard UI: [http://localhost:3000](http://localhost:3000)

---

## Test & Benchmark Verification Runners

### 1. Milestone 4 End-to-End Accuracy Benchmark (93.00% Score)
```bash
cd backend
python3 scripts/validate_m4_accuracy.py
```

### 2. Unified Unit & Integration Test Suite (100% Pass Rate across M1-M4)
```bash
cd backend
python3 tests/run_tests.py
```

### 3. Final Demonstration Showcase (5 Distinct Bug Pipeline Execution)
```bash
cd backend
python3 scripts/demo_showcase.py
```

---

## REST API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/bugs/submit` | Submit defect (JSON or multipart log upload) and execute 5-agent LangGraph workflow |
| `GET` | `/api/v1/bugs/submissions` | List all historical defect submission reports |
| `GET` | `/api/v1/bugs/submissions/{id}` | Get detailed defect diagnosis, root cause, diff patch, and duplicate matrix |
| `POST` | `/api/v1/bugs/submissions/{id}/resolve` | **Milestone 4.2**: Confirm resolution and ingest 3 chunks into ChromaDB knowledge base |
| `GET` | `/api/v1/bugs/knowledge-base/stats` | **Milestone 4.2**: Retrieve knowledge base chunk counts and growth stats |
| `GET` | `/api/v1/bugs/analytics/patterns` | **Milestone 4.1**: Retrieve systemic defect pattern analytics, themes & hotspots |
| `POST` | `/api/v1/bugs/search-similar` | Hybrid cosine vector search over ChromaDB historical defects |
