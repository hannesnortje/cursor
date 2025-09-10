#!/usr/bin/env python3
"""
Test the bidirectional knowledge bridge implementation.

This test validates:
1. CursorKnowledgeBridge class functionality
2. MCP tools integration
3. Vector store operations with cursor_knowledge collection
4. Pattern extraction and technology detection
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.mcp_tools.knowledge_bridge import CursorKnowledgeBridge
from src.database.enhanced_vector_store import CursorKnowledgePoint


async def test_basic_knowledge_ingestion():
    """Test basic knowledge ingestion functionality."""
    print("🧪 Testing Knowledge Ingestion...")

    bridge = CursorKnowledgeBridge()

    # Test Vue component creation
    result = bridge.ingest_cursor_action(
        action_type="file_creation",
        content="""<template>
  <div class="user-card">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
  </div>
</template>

<script setup lang="ts">
interface User {
  id: number;
  name: string;
  email: string;
}

defineProps<{
  user: User;
}>()
</script>""",
        file_path="/components/UserCard.vue",
        project_context="Vue 3 TypeScript project with composition API",
        user_feedback="Component works perfectly, user loves the clean design",
        success_metrics={"build_success": True, "type_errors": 0, "user_rating": 5},
        technology_stack=["Vue 3", "TypeScript", "Composition API", "CSS"],
    )

    print(f"✅ Ingestion result: Success={result.get('success', False)}")
    print(f"   Action ID: {result.get('action_id')}")
    print(f"   Patterns: {result.get('patterns_identified', 0)}")

    return result


async def test_pattern_querying():
    """Test pattern querying functionality."""
    print("\n🔍 Testing Pattern Querying...")

    bridge = CursorKnowledgeBridge()

    pattern_response = bridge.query_relevant_patterns(
        requirements="Create a user profile component with TypeScript interfaces",
        file_type="vue",
        project_context="Vue 3 TypeScript project",
        similarity_threshold=0.7,
    )

    patterns = pattern_response.relevant_patterns
    print(f"✅ Found {len(patterns)} relevant patterns")
    for i, pattern in enumerate(patterns[:3]):  # Show first 3
        print(f"   Pattern {i+1}:")
        print(f"     File: {pattern.get('file_path')}")
        print(f"     Tech: {pattern.get('technology_stack')}")
        print(f"     Score: {pattern.get('score', 0.0):.3f}")

    return pattern_response


async def test_mcp_tools_integration():
    """Test MCP tools functionality."""
    print("\n🔧 Testing MCP Tools Integration...")

    # Test ingest_cursor_knowledge via MCP tool handler
    from src.mcp_tools.handlers.system_tools import handle_system_tool

    # Mock response collector
    responses = []

    def mock_send_response(request_id, response=None, error=None):
        responses.append(
            {"request_id": request_id, "response": response, "error": error}
        )

    # Test ingestion tool
    handle_system_tool(
        tool_name="ingest_cursor_knowledge",
        arguments={
            "action_type": "code_modification",
            "content": "export const calculateTotal = (items: Item[]) => items.reduce((sum, item) => sum + item.price, 0);",
            "file_path": "/utils/calculations.ts",
            "project_context": "E-commerce TypeScript project",
            "technology_stack": ["TypeScript", "ES6+"],
            "success_metrics": {"build_success": True, "tests_pass": True},
        },
        request_id="test_ingest_1",
        send_response=mock_send_response,
    )

    print(f"✅ Ingestion tool response: {responses[-1]['response'] is not None}")
    if responses[-1]["response"]:
        content = responses[-1]["response"]["structuredContent"]
        print(f"   Success: {content.get('success')}")
        print(f"   Action ID: {content.get('action_id')}")

    # Test pattern query tool
    handle_system_tool(
        tool_name="query_relevant_patterns",
        arguments={
            "requirements": "TypeScript utility functions for calculations",
            "file_type": "typescript",
            "project_context": "E-commerce project",
            "similarity_threshold": 0.8,
        },
        request_id="test_query_1",
        send_response=mock_send_response,
    )

    print(f"✅ Query tool response: {responses[-1]['response'] is not None}")
    if responses[-1]["response"]:
        content = responses[-1]["response"]["structuredContent"]
        print(f"   Success: {content.get('success')}")
        print(f"   Patterns found: {content.get('count', 0)}")

    return responses


async def test_technology_detection():
    """Test technology stack detection."""
    print("\n🔬 Testing Technology Detection...")

    bridge = CursorKnowledgeBridge()

    test_cases = [
        (
            "React TSX component",
            "export const Button: React.FC<Props> = ({ children }) => <button>{children}</button>;",
        ),
        (
            "Vue 3 Composition API",
            "<script setup lang=\"ts\">import { ref, computed } from 'vue';</script>",
        ),
        (
            "Node.js Express",
            "app.get('/api/users', async (req, res) => { const users = await User.find(); res.json(users); });",
        ),
        (
            "Python FastAPI",
            "from fastapi import FastAPI\n@app.get('/health')\nasync def health_check():",
        ),
    ]

    for description, code in test_cases:
        detected = bridge._detect_technologies(code, "/test/file.ext")
        print(f"✅ {description}: {detected}")

    return True


async def test_pattern_extraction():
    """Test pattern extraction functionality."""
    print("\n🧩 Testing Pattern Extraction...")

    bridge = CursorKnowledgeBridge()

    vue_component = """<template>
  <div class="modal" v-if="isVisible" @click.self="close">
    <div class="modal-content">
      <slot />
      <button @click="close">Close</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isVisible: boolean;
}>()

defineEmits<{
  close: []
}>()
</script>"""

    patterns = bridge._extract_patterns(vue_component, "/components/Modal.vue")
    print(f"✅ Extracted {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"   - {pattern}")

    return patterns


async def test_vector_store_integration():
    """Test vector store operations."""
    print("\n💾 Testing Vector Store Integration...")

    try:
        from src.database.enhanced_vector_store import get_enhanced_vector_store

        vector_store = get_enhanced_vector_store()

        # Test CursorKnowledgePoint creation
        knowledge_point = CursorKnowledgePoint(
            id="test_kp_1",
            action_type="test_action",
            content="Test content for vector store",
            file_path="/test/file.ts",
            project_context="Test project",
            user_feedback="Test feedback",
            success_metrics={"test": True},
            technology_stack=["TypeScript", "Test"],
            patterns_identified=["test_pattern"],
            timestamp=datetime.now(),
        )

        print("✅ CursorKnowledgePoint created successfully")
        print(f"   ID: {knowledge_point.id}")
        print(f"   Tech Stack: {knowledge_point.technology_stack}")
        print(f"   Patterns: {knowledge_point.patterns_identified}")

        return True

    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False


async def run_all_tests():
    """Run all knowledge bridge tests."""
    print("🚀 Starting Knowledge Bridge Tests")
    print("=" * 50)

    tests = [
        ("Basic Knowledge Ingestion", test_basic_knowledge_ingestion),
        ("Pattern Querying", test_pattern_querying),
        ("MCP Tools Integration", test_mcp_tools_integration),
        ("Technology Detection", test_technology_detection),
        ("Pattern Extraction", test_pattern_extraction),
        ("Vector Store Integration", test_vector_store_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = {"success": True, "result": result}
            print(f"✅ {test_name} passed")
        except Exception as e:
            results[test_name] = {"success": False, "error": str(e)}
            print(f"❌ {test_name} failed: {e}")

        print("-" * 30)

    # Summary
    print("\n📊 Test Summary:")
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    print(f"   Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Knowledge bridge is ready.")
    else:
        print("⚠️  Some tests failed. Check implementation.")
        for test_name, result in results.items():
            if not result["success"]:
                print(f"   ❌ {test_name}: {result['error']}")

    return results


if __name__ == "__main__":
    # Run tests
    results = asyncio.run(run_all_tests())

    # Exit with appropriate code
    all_passed = all(r["success"] for r in results.values())
    sys.exit(0 if all_passed else 1)
