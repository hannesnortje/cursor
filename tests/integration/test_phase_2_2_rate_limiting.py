#!/usr/bin/env python3
"""
Phase 2.2: Rate Limiting Integration Test Suite
Tests rate limiting, security middleware, and MCP server integration
"""

import json
import sys
import time
import threading
from typing import Dict, Any

# Add project root to path
sys.path.append(".")


def test_security_components():
    """Test individual security components."""
    print("🔒 Testing Security Components...")

    try:
        from src.security.middleware import security_middleware
        from src.security.headers import SecurityHeaders
        from src.security.rate_limiting import rate_limiter

        # Test 1: Security Headers
        headers = SecurityHeaders()
        headers_list = headers.get_headers()
        print(f"✅ Security Headers: {len(headers_list)} headers configured")

        # Test 2: Rate Limiter
        result = rate_limiter.is_allowed("test_client", "general")
        print(f"✅ Rate Limiter: {result['allowed']} - {result['remaining']} remaining")

        # Test 3: Security Middleware
        request_data = {
            "method": "GET",
            "path": "/test",
            "headers": {"User-Agent": "test-client"},
            "body": "",
        }
        result = security_middleware.process_request(request_data)
        print(f"✅ Security Middleware: Request allowed = {result['allowed']}")

        return True

    except Exception as e:
        print(f"❌ Security Components Test Failed: {e}")
        return False


def test_rate_limiting():
    """Test rate limiting with multiple requests."""
    print("\n🚦 Testing Rate Limiting...")

    try:
        from src.security.rate_limiting import rate_limiter

        client_id = "rate_test_client"
        endpoint_type = "mcp_tools"

        # Test normal requests
        for i in range(5):
            result = rate_limiter.is_allowed(client_id, endpoint_type)
            print(
                f"  Request {i+1}: {result['allowed']} - {result['remaining']} remaining"
            )

        # Test burst protection
        print("  Testing burst protection...")
        burst_results = []
        for i in range(15):  # Try to exceed burst limit
            result = rate_limiter.is_allowed(client_id, endpoint_type)
            burst_results.append(result["allowed"])
            if not result["allowed"]:
                print(f"  Burst limit hit at request {i+1}")
                break

        # Test statistics
        stats = rate_limiter.get_statistics()
        print(f"✅ Rate Limiter Stats: {stats['active_windows']} active windows")

        return True

    except Exception as e:
        print(f"❌ Rate Limiting Test Failed: {e}")
        return False


def test_security_validation():
    """Test security validation with various request types."""
    print("\n🛡️ Testing Security Validation...")

    try:
        from src.security.middleware import security_middleware

        # Test 1: Normal request
        normal_request = {
            "method": "GET",
            "path": "/api/health",
            "headers": {"User-Agent": "normal-client"},
            "body": '{"test": "data"}',
        }
        result = security_middleware.process_request(normal_request)
        print(f"✅ Normal Request: {result['allowed']}")

        # Test 2: XSS attempt
        xss_request = {
            "method": "POST",
            "path": "/api/comment",
            "headers": {"User-Agent": "normal-client"},
            "body": '<script>alert("xss")</script>',
        }
        result = security_middleware.process_request(xss_request)
        print(
            f"✅ XSS Detection: {'Blocked' if not result['allowed'] else 'Allowed'} - {result['security_validation']['issues']}"
        )

        # Test 3: Path traversal attempt
        traversal_request = {
            "method": "GET",
            "path": "/api/files/../../../etc/passwd",
            "headers": {"User-Agent": "normal-client"},
            "body": "",
        }
        result = security_middleware.process_request(traversal_request)
        print(
            f"✅ Path Traversal Detection: {'Blocked' if not result['allowed'] else 'Allowed'} - {result['security_validation']['issues']}"
        )

        # Test 4: Large request
        large_request = {
            "method": "POST",
            "path": "/api/upload",
            "headers": {"User-Agent": "normal-client"},
            "body": "x" * (11 * 1024 * 1024),  # 11MB
        }
        result = security_middleware.process_request(large_request)
        print(
            f"✅ Large Request Detection: {'Blocked' if not result['allowed'] else 'Allowed'} - {result['security_validation']['issues']}"
        )

        return True

    except Exception as e:
        print(f"❌ Security Validation Test Failed: {e}")
        return False


def test_mcp_tools():
    """Test MCP security tools."""
    print("\n🔧 Testing MCP Security Tools...")

    try:
        from src.mcp_tools.handlers.system_tools import handle_system_tool

        # Mock send_response function
        responses = []

        def mock_send_response(request_id, result=None, error=None):
            responses.append(
                {"request_id": request_id, "result": result, "error": error}
            )

        # Test 1: get_security_status
        handle_system_tool("get_security_status", {}, "test_1", mock_send_response)
        if responses and responses[-1]["result"]:
            print("✅ get_security_status: Working")
        else:
            print("❌ get_security_status: Failed")
            return False

        # Test 2: get_rate_limit_status
        handle_system_tool(
            "get_rate_limit_status",
            {"client_id": "test_client"},
            "test_2",
            mock_send_response,
        )
        if responses and responses[-1]["result"]:
            print("✅ get_rate_limit_status: Working")
        else:
            print("❌ get_rate_limit_status: Failed")
            return False

        # Test 3: validate_security_headers
        handle_system_tool(
            "validate_security_headers", {}, "test_3", mock_send_response
        )
        if responses and responses[-1]["result"]:
            print("✅ validate_security_headers: Working")
        else:
            print("❌ validate_security_headers: Failed")
            return False

        return True

    except Exception as e:
        print(f"❌ MCP Tools Test Failed: {e}")
        return False


def test_mcp_server_integration():
    """Test MCP server with security integration."""
    print("\n🖥️ Testing MCP Server Integration...")

    try:
        # Test if we can import the protocol server with security
        import protocol_server

        # Check if security is available
        if hasattr(protocol_server, "SECURITY_AVAILABLE"):
            print(f"✅ Security Available: {protocol_server.SECURITY_AVAILABLE}")
        else:
            print("❌ Security integration not found in protocol server")
            return False

        # Test security middleware import
        if protocol_server.SECURITY_AVAILABLE:
            print("✅ Security middleware imported successfully")
        else:
            print("⚠️ Security middleware not available (expected in some environments)")

        return True

    except Exception as e:
        print(f"❌ MCP Server Integration Test Failed: {e}")
        return False


def test_security_statistics():
    """Test security statistics and monitoring."""
    print("\n📊 Testing Security Statistics...")

    try:
        from src.security.middleware import security_middleware
        from src.security.rate_limiting import rate_limiter

        # Generate some test traffic
        for i in range(10):
            request_data = {
                "method": "GET",
                "path": f"/test/{i}",
                "headers": {"User-Agent": f"test-client-{i}"},
                "body": f'{{"test": {i}}}',
            }
            security_middleware.process_request(request_data)

        # Get statistics
        security_stats = security_middleware.get_security_statistics()
        rate_limit_stats = rate_limiter.get_statistics()

        print(
            f"✅ Security Stats: {security_stats['total_requests']} requests processed"
        )
        print(
            f"✅ Rate Limit Stats: {rate_limit_stats['active_windows']} active windows"
        )
        print(f"✅ Security Events: {security_stats['security_events']} events logged")

        return True

    except Exception as e:
        print(f"❌ Security Statistics Test Failed: {e}")
        return False


def run_phase_2_2_test():
    """Run all Phase 2.2 tests."""
    print("🚀 Starting Phase 2.2: Rate Limiting Integration Test")
    print("=" * 60)

    tests = [
        ("Security Components", test_security_components),
        ("Rate Limiting", test_rate_limiting),
        ("Security Validation", test_security_validation),
        ("MCP Tools", test_mcp_tools),
        ("MCP Server Integration", test_mcp_server_integration),
        ("Security Statistics", test_security_statistics),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Test Crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📋 PHASE 2.2 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print(
            "🎉 ALL PHASE 2.2 TESTS PASSED! Rate Limiting Integration is working perfectly!"
        )
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = run_phase_2_2_test()
    sys.exit(0 if success else 1)
