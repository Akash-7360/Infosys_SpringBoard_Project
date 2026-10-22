import sys
import os
import logging

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import vector_store_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_data")

HISTORICAL_DEFECTS_DATASET = [
    # APACHE REPOSITORY DEFECTS
    {
        "bug_id": "APACHE-KAFKA-10294",
        "repository": "Apache",
        "component": "Messaging/Queue",
        "title": "NullPointerException in RecordAccumulator drain during high memory pressure batch flush",
        "description": "Producer application crashes under heavy load when batch size exceeds buffer memory threshold. The drain loop attempts to reference a recycled TopicPartition batch object.",
        "stack_trace": (
            "java.lang.NullPointerException: Cannot invoke 'org.apache.kafka.clients.producer.internals.ProducerBatch.drain()' because 'batch' is null\n"
            "\tat org.apache.kafka.clients.producer.internals.RecordAccumulator.drain(RecordAccumulator.java:248)\n"
            "\tat org.apache.kafka.clients.producer.internals.Sender.sendProducerData(Sender.java:335)\n"
            "\tat org.apache.kafka.clients.producer.internals.Sender.runOnce(Sender.java:281)\n"
            "\tat org.apache.kafka.clients.producer.internals.Sender.run(Sender.java:240)"
        ),
        "offending_function": "RecordAccumulator.drain",
        "root_cause": "Race condition between ProducerBatch de-allocation thread and Sender thread polling active partition queues.",
        "resolution": "Added explicit null check and synchronized barrier prior to dequeuing ProducerBatch instances during buffer pool eviction."
    },
    {
        "bug_id": "APACHE-SPARK-34812",
        "repository": "Apache",
        "component": "Core",
        "title": "OutOfMemoryError in TaskMemoryManager during shuffle hash join spilled partition read",
        "description": "Executor crashes with OOM when processing skewed join keys. Memory manager fails to spill in-memory hash maps before allocation request.",
        "stack_trace": (
            "java.lang.OutOfMemoryError: Java heap space\n"
            "\tat org.apache.spark.memory.TaskMemoryManager.allocatePage(TaskMemoryManager.java:298)\n"
            "\tat org.apache.spark.sql.execution.joins.HashedRelation$.apply(HashedRelation.scala:124)\n"
            "\tat org.apache.spark.sql.execution.joins.ShuffledHashJoinExec.doExecute(ShuffledHashJoinExec.scala:89)"
        ),
        "offending_function": "TaskMemoryManager.allocatePage",
        "root_cause": "Memory consumer failed to register disk spiller interface during task init, resulting in un-spilled hash map expansion.",
        "resolution": "Registered fallback DiskHashedRelation spiller inside HashedRelation initialization fallback."
    },
    {
        "bug_id": "APACHE-HTTPD-59310",
        "repository": "Apache",
        "component": "Networking",
        "title": "SIGSEGV crash in mod_proxy_http worker during TLS handshake renegotiation",
        "description": "HTTPD child worker process segmentation fault when client triggers SSL renegotiation over HTTP/1.1 persistent connection.",
        "stack_trace": (
            "Program received signal SIGSEGV, Segmentation fault.\n"
            "0x00007ffff7bd21a4 in ap_proxy_http_process_response (r=0x7fffd0012890) at mod_proxy_http.c:1842\n"
            "1842        if (backend->ssl_renegotiate_pending) {\n"
            "Frame #0: 0x00007ffff7bd21a4 in ap_proxy_http_process_response\n"
            "Frame #1: 0x00007ffff7bca012 in proxy_http_handler at mod_proxy_http.c:2104"
        ),
        "offending_function": "ap_proxy_http_process_response",
        "root_cause": "Dangling pointer reference to `backend` socket context after SSL connection reset by peer.",
        "resolution": "Reset connection state structure to NULL upon SSL handshake failure in proxy cleanup routine."
    },
    {
        "bug_id": "APACHE-CASSANDRA-17210",
        "repository": "Apache",
        "component": "Database/Storage",
        "title": "CorruptSSTableException during compaction of compressed SSTable with checksum mismatch",
        "description": "Compaction execution thread fails abruptly on node restart when reading compressed chunk header checksums.",
        "stack_trace": (
            "org.apache.cassandra.io.sstable.CorruptSSTableException: Corrupted SSTable /var/lib/cassandra/data/keyspace/table/me-102-big-Data.db\n"
            "\tat org.apache.cassandra.io.compress.CompressedSequentialWriter.writeChunk(CompressedSequentialWriter.java:182)\n"
            "\tat org.apache.cassandra.db.compaction.CompactionTask.executeInternal(CompactionTask.java:194)"
        ),
        "offending_function": "CompressedSequentialWriter.writeChunk",
        "root_cause": "Unflushed tail chunk buffer truncated during hard shutdown.",
        "resolution": "Implied SSTable verify check on startup and automatic quarantine of truncated checksum chunks."
    },

    # MOZILLA REPOSITORY DEFECTS
    {
        "bug_id": "MOZILLA-GECKO-1589410",
        "repository": "Mozilla",
        "component": "Frontend/UI",
        "title": "Use-after-free in nsDocShell::Destroy when closing subframe tabs rapidly",
        "description": "Firefox crashes when closing tabs containing iframe trees quickly due to document shell lifecycle destruction race.",
        "stack_trace": (
            "CRASH INFO: Crash Type: EXCEPTION_ACCESS_VIOLATION_READ (Use-After-Free)\n"
            "\tat nsDocShell::Destroy() (docshell/base/nsDocShell.cpp:4812)\n"
            "\tat nsDocShell::DestroyChildren() (docshell/base/nsDocShell.cpp:4850)\n"
            "\tat mozilla::dom::BrowsingContext::Detach() (dom/base/BrowsingContext.cpp:1120)"
        ),
        "offending_function": "nsDocShell::Destroy",
        "root_cause": "Child frame array mutated during forward iteration in DestroyChildren destructor loop.",
        "resolution": "Used RefPtr smart pointers and backward index iteration to protect child frame lifecycles."
    },
    {
        "bug_id": "MOZILLA-SPIDERMONKEY-1620401",
        "repository": "Mozilla",
        "component": "Core",
        "title": "JIT compilation failure in IonMonkey optimization pass for AsyncGenerator next()",
        "description": "SpiderMonkey JS Engine throws assertion error in IonGraph optimization pass when compiling nested async generator loops.",
        "stack_trace": (
            "Assertion failure: [IonMonkey] range.hasLowerBound() failed at js/src/jit/RangeAnalysis.cpp:1420\n"
            "\tat js::jit::RangeAnalysis::analyze() (js/src/jit/RangeAnalysis.cpp:1420)\n"
            "\tat js::jit::OptimizeMIR() (js/src/jit/Ion.cpp:1890)"
        ),
        "offending_function": "js::jit::RangeAnalysis::analyze",
        "root_cause": "Integer range overflow analysis omitted lower bound check for negative iterator steps.",
        "resolution": "Added lower bound cap check in MIR range analysis phase for AsyncGenerator yield resume steps."
    },
    {
        "bug_id": "MOZILLA-NSS-1492019",
        "repository": "Mozilla",
        "component": "Security/Auth",
        "title": "Buffer overflow in NSS SECITEM_AllocItem during RSA PKCS#1 v1.5 signature verification",
        "description": "Security error when processing malformed ASN.1 signature structure containing invalid length byte.",
        "stack_trace": (
            "SEC_ERROR_INVALID_ARGS: security library invalid arguments\n"
            "\tat SECITEM_AllocItem_Util (security/nss/lib/util/secitem.c:115)\n"
            "\tat RSA_VerifyPKCS1FromDigest (security/nss/lib/freebl/rsa.c:482)"
        ),
        "offending_function": "SECITEM_AllocItem_Util",
        "root_cause": "Integer overflow in size parameter calculation `len + 1` when len == UINT32_MAX.",
        "resolution": "Added maximum size check validation before allocating SECITEM buffer."
    },

    # ECLIPSE REPOSITORY DEFECTS
    {
        "bug_id": "ECLIPSE-JDT-512903",
        "repository": "Eclipse",
        "component": "Core",
        "title": "Compiler Deadlock in TypeSystem.resolveType during Java 17 sealed class interface hierarchy check",
        "description": "Eclipse Java Compiler hangs indefinitely when resolving circular permitted subtype declarations across multiple source files.",
        "stack_trace": (
            "java.lang.Thread$State: BLOCKED (on object monitor org.eclipse.jdt.internal.compiler.lookup.TypeSystem)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.TypeSystem.resolveType(TypeSystem.java:412)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.SourceTypeBinding.permittedTypes(SourceTypeBinding.java:891)\n"
            "\tat org.eclipse.jdt.internal.compiler.lookup.CompilationUnitScope.connectTypeHierarchy(CompilationUnitScope.java:310)"
        ),
        "offending_function": "TypeSystem.resolveType",
        "root_cause": "Lock ordering discrepancy between CompilationUnitScope and global TypeSystem lock during hierarchy resolution.",
        "resolution": "Replaced coarse synchronized block with ConcurrentHashMap memoization for permitted types lookup."
    },
    {
        "bug_id": "ECLIPSE-EQUINOX-489012",
        "repository": "Eclipse",
        "component": "Core",
        "title": "BundleException in OSGi Framework Storage during dynamic bundle resolution update",
        "description": "Equinox OSGi runtime throws BundleException when refreshing bundle dependency wiring under concurrent plugin install requests.",
        "stack_trace": (
            "org.osgi.framework.BundleException: Could not resolve module: org.eclipse.core.resources [52]\n"
            "\tat org.eclipse.osgi.container.Module.start(Module.java:464)\n"
            "\tat org.eclipse.osgi.internal.framework.EquinoxBundle.start(EquinoxBundle.java:439)\n"
            "\tat org.eclipse.core.runtime.internal.adaptor.ContextFinder.loadClass(ContextFinder.java:120)"
        ),
        "offending_function": "EquinoxBundle.start",
        "root_cause": "Stale wire reference stored in module container graph during concurrent bundle lifecycle update.",
        "resolution": "Invalidated dependency cache prior to committing new bundle wiring state in OSGi container graph."
    },
    {
        "bug_id": "ECLIPSE-SWT-567112",
        "repository": "Eclipse",
        "component": "Frontend/UI",
        "title": "SWTError: No more handles [gtk_widget_get_window failed] on Wayland desktop layout display",
        "description": "Eclipse IDE workspace window crashes after opening 50+ code editors under GTK3/Wayland environment.",
        "stack_trace": (
            "org.eclipse.swt.SWTError: No more handles\n"
            "\tat org.eclipse.swt.SWT.error(SWT.java:4604)\n"
            "\tat org.eclipse.swt.widgets.Widget.error(Widget.java:482)\n"
            "\tat org.eclipse.swt.widgets.Control.internal_new_GC(Control.java:2140)\n"
            "\tat org.eclipse.swt.graphics.GC.gtk_render_background(GC.java:1912)"
        ),
        "offending_function": "Control.internal_new_GC",
        "root_cause": "Leaked Cairo surface context handles when rendering tree items with custom CSS styles.",
        "resolution": "Explicitly disposed Cairo surface contexts in GC lifecycle teardown hook."
    }
]


def seed_vector_db():
    logger.info("Starting historical defect vector database seeding...")
    count = vector_store_service.add_defects(HISTORICAL_DEFECTS_DATASET)
    logger.info(f"Successfully seeded {len(HISTORICAL_DEFECTS_DATASET)} bug records ({count} total chunks) into ChromaDB!")


if __name__ == "__main__":
    seed_vector_db()
