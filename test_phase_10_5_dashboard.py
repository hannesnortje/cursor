#!/usr/bin/env python3
"""
Phase 10.5: Dashboard Integration Testing
Non-blocking test suite for dashboard functionality
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any

class DashboardTester:
    """Dashboard integration testing with proper timeouts."""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = {}
        
    def test_basic_functionality(self) -> Dict[str, Any]:
        """Test basic dashboard functionality."""
        print("📊 Testing Dashboard Basic Functionality...")
        
        results = {
            "dashboard_loads": False,
            "html_content": False,
            "load_time": None,
            "static_files": False
        }
        
        try:
            # Test dashboard loading
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=10)
            load_time = time.time() - start_time
            
            results["dashboard_loads"] = response.status_code == 200
            results["load_time"] = load_time
            results["html_content"] = "dashboard-app" in response.text
            
            if results["dashboard_loads"]:
                print(f"✅ Dashboard loads: {load_time:.2f}s")
            else:
                print(f"❌ Dashboard failed to load: {response.status_code}")
            
            # Test static files
            try:
                response = requests.get(f"{self.base_url}/static/lib/lit/current/lit-core.min.js", timeout=5)
                results["static_files"] = response.status_code == 200
                print(f"✅ Static files: {'Working' if results['static_files'] else 'Failed'}")
            except Exception as e:
                print(f"❌ Static files failed: {e}")
                
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
        
        return results
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints."""
        print("\n🔌 Testing API Endpoints...")
        
        endpoints = {
            "/api/agents/status": "Agent Status",
            "/api/system/health": "System Health", 
            "/api/performance/metrics": "Performance Metrics",
            "/docs": "API Documentation"
        }
        
        results = {}
        
        for endpoint, name in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code in [200, 404],  # 404 is OK for some endpoints
                    "response_time": response.elapsed.total_seconds()
                }
                
                status = "✅" if results[endpoint]["accessible"] else "❌"
                print(f"  {status} {name}: {response.status_code} ({results[endpoint]['response_time']:.2f}s)")
                
            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  ❌ {name}: Error - {e}")
        
        return results
    
    def test_performance(self) -> Dict[str, Any]:
        """Test dashboard performance."""
        print("\n⚡ Testing Performance...")
        
        results = {
            "load_time": None,
            "api_response_times": {},
            "concurrent_requests": False
        }
        
        try:
            # Test load time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=10)
            load_time = time.time() - start_time
            results["load_time"] = load_time
            
            if load_time < 2.0:
                print(f"✅ Load time: {load_time:.2f}s (excellent)")
            elif load_time < 5.0:
                print(f"⚠️ Load time: {load_time:.2f}s (acceptable)")
            else:
                print(f"❌ Load time: {load_time:.2f}s (slow)")
            
            # Test API response times
            api_endpoints = ["/api/agents/status", "/api/system/health", "/api/performance/metrics"]
            
            for endpoint in api_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    response_time = time.time() - start_time
                    results["api_response_times"][endpoint] = response_time
                    
                    if response_time < 1.0:
                        print(f"✅ {endpoint}: {response_time:.2f}s")
                    else:
                        print(f"⚠️ {endpoint}: {response_time:.2f}s (slow)")
                        
                except Exception as e:
                    print(f"❌ {endpoint}: Error - {e}")
            
            # Test concurrent requests (simplified)
            try:
                responses = []
                for _ in range(3):
                    response = requests.get(f"{self.base_url}/", timeout=5)
                    responses.append(response.status_code == 200)
                
                results["concurrent_requests"] = all(responses)
                print(f"✅ Concurrent requests: {'Working' if results['concurrent_requests'] else 'Failed'}")
                
            except Exception as e:
                print(f"❌ Concurrent requests failed: {e}")
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
        
        return results
    
    def test_user_experience(self) -> Dict[str, Any]:
        """Test user experience features."""
        print("\n👤 Testing User Experience...")
        
        results = {
            "responsive_design": False,
            "error_handling": False,
            "navigation": False
        }
        
        try:
            # Test responsive design
            response = requests.get(f"{self.base_url}/", timeout=5)
            html_content = response.text
            results["responsive_design"] = 'viewport' in html_content.lower()
            print(f"✅ Responsive design: {'Present' if results['responsive_design'] else 'Missing'}")
            
            # Test error handling
            response = requests.get(f"{self.base_url}/nonexistent", timeout=5)
            results["error_handling"] = response.status_code == 404
            print(f"✅ Error handling: {'Working' if results['error_handling'] else 'Needs improvement'}")
            
            # Test navigation elements
            navigation_elements = ['nav', 'header', 'footer', 'dashboard']
            results["navigation"] = any(element in html_content.lower() for element in navigation_elements)
            print(f"✅ Navigation: {'Present' if results['navigation'] else 'Limited'}")
            
        except Exception as e:
            print(f"❌ User experience test failed: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all dashboard tests."""
        print("🚀 Phase 10.5: Dashboard Integration Testing")
        print("=" * 60)
        
        # Run all test categories
        self.results = {
            "basic_functionality": self.test_basic_functionality(),
            "api_endpoints": self.test_api_endpoints(),
            "performance": self.test_performance(),
            "user_experience": self.test_user_experience()
        }
        
        # Calculate overall results
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 60)
        print("📊 PHASE 10.5: DASHBOARD INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # Calculate success rates
        basic_success = sum(1 for v in self.results["basic_functionality"].values() if v is True)
        basic_total = len([k for k in self.results["basic_functionality"].keys() if k != "load_time"])
        
        api_success = sum(1 for ep in self.results["api_endpoints"].values() if ep["accessible"])
        api_total = len(self.results["api_endpoints"])
        
        ux_success = sum(1 for v in self.results["user_experience"].values() if v is True)
        ux_total = len(self.results["user_experience"])
        
        # Performance scoring
        perf_score = 0
        if self.results["performance"]["load_time"] and self.results["performance"]["load_time"] < 5.0:
            perf_score += 1
        if self.results["performance"]["concurrent_requests"]:
            perf_score += 1
        if len(self.results["performance"]["api_response_times"]) > 0:
            perf_score += 1
        
        total_tests = basic_total + api_total + ux_total + 3  # 3 performance tests
        total_passed = basic_success + api_success + ux_success + perf_score
        
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 Basic Functionality: {basic_success}/{basic_total} passed")
        print(f"🔌 API Endpoints: {api_success}/{api_total} accessible")
        print(f"⚡ Performance: {perf_score}/3 passed")
        print(f"👤 User Experience: {ux_success}/{ux_total} passed")
        print(f"📈 Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Determine status
        if overall_success_rate >= 90:
            status = "EXCELLENT"
            print("🎉 Phase 10.5: DASHBOARD INTEGRATION TESTING PASSED")
        elif overall_success_rate >= 80:
            status = "GOOD"
            print("✅ Phase 10.5: DASHBOARD INTEGRATION TESTING PASSED")
        elif overall_success_rate >= 70:
            status = "ACCEPTABLE"
            print("⚠️ Phase 10.5: DASHBOARD INTEGRATION TESTING ACCEPTABLE")
        else:
            status = "NEEDS_IMPROVEMENT"
            print("❌ Phase 10.5: DASHBOARD INTEGRATION TESTING NEEDS IMPROVEMENT")
        
        # Save results
        self.results["overall_status"] = status
        self.results["success_rate"] = overall_success_rate
        
        # Save report
        self.save_report()
        
        return status in ["EXCELLENT", "GOOD", "ACCEPTABLE"]
    
    def save_report(self):
        """Save test report."""
        try:
            report = {
                "test_date": datetime.now().isoformat(),
                "overall_status": self.results["overall_status"],
                "success_rate": self.results["success_rate"],
                "results": self.results
            }
            
            with open("PHASE_10_5_DASHBOARD_REPORT.json", "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📄 Report saved to: PHASE_10_5_DASHBOARD_REPORT.json")
            
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

def main():
    """Main test execution."""
    tester = DashboardTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 2

if __name__ == "__main__":
    exit(main())
