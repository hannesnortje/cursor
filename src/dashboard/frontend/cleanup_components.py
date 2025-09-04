#!/usr/bin/env python3
"""
Script to clean up component files by removing getLit().then() error handling
"""

import os
import re

def clean_component_file(filepath):
    """Clean up a component file by removing error handling code"""
    print(f"Cleaning {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove the error handling pattern
    # Look for the pattern: }).catch(error => { ... });
    pattern = r'}\s*\)\.catch\(error\s*=>\s*\{[^}]*\}\s*\);\s*$'
    content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Also remove any remaining error handling blocks
    pattern2 = r'// Create a fallback component.*?customElements\.define\([^)]+\);\s*$'
    content = re.sub(pattern2, '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Clean up any duplicate customElements.define calls
    lines = content.split('\n')
    cleaned_lines = []
    seen_define = False
    
    for line in lines:
        if 'customElements.define(' in line and not seen_define:
            cleaned_lines.append(line)
            seen_define = True
        elif 'customElements.define(' in line and seen_define:
            # Skip duplicate defines
            continue
        else:
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Write back the cleaned content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Cleaned {filepath}")

def main():
    """Clean all component files"""
    components_dir = "components"
    
    if not os.path.exists(components_dir):
        print(f"Directory {components_dir} not found")
        return
    
    component_files = [
        "dashboard-header.ts",
        "dashboard-footer.ts", 
        "system-health-card.ts",
        "performance-card.ts",
        "quick-actions-card.ts"
    ]
    
    for filename in component_files:
        filepath = os.path.join(components_dir, filename)
        if os.path.exists(filepath):
            clean_component_file(filepath)
        else:
            print(f"⚠️  File {filepath} not found")
    
    print("🎉 All component files cleaned!")

if __name__ == "__main__":
    main()
