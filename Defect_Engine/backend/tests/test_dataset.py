"""
M2 Benchmark Test Dataset for Defect Triage & Log Analysis Accuracy Validation.
Includes 24 representative test cases covering diverse error types, stack trace formats,
input completeness, and severity/component classes.
"""

M2_VALIDATION_DATASET = [
    # 1. Java / Apache - Critical OOM
    {
        "id": "TC-01",
        "title": "OutOfMemoryError in TaskMemoryManager during shuffle join",
        "description": "Executor crashed with Java heap space error during large scale dataset shuffle join operation under skewed key distribution.",
        "stack_trace": (
            "java.lang.OutOfMemoryError: Java heap space\n"
            "\tat org.apache.spark.memory.TaskMemoryManager.allocatePage(TaskMemoryManager.java:298)\n"
            "\tat org.apache.spark.sql.execution.joins.HashedRelation$.apply(HashedRelation.scala:124)"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Core",
        "expected_exception": "OutOfMemoryError",
        "expected_file": "TaskMemoryManager.java",
        "expected_line": 298,
        "format": "Java"
    },
    # 2. Java / Apache - High NullPointer
    {
        "id": "TC-02",
        "title": "NullPointerException in RecordAccumulator drain loop",
        "description": "Kafka Producer crashed when draining records under heavy memory pressure batch flush.",
        "stack_trace": (
            "java.lang.NullPointerException: Cannot invoke ProducerBatch.drain() because batch is null\n"
            "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)\n"
            "\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Messaging/Queue",
        "expected_exception": "NullPointerException",
        "expected_file": "RecordAccumulator.java",
        "expected_line": 248,
        "format": "Java"
    },
    # 3. C++ / Apache - Critical SIGSEGV
    {
        "id": "TC-03",
        "title": "SIGSEGV crash in mod_proxy_http worker during TLS handshake",
        "description": "Segmentation fault in HTTPD worker when client triggers SSL renegotiation.",
        "stack_trace": (
            "Program received signal SIGSEGV, Segmentation fault.\n"
            "Frame #0: 0x00007ffff7bd21a4 in ap_proxy_http_process_response (r=0x7fffd0012890) at mod_proxy_http.c:1842\n"
            "Frame #1: 0x00007ffff7bca012 in proxy_http_handler at mod_proxy_http.c:2104"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Networking",
        "expected_exception": "SIGSEGV",
        "expected_file": "mod_proxy_http.c",
        "expected_line": 1842,
        "format": "C/C++"
    },
    # 4. Java / Eclipse - High CorruptSSTable
    {
        "id": "TC-04",
        "title": "CorruptSSTableException during Cassandra compaction",
        "description": "Compaction thread fails abruptly on node restart due to corrupted SSTable checksum.",
        "stack_trace": (
            "org.apache.cassandra.io.sstable.CorruptSSTableException: Corrupted SSTable /data/table/me-102-big-Data.db\n"
            "\tat org.apache.cassandra.io.compress.CompressedSequentialWriter.writeChunk(CompressedSequentialWriter.java:182)\n"
            "\tat org.apache.cassandra.db.compaction.CompactionTask.executeInternal(CompactionTask.java:194)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Database/Storage",
        "expected_exception": "CorruptSSTableException",
        "expected_file": "CompressedSequentialWriter.java",
        "expected_line": 182,
        "format": "Java"
    },
    # 5. C++ / Mozilla - Critical Use-After-Free
    {
        "id": "TC-05",
        "title": "Use-after-free in nsDocShell::Destroy when closing tabs",
        "description": "Firefox crashes when rapidly closing tabs containing iframe trees.",
        "stack_trace": (
            "CRASH INFO: EXCEPTION_ACCESS_VIOLATION_READ (Use-After-Free)\n"
            "\tat nsDocShell::Destroy() (docshell/base/nsDocShell.cpp:4812)\n"
            "\tat nsDocShell::DestroyChildren() (docshell/base/nsDocShell.cpp:4850)"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Frontend/UI",
        "expected_exception": "EXCEPTION_ACCESS_VIOLATION_READ",
        "expected_file": "nsDocShell.cpp",
        "expected_line": 4812,
        "format": "C/C++"
    },
    # 6. C++ / Mozilla - High Buffer Overflow
    {
        "id": "TC-06",
        "title": "Buffer overflow in NSS SECITEM_AllocItem during RSA verification",
        "description": "Security error when processing malformed ASN.1 signature structure.",
        "stack_trace": (
            "SEC_ERROR_INVALID_ARGS: security library invalid arguments\n"
            "\tat SECITEM_AllocItem_Util (security/nss/lib/util/secitem.c:115)\n"
            "\tat RSA_VerifyPKCS1FromDigest (security/nss/lib/freebl/rsa.c:482)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Security/Auth",
        "expected_exception": "SEC_ERROR_INVALID_ARGS",
        "expected_file": "secitem.c",
        "expected_line": 115,
        "format": "C/C++"
    },
    # 7. Java / Eclipse - Critical Deadlock
    {
        "id": "TC-07",
        "title": "Compiler Deadlock in TypeSystem.resolveType during sealed class check",
        "description": "Eclipse Java compiler hangs indefinitely due to circular permitted subtype lock contention.",
        "stack_trace": (
            "java.lang.Thread$State: BLOCKED (on object monitor org.eclipse.jdt.internal.compiler.lookup.TypeSystem)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.TypeSystem.resolveType(TypeSystem.java:412)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.SourceTypeBinding.permittedTypes(SourceTypeBinding.java:891)"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Core",
        "expected_exception": "TypeSystem",
        "expected_file": "TypeSystem.java",
        "expected_line": 412,
        "format": "Java"
    },
    # 8. Java / Eclipse - High BundleException
    {
        "id": "TC-08",
        "title": "BundleException in OSGi Framework Storage resolution",
        "description": "Equinox OSGi runtime throws BundleException when refreshing bundle dependency wiring.",
        "stack_trace": (
            "org.osgi.framework.BundleException: Could not resolve module: org.eclipse.core.resources [52]\n"
            "\tat org.eclipse.osgi.container.Module.start(Module.java:464)\n"
            "\tat org.eclipse.osgi.internal.framework.EquinoxBundle.start(EquinoxBundle.java:439)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Core",
        "expected_exception": "BundleException",
        "expected_file": "Module.java",
        "expected_line": 464,
        "format": "Java"
    },
    # 9. Java / Eclipse - Medium SWT Display Error
    {
        "id": "TC-09",
        "title": "SWTError: No more handles on GTK3 Wayland display",
        "description": "Eclipse UI displays warning/error after opening 50+ code editors due to handle leaks.",
        "stack_trace": (
            "org.eclipse.swt.SWTError: No more handles\n"
            "\tat org.eclipse.swt.SWT.error(SWT.java:4604)\n"
            "\tat org.eclipse.swt.widgets.Widget.error(Widget.java:482)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Frontend/UI",
        "expected_exception": "SWTError",
        "expected_file": "SWT.java",
        "expected_line": 4604,
        "format": "Java"
    },
    # 10. Python - High TypeError
    {
        "id": "TC-10",
        "title": "TypeError: unsupported operand type(s) for + in data pipeline",
        "description": "Backend async worker failed during metrics aggregation stage.",
        "stack_trace": (
            'Traceback (most recent call last):\n'
            '  File "app/services/metrics.py", line 87, in aggregate_scores\n'
            '    total += item["score"]\n'
            'TypeError: unsupported operand type(s) for +: "int" and "str"'
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Core",
        "expected_exception": "TypeError",
        "expected_file": "metrics.py",
        "expected_line": 87,
        "format": "Python"
    },
    # 11. JavaScript / Node.js - High ReferenceError
    {
        "id": "TC-11",
        "title": "Uncaught ReferenceError: window is not defined during SSR render",
        "description": "Next.js server side rendering failed when component accessed client object.",
        "stack_trace": (
            "ReferenceError: window is not defined\n"
            "    at HeaderNavigation (src/components/Header.js:34:12)\n"
            "    at renderElement (node_modules/react-dom/server.js:102:4)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Frontend/UI",
        "expected_exception": "ReferenceError",
        "expected_file": "Header.js",
        "expected_line": 34,
        "format": "JavaScript"
    },
    # 12. Go - Critical Panic
    {
        "id": "TC-12",
        "title": "panic: runtime error: invalid memory address or nil pointer dereference",
        "description": "Go microservice crashed during gRPC request handling loop.",
        "stack_trace": (
            "panic: runtime error: invalid memory address or nil pointer dereference\n"
            "main.HandleRequest(0x0, 0x0)\n"
            "\t/app/server/handler.go:142 +0x3b"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Networking",
        "expected_exception": "panic",
        "expected_file": "handler.go",
        "expected_line": 142,
        "format": "Go"
    },
    # 13. Edge Case: Description ONLY (No Stack Trace)
    {
        "id": "TC-13",
        "title": "Slow database query execution during peak user login hours",
        "description": "Users experience 5-10 second delays when authenticating during morning shift. Database connection pool connection queries warning.",
        "stack_trace": "",
        "expected_severity": "Medium",
        "expected_priority": "P3",
        "expected_component": "Database/Storage",
        "expected_exception": "ApplicationDefect",
        "expected_file": None,
        "expected_line": None,
        "format": "DescriptionOnly"
    },
    # 14. Edge Case: Log File ONLY (No Description)
    {
        "id": "TC-14",
        "title": "Raw log upload test case",
        "description": "",
        "stack_trace": (
            "2026-09-07 14:22:01 ERROR [thread-4] com.example.db.ConnectionPool - ConnectionRefusedException: Unable to acquire JDBC connection\n"
            "\tat com.example.db.ConnectionPool.getConnection(ConnectionPool.java:95)\n"
            "\tat com.example.service.UserService.findUser(UserService.java:42)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Database/Storage",
        "expected_exception": "ConnectionRefusedException",
        "expected_file": "ConnectionPool.java",
        "expected_line": 95,
        "format": "LogOnly"
    },
    # 15. Edge Case: Messy / Unstructured Logs
    {
        "id": "TC-15",
        "title": "Unstructured server crash log from syslog",
        "description": "Kernel out of memory killer killed backend python daemon process.",
        "stack_trace": (
            "[14002.41] kernel: Out of memory: Kill process 1892 (python3) score 850 or sacrifice child\n"
            "[14002.42] kernel: Killed process 1892 (python3) total-vm:4120892kB, anon-rss:3219000kB"
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Core",
        "expected_exception": "ApplicationDefect",
        "expected_file": None,
        "expected_line": None,
        "format": "UnstructuredLog"
    },
    # 16. Medium Severity - Performance Degradation
    {
        "id": "TC-16",
        "title": "High CPU utilization and slow search queries on Elastic cluster",
        "description": "Search latency increased to 1200ms under heavy warning load. Garbage collection retries observed.",
        "stack_trace": "",
        "expected_severity": "Medium",
        "expected_priority": "P3",
        "expected_component": "Database/Storage",
        "expected_exception": "ApplicationDefect",
        "expected_file": None,
        "expected_line": None,
        "format": "DescriptionOnly"
    },
    # 17. Low Severity - Cosmetic / Documentation Typo
    {
        "id": "TC-17",
        "title": "Typo in user settings documentation link",
        "description": "Settings footer link points to missing doc page. Cosmetic update required.",
        "stack_trace": "",
        "expected_severity": "Low",
        "expected_priority": "P4",
        "expected_component": "Frontend/UI",
        "expected_exception": "ApplicationDefect",
        "expected_file": None,
        "expected_line": None,
        "format": "DescriptionOnly"
    },
    # 18. Python - Critical RecursionError
    {
        "id": "TC-18",
        "title": "RecursionError: maximum recursion depth exceeded in graph traversal",
        "description": "Agent state graph entered infinite loop during cycle resolution.",
        "stack_trace": (
            'Traceback (most recent call last):\n'
            '  File "app/agents/graph.py", line 150, in resolve_cycle\n'
            '    return resolve_cycle(node.parent)\n'
            'RecursionError: maximum recursion depth exceeded'
        ),
        "expected_severity": "Critical",
        "expected_priority": "P1",
        "expected_component": "Core",
        "expected_exception": "RecursionError",
        "expected_file": "graph.py",
        "expected_line": 150,
        "format": "Python"
    },
    # 19. Java / Security - High Auth JWT Error
    {
        "id": "TC-19",
        "title": "JWTVerificationException in AuthFilter during token decode",
        "description": "User requests rejected with 401 due to expired signature validation fault.",
        "stack_trace": (
            "com.auth0.jwt.exceptions.JWTVerificationException: The Token has expired on Sun Aug 28 12:00:00 UTC 2026\n"
            "\tat com.example.security.JWTVerifier.verifyToken(JWTVerifier.java:78)\n"
            "\tat com.example.security.AuthFilter.doFilter(AuthFilter.java:55)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Security/Auth",
        "expected_exception": "JWTVerificationException",
        "expected_file": "JWTVerifier.java",
        "expected_line": 78,
        "format": "Java"
    },
    # 20. JavaScript / UI - Medium Render Crash
    {
        "id": "TC-20",
        "title": "TypeError: Cannot read properties of undefined (reading 'map')",
        "description": "Frontend grid component layout crashed when receiving empty search response payload.",
        "stack_trace": (
            "TypeError: Cannot read properties of undefined (reading 'map')\n"
            "    at ProductGrid (src/components/ProductGrid.jsx:45:22)\n"
            "    at renderWithHooks (node_modules/react-dom/cjs/react-dom.development.js:16305:18)"
        ),
        "expected_severity": "High",
        "expected_priority": "P2",
        "expected_component": "Frontend/UI",
        "expected_exception": "TypeError",
        "expected_file": "ProductGrid.jsx",
        "expected_line": 45,
        "format": "JavaScript"
    }
]
