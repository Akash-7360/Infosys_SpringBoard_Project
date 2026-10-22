import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
from app.agents.state import DefectAnalysisState
from app.core.config import settings


async def triage_agent_node(state: DefectAnalysisState) -> Dict[str, Any]:
    """
    Triage Agent Node:
    Assesses submitted defect to determine Severity (Critical, High, Medium, Low),
    Priority (P1, P2, P3, P4), Component classification, Confidence score, and Reasoning.
    """
    title = state.get("raw_title", "")
    desc = state.get("raw_description", "")
    parsed_log = state.get("parsed_log", {})
    exc_type = parsed_log.get("exception_type", "Unknown")
    exc_msg = parsed_log.get("exception_message", "")
    
    component = state.get("component") or "General"
    text_corpus = f"{title} {desc} {exc_type} {exc_msg}".lower()

    severity = "High"
    priority = "P2"
    confidence_score = 0.85
    reasoning = ""

    # Smart Rule Engine Evaluation
    exc_lower = exc_type.lower()
    
    # 1. Exception Type Precedence
    if any(k in exc_lower for k in [
        "outofmemory", "sigsegv", "panic", "access_violation", "typesystem", 
        "recursionerror", "memoryerror", "segmentation"
    ]) or any(k in text_corpus for k in ["deadlock", "use-after-free", "out of memory", "heap space"]):
        severity = "Critical"
        priority = "P1"
        confidence_score = 0.95
        reasoning = "Critical system impact: Application crash, OOM, SIGSEGV, memory violation, or compiler deadlock detected."
    elif any(k in exc_lower for k in [
        "nullpointer", "connectionrefused", "corruptsstable", "sec_error", 
        "bundleexception", "swterror", "typeerror", "referenceerror", 
        "jwtverificationexception", "jwt"
    ]) or any(k in text_corpus for k in ["nullpointer", "connectionrefused", "jwt", "unhandled exception"]):
        severity = "High"
        priority = "P2"
        confidence_score = 0.90
        reasoning = "High severity failure: Subsystem component exception impacting functional operational workflow."
    elif any(k in text_corpus for k in ["typo", "cosmetic", "doc", "comment", "style"]):
        severity = "Low"
        priority = "P4"
        confidence_score = 0.80
        reasoning = "Low impact: Minor cosmetic update or documentation suggestion."
    elif any(k in text_corpus for k in ["slow", "degraded", "warning", "retry", "latency", "delay", "high cpu"]):
        severity = "Medium"
        priority = "P3"
        confidence_score = 0.82
        reasoning = "Medium impact: Performance degradation, high query latency, or non-fatal retry behavior."
    else:
        severity = "High"
        priority = "P2"
        confidence_score = 0.85
        reasoning = "Standard functional defect requiring triage assessment and engineering fix."


    # Refine Component if unspecified or generic
    if component in ["General", "Core", "Mozilla/Apache/Eclipse", ""] or not component:
        if any(k in text_corpus for k in ["kafka", "queue", "broker", "topic", "partition", "messaging", "recordaccumulator"]):
            component = "Messaging/Queue"
        elif any(k in text_corpus for k in ["sql", "db", "query", "database", "postgres", "sqlite", "cassandra", "sstable", "elastic", "hashedrelation"]):
            component = "Database/Storage"
        elif any(k in text_corpus for k in ["http", "network", "connect", "rest", "api", "tls", "ssl", "proxy", "grpc", "socket"]):
            component = "Networking"
        elif any(k in text_corpus for k in ["auth", "token", "jwt", "permission", "secitem", "pkcs", "nss", "security"]):
            component = "Security/Auth"
        elif any(k in text_corpus for k in ["ui", "layout", "render", "css", "dom", "gtk", "widget", "docshell", "swt", "header", "grid", "frontend"]):
            component = "Frontend/UI"
        else:
            component = "Core"


    # Optional LLM refinement if OpenAI API Key is configured
    if settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate
            llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            prompt = PromptTemplate.from_template(
                "You are an expert bug triage engineer.\n"
                "Title: {title}\nDescription: {desc}\nException: {exc_type}\nMessage: {exc_msg}\n"
                "Return JSON with exact keys: severity (Critical/High/Medium/Low), priority (P1/P2/P3/P4), component, confidence_score (0.0 to 1.0), reasoning."
            )
            chain = prompt | llm
            res = chain.invoke({"title": title, "desc": desc, "exc_type": exc_type, "exc_msg": exc_msg})
            data = json.loads(res.content)
            severity = data.get("severity", severity)
            priority = data.get("priority", priority)
            component = data.get("component", component)
            confidence_score = float(data.get("confidence_score", confidence_score))
            reasoning = data.get("reasoning", reasoning)
        except Exception:
            pass # Fall back to rule engine result

    triage_output = {
        "severity": severity,
        "priority": priority,
        "component": component,
        "confidence_score": round(confidence_score, 2),
        "triage_reasoning": reasoning
    }

    step_log = {
        "agent": "TriageAgent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": (
            f"Triaged defect: Severity = {severity}, Priority = {priority}, "
            f"Component = {component}, Confidence = {int(confidence_score * 100)}%."
        )
    }

    steps = list(state.get("workflow_steps", []))
    steps.append(step_log)

    return {
        "triage_info": triage_output,
        "component": component,
        "workflow_steps": steps
    }

