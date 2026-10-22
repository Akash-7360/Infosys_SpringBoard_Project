import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.agents.state import DefectAnalysisState
from app.agents.log_analysis_agent import log_analysis_agent_node
from app.agents.duplicate_agent import duplicate_agent_node
from app.agents.triage_agent import triage_agent_node
from app.agents.root_cause_agent import root_cause_agent_node
from app.agents.remediation_agent import remediation_agent_node

logger = logging.getLogger(__name__)


def create_defect_analysis_graph():
    """
    Constructs and compiles the LangGraph StateGraph for multi-agent defect analysis & triage.
    Pipeline: START -> log_analysis -> duplicate_detection -> triage -> root_cause -> remediation -> END
    """
    workflow = StateGraph(DefectAnalysisState)

    # Add 5 specialized agent nodes
    workflow.add_node("log_analysis", log_analysis_agent_node)
    workflow.add_node("duplicate_detection", duplicate_agent_node)
    workflow.add_node("triage", triage_agent_node)
    workflow.add_node("root_cause", root_cause_agent_node)
    workflow.add_node("remediation", remediation_agent_node)

    # Set flow edges
    workflow.add_edge(START, "log_analysis")
    workflow.add_edge("log_analysis", "triage")
    workflow.add_edge("triage", "duplicate_detection")
    workflow.add_edge("duplicate_detection", "root_cause")
    workflow.add_edge("root_cause", "remediation")
    workflow.add_edge("remediation", END)

    return workflow.compile()


# Orchestrator app instance
orchestrator_graph = create_defect_analysis_graph()


async def run_defect_analysis_pipeline(
    bug_id: str,
    title: str,
    description: str,
    stack_trace: str,
    raw_log_content: str,
    environment_details: str,
    repository: str = "General",
    component: str = "General"
) -> Dict[str, Any]:
    """
    Executes the multi-agent orchestration pipeline for a given bug submission.
    """
    initial_state: DefectAnalysisState = {
        "bug_id": bug_id,
        "raw_title": title,
        "raw_description": description or "",
        "raw_stack_trace": stack_trace or "",
        "raw_log_content": raw_log_content or "",
        "environment_details": environment_details or "",
        "repository": repository or "General",
        "component": component or "General",
        "parsed_log": {},
        "triage_info": {},
        "duplicate_info": {},
        "root_cause_info": {},
        "remediation_info": {},
        "retrieved_docs": [],
        "status": "PROCESSING",
        "workflow_steps": []
    }

    try:
        final_state = await orchestrator_graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        logger.error(f"Error executing multi-agent graph: {e}", exc_info=True)
        initial_state["status"] = "FAILED"
        initial_state["workflow_steps"].append({
            "agent": "Orchestrator",
            "summary": f"Pipeline execution error: {str(e)}"
        })
        return initial_state
