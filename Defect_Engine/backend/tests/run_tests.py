import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_m2 import (
    test_java_log_parser_and_failure_point,
    test_python_log_parser_and_failure_point,
    test_triage_agent_critical_classification,
    test_multi_agent_orchestrator_pipeline_resilience
)
from tests.test_m3 import (
    test_m3_duplicate_detection_agent,
    test_m3_root_cause_agent,
    test_m3_remediation_agent,
    test_m3_end_to_end_pipeline
)
from tests.test_m4_end_to_end import (
    test_m4_defect_pattern_analytics,
    test_m4_knowledge_base_growth_and_feedback_loop,
    test_m4_multi_language_pipeline_coverage
)
from tests.test_rate_limiting import (
    test_rate_limit_headers_injected,
    test_client_ip_proxy_extraction,
    test_rate_limit_exceeded_returns_429,
    test_separate_client_ips_have_independent_quotas
)


async def main():
    print("=" * 60)
    print("Running Milestone 1, 2, 3, and 4 Unit & Integration Tests...")
    print("=" * 60)
    
    # Milestone 2 Tests
    await test_java_log_parser_and_failure_point()
    print("✓ M2 test_java_log_parser_and_failure_point PASSED")
    await test_python_log_parser_and_failure_point()
    print("✓ M2 test_python_log_parser_and_failure_point PASSED")
    await test_triage_agent_critical_classification()
    print("✓ M2 test_triage_agent_critical_classification PASSED")
    await test_multi_agent_orchestrator_pipeline_resilience()
    print("✓ M2 test_multi_agent_orchestrator_pipeline_resilience PASSED")

    # Milestone 3 Tests
    await test_m3_duplicate_detection_agent()
    print("✓ M3.2 test_m3_duplicate_detection_agent PASSED")
    await test_m3_root_cause_agent()
    print("✓ M3.1 test_m3_root_cause_agent PASSED")
    await test_m3_remediation_agent()
    print("✓ M3.3 test_m3_remediation_agent PASSED")
    await test_m3_end_to_end_pipeline()
    print("✓ M3 test_m3_end_to_end_pipeline PASSED")

    # Milestone 4 Tests
    await test_m4_defect_pattern_analytics()
    print("✓ M4.1 test_m4_defect_pattern_analytics PASSED")
    await test_m4_knowledge_base_growth_and_feedback_loop()
    print("✓ M4.2 test_m4_knowledge_base_growth_and_feedback_loop PASSED")
    await test_m4_multi_language_pipeline_coverage()
    print("✓ M4.3 test_m4_multi_language_pipeline_coverage PASSED")

    # API Security & Rate Limiting Tests
    test_rate_limit_headers_injected()
    print("✓ Security: test_rate_limit_headers_injected PASSED")
    test_client_ip_proxy_extraction()
    print("✓ Security: test_client_ip_proxy_extraction PASSED")
    test_rate_limit_exceeded_returns_429()
    print("✓ Security: test_rate_limit_exceeded_returns_429 PASSED")
    test_separate_client_ips_have_independent_quotas()
    print("✓ Security: test_separate_client_ips_have_independent_quotas PASSED")

    print("=" * 60)
    print("ALL MILESTONE 1, 2, 3, AND 4 + RATE LIMITING TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

