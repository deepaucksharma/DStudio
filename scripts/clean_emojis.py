#!/usr/bin/env python3
"""
Script to clean emoji usage from markdown files
"""
import os
import re
import glob

# Common emoji patterns to remove from headers and lists
EMOJI_PATTERNS = [
    r'[🎯📊🏆🔍📈📋🚨🔧📝💡🎮⚡🌟📌🧭🎪🏗️🎨🔮🎭🎪🔥🚀💰🎖️🎨🧠⚙️🛡️📡🎚️🔬🧪🔄⚖️🎯🎲🎹🔊📈🔍🔧💼🌐🎬📱💻🖥️📊📋🗂️📁🌟⭐🔥💥✨🎆🎇🌈🦄🎁🎉🎊🥳🥇🥈🥉🏅💬⚡🚀⏱️🪜📐⏰🎛️⚙️🔧🎯📝💻🌍⚙️🔧]',
    r'[⚖️🎯🧠💰⏳🌪️🤯⛓️🔍📊🏆📈📋🚨🔧]',
    r'[🟢🟡🔴]',  # Color indicators
]

def clean_emojis_from_file(file_path):
    """Clean emojis from a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Clean headers (lines starting with #)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip cleaning certain special sections like mermaid diagrams
            if 'mermaid' in line or '```' in line:
                cleaned_lines.append(line)
                continue
                
            # Clean headers
            if line.strip().startswith('#'):
                for pattern in EMOJI_PATTERNS:
                    line = re.sub(pattern, '', line)
                # Clean up extra spaces
                line = re.sub(r'\s+', ' ', line).strip()
                # Fix header format
                if line.startswith('#'):
                    line = re.sub(r'^(#+)\s*', r'\1 ', line)
            
            # Clean list items with emoji bullets
            elif line.strip().startswith('-') and any(re.search(pattern, line) for pattern in EMOJI_PATTERNS):
                for pattern in EMOJI_PATTERNS:
                    line = re.sub(pattern, '', line)
                # Clean up extra spaces but preserve list indentation
                indent = len(line) - len(line.lstrip())
                line = line.lstrip()
                line = re.sub(r'\s+', ' ', line).strip()
                line = ' ' * indent + line
            
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Only write if content changed
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Cleaned: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to clean all markdown files"""
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        print("docs directory not found")
        return
    
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        # Skip backup files
        if '.bak' in root:
            continue
        for file in files:
            if file.endswith('.md') and not file.endswith('.bak'):
                md_files.append(os.path.join(root, file))
    
    print(f"Found {len(md_files)} markdown files to process")
    
    cleaned_count = 0
    for file_path in md_files:
        if clean_emojis_from_file(file_path):
            cleaned_count += 1
    
    print(f"Cleaned {cleaned_count} files")

if __name__ == "__main__":
    main()