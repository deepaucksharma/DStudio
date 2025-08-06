-- Automated fixes for path mismatches
BEGIN TRANSACTION;


UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/behavioral/by-level', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/index' 
  AND dst_page = 'interview-prep/interview-prep/ic-interviews/behavioral/by-level';

UPDATE links 
SET dst_page = 'architects-handbook/quantitative-analysis/latency-numbers', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/cheatsheets/index' 
  AND dst_page = 'interview-prep/architects-handbook/quantitative-analysis/latency-numbers';

UPDATE links 
SET dst_page = 'interview-prep/engineering-leadership/framework-index', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/cheatsheets/system-design-checklist/index' 
  AND dst_page = 'interview-prep/ic-interviews/engineering-leadership/framework-index';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/cloud-storage', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/cloud-storage';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/collaborative-editor';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/cicd-pipeline';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/iot-platform', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/iot-platform';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/ml-serving', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/ml-serving';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/cloud-storage', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/cloud-storage';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/collaborative-editor';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/cicd-pipeline';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/iot-platform', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/iot-platform';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/common-problems/ml-serving', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/common-problems/ml-serving';

UPDATE links 
SET dst_page = 'interview-prep/ic-interviews/cheatsheets/system-design-checklist', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/index' 
  AND dst_page = 'interview-prep/ic-interviews/ic-interviews/cheatsheets/system-design-checklist';

UPDATE links 
SET dst_page = 'pattern-library/data-management/event-sourcing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/data-management/event-sourcing';

UPDATE links 
SET dst_page = 'pattern-library/data-management/materialized-view', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/data-management/materialized-view';

UPDATE links 
SET dst_page = 'pattern-library/resilience/circuit-breaker', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/resilience/circuit-breaker';

UPDATE links 
SET dst_page = 'pattern-library/scaling/load-balancing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/scaling/load-balancing';

UPDATE links 
SET dst_page = 'pattern-library/communication/api-gateway', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/communication/api-gateway';

UPDATE links 
SET dst_page = 'pattern-library/scaling/caching-strategies', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/scaling/caching-strategies';

UPDATE links 
SET dst_page = 'pattern-library/data-management/event-sourcing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/data-management/event-sourcing';

UPDATE links 
SET dst_page = 'pattern-library/resilience/bulkhead', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/ml-serving' 
  AND dst_page = 'interview-prep/pattern-library/resilience/bulkhead';

UPDATE links 
SET dst_page = 'pattern-library/data-management/event-sourcing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/data-management/event-sourcing';

UPDATE links 
SET dst_page = 'pattern-library/architecture/event-streaming', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/architecture/event-streaming';

UPDATE links 
SET dst_page = 'pattern-library/data-management/lsm-tree', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/data-management/lsm-tree';

UPDATE links 
SET dst_page = 'pattern-library/coordination/distributed-queue', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/coordination/distributed-queue';

UPDATE links 
SET dst_page = 'pattern-library/communication/api-gateway', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/communication/api-gateway';

UPDATE links 
SET dst_page = 'pattern-library/resilience/circuit-breaker', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/resilience/circuit-breaker';

UPDATE links 
SET dst_page = 'pattern-library/scaling/sharding', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/scaling/sharding';

UPDATE links 
SET dst_page = 'pattern-library/scaling/load-balancing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/iot-platform' 
  AND dst_page = 'interview-prep/pattern-library/scaling/load-balancing';

UPDATE links 
SET dst_page = 'pattern-library/architecture/event-driven', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/architecture/event-driven';

UPDATE links 
SET dst_page = 'pattern-library/coordination/distributed-queue', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/coordination/distributed-queue';

UPDATE links 
SET dst_page = 'pattern-library/resilience/circuit-breaker', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/resilience/circuit-breaker';

UPDATE links 
SET dst_page = 'pattern-library/resilience/bulkhead', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/resilience/bulkhead';

UPDATE links 
SET dst_page = 'pattern-library/data-management/saga', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/data-management/saga';

UPDATE links 
SET dst_page = 'pattern-library/scaling/sharding', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/scaling/sharding';

UPDATE links 
SET dst_page = 'pattern-library/scaling/caching-strategies', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cicd-pipeline' 
  AND dst_page = 'interview-prep/pattern-library/scaling/caching-strategies';

UPDATE links 
SET dst_page = 'pattern-library/data-management/merkle-trees', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/data-management/merkle-trees';

UPDATE links 
SET dst_page = 'pattern-library/data-management/event-sourcing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/data-management/event-sourcing';

UPDATE links 
SET dst_page = 'pattern-library/data-management/cqrs', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/data-management/cqrs';

UPDATE links 
SET dst_page = 'pattern-library/scaling/sharding', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/scaling/sharding';

UPDATE links 
SET dst_page = 'pattern-library/resilience/circuit-breaker', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/resilience/circuit-breaker';

UPDATE links 
SET dst_page = 'pattern-library/scaling/rate-limiting', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/scaling/rate-limiting';

UPDATE links 
SET dst_page = 'pattern-library/communication/publish-subscribe', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/cloud-storage' 
  AND dst_page = 'interview-prep/pattern-library/communication/publish-subscribe';

UPDATE links 
SET dst_page = 'pattern-library/data-management/crdt', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/data-management/crdt';

UPDATE links 
SET dst_page = 'pattern-library/data-management/crdt', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/data-management/crdt';

UPDATE links 
SET dst_page = 'pattern-library/communication/websocket', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/communication/websocket';

UPDATE links 
SET dst_page = 'pattern-library/data-management/event-sourcing', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/data-management/event-sourcing';

UPDATE links 
SET dst_page = 'pattern-library/communication/publish-subscribe', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/communication/publish-subscribe';

UPDATE links 
SET dst_page = 'pattern-library/scaling/caching-strategies', is_valid = 1
WHERE src_page = 'interview-prep/ic-interviews/common-problems/collaborative-editor' 
  AND dst_page = 'interview-prep/pattern-library/scaling/caching-strategies';

COMMIT;
