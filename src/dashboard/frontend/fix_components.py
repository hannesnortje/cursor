#!/usr/bin/env python3
"""
Script to fix component files by removing error handling and fixing structure
"""

import os
import re

def fix_component_file(filepath):
    """Fix a component file by removing error handling and fixing structure"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove everything after the last closing brace of the class
    # Find the last static styles closing brace and everything after it
    lines = content.split('\n')
    fixed_lines = []
    
    in_styles = False
    brace_count = 0
    found_class_end = False
    
    for i, line in enumerate(lines):
        if 'static styles' in line:
            in_styles = True
            fixed_lines.append(line)
        elif in_styles and line.strip() == '`;':
            fixed_lines.append(line)
            in_styles = False
        elif in_styles:
            fixed_lines.append(line)
        elif not in_styles and line.strip() == '}' and not found_class_end:
            fixed_lines.append(line)
            found_class_end = True
        elif found_class_end and line.strip() == '':
            fixed_lines.append(line)
        elif found_class_end and 'customElements.define(' in line:
            fixed_lines.append(line)
            break
        elif not found_class_end:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Fixed {filepath}")

def main():
    """Fix all component files"""
    components_dir = "components"
    
    if not os.path.exists(components_dir):
        print(f"Directory {components_dir} not found")
        return
    
    component_files = [
        "dashboard-footer.ts", 
        "system-health-card.ts",
        "performance-card.ts",
        "quick-actions-card.ts"
    ]
    
    for filename in component_files:
        filepath = os.path.join(components_dir, filename)
        if os.path.exists(filepath):
            fix_component_file(filepath)
        else:
            print(f"⚠️  File {filepath} not found")
    
    print("🎉 All component files fixed!")

if __name__ == "__main__":
    main()
