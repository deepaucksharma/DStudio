#\!/usr/bin/env python3
"""Convert duplicate files to redirects"""

from pathlib import Path

def convert_to_redirect(file_path: Path, redirect_to: str):
    """Convert a file to a redirect"""
    title = file_path.stem.replace('-', ' ').title()
    
    content = f"""---
title: {title}
redirect_to: /{redirect_to}/
---

# {title}

\!\!\! info "This page has moved"
    Please visit [{redirect_to}](/{redirect_to}/)

<meta http-equiv="refresh" content="0; url=/{redirect_to}/">
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Converted {file_path.name} to redirect -> {redirect_to}")

def main():
    base_dir = Path('/home/deepak/DStudio')
    
    # Map of duplicates to their canonical locations
    redirects = {
        'docs/monolith-to-microservices.md': 'excellence/migrations/monolith-to-microservices',
        'docs/performance-testing.md': 'architects-handbook/quantitative-analysis/performance-testing',
        'docs/incident-response.md': 'architects-handbook/human-factors/incident-response',
        'docs/latency-calculator.md': 'architects-handbook/tools/latency-calculator',
        'docs/human-factors.md': 'architects-handbook/human-factors',
        'docs/architects-handbook/amazon-dynamo.md': 'architects-handbook/case-studies/databases/amazon-dynamo',
        'docs/architects-handbook/netflix-chaos.md': 'architects-handbook/case-studies/elite-engineering/netflix-chaos',
        'docs/architects-handbook/google-spanner.md': 'architects-handbook/case-studies/databases/google-spanner',
        'docs/quantitative-analysis/littles-law.md': 'architects-handbook/quantitative-analysis/littles-law',
        'docs/quantitative-analysis/cap-theorem.md': 'architects-handbook/quantitative-analysis/cap-theorem',
        'docs/quantitative-analysis/capacity-planning.md': 'architects-handbook/quantitative-analysis/capacity-planning',
        'docs/quantitative-analysis/availability-math.md': 'architects-handbook/quantitative-analysis/availability-math',
        'docs/quantitative-analysis/coordination-costs.md': 'architects-handbook/quantitative-analysis/coordination-costs',
        'docs/quantitative-analysis/queueing-models.md': 'architects-handbook/quantitative-analysis/queueing-models',
        'docs/analysis/littles-law.md': 'architects-handbook/quantitative-analysis/littles-law',
        'docs/analysis/cap-theorem.md': 'architects-handbook/quantitative-analysis/cap-theorem',
        'docs/analysis/queueing-models.md': 'architects-handbook/quantitative-analysis/queueing-models',
        'docs/case-studies/amazon-dynamo.md': 'architects-handbook/case-studies/databases/amazon-dynamo',
        'docs/case-studies/netflix-chaos.md': 'architects-handbook/case-studies/elite-engineering/netflix-chaos',
        'docs/case-studies/google-spanner.md': 'architects-handbook/case-studies/databases/google-spanner',
        'docs/tools/latency-calculator.md': 'architects-handbook/tools/latency-calculator',
        'docs/tools/capacity-calculator.md': 'architects-handbook/tools/capacity-calculator',
        'docs/tools/availability-calculator.md': 'architects-handbook/tools/availability-calculator',
        'docs/tools/throughput-calculator.md': 'architects-handbook/tools/throughput-calculator',
    }
    
    converted_count = 0
    for file_path, redirect_to in redirects.items():
        full_path = base_dir / file_path
        if full_path.exists():
            convert_to_redirect(full_path, redirect_to)
            converted_count += 1
    
    print(f"\nConverted {converted_count} duplicate files to redirects")

if __name__ == '__main__':
    main()
