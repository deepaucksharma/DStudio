#\!/usr/bin/env python3
"""Create comprehensive redirect map for all moved content"""

from pathlib import Path

def create_redirect_file(base_dir: Path, from_path: str, to_path: str):
    """Create a redirect file"""
    file_path = base_dir / 'docs' / from_path
    
    if file_path.exists():
        return False
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract title from path
    title = from_path.split('/')[-1].replace('.md', '').replace('-', ' ').title()
    
    content = f"""---
title: {title} - Redirect
redirect_to: /{to_path}/
---

# {title}

\!\!\! info "This page has moved"
    Please visit [{to_path}](/{to_path}/)

<meta http-equiv="refresh" content="0; url=/{to_path}/">
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    base_dir = Path('/home/deepak/DStudio')
    
    # Comprehensive redirect map based on 404 patterns
    redirects = [
        # Pattern library redirects
        ('pattern-library/index.md', 'pattern-library'),
        ('pattern-library/resilience/index.md', 'pattern-library/resilience'),
        ('pattern-library/scaling/index.md', 'pattern-library/scaling'),
        ('pattern-library/data-management/index.md', 'pattern-library/data-management'),
        ('pattern-library/architecture/index.md', 'pattern-library/architecture'),
        ('pattern-library/communication/index.md', 'pattern-library/communication'),
        ('pattern-library/coordination/index.md', 'pattern-library/coordination'),
        ('pattern-library/security/index.md', 'pattern-library/security'),
        
        # Core principles pattern redirects
        ('core-principles/patterns/bulkhead.md', 'pattern-library/resilience/bulkhead'),
        ('core-principles/patterns/circuit-breaker.md', 'pattern-library/resilience/circuit-breaker-transformed'),
        ('core-principles/patterns/load-balancing.md', 'pattern-library/scaling/load-balancing'),
        ('core-principles/patterns/sharding.md', 'pattern-library/scaling/sharding'),
        ('core-principles/patterns/multi-region.md', 'pattern-library/scaling/geo-distribution'),
        ('core-principles/patterns/retry-backoff.md', 'pattern-library/resilience/retry-backoff'),
        ('core-principles/patterns/backpressure.md', 'pattern-library/scaling/backpressure'),
        ('core-principles/patterns/rate-limiting.md', 'pattern-library/scaling/rate-limiting'),
        ('core-principles/patterns/auto-scaling.md', 'pattern-library/scaling/auto-scaling'),
        ('core-principles/patterns/cap-theorem.md', 'pattern-library/architecture/cap-theorem'),
        ('core-principles/patterns/caching-strategies.md', 'pattern-library/scaling/caching-strategies'),
        ('core-principles/patterns/edge-computing.md', 'pattern-library/scaling/edge-computing'),
        
        # Implementation playbook redirects
        ('architects-handbook/implementation-playbooks/index.md', 'architects-handbook/implementation-playbooks'),
        ('implementation-playbooks/index.md', 'architects-handbook/implementation-playbooks'),
        ('implementation-playbooks/migration-checklist/index.md', 'architects-handbook/implementation-playbooks/migration-checklist'),
        ('implementation-playbooks/monolith-to-microservices/index.md', 'architects-handbook/implementation-playbooks/monolith-to-microservices'),
        ('implementation-playbooks/performance-testing/index.md', 'architects-handbook/implementation-playbooks/performance-testing'),
        ('implementation-playbooks/incident-response/index.md', 'architects-handbook/implementation-playbooks/incident-response'),
        ('implementation-playbooks/security-audit/index.md', 'architects-handbook/implementation-playbooks/security-audit'),
        ('implementation-playbooks/compliance-checklist/index.md', 'architects-handbook/implementation-playbooks/compliance-checklist'),
        
        # Excellence migration redirects
        ('excellence/migrations/index.md', 'excellence/migrations'),
        ('migrations/index.md', 'excellence/migrations'),
        ('migrations/2pc-to-saga.md', 'excellence/migrations/2pc-to-saga'),
        ('migrations/batch-to-streaming.md', 'excellence/migrations/batch-to-streaming'),
        ('migrations/monolith-to-microservices.md', 'excellence/migrations/monolith-to-microservices'),
        ('migrations/polling-to-websocket.md', 'excellence/migrations/polling-to-websocket'),
        ('migrations/shared-database-to-microservices.md', 'excellence/migrations/shared-database-to-microservices'),
        ('migrations/thick-client-to-api-first.md', 'excellence/migrations/thick-client-to-api-first'),
        ('migrations/vector-clocks-to-hlc.md', 'excellence/migrations/vector-clocks-to-hlc'),
        
        # Case study redirects
        ('case-studies/amazon-dynamo.md', 'architects-handbook/case-studies/databases/amazon-dynamo'),
        ('case-studies/netflix-chaos.md', 'architects-handbook/case-studies/elite-engineering/netflix-chaos'),
        ('case-studies/google-spanner.md', 'architects-handbook/case-studies/databases/google-spanner'),
        ('case-studies/uber-ringpop.md', 'architects-handbook/case-studies/location-services/uber-ringpop'),
        ('case-studies/linkedin-kafka.md', 'architects-handbook/case-studies/messaging-streaming/linkedin-kafka'),
        
        # Tool redirects
        ('tools/latency-calculator.md', 'architects-handbook/tools/latency-calculator'),
        ('tools/capacity-calculator.md', 'architects-handbook/tools/capacity-calculator'),
        ('tools/availability-calculator.md', 'architects-handbook/tools/availability-calculator'),
        ('tools/throughput-calculator.md', 'architects-handbook/tools/throughput-calculator'),
        
        # Quantitative analysis redirects
        ('quantitative-analysis/index.md', 'architects-handbook/quantitative-analysis'),
        ('analysis/littles-law.md', 'architects-handbook/quantitative-analysis/littles-law'),
        ('analysis/cap-theorem.md', 'architects-handbook/quantitative-analysis/cap-theorem'),
        ('analysis/queueing-models.md', 'architects-handbook/quantitative-analysis/queueing-models'),
    ]
    
    created_count = 0
    skipped_count = 0
    
    for from_path, to_path in redirects:
        if create_redirect_file(base_dir, from_path, to_path):
            print(f"Created redirect: {from_path} -> {to_path}")
            created_count += 1
        else:
            skipped_count += 1
    
    print(f"\nRedirect Summary:")
    print(f"Created: {created_count}")
    print(f"Skipped (already exist): {skipped_count}")

if __name__ == '__main__':
    main()
