"""
Milestone 3 Accuracy & Performance Evaluation Runner.
Executes the Milestone 3 Agent Pipeline (Log Analysis, Triage, Duplicate Detection,
Root Cause Analysis, Remediation) across the benchmark test suite (test_m3_dataset.py)
and computes evaluation metrics for:
- M3.1 Root Cause Hypothesis & Mechanism Accuracy
- M3.2 Duplicate Detection Precision, Recall & Classification
- M3.3 Remediation Relevance, Patch Validity & Evidence Grounding
"""

import sys
import os
import asyncio
import logging

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.log_analysis_agent import log_analysis_agent_node
from app.agents.triage_agent import triage_agent_node
from app.agents.duplicate_agent import duplicate_agent_node
from app.agents.root_cause_agent import root_cause_agent_node
from app.agents.remediation_agent import remediation_agent_node
from app.agents.state import DefectAnalysisState
from tests.test_m3_dataset import M3_BENCHMARK_DATASET

logging.basicConfig(level=logging.WARNING)


async def run_m3_accuracy_validation():
    print("=" * 105)
    print("      AUTONOMOUS DEFECT ENGINE - MILESTONE 3 ACCURACY & PERFORMANCE VALIDATION")
    print("=" * 105)

    total_cases = len(M3_BENCHMARK_DATASET)
    
    # Counters
    dup_status_correct = 0
    dup_id_correct = 0
    dup_eval_total = 0
    
    rc_hypothesis_correct = 0
    rc_evidence_status_correct = 0
    rc_confidence_valid = 0
    
    rem_patch_valid = 0
    rem_grounding_correct = 0
    rem_speculative_correct = 0
    rem_target_module_correct = 0

    results_table = []

    for tc in M3_BENCHMARK_DATASET:
        tc_id = tc["id"]
        category = tc["category"]
        title = tc["title"]
        desc = tc["description"]
        trace = tc["stack_trace"]
        repo = tc["repository"]
        comp = tc["component"]

        # Initial State
        state: DefectAnalysisState = {
            "bug_id": f"BENCH-{tc_id}",
            "raw_title": title,
            "raw_description": desc,
            "raw_stack_trace": trace,
            "raw_log_content": trace,
            "environment_details": "Benchmark Linux 5.15 x86_64",
            "repository": repo,
            "component": comp,
            "parsed_log": {},
            "triage_info": {},
            "duplicate_info": {},
            "root_cause_info": {},
            "remediation_info": {},
            "retrieved_docs": [],
            "status": "PROCESSING",
            "workflow_steps": []
        }

        # 1. Log Analysis Node
        log_res = await log_analysis_agent_node(state)
        state["parsed_log"] = log_res.get("parsed_log", {})
        state["workflow_steps"].extend(log_res.get("workflow_steps", []))

        # 2. Triage Node
        triage_res = await triage_agent_node(state)
        state["triage_info"] = triage_res.get("triage_info", {})
        state["component"] = triage_res.get("component") or comp
        state["workflow_steps"].extend(triage_res.get("workflow_steps", []))

        # 3. Duplicate Detection Node (M3.2)
        dup_res = await duplicate_agent_node(state)
        state["duplicate_info"] = dup_res.get("duplicate_info", {})
        state["retrieved_docs"] = dup_res.get("retrieved_docs", [])
        state["workflow_steps"].extend(dup_res.get("workflow_steps", []))

        # 4. Root Cause Node (M3.1)
        rc_res = await root_cause_agent_node(state)
        state["root_cause_info"] = rc_res.get("root_cause_info", {})
        state["workflow_steps"].extend(rc_res.get("workflow_steps", []))

        # 5. Remediation Node (M3.3)
        rem_res = await remediation_agent_node(state)
        state["remediation_info"] = rem_res.get("remediation_info", {})
        state["workflow_steps"].extend(rem_res.get("workflow_steps", []))

        # Extract predictions
        dup_info = state["duplicate_info"]
        rc_info = state["root_cause_info"]
        rem_info = state["remediation_info"]

        pred_dup_status = dup_info.get("duplicate_status")
        pred_dup_id = dup_info.get("duplicate_bug_id")
        highest_score = dup_info.get("highest_similarity_score", 0.0)

        pred_hypo = rc_info.get("primary_hypothesis", "")
        pred_mech = rc_info.get("primary_failure_mechanism", "")
        pred_rc_status = rc_info.get("evidence_status", "")
        rc_conf = rc_info.get("confidence_score", 0.0)

        pred_patch = rem_info.get("suggested_patch_diff", "")
        pred_fixes = rem_info.get("recommended_fixes", [])
        pred_grounding = pred_fixes[0].get("grounding_type") if pred_fixes else ""
        pred_speculative = rem_info.get("is_speculative", False)
        tech_rec = rem_info.get("technical_recommendations") or {}
        pred_target = tech_rec.get("target_module", "")

        # Evaluation against Ground Truth
        exp_dup_status = tc["expected_duplicate_status"]
        exp_dup_id = tc.get("expected_duplicate_bug_id")
        exp_rc_status = tc.get("expected_evidence_status")
        exp_grounding = tc.get("expected_grounding_type")
        exp_speculative = tc.get("expected_is_speculative", False)
        exp_target_module = tc.get("expected_target_module")
        exp_keywords = tc.get("expected_failure_mechanism_keywords", [])

        # Match flags
        m_dup_status = pred_dup_status == exp_dup_status
        if m_dup_status:
            dup_status_correct += 1

        if exp_dup_id:
            dup_eval_total += 1
            if pred_dup_id == exp_dup_id:
                dup_id_correct += 1

        m_rc_status = (pred_rc_status == exp_rc_status) if exp_rc_status else True
        if m_rc_status:
            rc_evidence_status_correct += 1

        # Check if root cause mechanism or hypothesis matches keywords
        text_corpus = f"{pred_hypo} {pred_mech}".lower()
        m_rc_hypo = any(kw.lower() in text_corpus for kw in exp_keywords) if exp_keywords else (len(pred_hypo) > 20)
        if m_rc_hypo:
            rc_hypothesis_correct += 1

        # Confidence validity
        if exp_speculative:
            m_conf = rc_conf <= 0.60
        else:
            m_conf = rc_conf >= 0.70
        if m_conf:
            rc_confidence_valid += 1

        # Remediation matches
        m_patch = ("--- a/" in pred_patch and "+++ b/" in pred_patch)
        if m_patch:
            rem_patch_valid += 1

        m_grounding = (pred_grounding == exp_grounding) if exp_grounding else True
        if m_grounding:
            rem_grounding_correct += 1

        m_speculative = (pred_speculative == exp_speculative)
        if m_speculative:
            rem_speculative_correct += 1

        m_target = (exp_target_module.lower() in pred_target.lower()) if exp_target_module else True
        if m_target:
            rem_target_module_correct += 1

        overall_case_pass = m_dup_status and m_rc_hypo and m_patch and m_speculative

        results_table.append({
            "id": tc_id,
            "category": category,
            "status": "✓ PASS" if overall_case_pass else "✗ REVIEW",
            "dup_status": f"{pred_dup_status} ({int(highest_score*100)}%)",
            "rc_mech": pred_mech[:26] + ".." if len(pred_mech) > 26 else pred_mech,
            "grounding": pred_grounding,
            "conf": f"RC:{int(rc_conf*100)}%"
        })

    # Results table display
    print(f"\n{'ID':<9} | {'Category':<16} | {'Status':<9} | {'Duplicate Status (Score)':<26} | {'Failure Mechanism':<28} | {'Grounding':<22}")
    print("-" * 115)
    for r in results_table:
        print(f"{r['id']:<9} | {r['category']:<16} | {r['status']:<9} | {r['dup_status']:<26} | {r['rc_mech']:<28} | {r['grounding']:<22}")

    # Accuracy Metrics
    acc_dup_status = (dup_status_correct / total_cases) * 100
    acc_dup_id = (dup_id_correct / dup_eval_total) * 100 if dup_eval_total else 100.0
    acc_rc_hypo = (rc_hypothesis_correct / total_cases) * 100
    acc_rc_status = (rc_evidence_status_correct / total_cases) * 100
    acc_patch = (rem_patch_valid / total_cases) * 100
    acc_grounding = (rem_grounding_correct / total_cases) * 100
    acc_speculative = (rem_speculative_correct / total_cases) * 100
    acc_target = (rem_target_module_correct / total_cases) * 100

    overall_m3_score = (acc_dup_status + acc_dup_id + acc_rc_hypo + acc_patch + acc_grounding + acc_speculative) / 6.0

    print("\n" + "=" * 105)
    print("                            MILESTONE 3 BENCHMARK ACCURACY REPORT")
    print("=" * 105)
    print(f" Total Benchmark Evaluation Cases            : {total_cases}")
    print(f" M3.1 Root Cause Hypothesis Accuracy         : {acc_rc_hypo:6.2f}% ({rc_hypothesis_correct}/{total_cases})")
    print(f" M3.1 Root Cause Evidence Status Precision   : {acc_rc_status:6.2f}% ({rc_evidence_status_correct}/{total_cases})")
    print(f" M3.2 Duplicate Status Classification        : {acc_dup_status:6.2f}% ({dup_status_correct}/{total_cases})")
    print(f" M3.2 Duplicate Ticket Identification        : {acc_dup_id:6.2f}% ({dup_id_correct}/{dup_eval_total})")
    print(f" M3.3 Remediation Unified Diff Validity      : {acc_patch:6.2f}% ({rem_patch_valid}/{total_cases})")
    print(f" M3.3 Remediation Grounding Attribution      : {acc_grounding:6.2f}% ({rem_grounding_correct}/{total_cases})")
    print(f" M3.3 Speculative Guard Protection           : {acc_speculative:6.2f}% ({rem_speculative_correct}/{total_cases})")
    print(f" M3.3 Target Module Localization             : {acc_target:6.2f}% ({rem_target_module_correct}/{total_cases})")
    print("-" * 105)
    print(f" OVERALL MILESTONE 3 ACCURACY SCORE          : {overall_m3_score:6.2f}%")
    print("=" * 105)

    if overall_m3_score >= 85.0:
        print(" SUCCESS: Milestone 3 Agent Engine meets all accuracy & performance requirements! (Score >= 85%)")
    else:
        print(" WARNING: Overall Milestone 3 accuracy below 85% target threshold.")
    print("=" * 105 + "\n")

    return overall_m3_score


if __name__ == "__main__":
    asyncio.run(run_m3_accuracy_validation())
