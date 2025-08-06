#\!/usr/bin/env python3
"""Check for duplicate or similar files to newly created ones"""

from pathlib import Path
import difflib

def find_similar_files(base_dir: Path):
    """Find files with similar names or content"""
    docs_dir = base_dir / 'docs'
    
    # Files we recently created
    new_files = [
        'docs/monolith-to-microservices.md',
        'docs/performance-testing.md',
        'docs/incident-response.md',
        'docs/latency-calculator.md',
        'docs/human-factors.md',
        'docs/architects-handbook/amazon-dynamo.md',
        'docs/architects-handbook/netflix-chaos.md',
        'docs/architects-handbook/google-spanner.md',
        'docs/quantitative-analysis/littles-law.md',
        'docs/quantitative-analysis/cap-theorem.md',
    ]
    
    duplicates = []
    
    for new_file_path in new_files:
        new_file = base_dir / new_file_path
        if not new_file.exists():
            continue
            
        # Extract base name for comparison
        new_name = new_file.stem.replace('-', '_').lower()
        
        # Search for similar files
        for md_file in docs_dir.rglob('*.md'):
            if str(md_file) == str(new_file):
                continue
                
            # Check for similar names
            existing_name = md_file.stem.replace('-', '_').lower()
            similarity = difflib.SequenceMatcher(None, new_name, existing_name).ratio()
            
            if similarity > 0.8:  # 80% similar
                rel_path = md_file.relative_to(base_dir)
                duplicates.append({
                    'new': new_file_path,
                    'existing': str(rel_path),
                    'similarity': similarity
                })
    
    return duplicates

def check_specific_patterns(base_dir: Path):
    """Check for specific pattern duplications"""
    patterns = {
        'latency-calculator': ['latency', 'calculator', 'calc'],
        'amazon-dynamo': ['dynamo', 'amazon', 'aurora'],
        'netflix-chaos': ['netflix', 'chaos', 'engineering'],
        'google-spanner': ['spanner', 'google'],
        'littles-law': ['little', 'law', 'queueing'],
        'monolith-to-microservices': ['monolith', 'microservice', 'migration'],
    }
    
    matches = []
    docs_dir = base_dir / 'docs'
    
    for pattern_key, keywords in patterns.items():
        matching_files = []
        
        for md_file in docs_dir.rglob('*.md'):
            file_path_lower = str(md_file).lower()
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword in file_path_lower:
                    rel_path = md_file.relative_to(base_dir)
                    matching_files.append(str(rel_path))
                    break
        
        if len(matching_files) > 1:
            matches.append({
                'pattern': pattern_key,
                'files': matching_files
            })
    
    return matches

def main():
    base_dir = Path('/home/deepak/DStudio')
    
    print("Checking for duplicate or similar files...\n")
    
    # Check for similar file names
    duplicates = find_similar_files(base_dir)
    
    if duplicates:
        print("Found potentially duplicate files:\n")
        for dup in duplicates:
            print(f"New file: {dup['new']}")
            print(f"Similar to: {dup['existing']}")
            print(f"Similarity: {dup['similarity']:.2%}\n")
    
    # Check for pattern matches
    pattern_matches = check_specific_patterns(base_dir)
    
    if pattern_matches:
        print("\nFound files matching similar patterns:\n")
        for match in pattern_matches:
            print(f"Pattern: {match['pattern']}")
            print("Matching files:")
            for f in match['files'][:5]:  # Show max 5 matches
                print(f"  - {f}")
            if len(match['files']) > 5:
                print(f"  ... and {len(match['files']) - 5} more")
            print()

if __name__ == '__main__':
    main()
