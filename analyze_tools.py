#!/usr/bin/env python3
"""Analyze MCP tools in protocol_server.py to identify duplicates and optimization opportunities."""

import re
import json
from collections import defaultdict

def extract_tools_from_file():
    """Extract all tool definitions from protocol_server.py"""
    with open('protocol_server.py', 'r') as f:
        content = f.read()
    
    # Find the tools list section
    tools_section_match = re.search(r'"tools":\s*\[(.*?)\]', content, re.DOTALL)
    if not tools_section_match:
        print("Could not find tools section")
        return []
    
    tools_section = tools_section_match.group(1)
    
    # Extract individual tool definitions
    tool_pattern = r'\{\s*"name":\s*"([^"]+)"[^}]*\}'
    tools = re.findall(tool_pattern, tools_section)
    
    return tools

def categorize_tools(tools):
    """Categorize tools by functionality"""
    categories = {
        'Basic': [],
        'Project Management': [],
        'Communication': [],
        'Agile/Scrum': [],
        'Project Generation': [],
        'Backend Development': [],
        'LLM Integration': [],
        'Instance Management': [],
        'Qdrant/Database': [],
        'AutoGen': [],
        'Advanced Communication': [],
        'Knowledge Management': [],
        'Coordinator': [],
        'Dashboard': []
    }
    
    # Categorize each tool
    for tool in tools:
        if tool in ['add_numbers', 'reverse_text']:
            categories['Basic'].append(tool)
        elif 'project' in tool.lower() and 'coordinator' not in tool.lower():
            if 'agile' in tool.lower() or 'sprint' in tool.lower() or 'user_story' in tool.lower():
                categories['Agile/Scrum'].append(tool)
            elif 'generate' in tool.lower() or 'template' in tool.lower():
                categories['Project Generation'].append(tool)
            else:
                categories['Project Management'].append(tool)
        elif 'communication' in tool.lower() or 'chat' in tool.lower() or 'message' in tool.lower():
            if 'advanced' in tool.lower() or 'priority' in tool.lower() or 'compression' in tool.lower():
                categories['Advanced Communication'].append(tool)
            else:
                categories['Communication'].append(tool)
        elif 'coordinator' in tool.lower():
            categories['Coordinator'].append(tool)
        elif 'llm' in tool.lower() or 'model' in tool.lower():
            categories['LLM Integration'].append(tool)
        elif 'qdrant' in tool.lower() or 'database' in tool.lower() or 'backup' in tool.lower():
            categories['Qdrant/Database'].append(tool)
        elif 'autogen' in tool.lower():
            categories['AutoGen'].append(tool)
        elif 'knowledge' in tool.lower() or 'search' in tool.lower():
            categories['Knowledge Management'].append(tool)
        elif 'dashboard' in tool.lower() or 'browser' in tool.lower():
            categories['Dashboard'].append(tool)
        elif 'api' in tool.lower() or 'backend' in tool.lower() or 'security' in tool.lower():
            categories['Backend Development'].append(tool)
        elif 'instance' in tool.lower() or 'registry' in tool.lower():
            categories['Instance Management'].append(tool)
        else:
            categories['Project Management'].append(tool)
    
    return categories

def find_duplicates(tools):
    """Find duplicate tools"""
    tool_counts = defaultdict(int)
    for tool in tools:
        tool_counts[tool] += 1
    
    duplicates = {tool: count for tool, count in tool_counts.items() if count > 1}
    return duplicates

def analyze_tool_consolidation():
    """Analyze potential tool consolidation opportunities"""
    consolidation_opportunities = {
        'Status/Health Tools': [
            'get_communication_status',
            'get_communication_health', 
            'get_qdrant_status',
            'get_dashboard_status',
            'get_all_dashboards_status',
            'get_browser_status',
            'get_registry_status',
            'get_instance_info'
        ],
        'Project List/Status Tools': [
            'list_project_databases',
            'list_generated_projects',
            'list_autogen_agents',
            'list_autogen_group_chats',
            'get_project_status',
            'get_generated_project_status'
        ],
        'Knowledge Search Tools': [
            'search_knowledge',
            'search_project_knowledge',
            'search_cross_chat_messages'
        ],
        'Template/Generation Tools': [
            'list_project_templates',
            'coordinator_list_project_templates',
            'generate_project',
            'coordinator_create_project_from_template',
            'create_custom_project',
            'coordinator_create_custom_project'
        ],
        'Communication Tools': [
            'start_communication_system',
            'start_advanced_communication',
            'create_cross_chat_session',
            'broadcast_cross_chat_message'
        ]
    }
    
    return consolidation_opportunities

def main():
    print("🔍 MCP Tools Analysis Report")
    print("=" * 50)
    
    # Extract tools
    tools = extract_tools_from_file()
    print(f"Total Tools Found: {len(tools)}")
    print()
    
    # Find duplicates
    duplicates = find_duplicates(tools)
    if duplicates:
        print("🚨 DUPLICATE TOOLS FOUND:")
        for tool, count in duplicates.items():
            print(f"  - {tool}: {count} occurrences")
        print()
    
    # Categorize tools
    categories = categorize_tools(tools)
    print("📊 TOOLS BY CATEGORY:")
    total_categorized = 0
    for category, tool_list in categories.items():
        if tool_list:
            print(f"  {category}: {len(tool_list)} tools")
            for tool in tool_list:
                print(f"    - {tool}")
            total_categorized += len(tool_list)
            print()
    
    print(f"Total Categorized: {total_categorized}")
    print(f"Uncategorized: {len(tools) - total_categorized}")
    print()
    
    # Analyze consolidation opportunities
    consolidation = analyze_tool_consolidation()
    print("🔄 CONSOLIDATION OPPORTUNITIES:")
    potential_savings = 0
    for group_name, tool_group in consolidation.items():
        if len(tool_group) > 1:
            print(f"  {group_name}: {len(tool_group)} tools")
            for tool in tool_group:
                print(f"    - {tool}")
            potential_savings += len(tool_group) - 1  # Can consolidate to 1 tool
            print()
    
    print(f"Potential Tools Reduction: {potential_savings}")
    print(f"Target Tools After Consolidation: {len(tools) - potential_savings}")
    print()
    
    # Specific recommendations
    print("💡 SPECIFIC RECOMMENDATIONS:")
    print()
    
    print("1. CONSOLIDATE STATUS TOOLS (Save 7 tools):")
    print("   - Create single 'get_system_status' tool with type parameter")
    print("   - Replace: get_communication_status, get_communication_health, get_qdrant_status,")
    print("     get_dashboard_status, get_all_dashboards_status, get_browser_status, get_registry_status")
    print()
    
    print("2. CONSOLIDATE PROJECT LIST TOOLS (Save 4 tools):")
    print("   - Create single 'list_resources' tool with resource_type parameter")
    print("   - Replace: list_project_databases, list_generated_projects, list_autogen_agents, list_autogen_group_chats")
    print()
    
    print("3. CONSOLIDATE SEARCH TOOLS (Save 2 tools):")
    print("   - Create single 'search_content' tool with content_type parameter")
    print("   - Replace: search_knowledge, search_project_knowledge")
    print()
    
    print("4. CONSOLIDATE TEMPLATE TOOLS (Save 4 tools):")
    print("   - Create single 'manage_templates' tool with action parameter")
    print("   - Replace: list_project_templates, coordinator_list_project_templates,")
    print("     generate_project, coordinator_create_project_from_template")
    print()
    
    print("5. CONSOLIDATE COMMUNICATION TOOLS (Save 2 tools):")
    print("   - Create single 'manage_communication' tool with action parameter")
    print("   - Replace: start_communication_system, start_advanced_communication")
    print()
    
    print("6. REMOVE REDUNDANT COORDINATOR TOOLS (Save 6 tools):")
    print("   - Remove coordinator_* versions of existing tools")
    print("   - Use direct tools instead of coordinator wrappers")
    print()
    
    total_recommended_savings = 7 + 4 + 2 + 4 + 2 + 6
    final_tool_count = len(tools) - total_recommended_savings
    
    print(f"🎯 FINAL RECOMMENDATIONS:")
    print(f"   Current Tools: {len(tools)}")
    print(f"   Recommended Reduction: {total_recommended_savings}")
    print(f"   Final Tool Count: {final_tool_count}")
    print(f"   Target Achieved: {'✅ YES' if final_tool_count <= 80 else '❌ NO'}")
    
    if final_tool_count > 80:
        additional_needed = final_tool_count - 80
        print(f"   Additional Reduction Needed: {additional_needed} tools")
        print()
        print("7. ADDITIONAL REDUCTIONS NEEDED:")
        print("   - Remove low-priority tools from each category")
        print("   - Combine similar functionality tools")
        print("   - Remove experimental or rarely-used tools")

if __name__ == "__main__":
    main()
