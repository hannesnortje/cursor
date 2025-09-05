#!/usr/bin/env python3
"""Comprehensive test suite for Phase 9.4: Predetermined Knowledge Bases."""

import json
import time
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase9_4_knowledge_bases():
    """Test Phase 9.4 predetermined knowledge bases functionality."""
    print("🧠 Phase 9.4: Predetermined Knowledge Bases - Comprehensive Testing")
    print("=" * 70)
    
    test_results = {
        "phase": "9.4",
        "name": "Predetermined Knowledge Bases",
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "success_rate": 0.0
        }
    }
    
    def run_test(test_name, test_func):
        """Run a single test and record results."""
        print(f"\n🔍 Testing: {test_name}")
        test_results["summary"]["total"] += 1
        
        try:
            result = test_func()
            if result["success"]:
                print(f"✅ PASSED: {result['message']}")
                test_results["summary"]["passed"] += 1
                test_results["tests"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "message": result["message"],
                    "details": result.get("details", {})
                })
            else:
                print(f"❌ FAILED: {result['message']}")
                test_results["summary"]["failed"] += 1
                test_results["tests"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "message": result["message"],
                    "error": result.get("error", "Unknown error")
                })
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            test_results["summary"]["failed"] += 1
            test_results["tests"].append({
                "name": test_name,
                "status": "ERROR",
                "message": f"Test execution failed: {str(e)}",
                "error": str(e)
            })
    
    # Test 1: Knowledge Base Initialization
    def test_knowledge_base_initialization():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            domains = knowledge_base.get_available_domains()
            expected_domains = ["pdca", "agile", "code_quality", "security", "testing", "documentation"]
            
            if set(domains) == set(expected_domains):
                return {
                    "success": True,
                    "message": f"Knowledge base initialized with {len(domains)} domains: {domains}",
                    "details": {"domains": domains}
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected domains {expected_domains}, got {domains}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to initialize knowledge base: {str(e)}"}
    
    # Test 2: PDCA Knowledge Content
    def test_pdca_knowledge():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            pdca_items = knowledge_base.get_knowledge_for_domain("pdca")
            
            if len(pdca_items) >= 5:  # Should have at least 5 PDCA items
                # Check for key PDCA concepts
                titles = [item.title for item in pdca_items]
                expected_concepts = ["PDCA Framework Overview", "Plan Phase", "Do Phase", "Check Phase", "Act Phase"]
                
                found_concepts = sum(1 for concept in expected_concepts if any(concept in title for title in titles))
                
                return {
                    "success": found_concepts >= 4,
                    "message": f"PDCA knowledge contains {len(pdca_items)} items, found {found_concepts}/5 key concepts",
                    "details": {"item_count": len(pdca_items), "titles": titles}
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected at least 5 PDCA items, got {len(pdca_items)}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test PDCA knowledge: {str(e)}"}
    
    # Test 3: Agile Knowledge Content
    def test_agile_knowledge():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            agile_items = knowledge_base.get_knowledge_for_domain("agile")
            
            if len(agile_items) >= 5:  # Should have at least 5 Agile items
                # Check for key Agile concepts
                titles = [item.title for item in agile_items]
                expected_concepts = ["Agile Manifesto", "Scrum Framework", "User Story", "Sprint Planning", "Retrospective"]
                
                found_concepts = sum(1 for concept in expected_concepts if any(concept in title for title in titles))
                
                return {
                    "success": found_concepts >= 4,
                    "message": f"Agile knowledge contains {len(agile_items)} items, found {found_concepts}/5 key concepts",
                    "details": {"item_count": len(agile_items), "titles": titles}
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected at least 5 Agile items, got {len(agile_items)}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test Agile knowledge: {str(e)}"}
    
    # Test 4: Knowledge Search Functionality
    def test_knowledge_search():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            # Search for "PDCA" across all domains
            all_knowledge = knowledge_base.get_all_knowledge()
            search_results = []
            
            for domain, items in all_knowledge.items():
                for item in items:
                    if "pdca" in item.title.lower() or "pdca" in item.content.lower():
                        search_results.append(item.title)
            
            if len(search_results) >= 1:  # Should find at least one PDCA reference
                return {
                    "success": True,
                    "message": f"Knowledge search found {len(search_results)} PDCA-related items",
                    "details": {"search_results": search_results}
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected at least 1 PDCA search result, got {len(search_results)}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test knowledge search: {str(e)}"}
    
    # Test 5: Knowledge Statistics
    def test_knowledge_statistics():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            all_knowledge = knowledge_base.get_all_knowledge()
            total_items = sum(len(items) for items in all_knowledge.values())
            
            # Check if we have a reasonable number of knowledge items
            if total_items >= 20:  # Should have at least 20 total items
                # Check category distribution
                categories = {}
                priorities = {}
                
                for items in all_knowledge.values():
                    for item in items:
                        categories[item.category] = categories.get(item.category, 0) + 1
                        priorities[item.priority] = priorities.get(item.priority, 0) + 1
                
                return {
                    "success": True,
                    "message": f"Knowledge base contains {total_items} items across {len(categories)} categories",
                    "details": {
                        "total_items": total_items,
                        "categories": categories,
                        "priorities": priorities
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected at least 20 total knowledge items, got {total_items}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test knowledge statistics: {str(e)}"}
    
    # Test 6: MCP Tools Integration
    def test_mcp_tools_integration():
        try:
            from src.mcp_tools.phase9_4_tools import get_available_knowledge_domains
            
            # Test getting available domains using synchronous wrapper
            result = get_available_knowledge_domains()
            
            if result["success"] and len(result["domains"]) >= 6:
                return {
                    "success": True,
                    "message": f"MCP tools integration working, found {len(result['domains'])} domains",
                    "details": {"domains": result["domains"]}
                }
            else:
                return {
                    "success": False,
                    "message": f"MCP tools integration failed: {result.get('message', 'Unknown error')}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test MCP tools integration: {str(e)}"}
    
    # Test 7: Knowledge Item Structure
    def test_knowledge_item_structure():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            # Get a sample item from any domain
            all_knowledge = knowledge_base.get_all_knowledge()
            sample_item = None
            
            for items in all_knowledge.values():
                if items:
                    sample_item = items[0]
                    break
            
            if sample_item:
                # Check required attributes
                required_attrs = ["title", "content", "category", "subcategory", "tags", "priority", "source", "version", "last_updated"]
                missing_attrs = [attr for attr in required_attrs if not hasattr(sample_item, attr)]
                
                if not missing_attrs:
                    return {
                        "success": True,
                        "message": f"Knowledge item structure is valid with all required attributes",
                        "details": {
                            "title": sample_item.title,
                            "category": sample_item.category,
                            "priority": sample_item.priority,
                            "tags_count": len(sample_item.tags)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Knowledge item missing attributes: {missing_attrs}"
                    }
            else:
                return {
                    "success": False,
                    "message": "No knowledge items found to test structure"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test knowledge item structure: {str(e)}"}
    
    # Test 8: Cross-Domain Knowledge Coverage
    def test_cross_domain_coverage():
        try:
            from src.knowledge.predetermined_knowledge import get_predetermined_knowledge
            knowledge_base = get_predetermined_knowledge()
            
            all_knowledge = knowledge_base.get_all_knowledge()
            expected_domains = ["pdca", "agile", "code_quality", "security", "testing", "documentation"]
            
            coverage_results = {}
            for domain in expected_domains:
                if domain in all_knowledge:
                    items = all_knowledge[domain]
                    coverage_results[domain] = {
                        "count": len(items),
                        "has_content": len(items) > 0,
                        "categories": list(set(item.category for item in items))
                    }
                else:
                    coverage_results[domain] = {"count": 0, "has_content": False, "categories": []}
            
            domains_with_content = sum(1 for result in coverage_results.values() if result["has_content"])
            
            if domains_with_content >= 5:  # At least 5 domains should have content
                return {
                    "success": True,
                    "message": f"Cross-domain coverage: {domains_with_content}/6 domains have content",
                    "details": coverage_results
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected at least 5 domains with content, got {domains_with_content}"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to test cross-domain coverage: {str(e)}"}
    
    # Run all tests
    run_test("Knowledge Base Initialization", test_knowledge_base_initialization)
    run_test("PDCA Knowledge Content", test_pdca_knowledge)
    run_test("Agile Knowledge Content", test_agile_knowledge)
    run_test("Knowledge Search Functionality", test_knowledge_search)
    run_test("Knowledge Statistics", test_knowledge_statistics)
    run_test("MCP Tools Integration", test_mcp_tools_integration)
    run_test("Knowledge Item Structure", test_knowledge_item_structure)
    run_test("Cross-Domain Knowledge Coverage", test_cross_domain_coverage)
    
    # Calculate success rate
    test_results["summary"]["success_rate"] = (
        test_results["summary"]["passed"] / test_results["summary"]["total"] * 100
        if test_results["summary"]["total"] > 0 else 0
    )
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Phase 9.4 Test Results Summary")
    print("=" * 70)
    print(f"Total Tests: {test_results['summary']['total']}")
    print(f"Passed: {test_results['summary']['passed']}")
    print(f"Failed: {test_results['summary']['failed']}")
    print(f"Success Rate: {test_results['summary']['success_rate']:.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"phase9_4_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Test results saved to: {filename}")
    
    # Overall assessment
    if test_results["summary"]["success_rate"] >= 90:
        print("\n🎉 Phase 9.4 Status: EXCELLENT - Production Ready!")
    elif test_results["summary"]["success_rate"] >= 80:
        print("\n✅ Phase 9.4 Status: GOOD - Minor issues to address")
    elif test_results["summary"]["success_rate"] >= 70:
        print("\n⚠️ Phase 9.4 Status: FAIR - Some issues need attention")
    else:
        print("\n❌ Phase 9.4 Status: POOR - Major issues need fixing")
    
    return test_results

if __name__ == "__main__":
    test_phase9_4_knowledge_bases()
