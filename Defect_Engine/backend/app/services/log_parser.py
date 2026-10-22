import re
from typing import Dict, Any, List, Optional, Tuple
from app.models.agent_state import ParsedLogResult, LogFrameInfo, LogFailurePoint

# Regex patterns for timestamp sanitization
TIMESTAMP_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+\d{2}:\d{2}:\d{2}\b',
    r'\[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4}\]',
    r'\b\d{2}:\d{2}:\d{2}\.\d{3}\b',
]

# Regex patterns for log levels / thread prefixes
NOISE_PATTERNS = [
    r'\[?(?:DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE|CRITICAL)\]?:?',
    r'\[thread-\d+\]',
    r'\[main\]',
    r'0x[0-9a-fA-F]{8,16}',
]

# Vendor / Standard library namespaces to mark as non-application frames
STDLIB_FRAME_PREFIXES = (
    'java.lang.', 'java.util.', 'java.io.', 'java.net.', 'java.nio.',
    'sun.reflect.', 'jdk.internal.', 'org.apache.commons.',
    'sys', 'os', 'threading', 'asyncio', 'site-packages/', '/usr/lib/python',
    'node_modules/', 'node:', 'v8/src', 'internal/process', 'runtime/'
)


def sanitize_log_text(raw_log: str) -> tuple[str, int]:
    """
    Sanitizes timestamps and log noise from raw log lines.
    Returns (sanitized_text, lines_removed_count).
    """
    if not raw_log:
        return "", 0

    lines = raw_log.strip().splitlines()
    sanitized_lines = []
    noise_count = 0

    for line in lines:
        cleaned_line = line
        # Strip timestamps
        for pattern in TIMESTAMP_PATTERNS:
            cleaned_line = re.sub(pattern, '', cleaned_line)

        # Strip noise prefixes
        for pattern in NOISE_PATTERNS:
            cleaned_line = re.sub(pattern, '', cleaned_line)

        cleaned_line = cleaned_line.strip()
        if cleaned_line:
            sanitized_lines.append(cleaned_line)
        else:
            noise_count += 1

    return "\n".join(sanitized_lines), noise_count


def extract_exception_info(log_text: str) -> tuple[str, str]:
    """
    Extracts the main exception type and error message from log/stack trace.
    """
    if not log_text or not log_text.strip():
        return "ApplicationDefect", "No stack trace provided."

    # Look for explicit Caused by line
    caused_by_match = re.search(r'Caused by:\s*([A-Za-z0-9_.]+(?:Exception|Error|Fault|Panic|Failure)):\s*(.*)', log_text)
    if caused_by_match:
        exc_full = caused_by_match.group(1).strip()
        return exc_full.split('.')[-1], caused_by_match.group(2).strip()

    # Look for Go panic pattern
    go_panic = re.search(r'^panic:\s*(.*)', log_text, re.MULTILINE)
    if go_panic:
        return "panic", go_panic.group(1).strip()

    # Look for uppercase error codes / constants like EXCEPTION_ACCESS_VIOLATION_READ or SEC_ERROR_INVALID_ARGS
    code_match = re.search(r'\b(EXCEPTION_[A-Z0-9_]+|SEC_ERROR_[A-Z0-9_]+|[A-Z0-9_]+_ERROR_[A-Z0-9_]+)\b:?\s*(.*)', log_text)
    if code_match:
        return code_match.group(1), code_match.group(2).strip()


    # Look for Java Thread BLOCKED / Deadlock
    thread_match = re.search(r'Thread\$State:\s*BLOCKED\s*\(on object monitor ([a-zA-Z0-9_.$]+)\)', log_text)
    if thread_match:
        class_name = thread_match.group(1).rsplit('.', 1)[-1]
        return class_name, f"Thread BLOCKED on object monitor {thread_match.group(1)}"

    # Look for Standard Python / Java / JS / C++ Exception patterns
    exc_match = re.search(r'\b([A-Za-z0-9_.]*(?:Exception|Error|Fault|Panic|Failure|SIGSEGV|SIGABRT|SWTError))\b:?\s*(.*)', log_text)
    if exc_match:
        exc_type = exc_match.group(1).split('.')[-1]
        exc_msg = exc_match.group(2).strip()
        return exc_type, exc_msg

    # Look for Assertion failures
    panic_match = re.search(r'Assertion failure:\s*(.*)', log_text, re.IGNORECASE)
    if panic_match:
        return "AssertionError", panic_match.group(1).strip()

    # Fallback to first non-empty line
    first_line = [l.strip() for l in log_text.splitlines() if l.strip()]
    first_str = first_line[0] if first_line else "Unknown Error"
    return "ApplicationDefect", first_str[:150]



def parse_stack_frames(log_text: str) -> Tuple[List[LogFrameInfo], List[LogFrameInfo], str]:
    """
    Parses application frames and standard library frames across Java, Python, JS, C++, and Go formats.
    Returns (app_frames, stdlib_frames, detected_format).
    """
    lines = log_text.splitlines()
    app_frames: List[LogFrameInfo] = []
    stdlib_frames: List[LogFrameInfo] = []
    frame_idx = 1
    format_counts = {"Java": 0, "Python": 0, "JavaScript": 0, "C/C++": 0, "Go": 0}

    i = 0
    while i < len(lines):
        line_str = lines[i].strip()
        if not line_str:
            i += 1
            continue

        # 1. Java pattern: at com.example.MyClass.method(MyClass.java:42)
        java_match = re.search(r'at\s+([a-zA-Z0-9_.$]+)\(([a-zA-Z0-9_.]+\.(?:java|kt)):(\d+)\)', line_str)
        if java_match:
            full_func = java_match.group(1)
            file_name = java_match.group(2)
            line_num = int(java_match.group(3))
            format_counts["Java"] += 1
            
            parts = full_func.rsplit('.', 1)
            class_name = parts[0] if len(parts) > 1 else None
            method_name = parts[1] if len(parts) > 1 else full_func

            is_stdlib = any(full_func.startswith(p) for p in STDLIB_FRAME_PREFIXES)
            frame = LogFrameInfo(
                frame_number=frame_idx,
                raw_line=line_str,
                file_path=file_name,
                line_number=line_num,
                function_name=full_func,
                class_name=class_name,
                method_name=method_name,
                is_app_code=not is_stdlib
            )
            (stdlib_frames if is_stdlib else app_frames).append(frame)
            frame_idx += 1
            i += 1
            continue

        # 2. Python pattern: File "app/main.py", line 45, in parse_data
        py_match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+([a-zA-Z0-9_]+)', line_str)
        if py_match:
            file_path = py_match.group(1)
            line_num = int(py_match.group(2))
            func_name = py_match.group(3)
            format_counts["Python"] += 1

            file_name = file_path.rsplit('/', 1)[-1]
            is_stdlib = any(p in file_path for p in STDLIB_FRAME_PREFIXES)
            frame = LogFrameInfo(
                frame_number=frame_idx,
                raw_line=line_str,
                file_path=file_path,
                line_number=line_num,
                function_name=func_name,
                class_name=file_name.split('.')[0] if '.' in file_name else None,
                method_name=func_name,
                is_app_code=not is_stdlib
            )
            (stdlib_frames if is_stdlib else app_frames).append(frame)
            frame_idx += 1
            i += 1
            continue

        # 3. JavaScript/Node.js pattern: at renderWidget (src/components/Widget.js:104:12) or at src/app.js:42:5
        js_match = re.search(r'at\s+(?:([a-zA-Z0-9_.$<>]+)\s+\()?([a-zA-Z0-9_./\\-]+\.[a-zA-Z]+):(\d+):(\d+)\)?', line_str)
        if js_match:
            func_name = js_match.group(1) or "anonymous"
            file_path = js_match.group(2)
            line_num = int(js_match.group(3))
            format_counts["JavaScript"] += 1

            file_name = file_path.rsplit('/', 1)[-1]
            is_stdlib = any(p in file_path for p in STDLIB_FRAME_PREFIXES)
            frame = LogFrameInfo(
                frame_number=frame_idx,
                raw_line=line_str,
                file_path=file_path,
                line_number=line_num,
                function_name=func_name,
                class_name=file_name.split('.')[0] if '.' in file_name else None,
                method_name=func_name,
                is_app_code=not is_stdlib
            )
            (stdlib_frames if is_stdlib else app_frames).append(frame)
            frame_idx += 1
            i += 1
            continue

        # 4. C/C++ GDB/Crash pattern: Frame #0: 0x... in func (args) at file.cpp:123 or func (file.cpp:123)
        cpp_match = re.search(r'(?:Frame\s+#\d+:\s*)?(?:0x[0-9a-fA-F]+\s+in\s+)?([a-zA-Z0-9_.:]+)\s*(?:\([^)]*\))?\s+(?:\([^)]*\)\s+at\s+|at\s+|\()([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]+):(\d+)\)?', line_str)
        if cpp_match:
            func_name = cpp_match.group(1)
            file_path = cpp_match.group(2)
            line_num = int(cpp_match.group(3))
            format_counts["C/C++"] += 1

            parts = func_name.rsplit('::', 1)
            class_name = parts[0] if len(parts) > 1 else None
            method_name = parts[1] if len(parts) > 1 else func_name

            frame = LogFrameInfo(
                frame_number=frame_idx,
                raw_line=line_str,
                file_path=file_path,
                line_number=line_num,
                function_name=func_name,
                class_name=class_name,
                method_name=method_name,
                is_app_code=True
            )
            app_frames.append(frame)
            frame_idx += 1
            i += 1
            continue

        # 5. Go Panic pattern: main.ProcessQueue(0x...)\n\t/app/worker.go:88 +0x45
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            go_func_match = re.search(r'^([a-zA-Z0-9_./-]+(?:\.[a-zA-Z0-9_]+)+)\(', line_str)
            go_file_match = re.search(r'^\t?([a-zA-Z0-9_./\\-]+\.go):(\d+)', next_line)
            if go_func_match and go_file_match:
                func_name = go_func_match.group(1)
                file_path = go_file_match.group(1)
                line_num = int(go_file_match.group(2))
                format_counts["Go"] += 1

                parts = func_name.rsplit('.', 1)
                class_name = parts[0] if len(parts) > 1 else None
                method_name = parts[1] if len(parts) > 1 else func_name

                frame = LogFrameInfo(
                    frame_number=frame_idx,
                    raw_line=f"{line_str} {next_line}",
                    file_path=file_path,
                    line_number=line_num,
                    function_name=func_name,
                    class_name=class_name,
                    method_name=method_name,
                    is_app_code=not func_name.startswith("runtime/")
                )
                if func_name.startswith("runtime/"):
                    stdlib_frames.append(frame)
                else:
                    app_frames.append(frame)
                frame_idx += 1
                i += 2
                continue

        i += 1

    # Determine dominant format
    detected_format = max(format_counts, key=format_counts.get) if max(format_counts.values()) > 0 else "Unstructured"
    return app_frames, stdlib_frames, detected_format


def parse_and_sanitize_logs(raw_log: str, stack_trace: str = "") -> ParsedLogResult:
    """
    Main entry point for log parser service. Sanitizes noise, parses multi-format frames,
    extracts structured LogFailurePoint, constructs code_path, and computes confidence score.
    """
    combined_raw = f"{raw_log or ''}\n{stack_trace or ''}".strip()
    sanitized_text, noise_removed = sanitize_log_text(combined_raw)
    
    exc_type, exc_msg = extract_exception_info(sanitized_text or combined_raw)
    app_frames, stdlib_frames, log_format = parse_stack_frames(combined_raw)

    top_offending = app_frames[0] if app_frames else (stdlib_frames[0] if stdlib_frames else None)

    # Build Failure Point
    failure_point: Optional[LogFailurePoint] = None
    if top_offending:
        file_name = top_offending.file_path.rsplit('/', 1)[-1] if top_offending.file_path else None
        failure_point = LogFailurePoint(
            file_name=file_name or top_offending.file_path,
            class_name=top_offending.class_name,
            method_name=top_offending.method_name or top_offending.function_name,
            line_number=top_offending.line_number,
            raw_frame=top_offending.raw_line
        )

    # Build Code Path Sequence
    code_path: List[str] = []
    all_frames = app_frames + stdlib_frames
    for f in all_frames[:8]: # Limit to top 8 calls for clarity
        location = f"{f.file_path}:{f.line_number}" if f.file_path and f.line_number else "unknown"
        func = f.function_name or "unknown_func"
        code_path.append(f"{func} ({location})")

    # Compute Parser Confidence Score
    confidence = 0.50 # Baseline for unstructured text
    if app_frames and top_offending and top_offending.line_number:
        confidence = 0.95
    elif stdlib_frames and stdlib_frames[0].line_number:
        confidence = 0.85
    elif exc_type != "UnknownException" and exc_type != "ApplicationDefect":
        confidence = 0.70

    return ParsedLogResult(
        exception_type=exc_type,
        exception_message=exc_msg,
        sanitized_trace=sanitized_text,
        top_offending_frame=top_offending,
        failure_point=failure_point,
        code_path=code_path,
        log_format=log_format,
        confidence_score=round(confidence, 2),
        application_frames=app_frames,
        stdlib_frames=stdlib_frames,
        noise_lines_removed=noise_removed
    )

