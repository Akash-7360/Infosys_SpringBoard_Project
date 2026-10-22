"""
M2 Accuracy & Performance Evaluation Runner.
Executes Triage Agent and Log Analysis Agent against the benchmark test set (test_dataset.py)
and computes accuracy metrics for Severity, Priority, Component, Exception Type, Failure Point, and Code Path.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.log_analysis_agent import log_analysis_agent_node
from app.agents.triage_agent import triage_agent_node
from app.agents.state import DefectAnalysisState
from tests.test_dataset import M2_VALIDATION_DATASET

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("m2_validation")


async def run_accuracy_validation():
    print("=" * 95)
    print("      AUTONOMOUS DEFECT ENGINE - MILESTONE 2 ACCURACY & PERFORMANCE VALIDATION")
    print("=" * 95)

    total_cases = len(M2_VALIDATION_DATASET)
    
    # Correct counters
    severity_correct = 0
    priority_correct = 0
    component_correct = 0
    exception_correct = 0
    failure_file_correct = 0
    failure_line_correct = 0
    code_path_correct = 0

    results_table = []

    for test_case in M2_VALIDATION_DATASET:
        tc_id = test_case["id"]
        title = test_case["title"]
        desc = test_case["description"]
        trace = test_case["stack_trace"]
        
        # Build initial graph state
        state: DefectAnalysisState = {
            "bug_id": f"TEST-{tc_id}",
            "raw_title": title,
            "raw_description": desc,
            "raw_stack_trace": trace,
            "raw_log_content": trace if test_case["format"] == "LogOnly" else "",
            "environment_details": "Test Environment",
            "repository": "Mozilla/Apache/Eclipse",
            "component": "General",
            "parsed_log": {},
            "triage_info": {},
            "duplicate_info": {},
            "root_cause_info": {},
            "remediation_info": {},
            "retrieved_docs": [],
            "status": "PROCESSING",
            "workflow_steps": []
        }

        # 1. Run Log Analysis Agent Node
        log_res = await log_analysis_agent_node(state)
        state["parsed_log"] = log_res.get("parsed_log", {})
        state["workflow_steps"].extend(log_res.get("workflow_steps", []))

        # 2. Run Triage Agent Node
        triage_res = await triage_agent_node(state)
        triage_info = triage_res.get("triage_info", {})

        # Extract Predictions
        pred_sev = triage_info.get("severity")
        pred_pri = triage_info.get("priority")
        pred_comp = triage_info.get("component")
        triage_conf = triage_info.get("confidence_score", 0.0)

        parsed_log = state.get("parsed_log", {})
        pred_exc = parsed_log.get("exception_type")
        fp = parsed_log.get("failure_point") or {}
        pred_file = fp.get("file_name")
        pred_line = fp.get("line_number")
        code_path = parsed_log.get("code_path", [])
        log_conf = parsed_log.get("confidence_score", 0.0)

        # Ground Truths
        exp_sev = test_case["expected_severity"]
        exp_pri = test_case["expected_priority"]
        exp_comp = test_case["expected_component"]
        exp_exc = test_case["expected_exception"]
        exp_file = test_case["expected_file"]
        exp_line = test_case["expected_line"]

        # Matches
        m_sev = pred_sev == exp_sev
        m_pri = pred_pri == exp_pri
        m_comp = pred_comp == exp_comp
        m_exc = pred_exc.lower() == exp_exc.lower() if (pred_exc and exp_exc) else False
        
        m_file = (pred_file and exp_file and exp_file.lower() in pred_file.lower()) or (pred_file is None and exp_file is None)
        m_line = (pred_line == exp_line) if exp_line is not None else True
        m_path = len(code_path) > 0 if exp_file else True

        if m_sev: severity_correct += 1
        if m_pri: priority_correct += 1
        if m_comp: component_correct += 1
        if m_exc: exception_correct += 1
        if m_file: failure_file_correct += 1
        if m_line: failure_line_correct += 1
        if m_path: code_path_correct += 1

        status_flag = "✓ PASS" if (m_sev and m_exc and m_file) else "✗ MISMATCH"
        results_table.append({
            "id": tc_id,
            "format": test_case["format"],
            "status": status_flag,
            "sev_match": f"{pred_sev} vs {exp_sev}",
            "exc_match": f"{pred_exc} vs {exp_exc}",
            "file_match": f"{pred_file or 'None'} vs {exp_file or 'None'}",
            "conf": f"T:{int(triage_conf*100)}% L:{int(log_conf*100)}%"
        })

    # Display Test Results Matrix
    print(f"\n{'ID':<6} | {'Format':<16} | {'Status':<10} | {'Severity (Pred vs Exp)':<22} | {'Exception (Pred vs Exp)':<30} | {'Confidence':<12}")
    print("-" * 105)
    for r in results_table:
        print(f"{r['id']:<6} | {r['format']:<16} | {r['status']:<10} | {r['sev_match']:<22} | {r['exc_match']:<30} | {r['conf']:<12}")

    # Compute Metrics
    acc_sev = (severity_correct / total_cases) * 100
    acc_pri = (priority_correct / total_cases) * 100
    acc_comp = (component_correct / total_cases) * 100
    acc_exc = (exception_correct / total_cases) * 100
    acc_file = (failure_file_correct / total_cases) * 100
    acc_line = (failure_line_correct / total_cases) * 100
    acc_path = (code_path_correct / total_cases) * 100

    overall_m2_accuracy = (acc_sev + acc_comp + acc_exc + acc_file) / 4.0

    print("\n" + "=" * 95)
    print("                            ACCURACY METRICS SUMMARY REPORT")
    print("=" * 95)
    print(f" Total Benchmark Evaluation Test Cases : {total_cases}")
    print(f" M2.1 Triage Severity Classification   : {acc_sev:6.2f}% ({severity_correct}/{total_cases})")
    print(f" M2.1 Triage Priority Assignment       : {acc_pri:6.2f}% ({priority_correct}/{total_cases})")
    print(f" M2.1 Triage Component Identification  : {acc_comp:6.2f}% ({component_correct}/{total_cases})")
    print(f" M2.2 Log Exception Extraction         : {acc_exc:6.2f}% ({exception_correct}/{total_cases})")
    print(f" M2.2 Failure Point File Extraction    : {acc_file:6.2f}% ({failure_file_correct}/{total_cases})")
    print(f" M2.2 Failure Point Line Extraction    : {acc_line:6.2f}% ({failure_line_correct}/{total_cases})")
    print(f" M2.2 Code Path Sequence Extraction    : {acc_path:6.2f}% ({code_path_correct}/{total_cases})")
    print("-" * 95)
    print(f" OVERALL MILESTONE 2 ACCURACY SCORE    : {overall_m2_accuracy:6.2f}%")
    print("=" * 95)

    if overall_m2_accuracy >= 85.0:
        print(" SUCCESS: Milestone 2 Agent Engine meets all accuracy requirements! (Score >= 85%)")
    else:
        print(" WARNING: Overall accuracy below 85% target threshold. Review misclassifications.")
    print("=" * 95 + "\n")

    return overall_m2_accuracy


if __name__ == "__main__":
    asyncio.run(run_accuracy_validation())
