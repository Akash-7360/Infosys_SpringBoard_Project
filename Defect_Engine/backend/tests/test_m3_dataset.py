"""
Milestone 3 Benchmark Test Dataset for Defect Engine Evaluation.
Contains 15 diverse test cases covering:
- Known duplicates of historical defects (Kafka, Spark, HTTPD, Cassandra, Gecko, JDT, SWT)
- Known related issues (subsystem related but differing root triggers)
- Known new / unmatched defect reports
- Insufficient evidence edge cases
"""

M3_BENCHMARK_DATASET = [
    # -------------------------------------------------------------
    # 1. Known Duplicates (Expect: duplicate_status="Duplicate", score >= 0.82)
    # -------------------------------------------------------------
    {
        "id": "M3-TC-01",
        "category": "Duplicate",
        "title": "Kafka Producer crash: NullPointerException in RecordAccumulator drain during high memory batch flush",
        "description": "Under high producer load with low memory buffer, the batch flush loop crashes referencing recycled TopicPartition batch.",
        "stack_trace": (
            "java.lang.NullPointerException: Cannot invoke 'ProducerBatch.drain()' because 'batch' is null\n"
            "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)\n"
            "\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)"
        ),
        "repository": "Apache",
        "component": "Messaging/Queue",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "APACHE-KAFKA-10294",
        "expected_failure_mechanism_keywords": ["null pointer", "de-allocation", "race condition"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "RecordAccumulator.java",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-02",
        "category": "Duplicate",
        "title": "Spark executor OutOfMemoryError in TaskMemoryManager during shuffle hash join spilled partition read",
        "description": "Executor crashes with OOM when processing skewed join keys. Memory manager fails to spill in-memory hash maps.",
        "stack_trace": (
            "java.lang.OutOfMemoryError: Java heap space\n"
            "\tat org.apache.spark.memory.TaskMemoryManager.allocatePage(TaskMemoryManager.java:298)\n"
            "\tat org.apache.spark.sql.execution.joins.HashedRelation$.apply(HashedRelation.scala:124)"
        ),
        "repository": "Apache",
        "component": "Core",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "APACHE-SPARK-34812",
        "expected_failure_mechanism_keywords": ["heap space", "exhaustion", "spill"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "TaskMemoryManager.java",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-03",
        "category": "Duplicate",
        "title": "Apache HTTPD worker segmentation fault in mod_proxy_http during SSL renegotiation",
        "description": "Child worker process segmentation fault when client triggers SSL renegotiation over HTTP/1.1 persistent connection.",
        "stack_trace": (
            "Program received signal SIGSEGV, Segmentation fault.\n"
            "0x00007ffff7bd21a4 in ap_proxy_http_process_response (r=0x7fffd0012890) at mod_proxy_http.c:1842\n"
            "Frame #0: 0x00007ffff7bd21a4 in ap_proxy_http_process_response at mod_proxy_http.c:1842"
        ),
        "repository": "Apache",
        "component": "Networking",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "APACHE-HTTPD-59310",
        "expected_failure_mechanism_keywords": ["dangling pointer", "sigsegv", "memory safety"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "mod_proxy_http.c",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-04",
        "category": "Duplicate",
        "title": "Cassandra CorruptSSTableException during compaction of compressed SSTable with checksum mismatch",
        "description": "Compaction execution thread fails abruptly on node restart when reading compressed chunk header checksums.",
        "stack_trace": (
            "org.apache.cassandra.io.sstable.CorruptSSTableException: Corrupted SSTable /var/lib/cassandra/data/keyspace/table/me-102-big-Data.db\n"
            "\tat org.apache.cassandra.io.compress.CompressedSequentialWriter.writeChunk(CompressedSequentialWriter.java:182)\n"
            "\tat org.apache.cassandra.db.compaction.CompactionTask.executeInternal(CompactionTask.java:194)"
        ),
        "repository": "Apache",
        "component": "Database/Storage",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "APACHE-CASSANDRA-17210",
        "expected_failure_mechanism_keywords": ["buffer truncation", "checksum", "unflushed"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "CompressedSequentialWriter.java",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-05",
        "category": "Duplicate",
        "title": "Firefox use-after-free crash in nsDocShell::Destroy when closing subframe tabs quickly",
        "description": "Browser crashes when closing tabs containing iframe trees quickly due to document shell lifecycle destruction race.",
        "stack_trace": (
            "CRASH INFO: Crash Type: EXCEPTION_ACCESS_VIOLATION_READ (Use-After-Free)\n"
            "\tat nsDocShell::Destroy() (docshell/base/nsDocShell.cpp:4812)\n"
            "\tat nsDocShell::DestroyChildren() (docshell/base/nsDocShell.cpp:4850)"
        ),
        "repository": "Mozilla",
        "component": "Frontend/UI",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "MOZILLA-GECKO-1589410",
        "expected_failure_mechanism_keywords": ["use-after-free", "dangling pointer", "access_violation"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "nsDocShell.cpp",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-06",
        "category": "Duplicate",
        "title": "Compiler Deadlock in TypeSystem.resolveType during Java sealed class hierarchy check",
        "description": "Eclipse Java Compiler hangs indefinitely when resolving circular permitted subtype declarations across multiple source files.",
        "stack_trace": (
            "java.lang.Thread$State: BLOCKED (on object monitor org.eclipse.jdt.internal.compiler.lookup.TypeSystem)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.TypeSystem.resolveType(TypeSystem.java:412)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.SourceTypeBinding.permittedTypes(SourceTypeBinding.java:891)"
        ),
        "repository": "Eclipse",
        "component": "Core",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "ECLIPSE-JDT-512903",
        "expected_failure_mechanism_keywords": ["deadlock", "lock ordering", "concurrent"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "TypeSystem.java",
        "expected_evidence_status": "Direct Match Evidence"
    },
    {
        "id": "M3-TC-07",
        "category": "Duplicate",
        "title": "SWTError: No more handles gtk_widget_get_window failed on Linux Wayland desktop layout",
        "description": "Eclipse IDE workspace window crashes after opening 50+ code editors under GTK3/Wayland environment.",
        "stack_trace": (
            "org.eclipse.swt.SWTError: No more handles\n"
            "\tat org.eclipse.swt.SWT.error(SWT.java:4604)\n"
            "\tat org.eclipse.swt.widgets.Control.internal_new_GC(Control.java:2140)"
        ),
        "repository": "Eclipse",
        "component": "Frontend/UI",
        "expected_duplicate_status": "Duplicate",
        "expected_duplicate_bug_id": "ECLIPSE-SWT-567112",
        "expected_failure_mechanism_keywords": ["handle leak", "cairo", "resource leak"],
        "expected_grounding_type": "Historical Defect Evidence",
        "expected_target_module": "Control.java",
        "expected_evidence_status": "Direct Match Evidence"
    },

    # -------------------------------------------------------------
    # 2. Known Related Issues (Expect: duplicate_status="Related Issue", 0.65 <= score < 0.82)
    # -------------------------------------------------------------
    {
        "id": "M3-TC-08",
        "category": "Related",
        "title": "Kafka Consumer timeout waiting for partition rebalance sync barrier",
        "description": "Consumer group coordinator times out when joining group during dynamic topic partition re-assignment.",
        "stack_trace": (
            "org.apache.kafka.common.errors.TimeoutException: Timeout of 60000ms expired before partition assignment\n"
            "\tat org.apache.kafka.clients.consumer.internals.ConsumerCoordinator.poll(ConsumerCoordinator.java:512)"
        ),
        "repository": "Apache",
        "component": "Messaging/Queue",
        "expected_duplicate_status": "Related Issue",
        "expected_failure_mechanism_keywords": ["socket", "timeout", "connection", "exception"],
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "ConsumerCoordinator.java",
        "expected_evidence_status": "Sufficient Evidence"
    },
    {
        "id": "M3-TC-09",
        "category": "Related",
        "title": "Cassandra read timeout during secondary index query on large partition",
        "description": "Read timeout 5000ms occurred while executing secondary index query across multiple replica nodes.",
        "stack_trace": (
            "org.apache.cassandra.exceptions.ReadTimeoutException: Operation timed out - received only 1 responses\n"
            "\tat org.apache.cassandra.service.AbstractReadExecutor.maybeTryAdditionalReplicas(AbstractReadExecutor.java:188)"
        ),
        "repository": "Apache",
        "component": "Database/Storage",
        "expected_duplicate_status": "Related Issue",
        "expected_failure_mechanism_keywords": ["timeout", "socket", "exception"],
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "AbstractReadExecutor.java",
        "expected_evidence_status": "Sufficient Evidence"
    },
    {
        "id": "M3-TC-10",
        "category": "Related",
        "title": "Firefox WebGL canvas crash on subframe destruction",
        "description": "WebGL context lost when rapidly closing tabs containing 3D canvas animations.",
        "stack_trace": (
            "mozilla::gl::GLContext::Destroy()\n"
            "\tat mozilla::dom::HTMLCanvasElement::GetContext(HTMLCanvasElement.cpp:892)"
        ),
        "repository": "Mozilla",
        "component": "Frontend/UI",
        "expected_duplicate_status": "Related Issue",
        "expected_failure_mechanism_keywords": ["dangling pointer", "use-after-free", "exception"],
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "HTMLCanvasElement.cpp",
        "expected_evidence_status": "Sufficient Evidence"
    },

    # -------------------------------------------------------------
    # 3. Known New / Unmatched Defect Reports (Expect: duplicate_status="New / Unmatched Issue", score < 0.65)
    # -------------------------------------------------------------
    {
        "id": "M3-TC-11",
        "category": "Unmatched",
        "title": "Python Microservice JWT signature verification fails on expired public key cache",
        "description": "FastAPI gateway rejects valid incoming Bearer tokens with JWTVerificationException when background key rotator runs.",
        "stack_trace": (
            'Traceback (most recent call last):\n'
            '  File "app/services/jwt_validator.py", line 114, in verify_token\n'
            '    decoded = jwt.decode(token, key, algorithms=["RS256"])\n'
            'JWTVerificationException: Signature verification failed'
        ),
        "repository": "General",
        "component": "Security/Auth",
        "expected_duplicate_status": "New / Unmatched Issue",
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "jwt_validator.py",
        "expected_evidence_status": "Sufficient Evidence"
    },
    {
        "id": "M3-TC-12",
        "category": "Unmatched",
        "title": "Golang grpc microservice panic in payment transaction ledger commit",
        "description": "Payment worker panics with runtime error when processing negative currency transfer amounts.",
        "stack_trace": (
            "panic: runtime error: index out of range [3] with length 2\n"
            "goroutine 88 [running]:\n"
            "services/ledger.CommitTransaction(0x140001a, 0x0)\n"
            "\t/app/services/ledger/processor.go:78 +0x140"
        ),
        "repository": "General",
        "component": "Core",
        "expected_duplicate_status": "New / Unmatched Issue",
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "processor.go",
        "expected_evidence_status": "Sufficient Evidence"
    },
    {
        "id": "M3-TC-13",
        "category": "Unmatched",
        "title": "Frontend React component renders NaN in dashboard summary analytics card",
        "description": "User profile dashboard displays NaN instead of user total account balance when balance is null.",
        "stack_trace": (
            "TypeError: Cannot read properties of undefined (reading 'amount')\n"
            "    at UserBalanceWidget (UserBalanceWidget.tsx:45:18)\n"
            "    at renderWithHooks (react-dom.production.min.js:14938)"
        ),
        "repository": "General",
        "component": "Frontend/UI",
        "expected_duplicate_status": "New / Unmatched Issue",
        "expected_grounding_type": "Best Practice Guideline",
        "expected_target_module": "UserBalanceWidget.tsx",
        "expected_evidence_status": "Sufficient Evidence"
    },

    # -------------------------------------------------------------
    # 4. Insufficient Evidence / Edge Cases
    # -------------------------------------------------------------
    {
        "id": "M3-TC-14",
        "category": "InsufficientEvidence",
        "title": "Application behaves unexpectedly during night batch",
        "description": "Something stopped working around 3 AM. No stack trace available in log directory.",
        "stack_trace": "",
        "repository": "General",
        "component": "General",
        "expected_duplicate_status": "New / Unmatched Issue",
        "expected_evidence_status": "Insufficient Evidence",
        "expected_is_speculative": True,
        "expected_grounding_type": "Agent Heuristic"
    },
    {
        "id": "M3-TC-15",
        "category": "InsufficientEvidence",
        "title": "Service restart notice in syslog",
        "description": "Syslog recorded a daemon stop signal. No errors thrown.",
        "stack_trace": "info: systemd[1]: Stopping Application Daemon...",
        "repository": "General",
        "component": "General",
        "expected_duplicate_status": "New / Unmatched Issue",
        "expected_evidence_status": "Insufficient Evidence",
        "expected_is_speculative": True,
        "expected_grounding_type": "Agent Heuristic"
    }
]
