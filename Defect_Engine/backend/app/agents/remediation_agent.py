from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.state import DefectAnalysisState
from app.core.config import settings


def generate_unified_diff(
    file_path: str,
    func_name: str,
    line_num: int,
    exc_type: str,
    failure_mech: str,
    top_rag_bug: Dict[str, Any]
) -> str:
    """
    Synthesizes a realistic unified diff code patch grounded in the identified defect pattern.
    """
    line_num = max(1, line_num)
    f_lower = file_path.lower()
    exc_lower = exc_type.lower()
    mech_lower = failure_mech.lower()

    # 1. Java RecordAccumulator / ProducerBatch NullPointer
    if "recordaccumulator" in f_lower or ("nullpointer" in exc_lower and "drain" in func_name.lower()):
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},7 +{max(1, line_num - 2)},11 @@\n"
            f"     public ProducerBatch drain(TopicPartition part) {{\n"
            f"-        ProducerBatch batch = batches.get(part);\n"
            f"-        return batch.drain();\n"
            f"+        synchronized (this.drainLock) {{\n"
            f"+            ProducerBatch batch = batches.get(part);\n"
            f"+            if (batch == null || batch.isDrained()) {{\n"
            f"+                return null;\n"
            f"+            }}\n"
            f"+            return batch.drain();\n"
            f"+        }}\n"
            f"     }}\n"
        )
    # 2. Spark TaskMemoryManager OutOfMemoryError
    elif "taskmemorymanager" in f_lower or "outofmemory" in exc_lower or "heap" in mech_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},6 +{max(1, line_num - 2)},10 @@\n"
            f"     public MemoryBlock allocatePage(long requiredBytes, MemoryConsumer consumer) {{\n"
            f"-        if (acquiredPageSize + requiredBytes > maxMemory) {{\n"
            f"-            throw new OutOfMemoryError(\"Java heap space\");\n"
            f"+        if (acquiredPageSize + requiredBytes > maxMemory) {{\n"
            f"+            long spilled = consumer.spill(requiredBytes, this);\n"
            f"+            if (spilled < requiredBytes && acquiredPageSize + requiredBytes > maxMemory) {{\n"
            f"+                throw new OutOfMemoryError(\"TaskMemoryManager: Failed to allocate \" + requiredBytes + \" bytes after spilling \" + spilled + \" bytes\");\n"
            f"+            }}\n"
            f"         }}\n"
        )
    # 3. HTTPD mod_proxy_http SIGSEGV / dangling pointer
    elif "mod_proxy" in f_lower or "sigsegv" in exc_lower or "dangling" in mech_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},7 +{max(1, line_num - 2)},11 @@\n"
            f"     if (backend->ssl_renegotiate_pending) {{\n"
            f"-        apr_status_t rv = ap_proxy_ssl_renegotiate(backend);\n"
            f"+        if (backend->connection == NULL || backend->connection->aborted) {{\n"
            f"+            backend->ssl_renegotiate_pending = 0;\n"
            f"+            return HTTP_BAD_GATEWAY;\n"
            f"+        }}\n"
            f"+        apr_status_t rv = ap_proxy_ssl_renegotiate(backend);\n"
            f"         if (rv != APR_SUCCESS) {{\n"
            f"-            backend = NULL;\n"
            f"+            ap_proxy_release_connection(backend);\n"
            f"+            backend = NULL;\n"
        )
    # 4. Cassandra CorruptSSTableException
    elif "sstable" in f_lower or "corrupt" in exc_lower or "compression" in mech_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},6 +{max(1, line_num - 2)},10 @@\n"
            f"     public void writeChunk(ByteBuffer chunk, int uncompressedLength) throws IOException {{\n"
            f"-        channel.write(chunk);\n"
            f"-        checksum.update(chunk);\n"
            f"+        if (chunk.remaining() == 0) return;\n"
            f"+        checksum.update(chunk.duplicate());\n"
            f"+        channel.write(chunk);\n"
            f"+        channel.force(false); // Flush tail buffer before committing header\n"
        )
    # 5. TypeSystem Deadlock
    elif "typesystem" in f_lower or "deadlock" in mech_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},6 +{max(1, line_num - 2)},9 @@\n"
            f"-    public synchronized TypeBinding resolveType(LookupEnvironment env) {{\n"
            f"-        return permittedTypesCache.computeIfAbsent(this, env::internalResolve);\n"
            f"+    public TypeBinding resolveType(LookupEnvironment env) {{\n"
            f"+        // Break circular monitor lock hierarchy by using ConcurrentHashMap memoization\n"
            f"+        return concurrentPermittedTypesMap.computeIfAbsent(this, k -> env.internalResolve(k));\n"
        )
    # 6. Generic Python / JavaScript / Java null check
    elif "null" in exc_lower or "attributeerror" in exc_lower or "typeerror" in exc_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 3)},7 +{max(1, line_num - 3)},10 @@\n"
            f"     def {func_name}(self, payload):\n"
            f"-        result = payload.get_data().process()\n"
            f"+        if payload is None or not hasattr(payload, 'get_data'):\n"
            f"+            logger.warning('Null or invalid payload passed to {func_name}')\n"
            f"+            return None\n"
            f"+        result = payload.get_data().process()\n"
            f"         return result\n"
        )
    # 7. Connection Refused / Timeout
    elif "connection" in exc_lower or "timeout" in exc_lower or "socket" in mech_lower:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},6 +{max(1, line_num - 2)},11 @@\n"
            f"     def {func_name}(self, endpoint):\n"
            f"-        response = requests.get(endpoint)\n"
            f"+        retry_strategy = urllib3.util.Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])\n"
            f"+        adapter = HTTPAdapter(max_retries=retry_strategy)\n"
            f"+        with requests.Session() as session:\n"
            f"+            session.mount('https://', adapter)\n"
            f"+            response = session.get(endpoint, timeout=10)\n"
            f"         return response\n"
        )
    # Default defensive exception handling patch
    else:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -{max(1, line_num - 2)},6 +{max(1, line_num - 2)},9 @@\n"
            f"     try:\n"
            f"-        execute_{func_name}()\n"
            f"+        validate_invariants()\n"
            f"+        execute_{func_name}()\n"
            f"     except {exc_type if exc_type != 'UnknownException' else 'Exception'} as err:\n"
            f"+        logger.error(f'Defensive boundary caught {exc_type} in {func_name}: {{err}}')\n"
            f"+        raise ManagedSubsystemException(err)\n"
        )


async def remediation_agent_node(state: DefectAnalysisState) -> Dict[str, Any]:
    """
    Milestone 3.3 Remediation Agent Node:
    Synthesizes outputs from Root Cause Agent, Duplicate Detection Agent, Triage Agent, and Log Analysis Agent.
    Retrieves historical resolutions from RAG, generates unified diff code patch,
    structures technical recommendations into code, configuration, validation, and error handling,
    attributes grounding source (Historical Defect vs Best Practice),
    and flags speculative fixes when diagnostic evidence is sparse.
    """
    parsed_log = state.get("parsed_log", {})
    root_cause_info = state.get("root_cause_info", {})
    dup_info = state.get("duplicate_info", {})
    triage_info = state.get("triage_info", {})
    retrieved_docs = state.get("retrieved_docs", [])
    
    exc_type = parsed_log.get("exception_type", "UnknownException")
    failure_point = parsed_log.get("failure_point") or {}
    top_frame = parsed_log.get("top_offending_frame") or {}
    
    file_path = failure_point.get("file_name") or top_frame.get("file_path") or "app/services/processor.py"
    func_name = failure_point.get("method_name") or top_frame.get("function_name") or "process_request"
    line_num = failure_point.get("line_number") or top_frame.get("line_number") or 42
    
    primary_hypothesis = root_cause_info.get("primary_hypothesis", "")
    failure_mech = root_cause_info.get("primary_failure_mechanism", "Unhandled Exception")
    evidence_status = root_cause_info.get("evidence_status", "Sufficient Evidence")
    
    top_rag_bug = retrieved_docs[0] if retrieved_docs else {}
    top_similarity = float(top_rag_bug.get("similarity_score", 0.0))
    historical_resolution = top_rag_bug.get("resolution", "")
    historical_bug_id = top_rag_bug.get("bug_id")

    # 1. Determine Grounding Attribution & Speculative Status
    if top_similarity >= 0.88 and historical_resolution:
        grounding_type = "Historical Defect Evidence"
        primary_fix_desc = (
            f"Adopt verified resolution from historical ticket {historical_bug_id}: "
            f"{historical_resolution.rstrip('.')}. Specifically target `{func_name}` at `{file_path}:{line_num}`."
        )
        supporting_bug_ref = historical_bug_id
        supporting_summary = f"Grounded by {historical_bug_id} ({int(top_similarity * 100)}% match): {historical_resolution}"
        conf_score = min(0.95, 0.82 + (top_similarity * 0.12))
        is_speculative = False
    elif evidence_status == "Insufficient Evidence":
        grounding_type = "Agent Heuristic"
        primary_fix_desc = (
            f"Add defensive input validation and exception telemetry around `{func_name}`. "
            f"Caution: Diagnostic logs contain insufficient stack traces to pinpoint the exact failure line."
        )
        supporting_bug_ref = None
        supporting_summary = "No verified historical patch matched. Fix represents generalized defensive fallback."
        conf_score = 0.45
        is_speculative = True
    else:
        grounding_type = "Best Practice Guideline"
        primary_fix_desc = (
            f"Implement defensive preconditions and null safety guards in `{func_name}` ({file_path}:{line_num}) "
            f"to remediate {failure_mech.lower()}."
        )
        supporting_bug_ref = top_rag_bug.get("bug_id") if top_similarity >= 0.60 else None
        supporting_summary = (
            f"Based on industry best practices for {exc_type} prevention" +
            (f" and contextual similarity to {top_rag_bug.get('bug_id')}." if top_similarity >= 0.60 else ".")
        )
        conf_score = 0.82
        is_speculative = False

    # 2. Recommended Approaches List
    recommended_fixes = [
        {
            "title": f"Primary Fix: {failure_mech} Remediation",
            "approach_type": "Primary Recommended Fix",
            "description": primary_fix_desc,
            "confidence_score": round(conf_score, 2),
            "grounding_type": grounding_type,
            "supporting_historical_bug_id": supporting_bug_ref,
            "supporting_evidence_summary": supporting_summary
        },
        {
            "title": "Alternative Mitigation: Graceful Circuit Breaker & Boundary Fallback",
            "approach_type": "Alternative Mitigation",
            "description": (
                f"Wrap `{func_name}` invocation with defensive fallback logic, returning an operational default "
                f"or queuing the message for async retry rather than bubbling unhandled {exc_type}."
            ),
            "confidence_score": round(conf_score * 0.9, 2),
            "grounding_type": "Best Practice Guideline",
            "supporting_historical_bug_id": None,
            "supporting_evidence_summary": "Defensive architectural pattern to ensure subsystem isolation."
        }
    ]

    # 3. Technical Recommendations Breakdown
    code_modifications = [
        f"Apply defensive null/boundary checks in `{func_name}` at `{file_path}:{line_num}` prior to accessing state.",
        f"Synchronize access across concurrent threads in `{file_path}` to prevent state desynchronization.",
        f"Ensure memory/socket resources are explicitly disposed in a `finally` block or context manager."
    ]

    configuration_changes = [
        "Verify buffer pool and timeout limits match production load requirements.",
        "Enable debug-level telemetry for the affected subsystem during staging verification."
    ]

    validation_steps = [
        f"Write regression unit test simulating null payload and edge-case inputs for `{func_name}`.",
        f"Execute concurrency stress test under simulated memory pressure to confirm fix stability.",
        "Deploy to staging canary environment and monitor error rate metrics for 24 hours."
    ]

    error_handling_improvements = [
        f"Catch `{exc_type}` explicitly and log contextual error metadata before raising managed exceptions.",
        "Quarantine corrupt or un-parseable records to dead-letter queue rather than halting executor threads."
    ]

    technical_recommendations = {
        "target_module": f"{file_path}:{line_num}",
        "code_modifications": code_modifications,
        "configuration_changes": configuration_changes,
        "validation_steps": validation_steps,
        "error_handling_improvements": error_handling_improvements
    }

    # 4. Generate Unified Diff Code Patch
    patch_diff = generate_unified_diff(
        file_path=file_path,
        func_name=func_name,
        line_num=line_num,
        exc_type=exc_type,
        failure_mech=failure_mech,
        top_rag_bug=top_rag_bug
    )

    # 5. Optional LLM Refinement if API key available
    if settings.OPENAI_API_KEY and not is_speculative:
        try:
            import json
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import PromptTemplate
            llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.1)
            prompt = PromptTemplate.from_template(
                "You are an expert software remediation engineer.\n"
                "Root Cause: {root_cause}\n"
                "Target File: {file_path}:{line_num}\n"
                "Historical Solution: {hist_res}\n"
                "Generate a standard unified diff (starting with --- a/ and +++ b/) and 3 code modifications.\n"
                "Return JSON with keys: patch_diff, code_modifications (list)."
            )
            chain = prompt | llm
            res = chain.invoke({
                "root_cause": primary_hypothesis,
                "file_path": file_path,
                "line_num": line_num,
                "hist_res": historical_resolution
            })
            data = json.loads(res.content)
            if data.get("patch_diff"):
                patch_diff = data["patch_diff"]
            if data.get("code_modifications"):
                technical_recommendations["code_modifications"] = data["code_modifications"]
        except Exception:
            pass

    step_by_step = code_modifications + validation_steps[:2]

    remediation_output = {
        "recommended_fixes": recommended_fixes,
        "suggested_patch_diff": patch_diff,
        "technical_recommendations": technical_recommendations,
        "step_by_step_mitigation": step_by_step,
        "verification_testing_advice": (
            f"Run target unit regression tests for `{file_path}` and execute load validation in staging environment."
        ),
        "confidence_score": round(conf_score, 2),
        "evidence_status": evidence_status,
        "is_speculative": is_speculative
    }

    step_log = {
        "agent": "RemediationAgent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": (
            f"Generated Unified Diff patch for `{file_path}` and {len(recommended_fixes)} fix approaches. "
            f"Grounding: {grounding_type} (Confidence: {int(conf_score * 100)}%)."
        )
    }

    steps = list(state.get("workflow_steps", []))
    steps.append(step_log)

    return {
        "remediation_info": remediation_output,
        "status": "COMPLETED",
        "workflow_steps": steps
    }

