#!/usr/bin/env python3
"""
Comprehensive validation of knowledge graph against deployed website URLs
"""

import sqlite3
from pathlib import Path
import json

def validate_knowledge_graph(db_path="knowledge_graph_ultimate.db"):
    """Validate our knowledge graph against deployed URLs"""
    
    # The FULL list of deployed URLs from the website
    deployed_urls = [
        # Root
        "https://deepaucksharma.github.io/DStudio/",
        
        # Top-level docs
        "https://deepaucksharma.github.io/DStudio/CALCULATOR_VALIDATION_TESTING_PLAN/",
        "https://deepaucksharma.github.io/DStudio/COMPREHENSIVE_FIX_IMPLEMENTATION_PLAN/",
        
        # Main sections
        "https://deepaucksharma.github.io/DStudio/architects-handbook/",
        "https://deepaucksharma.github.io/DStudio/company-specific/",
        "https://deepaucksharma.github.io/DStudio/core-principles/",
        "https://deepaucksharma.github.io/DStudio/human-factors/",
        "https://deepaucksharma.github.io/DStudio/implementation-playbooks/",
        "https://deepaucksharma.github.io/DStudio/incident-response/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/",
        "https://deepaucksharma.github.io/DStudio/latency-calculator/",
        "https://deepaucksharma.github.io/DStudio/migrations/",
        "https://deepaucksharma.github.io/DStudio/monolith-to-microservices/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/",
        "https://deepaucksharma.github.io/DStudio/patterns/",
        "https://deepaucksharma.github.io/DStudio/performance-testing/",
        "https://deepaucksharma.github.io/DStudio/progress/",
        "https://deepaucksharma.github.io/DStudio/quantitative-analysis/",
        "https://deepaucksharma.github.io/DStudio/reference/",
        "https://deepaucksharma.github.io/DStudio/start-here/",
        
        # Analysis section
        "https://deepaucksharma.github.io/DStudio/analysis/cap-theorem/",
        "https://deepaucksharma.github.io/DStudio/analysis/littles-law/",
        "https://deepaucksharma.github.io/DStudio/analysis/queueing-models/",
        
        # Architects handbook subsections
        "https://deepaucksharma.github.io/DStudio/architects-handbook/QUALITY_ASSURANCE_STRATEGY/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/QUALITY_IMPLEMENTATION_GUIDE/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/amazon-dynamo/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/apache-spark/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/chat-system/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/consistent-hashing/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/google-spanner/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/human-factors/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/implementation-playbooks/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/netflix-chaos/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/",
        
        # Tools
        "https://deepaucksharma.github.io/DStudio/tools/availability-calculator/",
        "https://deepaucksharma.github.io/DStudio/tools/capacity-calculator/",
        "https://deepaucksharma.github.io/DStudio/tools/latency-calculator/",
        "https://deepaucksharma.github.io/DStudio/tools/throughput-calculator/",
        
        # Patterns subsections
        "https://deepaucksharma.github.io/DStudio/patterns/resilience/",
        "https://deepaucksharma.github.io/DStudio/patterns/scaling/",
        "https://deepaucksharma.github.io/DStudio/patterns/security/",
        
        # Pattern library examples
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/circuit-breaker/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/saga/",
        
        # Core principles examples
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/asynchronous-reality/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/correlated-failure/",
        
        # Interview prep subsections
        "https://deepaucksharma.github.io/DStudio/interview-prep/coding-interviews/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/",
        
        # Company specific
        "https://deepaucksharma.github.io/DStudio/company-specific/amazon/",
        "https://deepaucksharma.github.io/DStudio/company-specific/apple/",
        "https://deepaucksharma.github.io/DStudio/company-specific/google/",
        "https://deepaucksharma.github.io/DStudio/company-specific/meta/",
        "https://deepaucksharma.github.io/DStudio/company-specific/microsoft/",
        "https://deepaucksharma.github.io/DStudio/company-specific/netflix/",
        
        # More architect handbook pages
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/amazon-aurora/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/amazon-dynamo/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/cassandra/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/etcd/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/google-spanner/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/key-value-store/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/memcached/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/mongodb/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/redis-architecture/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/vault/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/databases/zookeeper/",
        
        # Elite engineering case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/elite-engineering/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/elite-engineering/figma-crdt-collaboration/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/elite-engineering/netflix-chaos-engineering/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/elite-engineering/netflix-chaos/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/elite-engineering/stripe-api-excellence/",
        
        # Financial/commerce case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/ad-click-aggregation/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/ecommerce-platform/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/hotel-reservation/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/payment-system/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/paypal-payments/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/shopify-flash-sales/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/financial-commerce/stock-exchange/",
        
        # Gaming case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/gaming/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/gaming/global-matchmaking/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/gaming/mmo-game-architecture/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/gaming/real-time-game-sync/",
        
        # Healthcare case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/healthcare/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/healthcare/medical-imaging-pipeline/",
        
        # Infrastructure case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/blockchain/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/consistent-hashing/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/kubernetes/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/monolith-to-microservices/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/object-storage/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/s3-object-storage-enhanced/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/unique-id-generator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/url-shortener/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/web-crawler/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/infrastructure/zoom-scaling/",
        
        # Location services case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/apple-maps/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/find-my-device/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/google-maps/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/here-maps/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/life360/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/nearby-friends/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/openstreetmap/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/proximity-service/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/snap-map/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/strava-heatmaps/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/uber-location/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/location-services/uber-maps/",
        
        # Logistics case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/logistics/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/logistics/real-time-package-tracking/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/logistics/route-optimization/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/logistics/warehouse-automation/",
        
        # Messaging/streaming case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/apache-spark/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/batch-to-streaming/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/distributed-message-queue/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/kafka/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/mapreduce/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/netflix-streaming/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/messaging-streaming/polling-to-event-driven/",
        
        # Monitoring/observability case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/monitoring-observability/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/monitoring-observability/metrics-monitoring/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/monitoring-observability/prometheus/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/monitoring-observability/rate-limiter/",
        
        # Search/analytics case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/elasticsearch/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/gaming-leaderboard-enhanced/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/google-drive/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/google-search-infrastructure/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/google-search/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/search-autocomplete/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/search-analytics/spotify-recommendations/",
        
        # Social/communication case studies
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/chat-system/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/consistency-deep-dive-chat/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/news-feed/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/notification-system/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/slack-infrastructure/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/social-graph/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/social-media-feed/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/twitter-timeline/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/video-streaming/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/case-studies/social-communication/youtube/",
        
        # Human factors
        "https://deepaucksharma.github.io/DStudio/architects-handbook/human-factors/blameless-postmortems/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/human-factors/knowledge-management/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/human-factors/sre-practices/",
        
        # Learning paths
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/architect/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/blockchain-systems/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/cloud-migration-architect/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/consistency/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/cost/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/data-engineer/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/data-platform-architect/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/devops-sre/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/edge-computing/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/manager/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/microservices-architect/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/ml-infrastructure/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/new-graduate/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/performance-engineer/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/performance/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/platform-engineer/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/quantum-resilient/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/real-time-systems/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/reliability/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/security-architect/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/learning-paths/senior-engineer/",
        
        # Quantitative analysis
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/availability-math/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/availability/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/backpressure-math/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/battery-models/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/bayesian-reasoning/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/blast-radius/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/cap-theorem-enhanced/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/cap-theorem/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/capacity-planning/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/collision-probability/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/comp-geometry/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/compression/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/computational-geometry/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/computer-vision/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/consistency-models/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/failure-models/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/graph-models/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/graph-theory/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/haversine/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/information-theory/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/latency-ladder/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/latency-numbers/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/littles-law/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/markov-chains/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/mtbf-mttr/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/network-model/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/network-theory/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/performance-modeling/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/performance-testing/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/power-laws/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/privacy-metrics/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/probabilistic-structures/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/queueing-models/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/queueing-theory/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/queuing-networks/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/reliability-engineering/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/reliability-theory/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/social-networks/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/space-complexity/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/spatial-stats/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/stochastic-processes/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/storage-economics/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/storage-engines/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/time-complexity/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/quantitative-analysis/time-series/",
        
        # Tools
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/availability-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/cache-hierarchy-optimizer/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/capacity-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/consistency-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/cost-optimizer/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/database-sharding-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/geo-distribution-planner/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/latency-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/load-balancer-simulator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/observability-cost-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/rate-limiting-calculator/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/tools/throughput-calculator/",
        
        # Pattern library - architecture
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/ambassador/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/anti-corruption-layer/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/cap-theorem/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/cell-based/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/choreography/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/container-orchestration/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/event-driven/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/event-streaming/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/gitops-deployment/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/graphql-federation/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/kappa-architecture/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/serverless-faas/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/shared-nothing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/sidecar/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/strangler-fig/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/architecture/valet-key/",
        
        # Pattern library - communication
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/api-gateway/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/grpc/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/request-reply/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/service-discovery/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/service-mesh/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/service-registry/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/communication/websocket/",
        
        # Pattern library - coordination
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/actor-model/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/cas/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/clock-sync/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/consensus/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/distributed-lock/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/distributed-queue/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/emergent-leader/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/generation-clock/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/hlc/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/leader-election/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/leader-follower/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/logical-clocks/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/low-high-water-marks/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/state-watch/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/two-phase-commit/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/coordination/vector-clocks/",
        
        # Pattern library - cost optimization
        "https://deepaucksharma.github.io/DStudio/pattern-library/cost-optimization/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/cost-optimization/finops/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/cost-optimization/resource-rightsizing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/cost-optimization/spot-instance-management/",
        
        # Pattern library - data management
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/bloom-filter/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/cdc/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/consistent-hashing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/cqrs/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/crdt/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/data-lake/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/data-lakehouse/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/data-mesh/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/deduplication/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/delta-sync/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/distributed-storage/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/double-entry-ledger/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/event-sourcing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/eventual-consistency/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/idempotency/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/materialized-view/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/merkle-trees/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/outbox/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/polyglot-persistence/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/read-repair/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/saga/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/segmented-log/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/shared-database/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/spatial-indexing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/stream-processing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/data-management/write-ahead-log/",
        
        # Pattern library - deployment
        "https://deepaucksharma.github.io/DStudio/pattern-library/deployment/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/deployment/blue-green-deployment/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/deployment/canary-release/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/deployment/feature-flags/",
        
        # Pattern library - ML infrastructure
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/distributed-training/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/feature-store/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/ml-pipeline-orchestration/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/model-serving-scale/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/ml-infrastructure/model-versioning-rollback/",
        
        # Pattern library - resilience
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/bulkhead/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/circuit-breaker-transformed/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/circuit-breaker/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/failover/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/fault-tolerance/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/graceful-degradation/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/health-check/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/heartbeat/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/load-shedding/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/retry-backoff/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/split-brain/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/resilience/timeout/",
        
        # Pattern library - scaling
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/analytics-scale/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/auto-scaling/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/backpressure/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/caching-strategies/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/edge-computing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/geo-distribution/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/geo-replication/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/load-balancing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/queues-streaming/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/rate-limiting/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/request-batching/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/scatter-gather/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/serverless-event-processing/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/sharding/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/scaling/tile-caching/",
        
        # Pattern library - security
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/api-security-gateway/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/consent-management/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/location-privacy/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/secrets-management/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/security-scanning-pipeline/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/threat-modeling/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/zero-trust-architecture/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/security/zero-trust-security/",
        
        # Core principles - laws
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/asynchronous-reality/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/cognitive-load/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/correlated-failure/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/distributed-knowledge/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/economic-reality/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/emergent-chaos/",
        "https://deepaucksharma.github.io/DStudio/core-principles/laws/multidimensional-optimization/",
        
        # Core principles - pillars
        "https://deepaucksharma.github.io/DStudio/core-principles/pillars/",
        "https://deepaucksharma.github.io/DStudio/core-principles/pillars/control-distribution/",
        "https://deepaucksharma.github.io/DStudio/core-principles/pillars/state-distribution/",
        "https://deepaucksharma.github.io/DStudio/core-principles/pillars/truth-distribution/",
        "https://deepaucksharma.github.io/DStudio/core-principles/pillars/work-distribution/",
        
        # Excellence
        "https://deepaucksharma.github.io/DStudio/excellence/",
        "https://deepaucksharma.github.io/DStudio/excellence/framework-overview/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/data-consistency/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/migration-strategies/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/modern-distributed-systems-2025/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/operational-excellence/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/performance-optimization/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/platform-engineering-playbook/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/quick-start-guide/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/resilience-first/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/security-patterns/",
        "https://deepaucksharma.github.io/DStudio/excellence/implementation-guides/service-communication/",
        
        # Excellence - migrations
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/2pc-to-saga/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/anti-entropy-to-crdt/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/batch-to-streaming/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/gossip-to-service-mesh/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/master-slave-to-multi-primary/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/monolith-to-microservices/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/polling-to-websocket/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/shared-database-to-microservices/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/thick-client-to-api-first/",
        "https://deepaucksharma.github.io/DStudio/excellence/migrations/vector-clocks-to-hlc/",
        
        # Excellence - pattern discovery
        "https://deepaucksharma.github.io/DStudio/excellence/pattern-discovery/",
        "https://deepaucksharma.github.io/DStudio/excellence/pattern-discovery/bronze-patterns/",
        "https://deepaucksharma.github.io/DStudio/excellence/pattern-discovery/gold-patterns/",
        "https://deepaucksharma.github.io/DStudio/excellence/pattern-discovery/silver-patterns/",
        
        # Interview prep details
        "https://deepaucksharma.github.io/DStudio/interview-prep/coding-interviews/algorithm-patterns/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/coding-interviews/interview-tips/",
        
        # Engineering leadership
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/framework-index/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/hard-earned-wisdom/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/decision-making/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/human-behavior/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/integrity-ethics/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/systems-thinking/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-1-first-principles/value-creation/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-2-core-business/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-2-core-business/leadership/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-2-core-business/operations/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-2-core-business/risk-governance/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-2-core-business/strategy/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/business-acumen/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/business-acumen/business-metrics/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/organizational-design/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/organizational-design/team-topologies/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/people-management/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/people-management/hiring-interviewing/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/people-management/team-building-culture/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/technical-leadership/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-3-applications/technical-leadership/technical-strategy/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/behavioral/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/culture-values/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/system-org-design/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/technical-leadership/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/decision-trees/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/interview-timer/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/question-bank/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/self-assessment/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/interactive/star-matcher/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/principle-hooks/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/level-4-interview-execution/tools/star-framework/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/navigation-guide/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/practice-scenarios/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/practice-scenarios/stakeholder-negotiation-scenario/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/practice-scenarios/team-conflict-scenario/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/engineering-leadership/practice-scenarios/underperformer-scenario/",
        
        # IC interviews
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/behavioral/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/behavioral/by-level/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/behavioral/scenarios/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/cheatsheets/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/cheatsheets/system-design-checklist/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/cicd-pipeline/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/cloud-storage/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/collaborative-editor/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/iot-platform/",
        "https://deepaucksharma.github.io/DStudio/interview-prep/ic-interviews/common-problems/ml-serving/",
        
        # Reference
        "https://deepaucksharma.github.io/DStudio/reference/admonition-guide/",
        "https://deepaucksharma.github.io/DStudio/reference/code-example-framework/",
        "https://deepaucksharma.github.io/DStudio/reference/contributing/",
        "https://deepaucksharma.github.io/DStudio/reference/glossary/",
        "https://deepaucksharma.github.io/DStudio/reference/law-mapping-guide/",
        "https://deepaucksharma.github.io/DStudio/reference/navigation-maintenance/",
        "https://deepaucksharma.github.io/DStudio/reference/offline/",
        "https://deepaucksharma.github.io/DStudio/reference/pattern-health-dashboard/",
        "https://deepaucksharma.github.io/DStudio/reference/pattern-template/",
        "https://deepaucksharma.github.io/DStudio/reference/recipe-cards/",
        "https://deepaucksharma.github.io/DStudio/reference/tags/",
        "https://deepaucksharma.github.io/DStudio/reference/visual-design-standards/",
        "https://deepaucksharma.github.io/DStudio/reference/visual-implementation-guide/",
        
        # Templates
        "https://deepaucksharma.github.io/DStudio/architects-handbook/templates/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/templates/case-study-template/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/templates/progressive-disclosure-example/",
        "https://deepaucksharma.github.io/DStudio/architects-handbook/templates/structured-learning-path-example/",
        
        # Pattern library - observability
        "https://deepaucksharma.github.io/DStudio/pattern-library/observability/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/pattern-implementation-roadmap/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/pattern-migration-guides/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/pattern-template-v2/",
        
        # Pattern library - visual assets
        "https://deepaucksharma.github.io/DStudio/pattern-library/visual-assets/",
        "https://deepaucksharma.github.io/DStudio/pattern-library/visual-assets/RENDERING_INSTRUCTIONS/",
    ]
    
    # Extract path from URL (remove base URL and trailing slash)
    base_url = "https://deepaucksharma.github.io/DStudio/"
    deployed_page_ids = set()
    
    for url in deployed_urls:
        if url.startswith(base_url):
            path = url[len(base_url):].rstrip('/')
            if path:  # Skip empty (root)
                # Convert to page_id format (URLs ending with / map to /index)
                deployed_page_ids.add(path)
                # Also add /index version for directory URLs
                if not path.endswith('.html'):
                    deployed_page_ids.add(f"{path}/index")
            else:
                deployed_page_ids.add("index")
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH VALIDATION")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all pages from our knowledge graph
    cursor.execute("SELECT page_id FROM pages")
    kb_pages = set(row['page_id'] for row in cursor.fetchall())
    
    print(f"\nDeployed pages (from sitemap): {len(deployed_page_ids)}")
    print(f"Knowledge graph pages: {len(kb_pages)}")
    
    # Find pages that are deployed but not in our KB
    deployed_not_in_kb = deployed_page_ids - kb_pages
    if deployed_not_in_kb:
        print(f"\n⚠️  Pages deployed but NOT in knowledge graph ({len(deployed_not_in_kb)}):") 
        for page in sorted(deployed_not_in_kb)[:20]:
            print(f"   - {page}")
            # Check if it's a patterns redirect
            if page.startswith('patterns/'):
                pattern_lib_equivalent = page.replace('patterns/', 'pattern-library/')
                if pattern_lib_equivalent in kb_pages:
                    print(f"     → Likely redirect to {pattern_lib_equivalent}")
    
    # Find pages in KB but not deployed
    kb_not_deployed = kb_pages - deployed_page_ids
    if kb_not_deployed:
        print(f"\n⚠️  Pages in KB but NOT deployed ({len(kb_not_deployed)}):")
        for page in sorted(kb_not_deployed)[:20]:
            print(f"   - {page}")
    
    # Analyze broken links vs deployed pages
    print("\n" + "=" * 60)
    print("BROKEN LINK VALIDATION")
    print("=" * 60)
    
    # Check how many "broken" links are actually valid deployed URLs
    cursor.execute("""
        SELECT DISTINCT dst_page, COUNT(*) as count
        FROM links
        WHERE is_valid = 0 AND is_external = 0
        GROUP BY dst_page
        ORDER BY count DESC
    """)
    
    false_broken = []
    truly_broken = []
    
    for row in cursor.fetchall():
        dst_page = row['dst_page']
        if dst_page:
            # Check if this page is deployed
            if dst_page in deployed_page_ids or f"{dst_page}/index" in deployed_page_ids:
                false_broken.append((dst_page, row['count']))
            else:
                truly_broken.append((dst_page, row['count']))
    
    if false_broken:
        print(f"\n❌ Links marked as broken but page EXISTS on deployed site ({len(false_broken)} unique destinations):")
        for page, count in false_broken[:10]:
            print(f"  {count:3} links to {page}")
    
    if truly_broken:
        print(f"\n✅ Links correctly marked as broken ({len(truly_broken)} unique destinations):")
        for page, count in truly_broken[:10]:
            print(f"  {count:3} links to {page}")
    
    # Pattern analysis
    print("\n" + "=" * 60)
    print("URL PATTERN INSIGHTS")
    print("=" * 60)
    
    # Analyze patterns/ vs pattern-library/
    patterns_redirects = [p for p in deployed_page_ids if p.startswith('patterns/')]
    pattern_lib_pages = [p for p in kb_pages if p.startswith('pattern-library/')]
    
    print(f"\nDuplicate structure detected:")
    print(f"  - 'patterns/' paths in deployment: {len(patterns_redirects)}")
    print(f"  - 'pattern-library/' paths in KB: {len(pattern_lib_pages)}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    stats = {
        'deployed': len(deployed_page_ids),
        'kb': len(kb_pages),
        'missing_from_kb': len(deployed_not_in_kb),
        'missing_from_deployment': len(kb_not_deployed),
        'false_broken': len(false_broken),
        'truly_broken': len(truly_broken)
    }
    
    print(f"Deployed pages: {stats['deployed']}")
    print(f"Knowledge graph pages: {stats['kb']}")
    print(f"Missing from KB: {stats['missing_from_kb']}")
    print(f"Not deployed: {stats['missing_from_deployment']}")
    print(f"False broken links: {stats['false_broken']} unique destinations")
    print(f"Truly broken links: {stats['truly_broken']} unique destinations")
    
    # Fix false broken links
    if false_broken:
        print("\n" + "=" * 60)
        print("FIXING FALSE BROKEN LINKS")
        print("=" * 60)
        
        fixed_count = 0
        for dst_page, count in false_broken:
            cursor.execute("""
                UPDATE links
                SET is_valid = 1
                WHERE dst_page = ? AND is_external = 0 AND is_valid = 0
            """, (dst_page,))
            fixed_count += cursor.rowcount
            print(f"  Fixed {cursor.rowcount} links to {dst_page}")
        
        conn.commit()
        print(f"\nTotal links fixed: {fixed_count}")
    
    conn.close()
    return stats

if __name__ == "__main__":
    import os
    os.chdir("/home/deepak/DStudio/scripts/knowledge-graph")
    stats = validate_knowledge_graph()