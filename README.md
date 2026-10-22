# Infosys SpringBoard Project: Autonomous Software Defect Analysis & Multi-Agent Triage Engine (DefectMind)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.1-black?logo=next.js)](https://nextjs.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)](https://www.trychroma.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blue)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Repository Structure

```
Infosys_SpringBoard_Project/
├── Defect_Engine/                       # Core autonomous defect platform
│   ├── backend/                         # FastAPI, LangGraph orchestrator, ChromaDB RAG
│   ├── frontend/                        # Next.js 14 Glassmorphism dashboard
│   ├── README.md                        # DefectMind platform documentation
│   ├── PROJECT_REPORT_FINAL.md          # Comprehensive technical milestone report
│   ├── MILESTONES_SUMMARY.md            # Milestones 1–4 architecture & changelog
│   └── DEPLOYMENT_GUIDE.md              # Cloud deployment guide (Render, Supabase, Vercel)
│
├── Internship_artifacts/                # Populated internship delivery artifacts
│   ├── Unit_Test_Plan_v0.1.xlsx         # 18 comprehensive unit test cases
│   ├── Defect_Tracker Template_v0.1.xlsx# 14 real development defects across Sprints 1–4
│   └── Agile_Template_v0.1.xls          # Product Backlog, Sprint Backlog, Standups, Retros
│
├── DefectMind_Complete_Project_Guide_and_Demo_Script.pdf  # Master presentation & demo guide
├── DefectMind_UI_Guide.pdf                                # UI walkthrough documentation
├── LICENSE                                                # MIT License
└── README.md                                              # Repository root overview
```

---

## Project Overview: DefectMind

**DefectMind** is a production-grade, developer-first autonomous defect analysis engine designed to ingest heterogeneous error logs, strip framework noise, coordinate a 5-agent LangGraph orchestrator, diagnose failure mechanisms, detect duplicates via ChromaDB dense vector RAG, synthesize unified git diff code patches, continuously learn from confirmed resolutions, and aggregate systemic defect pattern analytics across codebases.

### Key Capabilities
1. **Multi-Format Log Parser**: Supports Java, Python, C/C++ GDB, Go panic traces, Node.js V8, and syslog streams with 100% extraction accuracy.
2. **Autonomous Triage Agent**: Classifies Severity (`Critical`/`High`/`Medium`/`Low`), Priority (`P1`–`P4`), and Subsystem routing with transparent rationale.
3. **ChromaDB 3-Chunk RAG**: Queries historical defect collections using calibrated thresholds ($\ge 88\%$ Duplicate, $75\%\text{--}87\%$ Related, $< 75\%$ New).
4. **Deductive Root Cause Deduction**: Identifies physical failure mechanisms (memory exhaustion, deadlocks, race conditions, corrupt blocks) while strictly separating deductive reasoning from retrieved evidence.
5. **Remediation & Patching**: Synthesizes syntactically valid unified git diff patches alongside 4-part architectural fix guidance (Code, Configuration, Validation, Error Handling).
6. **Defect Pattern Analytics (M4.1)**: Executive Systemic Health Score (0–100), Component Risk Index, and 6 recurring defect failure theme clusters.
7. **Continuous Knowledge Base Growth (M4.2)**: 1-click confirmation dynamically embeds verified fixes back into ChromaDB using the 3-chunk ingestion strategy.

For complete technical specifications, see **[`Defect_Engine/PROJECT_REPORT_FINAL.md`](Defect_Engine/PROJECT_REPORT_FINAL.md)**.
