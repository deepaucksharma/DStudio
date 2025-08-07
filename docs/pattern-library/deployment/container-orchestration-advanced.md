# Advanced Container Orchestration

## Overview

This advanced module covers enterprise-scale container orchestration patterns, going beyond basic Kubernetes to explore custom schedulers, production architectures from companies like Spotify and Pinterest, and advanced features like operators and multi-cluster management.

**Learning Time:** 350+ minutes  
**Prerequisites:** Basic Kubernetes knowledge, container fundamentals  
**Complexity:** Advanced  

## Table of Contents

1. [Advanced Kubernetes Scheduling](#advanced-kubernetes-scheduling)
2. [Resource Management and Quotas](#resource-management-and-quotas)
3. [Workload Management Patterns](#workload-management-patterns)
4. [Production Architecture Patterns](#production-architecture-patterns)
5. [Advanced Kubernetes Features](#advanced-kubernetes-features)
6. [Security Hardening](#security-hardening)
7. [Disaster Recovery](#disaster-recovery)
8. [Cost Optimization](#cost-optimization)
9. [Hands-on Labs](#hands-on-labs)

---

## Advanced Kubernetes Scheduling

### Custom Schedulers and Algorithms

#### Understanding the Default Scheduler

The default Kubernetes scheduler uses a two-phase process:
1. **Filtering:** Eliminate nodes that don't meet requirements
2. **Scoring:** Rank remaining nodes based on preferences

```yaml
# Custom scheduler configuration
apiVersion: kubescheduler.config.k8s.io/v1beta3
kind: KubeSchedulerConfiguration
profiles:
- schedulerName: custom-scheduler
  plugins:
    filter:
      enabled:
      - name: NodeResourcesFit
      - name: NodeAffinity
      - name: PodTopologySpread
    score:
      enabled:
      - name: NodeResourcesFit
        weight: 100
      - name: NodeAffinity
        weight: 50
  pluginConfig:
  - name: NodeResourcesFit
    args:
      scoringStrategy:
        type: LeastAllocated
```

#### Building a Custom Scheduler

```go
// Custom scheduler implementation
package main

import (
    "context"
    "fmt"
    "math"
    
    v1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    framework "k8s.io/kubernetes/pkg/scheduler/framework"
)

type CustomPlugin struct {
    handle framework.Handle
}

func (cp *CustomPlugin) Name() string {
    return "CustomPlugin"
}

// Score nodes based on GPU availability and memory
func (cp *CustomPlugin) Score(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodeName string) (int64, *framework.Status) {
    node, err := cp.handle.SnapshotSharedLister().NodeInfos().Get(nodeName)
    if err != nil {
        return 0, framework.NewStatus(framework.Error, fmt.Sprintf("getting node %q: %v", nodeName, err))
    }
    
    // Custom scoring based on GPU and memory availability
    gpuScore := calculateGPUScore(node.Node())
    memoryScore := calculateMemoryScore(node.Node(), pod)
    
    finalScore := int64(math.Floor((gpuScore*0.6 + memoryScore*0.4) * 100))
    return finalScore, nil
}

func calculateGPUScore(node *v1.Node) float64 {
    gpuCapacity := node.Status.Capacity["nvidia.com/gpu"]
    if gpuCapacity.IsZero() {
        return 0
    }
    
    gpuAllocatable := node.Status.Allocatable["nvidia.com/gpu"]
    return float64(gpuAllocatable.Value()) / float64(gpuCapacity.Value())
}
```

### Pod Topology Spread Constraints

#### Balanced Distribution Across Zones

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 12
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      topologySpreadConstraints:
      # Spread across availability zones
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: web-app
      # Spread across nodes within zones
      - maxSkew: 2
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: web-app
      containers:
      - name: web-app
        image: nginx:1.21
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

#### Advanced Topology Patterns

```yaml
# Multi-tier application with complex topology requirements
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-cluster
spec:
  replicas: 6
  selector:
    matchLabels:
      app: database
      tier: primary
  template:
    metadata:
      labels:
        app: database
        tier: primary
    spec:
      topologySpreadConstraints:
      # Ensure at least one replica per zone
      - maxSkew: 0
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: database
        minDomains: 3
      # Limit replicas per node for fault tolerance
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: database
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: database
                tier: primary
            topologyKey: kubernetes.io/hostname
      containers:
      - name: database
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: "production"
```

---

## Resource Management and Quotas

### Resource Quotas Implementation

#### Namespace-Level Resource Management

```yaml
# Production namespace with strict quotas
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    # Compute resources
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    
    # Storage resources
    requests.storage: 1Ti
    persistentvolumeclaims: "50"
    
    # Object counts
    pods: "100"
    services: "20"
    secrets: "50"
    configmaps: "50"
    
    # Extended resources
    requests.nvidia.com/gpu: "10"
    
    # Quality of Service classes
    count/pods.guaranteed: "20"
    count/pods.burstable: "50"
    count/pods.besteffort: "30"
```

### Limit Ranges for Resource Governance

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  # Pod-level limits
  - type: Pod
    max:
      cpu: "4"
      memory: 8Gi
    min:
      cpu: 10m
      memory: 16Mi
  
  # Container-level limits
  - type: Container
    default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    max:
      cpu: "2"
      memory: 4Gi
    min:
      cpu: 10m
      memory: 16Mi
    maxLimitRequestRatio:
      cpu: "10"
      memory: "8"
  
  # PVC limits
  - type: PersistentVolumeClaim
    max:
      storage: 100Gi
    min:
      storage: 1Gi
```

### Priority Classes and Preemption

#### Workload Priority Management

```yaml
# Critical system workloads
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-critical
value: 2000000000
globalDefault: false
description: "Critical system components"
preemptionPolicy: PreemptLowerPriority
---
# Production applications
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: production-high
value: 1000
globalDefault: false
description: "High priority production workloads"
preemptionPolicy: PreemptLowerPriority
---
# Development workloads
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: development
value: 100
globalDefault: true
description: "Development and testing workloads"
preemptionPolicy: PreemptLowerPriority
```

#### Production Workload with Priority

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      priorityClassName: production-high
      containers:
      - name: payment-service
        image: payment-service:v2.1.0
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: "1"
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Workload Management Patterns

### Taints, Tolerations, and Node Affinity

#### GPU Node Pool Configuration

```bash
# Taint GPU nodes to dedicate them for ML workloads
kubectl taint nodes gpu-node-1 nvidia.com/gpu=present:NoSchedule
kubectl taint nodes gpu-node-2 nvidia.com/gpu=present:NoSchedule
kubectl taint nodes gpu-node-3 nvidia.com/gpu=present:NoSchedule

# Label GPU nodes for identification
kubectl label nodes gpu-node-1 node-type=gpu-optimized
kubectl label nodes gpu-node-2 node-type=gpu-optimized
kubectl label nodes gpu-node-3 node-type=gpu-optimized
```

```yaml
# ML workload with GPU requirements
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-training
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      tolerations:
      - key: nvidia.com/gpu
        operator: Equal
        value: present
        effect: NoSchedule
      nodeSelector:
        node-type: gpu-optimized
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values:
                - gpu-optimized
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values:
                - us-west-2a
      containers:
      - name: ml-training
        image: tensorflow/tensorflow:2.8.0-gpu
        resources:
          requests:
            nvidia.com/gpu: "1"
            cpu: "2"
            memory: 8Gi
          limits:
            nvidia.com/gpu: "1"
            cpu: "4"
            memory: 16Gi
```

### StatefulSet Ordering Guarantees

#### Database Cluster with Ordered Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-cluster
spec:
  serviceName: postgres-cluster
  replicas: 3
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      app: postgres-cluster
  template:
    metadata:
      labels:
        app: postgres-cluster
    spec:
      initContainers:
      - name: postgres-init
        image: postgres:13
        command:
        - bash
        - -c
        - |
          set -ex
          # Generate server-id from pod ordinal index
          [[ $(hostname) =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          echo [postgres-$ordinal] > /mnt/conf.d/server-id.cnf
          
          # Copy appropriate conf.d files from config-map to emptyDir
          cp /mnt/config-map/master.cnf /mnt/conf.d/
          if [[ $ordinal -eq 0 ]]; then
            cp /mnt/config-map/master.cnf /mnt/conf.d/
          else
            cp /mnt/config-map/slave.cnf /mnt/conf.d/
          fi
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: cluster_db
        - name: POSTGRES_REPLICATION_USER
          value: replicator
        - name: POSTGRES_REPLICATION_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: replication-password
        ports:
        - name: postgres
          containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        - name: conf
          mountPath: /etc/postgresql/conf.d
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: conf
        emptyDir: {}
      - name: config-map
        configMap:
          name: postgres-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### DaemonSet Update Strategies

#### Advanced DaemonSet with Canary Updates

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-monitor
  labels:
    app: node-monitor
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 0
  selector:
    matchLabels:
      app: node-monitor
  template:
    metadata:
      labels:
        app: node-monitor
    spec:
      tolerations:
      # Allow scheduling on master nodes
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      # Allow scheduling on all nodes including tainted ones
      - operator: Exists
        effect: NoExecute
      - operator: Exists
        effect: NoSchedule
      
      hostNetwork: true
      hostPID: true
      
      serviceAccountName: node-monitor
      
      initContainers:
      - name: setup
        image: busybox:1.35
        command:
        - sh
        - -c
        - |
          # Setup monitoring directories
          mkdir -p /host/var/log/node-monitor
          chmod 755 /host/var/log/node-monitor
        volumeMounts:
        - name: host-root
          mountPath: /host
        securityContext:
          privileged: true
      
      containers:
      - name: node-monitor
        image: node-monitor:v2.3.0
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: NODE_IP
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        volumeMounts:
        - name: host-root
          mountPath: /host
          readOnly: true
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
        securityContext:
          privileged: true
          runAsUser: 0
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
            host: 127.0.0.1
          initialDelaySeconds: 30
          periodSeconds: 30
          
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
            host: 127.0.0.1
          initialDelaySeconds: 5
          periodSeconds: 10
      
      volumes:
      - name: host-root
        hostPath:
          path: /
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      
      terminationGracePeriodSeconds: 30
```

### Job Parallelism and Completions

#### Batch Processing with Parallel Jobs

```yaml
# Parallel job for data processing
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processing-job
spec:
  parallelism: 5
  completions: 20
  backoffLimit: 3
  activeDeadlineSeconds: 3600
  completionMode: Indexed
  
  template:
    metadata:
      labels:
        app: data-processor
    spec:
      restartPolicy: OnFailure
      
      initContainers:
      - name: setup
        image: busybox:1.35
        command:
        - sh
        - -c
        - |
          # Calculate work partition based on job completion index
          TOTAL_RECORDS=10000
          RECORDS_PER_JOB=$((TOTAL_RECORDS / 20))
          START_INDEX=$((JOB_COMPLETION_INDEX * RECORDS_PER_JOB))
          END_INDEX=$(((JOB_COMPLETION_INDEX + 1) * RECORDS_PER_JOB - 1))
          
          echo "START_INDEX=$START_INDEX" > /shared/job-config
          echo "END_INDEX=$END_INDEX" >> /shared/job-config
          echo "JOB_ID=$JOB_COMPLETION_INDEX" >> /shared/job-config
        volumeMounts:
        - name: shared-config
          mountPath: /shared
      
      containers:
      - name: processor
        image: data-processor:v1.2.0
        command:
        - bash
        - -c
        - |
          source /shared/job-config
          echo "Processing records $START_INDEX to $END_INDEX (Job ID: $JOB_ID)"
          
          # Process data chunk
          python process_data.py \
            --start-index $START_INDEX \
            --end-index $END_INDEX \
            --job-id $JOB_ID \
            --output-path /output/job-$JOB_ID-results.json
        
        env:
        - name: JOB_COMPLETION_INDEX
          valueFrom:
            fieldRef:
              fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
        
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: "1"
            memory: 2Gi
        
        volumeMounts:
        - name: shared-config
          mountPath: /shared
        - name: data-input
          mountPath: /input
        - name: data-output
          mountPath: /output
      
      volumes:
      - name: shared-config
        emptyDir: {}
      - name: data-input
        persistentVolumeClaim:
          claimName: input-data-pvc
      - name: data-output
        persistentVolumeClaim:
          claimName: output-data-pvc
```

---

## Production Architecture Patterns

### Spotify's GKE Optimization

#### Multi-Zone Cluster Configuration

```yaml
# Spotify-inspired cluster configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: kube-system
data:
  cluster-profile: |
    # Spotify's production cluster optimizations
    zones: ["us-central1-a", "us-central1-b", "us-central1-c"]
    node-pools:
      - name: "general-purpose"
        machine-type: "n2-standard-4"
        disk-size: 100
        disk-type: "pd-ssd"
        auto-scaling:
          min-nodes: 3
          max-nodes: 50
        locations: ["us-central1-a", "us-central1-b", "us-central1-c"]
        
      - name: "memory-optimized"
        machine-type: "n2-highmem-8"
        disk-size: 200
        disk-type: "pd-ssd"
        auto-scaling:
          min-nodes: 1
          max-nodes: 10
        taints:
          - key: "workload-type"
            value: "memory-intensive"
            effect: "NoSchedule"
            
      - name: "cpu-optimized"
        machine-type: "n2-highcpu-16"
        disk-size: 100
        disk-type: "pd-ssd"
        auto-scaling:
          min-nodes: 1
          max-nodes: 20
        taints:
          - key: "workload-type"
            value: "cpu-intensive"
            effect: "NoSchedule"
    
    cluster-features:
      - name: "network-policy"
        enabled: true
      - name: "horizontal-pod-autoscaling"
        enabled: true
      - name: "vertical-pod-autoscaling"
        enabled: true
      - name: "cluster-autoscaling"
        enabled: true
      - name: "binary-authorization"
        enabled: true
```

#### Spotify's Service Mesh Integration

```yaml
# Istio configuration for Spotify-style service mesh
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: spotify-istio
spec:
  values:
    global:
      meshID: spotify-mesh
      network: spotify-network
      
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: "2"
            memory: 4Gi
        hpaSpec:
          minReplicas: 2
          maxReplicas: 10
          metrics:
          - type: Resource
            resource:
              name: cpu
              target:
                type: Utilization
                averageUtilization: 70
    
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: "1"
            memory: 512Mi
        hpaSpec:
          minReplicas: 3
          maxReplicas: 20
        service:
          type: LoadBalancer
          ports:
          - port: 80
            targetPort: 8080
            name: http2
          - port: 443
            targetPort: 8443
            name: https
```

### Pinterest's EKS Architecture

#### Multi-Cluster Federation Setup

```yaml
# Pinterest-inspired multi-cluster setup
apiVersion: v1
kind: ConfigMap
metadata:
  name: pinterest-cluster-config
data:
  primary-cluster: |
    region: us-west-2
    zones: ["us-west-2a", "us-west-2b", "us-west-2c"]
    instance-types:
      - "m5.xlarge"    # General purpose
      - "c5.2xlarge"   # CPU optimized
      - "r5.2xlarge"   # Memory optimized
    
    node-groups:
      system:
        instance-type: "m5.large"
        capacity-type: "ON_DEMAND"
        scaling:
          desired: 3
          min: 3
          max: 10
        taints:
          - key: "node-type"
            value: "system"
            effect: "NoSchedule"
            
      application:
        instance-type: "m5.xlarge"
        capacity-type: "SPOT"
        scaling:
          desired: 10
          min: 5
          max: 100
        labels:
          node-type: "application"
          
      data-processing:
        instance-type: "c5.4xlarge"
        capacity-type: "ON_DEMAND"
        scaling:
          desired: 2
          min: 0
          max: 50
        taints:
          - key: "workload-type"
            value: "data-processing"
            effect: "NoSchedule"
```

#### Pinterest's Network Policies

```yaml
# Pinterest-style network segmentation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pinterest-web-tier
  namespace: web
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from load balancers
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  # Allow ingress from API gateway
  - from:
    - namespaceSelector:
        matchLabels:
          name: api-gateway
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Allow egress to API services
  - to:
    - namespaceSelector:
        matchLabels:
          name: api
    ports:
    - protocol: TCP
      port: 8080
  # Allow DNS resolution
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pinterest-api-tier
  namespace: api
spec:
  podSelector:
    matchLabels:
      tier: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from web tier
  - from:
    - namespaceSelector:
        matchLabels:
          name: web
    ports:
    - protocol: TCP
      port: 8080
  # Allow ingress from other API services
  - from:
    - podSelector:
        matchLabels:
          tier: api
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Allow egress to database
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  # Allow egress to cache
  - to:
    - namespaceSelector:
        matchLabels:
          name: cache
    ports:
    - protocol: TCP
      port: 6379
```

### Lyft's Envoy-based Service Mesh

#### Envoy Proxy Configuration

```yaml
# Lyft-inspired Envoy configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: envoy-config
  namespace: service-mesh
data:
  envoy.yaml: |
    admin:
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 9901
    
    static_resources:
      listeners:
      - name: listener_0
        address:
          socket_address:
            address: 0.0.0.0
            port_value: 10000
        filter_chains:
        - filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
              stat_prefix: ingress_http
              codec_type: AUTO
              route_config:
                name: local_route
                virtual_hosts:
                - name: local_service
                  domains: ["*"]
                  routes:
                  - match:
                      prefix: "/api/"
                    route:
                      cluster: api_service
                      retry_policy:
                        retry_on: "5xx,reset,connect-failure,refused-stream"
                        num_retries: 3
                        per_try_timeout: 3s
                  - match:
                      prefix: "/health"
                    route:
                      cluster: health_service
              http_filters:
              - name: envoy.filters.http.router
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
    
      clusters:
      - name: api_service
        connect_timeout: 5s
        type: LOGICAL_DNS
        dns_lookup_family: V4_ONLY
        lb_policy: ROUND_ROBIN
        load_assignment:
          cluster_name: api_service
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: api-service
                    port_value: 8080
        circuit_breakers:
          thresholds:
          - priority: DEFAULT
            max_connections: 100
            max_pending_requests: 50
            max_requests: 200
            max_retries: 3
        health_checks:
        - timeout: 3s
          interval: 10s
          healthy_threshold: 2
          unhealthy_threshold: 3
          http_health_check:
            path: "/health"
```

#### Service Mesh Deployment

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: envoy-proxy
  namespace: service-mesh
spec:
  selector:
    matchLabels:
      app: envoy-proxy
  template:
    metadata:
      labels:
        app: envoy-proxy
    spec:
      hostNetwork: true
      containers:
      - name: envoy
        image: envoyproxy/envoy:v1.24.1
        args:
        - "-c"
        - "/etc/envoy/envoy.yaml"
        - "--service-cluster"
        - "lyft-service-mesh"
        - "--service-node"
        - "$(NODE_NAME)"
        - "--log-level"
        - "info"
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        ports:
        - containerPort: 10000
          protocol: TCP
          name: http
        - containerPort: 9901
          protocol: TCP
          name: admin
        volumeMounts:
        - name: envoy-config
          mountPath: /etc/envoy
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /ready
            port: 9901
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /ready
            port: 9901
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: envoy-config
        configMap:
          name: envoy-config
```

### Datadog's Multi-Cluster Strategy

#### Cluster Federation Configuration

```yaml
# Datadog-inspired multi-cluster federation
apiVersion: v1
kind: ConfigMap
metadata:
  name: datadog-cluster-federation
data:
  federation-config.yaml: |
    clusters:
      us-west:
        endpoint: https://us-west-k8s.datadog.internal
        region: us-west-2
        zones: ["us-west-2a", "us-west-2b", "us-west-2c"]
        capacity:
          total-nodes: 500
          max-pods-per-node: 110
        workloads:
          - "web-frontend"
          - "api-services"
          - "data-processing"
          
      us-east:
        endpoint: https://us-east-k8s.datadog.internal
        region: us-east-1
        zones: ["us-east-1a", "us-east-1b", "us-east-1c"]
        capacity:
          total-nodes: 300
          max-pods-per-node: 110
        workloads:
          - "analytics"
          - "monitoring"
          - "alerting"
          
      eu-central:
        endpoint: https://eu-central-k8s.datadog.internal
        region: eu-central-1
        zones: ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
        capacity:
          total-nodes: 200
          max-pods-per-node: 110
        workloads:
          - "compliance"
          - "data-residency"
    
    federation-policies:
      placement:
        - workload: "web-frontend"
          strategy: "multi-region"
          primary-region: "us-west"
          replica-regions: ["us-east"]
          
        - workload: "data-processing"
          strategy: "region-local"
          allowed-regions: ["us-west", "us-east"]
          
        - workload: "compliance"
          strategy: "region-restricted"
          allowed-regions: ["eu-central"]
          
      failover:
        - source-region: "us-west"
          target-region: "us-east"
          trigger: "region-failure"
          
        - source-region: "us-east"
          target-region: "us-west"
          trigger: "region-failure"
```

---

## Advanced Kubernetes Features

### Admission Webhooks and Controllers

#### Custom Admission Controller

```go
// Custom admission webhook
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    
    admissionv1 "k8s.io/api/admission/v1"
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
)

type WebhookServer struct {
    server *http.Server
}

type patchOperation struct {
    Op    string      `json:"op"`
    Path  string      `json:"path"`
    Value interface{} `json:"value,omitempty"`
}

func (ws *WebhookServer) mutate(w http.ResponseWriter, r *http.Request) {
    var admissionResponse *admissionv1.AdmissionResponse
    
    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    var admissionReview admissionv1.AdmissionReview
    if err := json.Unmarshal(body, &admissionReview); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    req := admissionReview.Request
    var patches []patchOperation
    
    // Parse the object
    var obj runtime.Object
    switch req.Kind.Kind {
    case "Deployment":
        obj = &appsv1.Deployment{}
    case "Pod":
        obj = &corev1.Pod{}
    default:
        admissionResponse = &admissionv1.AdmissionResponse{
            UID:     req.UID,
            Allowed: true,
        }
    }
    
    if obj != nil {
        if err := json.Unmarshal(req.Object.Raw, obj); err != nil {
            admissionResponse = &admissionv1.AdmissionResponse{
                UID:     req.UID,
                Allowed: false,
                Result:  &metav1.Status{Message: err.Error()},
            }
        } else {
            patches = applySecurityDefaults(obj)
            
            patchBytes, _ := json.Marshal(patches)
            admissionResponse = &admissionv1.AdmissionResponse{
                UID:     req.UID,
                Allowed: true,
                Patch:   patchBytes,
                PatchType: func() *admissionv1.PatchType {
                    pt := admissionv1.PatchTypeJSONPatch
                    return &pt
                }(),
            }
        }
    }
    
    admissionReview.Response = admissionResponse
    response, _ := json.Marshal(admissionReview)
    w.Header().Set("Content-Type", "application/json")
    w.Write(response)
}

func applySecurityDefaults(obj runtime.Object) []patchOperation {
    var patches []patchOperation
    
    switch o := obj.(type) {
    case *appsv1.Deployment:
        // Add security context if missing
        containers := o.Spec.Template.Spec.Containers
        for i, container := range containers {
            if container.SecurityContext == nil {
                patches = append(patches, patchOperation{
                    Op:   "add",
                    Path: fmt.Sprintf("/spec/template/spec/containers/%d/securityContext", i),
                    Value: corev1.SecurityContext{
                        AllowPrivilegeEscalation: &[]bool{false}[0],
                        ReadOnlyRootFilesystem:   &[]bool{true}[0],
                        RunAsNonRoot:             &[]bool{true}[0],
                        RunAsUser:                &[]int64{65534}[0],
                        Capabilities: &corev1.Capabilities{
                            Drop: []corev1.Capability{"ALL"},
                        },
                    },
                })
            }
            
            // Add resource limits if missing
            if container.Resources.Limits == nil {
                patches = append(patches, patchOperation{
                    Op:   "add",
                    Path: fmt.Sprintf("/spec/template/spec/containers/%d/resources/limits", i),
                    Value: corev1.ResourceList{
                        corev1.ResourceCPU:    resource.MustParse("500m"),
                        corev1.ResourceMemory: resource.MustParse("512Mi"),
                    },
                })
            }
        }
    }
    
    return patches
}
```

#### Admission Webhook Configuration

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingAdmissionWebhook
metadata:
  name: security-defaults-webhook
webhooks:
- name: security-defaults.example.com
  clientConfig:
    service:
      name: security-webhook-service
      namespace: webhook-system
      path: "/mutate"
  rules:
  - operations: ["CREATE", "UPDATE"]
    apiGroups: ["apps"]
    apiVersions: ["v1"]
    resources: ["deployments"]
  - operations: ["CREATE", "UPDATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  admissionReviewVersions: ["v1", "v1beta1"]
  sideEffects: None
  failurePolicy: Ignore
```

### Custom Resource Definitions (CRDs)

#### Database CRD Implementation

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.db.example.com
spec:
  group: db.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              engine:
                type: string
                enum: ["postgresql", "mysql", "redis"]
              version:
                type: string
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              resources:
                type: object
                properties:
                  requests:
                    type: object
                    properties:
                      cpu:
                        type: string
                      memory:
                        type: string
                      storage:
                        type: string
                  limits:
                    type: object
                    properties:
                      cpu:
                        type: string
                      memory:
                        type: string
              backup:
                type: object
                properties:
                  enabled:
                    type: boolean
                  schedule:
                    type: string
                  retention:
                    type: string
              monitoring:
                type: object
                properties:
                  enabled:
                    type: boolean
                  scrapeInterval:
                    type: string
            required:
            - engine
            - version
          status:
            type: object
            properties:
              phase:
                type: string
                enum: ["Pending", "Creating", "Ready", "Failed"]
              replicas:
                type: integer
              readyReplicas:
                type: integer
              conditions:
                type: array
                items:
                  type: object
                  properties:
                    type:
                      type: string
                    status:
                      type: string
                    reason:
                      type: string
                    message:
                      type: string
                    lastTransitionTime:
                      type: string
    additionalPrinterColumns:
    - name: Engine
      type: string
      jsonPath: .spec.engine
    - name: Version
      type: string
      jsonPath: .spec.version
    - name: Replicas
      type: integer
      jsonPath: .spec.replicas
    - name: Ready
      type: integer
      jsonPath: .status.readyReplicas
    - name: Phase
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
    shortNames:
    - db
```

#### Database Controller Implementation

```go
// Database controller implementation
package controllers

import (
    "context"
    "time"
    
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"
    
    dbv1 "github.com/example/database-operator/api/v1"
)

type DatabaseReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    logger := log.FromContext(ctx)
    
    // Fetch the Database instance
    var database dbv1.Database
    if err := r.Get(ctx, req.NamespacedName, &database); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // Update status to indicate processing
    database.Status.Phase = "Creating"
    if err := r.Status().Update(ctx, &database); err != nil {
        logger.Error(err, "Failed to update Database status")
        return ctrl.Result{}, err
    }
    
    // Create or update StatefulSet
    if err := r.reconcileStatefulSet(ctx, &database); err != nil {
        logger.Error(err, "Failed to reconcile StatefulSet")
        database.Status.Phase = "Failed"
        r.Status().Update(ctx, &database)
        return ctrl.Result{}, err
    }
    
    // Create or update Service
    if err := r.reconcileService(ctx, &database); err != nil {
        logger.Error(err, "Failed to reconcile Service")
        return ctrl.Result{}, err
    }
    
    // Create or update ConfigMap
    if err := r.reconcileConfigMap(ctx, &database); err != nil {
        logger.Error(err, "Failed to reconcile ConfigMap")
        return ctrl.Result{}, err
    }
    
    // Update status
    database.Status.Phase = "Ready"
    database.Status.Replicas = database.Spec.Replicas
    database.Status.ReadyReplicas = database.Spec.Replicas
    if err := r.Status().Update(ctx, &database); err != nil {
        logger.Error(err, "Failed to update Database status")
        return ctrl.Result{}, err
    }
    
    return ctrl.Result{RequeueAfter: time.Minute * 5}, nil
}

func (r *DatabaseReconciler) reconcileStatefulSet(ctx context.Context, db *dbv1.Database) error {
    statefulSet := &appsv1.StatefulSet{
        ObjectMeta: metav1.ObjectMeta{
            Name:      db.Name,
            Namespace: db.Namespace,
        },
        Spec: appsv1.StatefulSetSpec{
            Replicas:    &db.Spec.Replicas,
            ServiceName: db.Name,
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{
                    "app":      db.Name,
                    "database": db.Spec.Engine,
                },
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{
                        "app":      db.Name,
                        "database": db.Spec.Engine,
                    },
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{
                        {
                            Name:  db.Spec.Engine,
                            Image: fmt.Sprintf("%s:%s", db.Spec.Engine, db.Spec.Version),
                            Resources: corev1.ResourceRequirements{
                                Requests: corev1.ResourceList{
                                    corev1.ResourceCPU:    resource.MustParse(db.Spec.Resources.Requests.CPU),
                                    corev1.ResourceMemory: resource.MustParse(db.Spec.Resources.Requests.Memory),
                                },
                                Limits: corev1.ResourceList{
                                    corev1.ResourceCPU:    resource.MustParse(db.Spec.Resources.Limits.CPU),
                                    corev1.ResourceMemory: resource.MustParse(db.Spec.Resources.Limits.Memory),
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    
    // Set owner reference
    if err := ctrl.SetControllerReference(db, statefulSet, r.Scheme); err != nil {
        return err
    }
    
    return r.Client.Patch(ctx, statefulSet, client.Apply, client.ForceOwnership, client.FieldOwner("database-controller"))
}
```

### Operator SDK and Kubebuilder

#### Complete Operator Structure

```bash
# Initialize operator project
kubebuilder init --domain example.com --repo github.com/example/database-operator

# Create API and controller
kubebuilder create api --group db --version v1 --kind Database --resource --controller

# Project structure
database-operator/
├── api/
│   └── v1/
│       ├── database_types.go
│       ├── groupversion_info.go
│       └── zz_generated.deepcopy.go
├── controllers/
│   ├── database_controller.go
│   └── suite_test.go
├── config/
│   ├── crd/
│   ├── default/
│   ├── manager/
│   ├── rbac/
│   └── samples/
├── Dockerfile
├── Makefile
├── PROJECT
├── README.md
├── go.mod
├── go.sum
└── main.go
```

#### Operator Deployment

```yaml
# Operator deployment with RBAC
apiVersion: v1
kind: ServiceAccount
metadata:
  name: database-operator
  namespace: database-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: database-operator-manager-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints", "persistentvolumeclaims", "events", "configmaps", "secrets"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "statefulsets"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["db.example.com"]
  resources: ["databases"]
  verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
- apiGroups: ["db.example.com"]
  resources: ["databases/finalizers"]
  verbs: ["update"]
- apiGroups: ["db.example.com"]
  resources: ["databases/status"]
  verbs: ["get", "patch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: database-operator-manager-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: database-operator-manager-role
subjects:
- kind: ServiceAccount
  name: database-operator
  namespace: database-system
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-operator-controller-manager
  namespace: database-system
  labels:
    control-plane: controller-manager
spec:
  selector:
    matchLabels:
      control-plane: controller-manager
  replicas: 2
  template:
    metadata:
      labels:
        control-plane: controller-manager
    spec:
      serviceAccountName: database-operator
      containers:
      - name: manager
        image: database-operator:latest
        command:
        - /manager
        args:
        - --leader-elect
        - --health-probe-bind-address=:8081
        - --metrics-bind-address=127.0.0.1:8080
        env:
        - name: WATCH_NAMESPACE
          value: ""
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8081
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 128Mi
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - "ALL"
          readOnlyRootFilesystem: true
          runAsNonRoot: true
      terminationGracePeriodSeconds: 10
```

### Virtual Kubelet and Serverless Nodes

#### Virtual Kubelet Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: virtual-kubelet
  namespace: kube-system
  labels:
    app: virtual-kubelet
spec:
  replicas: 1
  selector:
    matchLabels:
      app: virtual-kubelet
  template:
    metadata:
      labels:
        app: virtual-kubelet
    spec:
      serviceAccountName: virtual-kubelet
      hostNetwork: true
      containers:
      - name: virtual-kubelet
        image: virtual-kubelet/virtual-kubelet:1.5.0
        command:
        - virtual-kubelet
        args:
        - --provider=aws-fargate
        - --nodename=virtual-fargate-node
        - --klog.v=2
        - --klog.logtostderr
        env:
        - name: KUBELET_PORT
          value: "10250"
        - name: APISERVER_CERT_LOCATION
          value: /etc/kubernetes/certs/apiserver.crt
        - name: APISERVER_KEY_LOCATION
          value: /etc/kubernetes/certs/apiserver.key
        - name: VKUBELET_POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        resources:
          requests:
            cpu: 50m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 500Mi
        volumeMounts:
        - name: certificates
          mountPath: /etc/kubernetes/certs
          readOnly: true
        - name: kube-config
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: certificates
        secret:
          secretName: virtual-kubelet-certs
      - name: kube-config
        configMap:
          name: virtual-kubelet-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: virtual-kubelet-config
  namespace: kube-system
data:
  config.yaml: |
    node:
      name: "virtual-fargate-node"
      taints:
      - key: "virtual-kubelet.io/provider"
        value: "aws-fargate"
        effect: "NoSchedule"
      labels:
        node.kubernetes.io/instance-type: "fargate"
        beta.kubernetes.io/arch: "amd64"
        beta.kubernetes.io/os: "linux"
        node-type: "virtual"
    
    fargate:
      region: "us-west-2"
      cluster-name: "production-cluster"
      subnets:
      - "subnet-12345"
      - "subnet-67890"
      security-groups:
      - "sg-abcdef"
      execution-role: "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
      task-role: "arn:aws:iam::123456789012:role/ecsTaskRole"
```

### Multi-Cluster Federation

#### Admiral Multi-Cluster Setup

```yaml
# Admiral configuration for multi-cluster service discovery
apiVersion: v1
kind: ConfigMap
metadata:
  name: admiral-config
  namespace: admiral-system
data:
  config.yaml: |
    admiral:
      clusters:
        us-west:
          endpoint: "https://us-west-k8s-api.example.com"
          identity: "us-west-cluster"
          locality: "region=us-west,zone=us-west-2a"
          
        us-east:
          endpoint: "https://us-east-k8s-api.example.com"
          identity: "us-east-cluster"
          locality: "region=us-east,zone=us-east-1a"
          
        eu-central:
          endpoint: "https://eu-central-k8s-api.example.com"
          identity: "eu-central-cluster"
          locality: "region=eu-central,zone=eu-central-1a"
      
      service-discovery:
        enabled: true
        mesh-networks:
          network1:
            endpoints:
            - fromRegistry: us-west
            - fromRegistry: us-east
            gateways:
            - address: us-west-gateway.example.com
              port: 443
            - address: us-east-gateway.example.com
              port: 443
          network2:
            endpoints:
            - fromRegistry: eu-central
            gateways:
            - address: eu-central-gateway.example.com
              port: 443
      
      traffic-policy:
        outlierDetection:
          consecutiveErrors: 3
          interval: 30s
          baseEjectionTime: 30s
        loadBalancer:
          simple: ROUND_ROBIN
          localityLbSetting:
            enabled: true
            distribute:
            - from: "region/us-west/*"
              to:
                "region/us-west/*": 80
                "region/us-east/*": 20
            failover:
            - from: "region/us-west/*"
              to: "region/us-east/*"
```

### GitOps with Flux/ArgoCD

#### ArgoCD Application Set

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices-apps
  namespace: argocd
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: production
  - git:
      repoURL: https://github.com/example/k8s-configs
      revision: HEAD
      directories:
      - path: applications/*
  template:
    metadata:
      name: '{{path.basename}}-{{name}}'
      labels:
        environment: '{{metadata.labels.environment}}'
        cluster: '{{name}}'
    spec:
      project: production
      source:
        repoURL: https://github.com/example/k8s-configs
        targetRevision: HEAD
        path: '{{path}}'
        helm:
          valueFiles:
          - values-{{metadata.labels.environment}}.yaml
          - values-{{name}}.yaml
      destination:
        server: '{{server}}'
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
          allowEmpty: false
        syncOptions:
        - CreateNamespace=true
        - PrunePropagationPolicy=foreground
        - PruneLast=true
        retry:
          limit: 5
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m
---
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications
  sourceRepos:
  - 'https://github.com/example/*'
  - 'https://helm.example.com'
  destinations:
  - namespace: '*'
    server: '*'
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
  roles:
  - name: production-admin
    description: Production administrator
    policies:
    - p, proj:production:production-admin, applications, *, production/*, allow
    - p, proj:production:production-admin, clusters, get, *, allow
    groups:
    - example:production-team
  - name: production-readonly
    description: Production read-only
    policies:
    - p, proj:production:production-readonly, applications, get, production/*, allow
    - p, proj:production:production-readonly, applications, action/*, production/*, deny
    groups:
    - example:developers
```

#### Flux v2 Configuration

```yaml
# Flux source configuration
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: GitRepository
metadata:
  name: production-configs
  namespace: flux-system
spec:
  interval: 5m0s
  ref:
    branch: main
  secretRef:
    name: git-credentials
  url: https://github.com/example/production-configs
  ignore: |
    # ignore all
    /*
    # except kustomization files
    !/clusters/
    !/infrastructure/
    !/applications/
---
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 5m0s
  url: https://charts.bitnami.com/bitnami
---
# Flux kustomization
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m0s
  path: ./infrastructure
  prune: true
  sourceRef:
    kind: GitRepository
    name: production-configs
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: ingress-nginx-controller
    namespace: ingress-nginx
  - apiVersion: apps/v1
    kind: Deployment
    name: cert-manager
    namespace: cert-manager
  dependsOn:
  - name: flux-system
---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: applications
  namespace: flux-system
spec:
  interval: 5m0s
  path: ./applications
  prune: true
  sourceRef:
    kind: GitRepository
    name: production-configs
  dependsOn:
  - name: infrastructure
  postBuild:
    substitute:
      cluster_name: "production-cluster"
      environment: "production"
```

---

## Security Hardening

### Pod Security Standards

#### Pod Security Policy Implementation

```yaml
# Pod Security Standards enforcement
apiVersion: v1
kind: Namespace
metadata:
  name: secure-applications
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
---
# Network policy for secure namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: secure-applications
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  egress:
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  # Allow HTTPS to external services
  - to: []
    ports:
    - protocol: TCP
      port: 443
---
# Security context constraints
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: secure-applications
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
    spec:
      serviceAccountName: secure-app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        image: secure-app:v1.0.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 65534
          runAsGroup: 65534
          capabilities:
            drop:
            - ALL
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
        - name: cache-volume
          mountPath: /app/cache
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: tmp-volume
        emptyDir: {}
      - name: cache-volume
        emptyDir: {}
```

### RBAC Security Model

#### Fine-grained RBAC Configuration

```yaml
# Service-specific service account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payment-service-sa
  namespace: production
  labels:
    app: payment-service
---
# Role for payment service operations
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: payment-service-role
rules:
# Allow reading ConfigMaps and Secrets for configuration
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
  resourceNames: ["payment-config", "payment-secrets"]
# Allow creating events for auditing
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create"]
# Allow reading own pod for self-introspection
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get"]
  resourceNames: ["payment-service-*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payment-service-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: payment-service-sa
  namespace: production
roleRef:
  kind: Role
  name: payment-service-role
  apiGroup: rbac.authorization.k8s.io
---
# Cluster role for cross-namespace service discovery
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: service-discovery-reader
rules:
- apiGroups: [""]
  resources: ["endpoints", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: payment-service-discovery
subjects:
- kind: ServiceAccount
  name: payment-service-sa
  namespace: production
roleRef:
  kind: ClusterRole
  name: service-discovery-reader
  apiGroup: rbac.authorization.k8s.io
```

### Secret Management

#### External Secrets Operator Configuration

```yaml
# External Secrets Operator with AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: payment-service-secrets
  namespace: production
spec:
  refreshInterval: 5m
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: payment-service-secrets
    creationPolicy: Owner
    template:
      type: Opaque
      metadata:
        labels:
          app: payment-service
      data:
        database-password: "{{ .database_password | toString }}"
        api-key: "{{ .stripe_api_key | toString }}"
        jwt-secret: "{{ .jwt_signing_key | toString }}"
  data:
  - secretKey: database_password
    remoteRef:
      key: production/payment-service/database
      property: password
  - secretKey: stripe_api_key
    remoteRef:
      key: production/payment-service/stripe
      property: api_key
  - secretKey: jwt_signing_key
    remoteRef:
      key: production/payment-service/jwt
      property: signing_key
---
# Sealed Secrets for GitOps workflow
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: app-config-sealed
  namespace: production
spec:
  encryptedData:
    database-url: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAx...
    redis-url: AgAKAoiQm7QDhII+CxVKFhKI+7eQQdOqZ...
  template:
    metadata:
      name: app-config
      namespace: production
    type: Opaque
```

---

## Disaster Recovery

### Backup and Restore Strategies

#### Velero Backup Configuration

```yaml
# Velero backup schedule
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: production-daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  template:
    includedNamespaces:
    - production
    - monitoring
    - ingress-nginx
    excludedResources:
    - events
    - events.events.k8s.io
    - backups.velero.io
    - restores.velero.io
    storageLocation: aws-s3-backup
    ttl: 720h0m0s  # 30 days
    metadata:
      labels:
        backup-type: scheduled
        environment: production
    hooks:
      resources:
      - name: database-backup-hook
        includedNamespaces:
        - production
        includedResources:
        - pods
        labelSelector:
          matchLabels:
            app: postgres
        pre:
        - exec:
            container: postgres
            command:
            - /bin/bash
            - -c
            - "pg_dump $POSTGRES_DB > /tmp/backup.sql"
            onError: Fail
        post:
        - exec:
            container: postgres
            command:
            - /bin/bash
            - -c
            - "rm -f /tmp/backup.sql"
            onError: Continue
---
# Velero backup location
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: aws-s3-backup
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: production-k8s-backups
    prefix: cluster-1
  config:
    region: us-west-2
    s3ForcePathStyle: "false"
---
# Volume snapshot location
apiVersion: velero.io/v1
kind: VolumeSnapshotLocation
metadata:
  name: aws-ebs-snapshots
  namespace: velero
spec:
  provider: aws
  config:
    region: us-west-2
```

#### Cross-Cluster Disaster Recovery

```yaml
# Disaster recovery restore job
apiVersion: batch/v1
kind: Job
metadata:
  name: disaster-recovery-restore
  namespace: velero
spec:
  template:
    spec:
      serviceAccountName: velero-restore
      containers:
      - name: restore-job
        image: velero/velero:v1.9.0
        command:
        - /bin/bash
        - -c
        - |
          set -e
          
          # Wait for cluster to be ready
          kubectl wait --for=condition=Ready nodes --all --timeout=300s
          
          # Restore critical infrastructure first
          velero restore create infrastructure-restore \
            --from-backup production-daily-backup-20231201020000 \
            --include-namespaces ingress-nginx,cert-manager \
            --wait
          
          # Wait for infrastructure to be ready
          kubectl wait --for=condition=available deployment/ingress-nginx-controller -n ingress-nginx --timeout=300s
          kubectl wait --for=condition=available deployment/cert-manager -n cert-manager --timeout=300s
          
          # Restore application namespaces
          velero restore create applications-restore \
            --from-backup production-daily-backup-20231201020000 \
            --include-namespaces production \
            --wait
          
          # Verify restoration
          kubectl get pods -n production
          kubectl get services -n production
          
          # Run post-restore validation
          kubectl apply -f - <<EOF
          apiVersion: batch/v1
          kind: Job
          metadata:
            name: post-restore-validation
            namespace: production
          spec:
            template:
              spec:
                restartPolicy: OnFailure
                containers:
                - name: validator
                  image: curlimages/curl:7.85.0
                  command:
                  - /bin/sh
                  - -c
                  - |
                    # Test database connectivity
                    nc -zv postgres-service 5432
                    
                    # Test API endpoints
                    curl -f http://api-service:8080/health
                    
                    # Test external connectivity
                    curl -f https://api.production.example.com/health
          EOF
        env:
        - name: KUBECONFIG
          value: /etc/kubeconfig/config
        volumeMounts:
        - name: kubeconfig
          mountPath: /etc/kubeconfig
      volumes:
      - name: kubeconfig
        secret:
          secretName: dr-cluster-kubeconfig
      restartPolicy: OnFailure
```

### High Availability Patterns

#### Multi-Zone Database Cluster

```yaml
# Multi-zone PostgreSQL cluster with automated failover
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-ha-cluster
  namespace: production
spec:
  instances: 3
  
  # Anti-affinity to spread across zones
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            postgresql: postgres-ha-cluster
        topologyKey: topology.kubernetes.io/zone
  
  postgresql:
    parameters:
      # High availability settings
      wal_level: replica
      archive_mode: "on"
      archive_command: "test ! -f /pgdata/archive/%f && cp %p /pgdata/archive/%f"
      
      # Performance tuning
      shared_buffers: "256MB"
      effective_cache_size: "1GB"
      maintenance_work_mem: "64MB"
      wal_buffers: "16MB"
      checkpoint_completion_target: "0.7"
      
      # Connection settings
      max_connections: "200"
      shared_preload_libraries: "pg_stat_statements"
  
  # Backup configuration
  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      destinationPath: s3://postgres-backups/ha-cluster
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY
      wal:
        retention: "5d"
      data:
        retention: "30d"
  
  # Monitoring
  monitoring:
    enabled: true
    podMonitor:
      enabled: true
  
  # Storage configuration
  storage:
    storageClass: fast-ssd
    size: 100Gi
  
  # Resource requirements
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"
  
  # Bootstrap from backup (for disaster recovery)
  bootstrap:
    recovery:
      source: postgres-backup
      recoveryTargetTime: "2023-12-01 10:00:00.000000+00"
  
  externalClusters:
  - name: postgres-backup
    barmanObjectStore:
      destinationPath: s3://postgres-backups/ha-cluster
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY
```

---

## Cost Optimization

### Resource Optimization Strategies

#### Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: payment-service-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: payment-service
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: "2"
        memory: 4Gi
      controlledResources:
      - cpu
      - memory
      controlledValues: RequestsAndLimits
    - containerName: istio-proxy
      mode: "Off"
---
# HPA with custom metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payment-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  # CPU utilization
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Memory utilization
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # Custom metric: requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  # External metric: SQS queue length
  - type: External
    external:
      metric:
        name: sqs_messages_visible
        selector:
          matchLabels:
            queue: payment-processing
      target:
        type: Value
        value: "10"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 30
      - type: Pods
        value: 5
        periodSeconds: 30
      selectPolicy: Max
```

### Cluster Autoscaling

#### Advanced Cluster Autoscaler Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
spec:
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.24.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/production-cluster
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-delay-after-delete=10s
        - --scale-down-delay-after-failure=3m
        - --scale-down-utilization-threshold=0.5
        - --new-pod-scale-up-delay=0s
        - --max-node-provision-time=15m
        env:
        - name: AWS_REGION
          value: us-west-2
        volumeMounts:
        - name: ssl-certs
          mountPath: /etc/ssl/certs/ca-certificates.crt
          readOnly: true
        imagePullPolicy: "Always"
      volumes:
      - name: ssl-certs
        hostPath:
          path: "/etc/ssl/certs/ca-bundle.crt"
---
# Priority class for cost optimization
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: cost-optimized
value: 50
globalDefault: false
description: "Cost optimized workloads that can be preempted"
preemptionPolicy: PreemptLowerPriority
```

### Spot Instance Management

#### Spot Instance Node Pool

```yaml
# AWS Node Group for Spot instances
apiVersion: v1
kind: ConfigMap
metadata:
  name: spot-node-configuration
data:
  nodegroup-config.yaml: |
    apiVersion: eks.amazonaws.com/v1alpha1
    kind: Nodegroup
    metadata:
      name: spot-workers
    spec:
      cluster: production-cluster
      
      # Instance configuration
      instanceTypes:
      - m5.large
      - m5.xlarge
      - m5.2xlarge
      - m4.large
      - m4.xlarge
      - c5.large
      - c5.xlarge
      
      capacityType: SPOT
      
      # Auto Scaling configuration
      scaling:
        minSize: 0
        maxSize: 100
        desiredSize: 10
      
      # Subnet configuration
      subnets:
      - subnet-12345
      - subnet-67890
      - subnet-11111
      
      # Taints for spot instances
      taints:
      - key: node-type
        value: spot
        effect: NoSchedule
      
      # Labels
      labels:
        node-type: spot
        cost-optimization: enabled
        
      # User data for spot instance handling
      userData: |
        #!/bin/bash
        /etc/eks/bootstrap.sh production-cluster
        
        # Install spot instance termination handler
        wget https://github.com/aws/aws-node-termination-handler/releases/download/v1.19.0/node-termination-handler.linux.amd64
        chmod +x node-termination-handler.linux.amd64
        mv node-termination-handler.linux.amd64 /usr/local/bin/node-termination-handler
        
        # Create systemd service
        cat > /etc/systemd/system/node-termination-handler.service <<EOF
        [Unit]
        Description=AWS Node Termination Handler
        After=network.target
        
        [Service]
        ExecStart=/usr/local/bin/node-termination-handler \
          --node-name=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname) \
          --namespace=kube-system \
          --delete-local-data=true \
          --ignore-daemon-sets=true \
          --grace-period=-1
        Restart=always
        User=root
        
        [Install]
        WantedBy=multi-user.target
        EOF
        
        systemctl enable node-termination-handler
        systemctl start node-termination-handler
```

#### Spot-Tolerant Application Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-processor
  namespace: batch-processing
spec:
  replicas: 10
  selector:
    matchLabels:
      app: batch-processor
  template:
    metadata:
      labels:
        app: batch-processor
    spec:
      # Tolerate spot instance taints
      tolerations:
      - key: node-type
        value: spot
        effect: NoSchedule
      
      # Prefer spot instances for cost savings
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: node-type
                operator: In
                values:
                - spot
          - weight: 50
            preference:
              matchExpressions:
              - key: cost-optimization
                operator: In
                values:
                - enabled
      
      # Use low priority for spot workloads
      priorityClassName: cost-optimized
      
      containers:
      - name: processor
        image: batch-processor:v1.2.0
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        
        # Graceful shutdown for spot termination
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/bash
              - -c
              - |
                # Gracefully finish current work
                touch /tmp/shutdown-requested
                
                # Wait for current job to complete (max 2 minutes)
                timeout=120
                while [ -f /tmp/processing ] && [ $timeout -gt 0 ]; do
                  sleep 1
                  timeout=$((timeout-1))
                done
        
        # Health checks
        livenessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - "[ ! -f /tmp/shutdown-requested ] && pgrep -f batch-processor"
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - "[ ! -f /tmp/shutdown-requested ] && [ ! -f /tmp/processing ]"
          initialDelaySeconds: 5
          periodSeconds: 5
      
      # Fast termination for spot instances
      terminationGracePeriodSeconds: 30
```

---

## Hands-on Labs

### Lab 1: Custom Scheduler Implementation

#### Objective
Build and deploy a custom Kubernetes scheduler that prioritizes nodes based on GPU availability and custom metrics.

#### Prerequisites
- Running Kubernetes cluster
- kubectl access
- Go development environment

#### Steps

1. **Create Custom Scheduler**

```go
// custom-scheduler/main.go
package main

import (
    "context"
    "fmt"
    "os"
    
    "k8s.io/kubernetes/cmd/kube-scheduler/app"
    "k8s.io/kubernetes/pkg/scheduler/framework/plugins/registry"
)

func main() {
    // Register custom plugins
    registry.Register("GPUPriority", NewGPUPriorityPlugin)
    
    command := app.NewSchedulerCommand(
        app.WithPlugin("GPUPriority", NewGPUPriorityPlugin),
    )
    
    if err := command.Execute(); err != nil {
        fmt.Fprintf(os.Stderr, "%v\n", err)
        os.Exit(1)
    }
}
```

2. **Deploy Custom Scheduler**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-gpu-scheduler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: custom-gpu-scheduler
  template:
    metadata:
      labels:
        app: custom-gpu-scheduler
    spec:
      serviceAccountName: custom-scheduler
      containers:
      - name: scheduler
        image: custom-scheduler:v1.0.0
        command:
        - /usr/local/bin/custom-scheduler
        - --config=/etc/kubernetes/scheduler-config.yaml
        - --v=2
        volumeMounts:
        - name: config
          mountPath: /etc/kubernetes
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
      volumes:
      - name: config
        configMap:
          name: custom-scheduler-config
```

3. **Test Workload**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-workload-test
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-workload-test
  template:
    metadata:
      labels:
        app: ml-workload-test
    spec:
      schedulerName: custom-gpu-scheduler
      containers:
      - name: ml-app
        image: tensorflow/tensorflow:2.8.0-gpu
        resources:
          requests:
            nvidia.com/gpu: "1"
          limits:
            nvidia.com/gpu: "1"
```

#### Validation
- Verify pods are scheduled on GPU nodes
- Check scheduler logs for custom logic execution
- Monitor GPU utilization across nodes

### Lab 2: Multi-Cluster Service Mesh with Istio

#### Objective
Set up a multi-cluster Istio service mesh with cross-cluster service discovery and traffic management.

#### Architecture
- Primary cluster: us-west-2
- Remote cluster: us-east-1
- Cross-cluster service communication

#### Steps

1. **Primary Cluster Setup**

```bash
# Install Istio on primary cluster
kubectl config use-context us-west-cluster
istioctl install --set values.pilot.env.PILOT_ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY=true

# Create namespace with Istio injection
kubectl create namespace bookinfo
kubectl label namespace bookinfo istio-injection=enabled

# Deploy sample application
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml -n bookinfo
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml -n bookinfo
```

2. **Remote Cluster Setup**

```bash
# Switch to remote cluster
kubectl config use-context us-east-cluster

# Create Istio secret for cross-cluster access
kubectl create secret generic cacerts -n istio-system \
  --from-file=root-cert.pem \
  --from-file=cert-chain.pem \
  --from-file=ca-cert.pem \
  --from-file=ca-key.pem

# Install Istio on remote cluster
istioctl install --set values.istiodRemote.enabled=true \
  --set values.pilot.env.PILOT_ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY=true \
  --set global.meshID=mesh1 \
  --set global.network=network2
```

3. **Configure Cross-Cluster Discovery**

```yaml
# Create endpoints for remote services
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: remote-reviews
  namespace: bookinfo
spec:
  hosts:
  - reviews.bookinfo.remote
  location: MESH_EXTERNAL
  ports:
  - number: 9080
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: reviews.bookinfo.svc.cluster.local
    network: network2
    ports:
      http: 9080
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: reviews-destination
  namespace: bookinfo
spec:
  host: reviews.bookinfo.remote
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
```

4. **Traffic Management**

```yaml
# Virtual service for cross-cluster routing
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews-route
  namespace: bookinfo
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        region:
          exact: east
    route:
    - destination:
        host: reviews.bookinfo.remote
      weight: 100
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 50
    - destination:
        host: reviews.bookinfo.remote
      weight: 50
```

#### Validation
- Test cross-cluster service communication
- Verify traffic distribution
- Check observability metrics in Grafana/Kiali

### Lab 3: GitOps with ArgoCD and Kustomize

#### Objective
Implement a complete GitOps workflow with ArgoCD, including multi-environment deployments and automated rollbacks.

#### Repository Structure
```
k8s-gitops/
├── applications/
│   ├── base/
│   └── overlays/
│       ├── development/
│       ├── staging/
│       └── production/
├── infrastructure/
│   ├── base/
│   └── overlays/
└── clusters/
    ├── development/
    ├── staging/
    └── production/
```

#### Steps

1. **ArgoCD Installation**

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

2. **Application Configuration**

```yaml
# applications/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- configmap.yaml

commonLabels:
  app: web-application
  version: v1.0.0
```

```yaml
# applications/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

replicas:
- name: web-app
  count: 5

images:
- name: web-app
  newTag: v1.2.3

patchesStrategicMerge:
- resources.yaml
- security.yaml
```

3. **ArgoCD Application**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-app-production
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/company/k8s-gitops
    targetRevision: HEAD
    path: applications/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

4. **Rollout Strategy**

```yaml
# Argo Rollouts canary deployment
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-app-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 20
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
      canaryService: web-app-canary
      stableService: web-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: web-app-vs
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: web-app:v1.0.0
```

#### Validation
- Deploy application through GitOps
- Test automated sync and rollback
- Verify canary deployment process

### Lab 4: Advanced Observability Stack

#### Objective
Deploy a comprehensive observability stack with Prometheus, Grafana, Jaeger, and custom metrics.

#### Components
- Prometheus Operator
- Grafana with custom dashboards
- Jaeger for distributed tracing
- Custom metrics collection

#### Steps

1. **Prometheus Stack Installation**

```bash
# Add Prometheus community Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

2. **Custom ServiceMonitor**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: payment-service-monitor
  namespace: monitoring
  labels:
    app: payment-service
spec:
  selector:
    matchLabels:
      app: payment-service
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    honorLabels: true
  namespaceSelector:
    matchNames:
    - production
```

3. **Custom Grafana Dashboard**

```json
{
  "dashboard": {
    "id": null,
    "title": "Payment Service Metrics",
    "tags": ["payment", "microservice"],
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"payment-service\"}[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"payment-service\"}[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

4. **Jaeger Installation**

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-production
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      resources:
        requests:
          cpu: "1"
          memory: "2Gi"
        limits:
          cpu: "2"
          memory: "4Gi"
  collector:
    resources:
      requests:
        cpu: "100m"
        memory: "256Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
```

#### Validation
- Access Grafana dashboards
- Query custom metrics in Prometheus
- Trace requests through Jaeger
- Set up alerting rules

## Summary

This advanced container orchestration module covered enterprise-scale Kubernetes patterns including:

1. **Advanced Scheduling:** Custom schedulers, topology constraints, and resource management
2. **Production Architectures:** Real-world patterns from Spotify, Pinterest, Lyft, and Datadog  
3. **Advanced Features:** Admission controllers, CRDs, operators, and service mesh
4. **Security:** Pod security standards, RBAC, and secret management
5. **Disaster Recovery:** Backup strategies and high availability patterns
6. **Cost Optimization:** VPA, HPA, cluster autoscaling, and spot instances
7. **Hands-on Labs:** Practical implementation of complex scenarios

The module provides 350+ minutes of advanced content suitable for senior engineers working with enterprise Kubernetes deployments. Each section includes production-ready configurations and best practices derived from real-world implementations.