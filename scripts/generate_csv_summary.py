#!/usr/bin/env python3
"""
Generate CSV summary of pattern file analysis for spreadsheet use
"""

import csv
import json
from pathlib import Path
import sys

def generate_csv_summary():
    repo_root = Path("/home/deepak/DStudio")
    
    # Import the comprehensive analyzer
    sys.path.append(str(repo_root / "scripts"))
    from comprehensive_pattern_analyzer import ComprehensivePatternAnalyzer
    
    analyzer = ComprehensivePatternAnalyzer(str(repo_root))
    
    # Get quality analysis
    quality_results = analyzer.analyze_content_quality()
    
    # Get git comparison
    try:
        git_results = analyzer.get_git_size_comparison()
        git_dict = {Path(r['file_path']).name: r for r in git_results}
    except:
        git_dict = {}
    
    # Prepare CSV data
    csv_data = []
    
    for result in quality_results:
        filename = result['filename']
        git_info = git_dict.get(filename, {})
        
        csv_data.append({
            'Filename': filename,
            'Category': result['category'],
            'File_Size_Bytes': result['size_bytes'],
            'Word_Count': result['word_count'],
            'Quality_Score': result['quality_score'],
            'Quality_Rating': result['quality_rating'],
            'Sections_Found': result['sections_found'],
            'Sections_Missing': result['sections_missing'],
            'Code_Blocks': result['code_blocks'],
            'Diagrams': result['diagrams'],
            'Size_Change': git_info.get('size_diff', 0),
            'Percent_Change': git_info.get('percent_change', 0.0),
            'Git_Priority': git_info.get('priority', 'N/A'),
            'Review_Priority': 'HIGH' if result['quality_rating'] in ['POOR', 'INCOMPLETE'] else 'MEDIUM' if abs(git_info.get('size_diff', 0)) > 100 else 'LOW'
        })
    
    # Sort by review priority and quality score
    csv_data.sort(key=lambda x: (x['Review_Priority'], -x['Quality_Score']))
    
    # Write CSV
    csv_file = repo_root / "pattern_analysis_summary.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if csv_data:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
    
    print(f"CSV summary generated: {csv_file}")
    print(f"Total files: {len(csv_data)}")
    
    # Print summary stats
    high_priority = len([r for r in csv_data if r['Review_Priority'] == 'HIGH'])
    medium_priority = len([r for r in csv_data if r['Review_Priority'] == 'MEDIUM'])
    
    print(f"High priority reviews: {high_priority}")
    print(f"Medium priority reviews: {medium_priority}")
    
    return csv_file

if __name__ == "__main__":
    generate_csv_summary()