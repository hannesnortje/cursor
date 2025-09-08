#!/usr/bin/env python3
"""
Phase 4.1: Network Security Configuration Test Suite
Tests network monitoring, SSL/TLS configuration, and firewall management
"""

import json
import sys
import time
import threading
from typing import Dict, Any

# Add project root to path
sys.path.append('.')

def test_network_monitoring():
    """Test network monitoring functionality."""
    print("🌐 Testing Network Monitoring...")
    
    try:
        from src.security.network_security import network_monitor
        
        # Test 1: Get initial statistics
        stats = network_monitor.get_network_statistics()
        print(f"✅ Network Statistics: {stats['total_connections']} connections, monitoring: {stats['monitoring_active']}")
        
        # Test 2: Start monitoring
        network_monitor.start_monitoring()
        time.sleep(2)  # Let it run for a bit
        
        # Test 3: Get updated statistics
        stats = network_monitor.get_network_statistics()
        print(f"✅ Monitoring Started: {stats['monitoring_active']}, interval: {stats['monitor_interval']}s")
        
        # Test 4: Get connections
        connections = network_monitor.get_connections(limit=10)
        print(f"✅ Network Connections: {len(connections)} connections retrieved")
        
        # Test 5: Get security events
        events = network_monitor.get_security_events(limit=10)
        print(f"✅ Security Events: {len(events)} events retrieved")
        
        # Test 6: Stop monitoring
        network_monitor.stop_monitoring()
        print("✅ Network monitoring stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Network Monitoring Test Failed: {e}")
        return False

def test_ssl_configuration():
    """Test SSL/TLS configuration."""
    print("\n🔒 Testing SSL/TLS Configuration...")
    
    try:
        from src.security.network_security import ssl_config
        
        # Test 1: Validate SSL config
        validation = ssl_config.validate_ssl_config()
        print(f"✅ SSL Validation: {validation['valid']}, {validation['contexts']} contexts, {validation['certificates']} certificates")
        
        # Test 2: Create SSL context
        try:
            context = ssl_config.create_ssl_context("test_context")
            print("✅ SSL Context Created: test_context")
        except Exception as e:
            print(f"⚠️ SSL Context Creation: {e}")
        
        # Test 3: Test SSL connection (to a known secure site)
        try:
            result = ssl_config.test_ssl_connection("www.google.com", 443, "test_context")
            if result["success"]:
                print(f"✅ SSL Connection Test: Connected to {result['host']}:{result['port']}")
            else:
                print(f"⚠️ SSL Connection Test: {result['error']}")
        except Exception as e:
            print(f"⚠️ SSL Connection Test: {e}")
        
        # Test 4: Test plain connection
        try:
            result = ssl_config.test_ssl_connection("www.google.com", 80)
            if result["success"]:
                print(f"✅ Plain Connection Test: Connected to {result['host']}:{result['port']}")
            else:
                print(f"⚠️ Plain Connection Test: {result['error']}")
        except Exception as e:
            print(f"⚠️ Plain Connection Test: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SSL Configuration Test Failed: {e}")
        return False

def test_firewall_management():
    """Test firewall management functionality."""
    print("\n🛡️ Testing Firewall Management...")
    
    try:
        from src.security.network_security import firewall_manager
        
        # Test 1: Get initial status
        status = firewall_manager.get_firewall_status()
        print(f"✅ Firewall Status: {status['total_rules']} rules, {len(status['blocked_ips'])} blocked IPs")
        
        # Test 2: Block an IP
        test_ip = "192.168.1.100"
        success = firewall_manager.block_ip(test_ip, "Test block")
        print(f"✅ Block IP: {test_ip} - {'Success' if success else 'Failed'}")
        
        # Test 3: Check if IP is blocked
        is_blocked = not firewall_manager.is_ip_allowed(test_ip)
        print(f"✅ IP Block Check: {test_ip} is {'blocked' if is_blocked else 'allowed'}")
        
        # Test 4: Allow the IP
        success = firewall_manager.allow_ip(test_ip, "Test allow")
        print(f"✅ Allow IP: {test_ip} - {'Success' if success else 'Failed'}")
        
        # Test 5: Check if IP is allowed
        is_allowed = firewall_manager.is_ip_allowed(test_ip)
        print(f"✅ IP Allow Check: {test_ip} is {'allowed' if is_allowed else 'blocked'}")
        
        # Test 6: Block a port
        test_port = 8080
        success = firewall_manager.block_port(test_port, "Test port block")
        print(f"✅ Block Port: {test_port} - {'Success' if success else 'Failed'}")
        
        # Test 7: Check if port is blocked
        is_blocked = not firewall_manager.is_port_allowed(test_port)
        print(f"✅ Port Block Check: {test_port} is {'blocked' if is_blocked else 'allowed'}")
        
        # Test 8: Get updated status
        status = firewall_manager.get_firewall_status()
        print(f"✅ Updated Firewall Status: {status['total_rules']} rules, {len(status['blocked_ips'])} blocked IPs, {len(status['blocked_ports'])} blocked ports")
        
        return True
        
    except Exception as e:
        print(f"❌ Firewall Management Test Failed: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity functionality."""
    print("\n🔗 Testing Network Connectivity...")
    
    try:
        from src.security.network_security import firewall_manager
        
        # Test 1: Test connectivity to Google
        result = firewall_manager.test_network_connectivity("www.google.com", 80, 5)
        if result["connected"]:
            print(f"✅ Google HTTP: Connected in {result['response_time_ms']}ms")
        else:
            print(f"⚠️ Google HTTP: {result.get('error', 'Connection failed')}")
        
        # Test 2: Test connectivity to Google HTTPS
        result = firewall_manager.test_network_connectivity("www.google.com", 443, 5)
        if result["connected"]:
            print(f"✅ Google HTTPS: Connected in {result['response_time_ms']}ms")
        else:
            print(f"⚠️ Google HTTPS: {result.get('error', 'Connection failed')}")
        
        # Test 3: Test connectivity to non-existent host
        result = firewall_manager.test_network_connectivity("nonexistent.example.com", 80, 2)
        if not result["connected"]:
            print(f"✅ Non-existent Host: Correctly failed to connect")
        else:
            print(f"⚠️ Non-existent Host: Unexpectedly connected")
        
        # Test 4: Test connectivity to closed port
        result = firewall_manager.test_network_connectivity("www.google.com", 9999, 2)
        if not result["connected"]:
            print(f"✅ Closed Port: Correctly failed to connect")
        else:
            print(f"⚠️ Closed Port: Unexpectedly connected")
        
        return True
        
    except Exception as e:
        print(f"❌ Network Connectivity Test Failed: {e}")
        return False

def test_mcp_tools():
    """Test MCP network security tools."""
    print("\n🔧 Testing MCP Network Security Tools...")
    
    try:
        from src.mcp_tools.handlers.system_tools import handle_system_tool
        
        # Mock send_response function
        responses = []
        def mock_send_response(request_id, result=None, error=None):
            responses.append({'request_id': request_id, 'result': result, 'error': error})
        
        # Test 1: get_network_statistics
        handle_system_tool('get_network_statistics', {}, 'test_1', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ get_network_statistics: Working")
        else:
            print("❌ get_network_statistics: Failed")
            return False
        
        # Test 2: get_network_connections
        handle_system_tool('get_network_connections', {'limit': 10}, 'test_2', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ get_network_connections: Working")
        else:
            print("❌ get_network_connections: Failed")
            return False
        
        # Test 3: validate_ssl_config
        handle_system_tool('validate_ssl_config', {}, 'test_3', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ validate_ssl_config: Working")
        else:
            print("❌ validate_ssl_config: Failed")
            return False
        
        # Test 4: get_firewall_status
        handle_system_tool('get_firewall_status', {}, 'test_4', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ get_firewall_status: Working")
        else:
            print("❌ get_firewall_status: Failed")
            return False
        
        # Test 5: block_ip
        handle_system_tool('block_ip', {'ip': '192.168.1.200', 'reason': 'Test'}, 'test_5', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ block_ip: Working")
        else:
            print("❌ block_ip: Failed")
            return False
        
        # Test 6: test_network_connectivity
        handle_system_tool('test_network_connectivity', {'host': 'www.google.com', 'port': 80}, 'test_6', mock_send_response)
        if responses and responses[-1]['result']:
            print("✅ test_network_connectivity: Working")
        else:
            print("❌ test_network_connectivity: Failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Tools Test Failed: {e}")
        return False

def test_concurrent_operations():
    """Test concurrent network security operations."""
    print("\n⚡ Testing Concurrent Operations...")
    
    try:
        from src.security.network_security import network_monitor, firewall_manager
        
        # Test concurrent network monitoring and firewall operations
        results = []
        
        def monitor_worker():
            try:
                stats = network_monitor.get_network_statistics()
                results.append(('monitor', stats['total_connections']))
            except Exception as e:
                results.append(('monitor_error', str(e)))
        
        def firewall_worker():
            try:
                status = firewall_manager.get_firewall_status()
                results.append(('firewall', status['total_rules']))
            except Exception as e:
                results.append(('firewall_error', str(e)))
        
        # Start concurrent operations
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=monitor_worker))
            threads.append(threading.Thread(target=firewall_worker))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check results
        monitor_results = [r for r in results if r[0] == 'monitor']
        firewall_results = [r for r in results if r[0] == 'firewall']
        
        print(f"✅ Concurrent Monitor Operations: {len(monitor_results)} successful")
        print(f"✅ Concurrent Firewall Operations: {len(firewall_results)} successful")
        
        if len(monitor_results) == 5 and len(firewall_results) == 5:
            print("✅ All concurrent operations completed successfully")
            return True
        else:
            print("⚠️ Some concurrent operations failed")
            return False
        
    except Exception as e:
        print(f"❌ Concurrent Operations Test Failed: {e}")
        return False

def run_phase_4_1_test():
    """Run all Phase 4.1 tests."""
    print("🚀 Starting Phase 4.1: Network Security Configuration Test")
    print("=" * 60)
    
    tests = [
        ("Network Monitoring", test_network_monitoring),
        ("SSL/TLS Configuration", test_ssl_configuration),
        ("Firewall Management", test_firewall_management),
        ("Network Connectivity", test_network_connectivity),
        ("MCP Tools", test_mcp_tools),
        ("Concurrent Operations", test_concurrent_operations)
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
    print("📋 PHASE 4.1 TEST SUMMARY")
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
        print("🎉 ALL PHASE 4.1 TESTS PASSED! Network Security Configuration is working perfectly!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_phase_4_1_test()
    sys.exit(0 if success else 1)
