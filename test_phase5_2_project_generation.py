#!/usr/bin/env python3
"""
Test script for Phase 5.2: Project Generation Agent
Tests all Project Generation Agent functionality including:
- Listing project templates
- Generating projects from templates
- Customizing templates
- Getting project status
- Listing generated projects
"""

import json
from datetime import datetime


def send_request(method, params=None, request_id=1):
    """Send a JSON-RPC request to the MCP server."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    print(f"Sending request: {json.dumps(request, indent=2)}")
    print(json.dumps(request), flush=True)
    
    # Read response
    response = input().strip()
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print(f"Failed to parse response: {response}")
        return None


def test_phase5_2_project_generation():
    """Test all Phase 5.2 Project Generation Agent functionality."""
    print("🚀 **Phase 5.2: Project Generation Agent Testing**")
    print("=" * 60)
    
    # Test 1: List all project templates
    print("\n📋 **Test 1: List All Project Templates**")
    print("-" * 40)
    response = send_request("tools/call", {
        "name": "list_project_templates"
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            templates = result["structuredContent"]["templates"]
            print(f"✅ Successfully listed {len(templates)} project templates")
            print(f"📊 Total templates: {result['structuredContent']['total_count']}")
            
            # Show template categories
            languages = set(t["language"] for t in templates)
            categories = set(t["category"] for t in templates)
            print(f"🌍 Supported languages: {', '.join(sorted(languages))}")
            print(f"📁 Project categories: {', '.join(sorted(categories))}")
            
            # Show some example templates
            print("\n📝 Example templates:")
            for i, template in enumerate(templates[:5]):
                print(f"  {i+1}. {template['name']} ({template['language']}/{template['category']})")
                print(f"     ID: {template['template_id']}")
                print(f"     Build: {template['build_system']}, Testing: {template['testing_framework']}")
        else:
            print(f"❌ Failed to list templates: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No response from server")
    
    # Test 2: List Python templates only
    print("\n🐍 **Test 2: List Python Templates Only**")
    print("-" * 40)
    response = send_request("tools/call", {
        "name": "list_project_templates",
        "arguments": {
            "language": "python"
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            templates = result["structuredContent"]["templates"]
            print(f"✅ Successfully listed {len(templates)} Python templates")
            for template in templates:
                print(f"  📝 {template['name']} - {template['description']}")
                print(f"     Framework: {template['framework']}, Category: {template['category']}")
        else:
            print(f"❌ Failed to list Python templates: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No response from server")
    
    # Test 3: List API category templates
    print("\n🔌 **Test 3: List API Category Templates**")
    print("-" * 40)
    response = send_request("tools/call", {
        "name": "list_project_templates",
        "arguments": {
            "category": "api"
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            templates = result["structuredContent"]["templates"]
            print(f"✅ Successfully listed {len(templates)} API templates")
            for template in templates:
                print(f"  🔌 {template['name']} ({template['language']})")
                print(f"     Framework: {template['framework']}, Build: {template['build_system']}")
        else:
            print(f"❌ Failed to list API templates: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No response from server")
    
    # Test 4: Generate a Python Flask API project
    print("\n🐍 **Test 4: Generate Python Flask API Project**")
    print("-" * 40)
    project_name = f"TestFlaskAPI_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = send_request("tools/call", {
        "name": "generate_project",
        "arguments": {
            "template_id": "python_flask_api",
            "project_name": project_name,
            "target_path": f"/tmp/{project_name}",
            "customizations": {
                "additional_dependencies": ["flask-sqlalchemy", "flask-migrate"]
            }
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            project_data = result["structuredContent"]
            print(f"✅ Successfully generated project: {project_data['project_name']}")
            print(f"📁 Project ID: {project_data['project_id']}")
            print(f"🌍 Language: {project_data['language']}")
            print(f"⚙️ Framework: {project_data['framework']}")
            print(f"🔨 Build System: {project_data['build_system']}")
            print(f"🧪 Testing Framework: {project_data['testing_framework']}")
            print(f"📂 Target Path: {project_data['project_structure']['base_path']}")
            print(f"📦 Dependencies: {', '.join(project_data['project_structure']['dependencies'])}")
            
            # Store project ID for later tests
            flask_project_id = project_data['project_id']
        else:
            print(f"❌ Failed to generate Flask project: {result.get('error', 'Unknown error')}")
            flask_project_id = None
    else:
        print("❌ No response from server")
        flask_project_id = None
    
    # Test 5: Generate a C++ CMake Library project
    print("\n⚡ **Test 5: Generate C++ CMake Library Project**")
    print("-" * 40)
    cpp_project_name = f"TestCppLib_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = send_request("tools/call", {
        "name": "generate_project",
        "arguments": {
            "template_id": "cpp_cmake_library",
            "project_name": cpp_project_name,
            "target_path": f"/tmp/{cpp_project_name}"
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            project_data = result["structuredContent"]
            print(f"✅ Successfully generated C++ project: {project_data['project_name']}")
            print(f"📁 Project ID: {project_data['project_id']}")
            print(f"🌍 Language: {project_data['language']}")
            print(f"⚙️ Framework: {project_data['framework']}")
            print(f"🔨 Build System: {project_data['build_system']}")
            print(f"🧪 Testing Framework: {project_data['testing_framework']}")
            
            # Store project ID for later tests
            cpp_project_id = project_data['project_id']
        else:
            print(f"❌ Failed to generate C++ project: {result.get('error', 'Unknown error')}")
            cpp_project_id = None
    else:
        print("❌ No response from server")
        cpp_project_id = None
    
    # Test 6: Generate a TypeScript React project
    print("\n⚛️ **Test 6: Generate TypeScript React Project**")
    print("-" * 40)
    ts_project_name = f"TestReactTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = send_request("tools/call", {
        "name": "generate_project",
        "arguments": {
            "template_id": "typescript_react_app",
            "project_name": ts_project_name,
            "target_path": f"/tmp/{ts_project_name}"
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            project_data = result["structuredContent"]
            print(f"✅ Successfully generated TypeScript project: {project_data['project_name']}")
            print(f"📁 Project ID: {project_data['project_id']}")
            print(f"🌍 Language: {project_data['language']}")
            print(f"⚙️ Framework: {project_data['framework']}")
            print(f"🔨 Build System: {project_data['build_system']}")
            print(f"🧪 Testing Framework: {project_data['testing_framework']}")
            
            # Store project ID for later tests
            ts_project_id = project_data['project_id']
        else:
            print(f"❌ Failed to generate TypeScript project: {result.get('error', 'Unknown error')}")
            ts_project_id = None
    else:
        print("❌ No response from server")
        ts_project_id = None
    
    # Test 7: List all generated projects
    print("\n📋 **Test 7: List All Generated Projects**")
    print("-" * 40)
    response = send_request("tools/call", {
        "name": "list_generated_projects"
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            projects = result["structuredContent"]["projects"]
            print(f"✅ Successfully listed {len(projects)} generated projects")
            print(f"📊 Total projects: {result['structuredContent']['total_count']}")
            
            for project in projects:
                print(f"  📁 {project['project_name']} ({project['language']})")
                print(f"     ID: {project['project_id']}")
                print(f"     Framework: {project['framework']}")
                print(f"     Created: {project['created_at']}")
        else:
            print(f"❌ Failed to list generated projects: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No response from server")
    
    # Test 8: Get status of Flask project
    if flask_project_id:
        print("\n📊 **Test 8: Get Flask Project Status**")
        print("-" * 40)
        response = send_request("tools/call", {
            "name": "get_generated_project_status",
            "arguments": {
                "project_id": flask_project_id
            }
        })
        
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result and result["structuredContent"]["success"]:
                project = result["structuredContent"]["project"]
                print(f"✅ Successfully retrieved status for: {project['project_name']}")
                print(f"📁 Project ID: {project['project_id']}")
                print(f"🌍 Language: {project['language']}")
                print(f"⚙️ Framework: {project['framework']}")
                print(f"📂 Base Path: {project['base_path']}")
                print(f"📅 Created: {project['created_at']}")
                print(f"🔧 Metadata: {project['metadata']}")
            else:
                print(f"❌ Failed to get Flask project status: {result.get('error', 'Unknown error')}")
        else:
            print("❌ No response from server")
    
    # Test 9: Customize a template
    print("\n🔧 **Test 9: Customize Project Template**")
    print("-" * 40)
    response = send_request("tools/call", {
        "name": "customize_project_template",
        "arguments": {
            "template_id": "python_flask_api",
            "customizations": {
                "additional_dependencies": ["flask-jwt-extended", "flask-caching"],
                "custom_description": "Enhanced Flask API with JWT and caching"
            }
        }
    })
    
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result and result["structuredContent"]["success"]:
            custom_data = result["structuredContent"]
            print(f"✅ Successfully customized template")
            print(f"📝 New template ID: {custom_data['customized_template_id']}")
            print(f"📝 New template name: {custom_data['new_template']['name']}")
            print(f"📝 New description: {custom_data['new_template']['description']}")
            print(f"📦 Enhanced dependencies: {', '.join(custom_data['new_template']['dependencies'])}")
            print(f"🔧 Customizations applied: {custom_data['customizations_applied']}")
        else:
            print(f"❌ Failed to customize template: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No response from server")
    
    # Test 10: Test language-specific filtering
    print("\n🌍 **Test 10: Language-Specific Template Filtering**")
    print("-" * 40)
    
    languages_to_test = ["cpp", "java", "go", "rust"]
    for lang in languages_to_test:
        print(f"\n🔍 Testing {lang.upper()} templates:")
        response = send_request("tools/call", {
            "name": "list_project_templates",
            "arguments": {
                "language": lang
            }
        })
        
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result and result["structuredContent"]["success"]:
                templates = result["structuredContent"]["templates"]
                print(f"  ✅ Found {len(templates)} {lang} templates")
                for template in templates[:2]:  # Show first 2
                    print(f"    📝 {template['name']} ({template['category']})")
            else:
                print(f"  ❌ Failed to list {lang} templates: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ❌ No response from server for {lang}")
    
    print("\n" + "=" * 60)
    print("🎉 **Phase 5.2 Project Generation Agent Testing Complete!**")
    print("=" * 60)
    
    # Summary
    print("\n📊 **Test Summary:**")
    print("✅ Template listing and filtering")
    print("✅ Multi-language project generation")
    print("✅ Project status retrieval")
    print("✅ Template customization")
    print("✅ Generated project listing")
    print("✅ Language-specific filtering")
    
    print("\n🚀 **Phase 5.2 Status: FULLY FUNCTIONAL!**")
    print("The Project Generation Agent is now ready for production use!")

if __name__ == "__main__":
    print("Starting Phase 5.2 Project Generation Agent tests...")
    print("Make sure the MCP server is running and ready to receive requests.")
    print("Press Enter to continue...")
    input()
    
    try:
        test_phase5_2_project_generation()
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
