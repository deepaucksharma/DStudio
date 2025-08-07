# Kubernetes Distributed Patterns - Elite Engineering Module

*Advanced Kubernetes patterns for production-scale distributed systems (350+ minutes)*

## Module Overview

This elite module covers advanced Kubernetes patterns for distributed systems, focusing on production-grade deployments handling 1000+ nodes. Learn from real-world case studies and implement enterprise-grade solutions.

### Prerequisites
- Deep Kubernetes knowledge (CKA/CKAD level)
- Container orchestration experience
- Distributed systems fundamentals
- Production operations background

### Learning Outcomes
- Master advanced Kubernetes patterns for distributed systems
- Implement production-grade multi-tenant architectures
- Design resilient, scalable Kubernetes platforms
- Apply GitOps and progressive delivery strategies
- Optimize costs and performance at scale

---

## Part I: Advanced Kubernetes Patterns (120 minutes)

### 1. StatefulSets for Distributed Databases (25 minutes)

#### Pattern Overview
StatefulSets provide guarantees about ordering and uniqueness for stateful distributed applications, making them ideal for databases, message queues, and distributed storage systems.

#### Core Components

**StatefulSet Configuration:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cassandra
spec:
  serviceName: cassandra
  replicas: 3
  selector:
    matchLabels:
      app: cassandra
  template:
    metadata:
      labels:
        app: cassandra
    spec:
      terminationGracePeriodSeconds: 1800
      containers:
      - name: cassandra
        image: cassandra:3.11
        ports:
        - containerPort: 7000
          name: intra-node
        - containerPort: 7001
          name: tls-intra-node
        - containerPort: 7199
          name: jmx
        - containerPort: 9042
          name: cql
        resources:
          limits:
            cpu: "500m"
            memory: 1Gi
          requests:
            cpu: "500m"
            memory: 1Gi
        securityContext:
          capabilities:
            add:
              - IPC_LOCK
        lifecycle:
          preStop:
            exec:
              command: 
              - /bin/sh
              - -c
              - nodetool drain
        env:
          - name: MAX_HEAP_SIZE
            value: 512M
          - name: HEAP_NEWSIZE
            value: 100M
          - name: CASSANDRA_SEEDS
            value: "cassandra-0.cassandra.default.svc.cluster.local"
          - name: CASSANDRA_CLUSTER_NAME
            value: "K8Demo"
          - name: CASSANDRA_DC
            value: "DC1-K8Demo"
          - name: CASSANDRA_RACK
            value: "Rack1-K8Demo"
          - name: POD_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
        readinessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - /ready-probe.sh
          initialDelaySeconds: 15
          timeoutSeconds: 5
        volumeMounts:
        - name: cassandra-data
          mountPath: /cassandra_data
  volumeClaimTemplates:
  - metadata:
      name: cassandra-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

**Headless Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: cassandra
  name: cassandra
spec:
  clusterIP: None
  ports:
  - port: 9042
  selector:
    app: cassandra
```

#### Best Practices for StatefulSets

1. **Ordered Startup/Shutdown:**
```yaml
spec:
  podManagementPolicy: OrderedReady  # Default
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
```

2. **Persistent Volume Management:**
```yaml
volumeClaimTemplates:
- metadata:
    name: data
    annotations:
      volume.beta.kubernetes.io/storage-class: "fast-ssd"
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 100Gi
```

3. **Network Identity:**
```yaml
# Pod DNS: cassandra-0.cassandra.default.svc.cluster.local
# Stable hostname across restarts
```

#### Hands-on Exercise: Deploy MongoDB Replica Set
```bash
# Deploy MongoDB StatefulSet with authentication
kubectl apply -f mongodb-statefulset.yaml
kubectl exec -it mongodb-0 -- mongo --eval "rs.initiate()"
kubectl exec -it mongodb-0 -- mongo --eval "rs.add('mongodb-1.mongodb:27017')"
```

### 2. Operator Pattern for Complex Applications (30 minutes)

#### Custom Resource Definitions (CRDs)
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.stable.example.com
spec:
  group: stable.example.com
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
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              version:
                type: string
                pattern: '^[0-9]+\.[0-9]+\.[0-9]+$'
              backupSchedule:
                type: string
                pattern: '^[0-9*,-/ ]+$'
          status:
            type: object
            properties:
              phase:
                type: string
                enum: ["Pending", "Running", "Failed"]
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: databases
    singular: database
    kind: Database
```

#### Operator Controller (Go Example)
```go
package main

import (
    "context"
    "fmt"
    "time"

    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/util/intstr"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    
    stablev1 "github.com/example/database-operator/api/v1"
)

type DatabaseReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // Fetch the Database instance
    database := &stablev1.Database{}
    err := r.Get(ctx, req.NamespacedName, database)
    if err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Define desired StatefulSet
    statefulSet := &appsv1.StatefulSet{
        ObjectMeta: metav1.ObjectMeta{
            Name:      database.Name,
            Namespace: database.Namespace,
        },
    }

    // Create or Update StatefulSet
    op, err := ctrl.CreateOrUpdate(ctx, r.Client, statefulSet, func() error {
        return r.mutateStatefulSet(statefulSet, database)
    })

    if err != nil {
        return ctrl.Result{}, err
    }

    // Update status
    database.Status.Phase = "Running"
    database.Status.Replicas = database.Spec.Replicas
    
    if err := r.Status().Update(ctx, database); err != nil {
        return ctrl.Result{}, err
    }

    // Requeue after 30 seconds for status updates
    return ctrl.Result{RequeueAfter: time.Second * 30}, nil
}

func (r *DatabaseReconciler) mutateStatefulSet(sts *appsv1.StatefulSet, db *stablev1.Database) error {
    sts.Spec.Replicas = &db.Spec.Replicas
    sts.Spec.Selector = &metav1.LabelSelector{
        MatchLabels: map[string]string{
            "app": db.Name,
        },
    }
    
    sts.Spec.Template = corev1.PodTemplateSpec{
        ObjectMeta: metav1.ObjectMeta{
            Labels: map[string]string{
                "app": db.Name,
            },
        },
        Spec: corev1.PodSpec{
            Containers: []corev1.Container{
                {
                    Name:  "database",
                    Image: fmt.Sprintf("postgres:%s", db.Spec.Version),
                    Ports: []corev1.ContainerPort{
                        {
                            ContainerPort: 5432,
                            Name:          "postgres",
                        },
                    },
                    Env: []corev1.EnvVar{
                        {
                            Name:  "POSTGRES_DB",
                            Value: "myapp",
                        },
                        {
                            Name: "POSTGRES_PASSWORD",
                            ValueFrom: &corev1.EnvVarSource{
                                SecretKeyRef: &corev1.SecretKeySelector{
                                    LocalObjectReference: corev1.LocalObjectReference{
                                        Name: db.Name + "-secret",
                                    },
                                    Key: "password",
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    
    // Set owner reference
    return controllerutil.SetControllerReference(db, sts, r.Scheme)
}
```

#### Operator Deployment Pattern
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-operator
spec:
  replicas: 1
  selector:
    matchLabels:
      name: database-operator
  template:
    metadata:
      labels:
        name: database-operator
    spec:
      serviceAccountName: database-operator
      containers:
      - name: operator
        image: database-operator:latest
        command:
        - database-operator
        env:
        - name: WATCH_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: OPERATOR_NAME
          value: "database-operator"
```

### 3. Multi-Tenancy Strategies (30 minutes)

#### Namespace-Based Multi-Tenancy
```yaml
# Tenant namespace with resource quotas
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-acme
  labels:
    tenant: acme
    tier: premium
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-acme-quota
  namespace: tenant-acme
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    persistentvolumeclaims: "20"
    services: "10"
    secrets: "10"
    configmaps: "10"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-acme-limits
  namespace: tenant-acme
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

#### RBAC for Multi-Tenancy
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: tenant-acme
  name: tenant-admin
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims"]
  verbs: ["*"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "statefulsets", "daemonsets"]
  verbs: ["*"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses", "networkpolicies"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tenant-acme-admin-binding
  namespace: tenant-acme
subjects:
- kind: User
  name: acme-admin
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: tenant-admin
  apiGroup: rbac.authorization.k8s.io
```

#### Virtual Cluster Pattern (vCluster)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vcluster-config
data:
  values.yaml: |
    vcluster:
      image: rancher/k3s:v1.21.1-k3s1
    syncer:
      extraArgs:
        - --out-kube-config-server=https://my-vcluster.example.com
    storage:
      persistence: true
      size: 5Gi
    rbac:
      clusterRole:
        create: true
    multiNamespaceMode:
      enabled: true
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: my-vcluster
spec:
  serviceName: my-vcluster-headless
  replicas: 1
  selector:
    matchLabels:
      app: vcluster
      release: my-vcluster
  template:
    metadata:
      labels:
        app: vcluster
        release: my-vcluster
    spec:
      serviceAccountName: vc-my-vcluster
      containers:
      - image: loftsh/vcluster:0.8.0
        name: vcluster
        args:
          - --service-name=my-vcluster
          - --suffix=my-vcluster
          - --owning-statefulset=my-vcluster
        env:
        - name: VCLUSTER_NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
```

### 4. Service Mesh Integration (35 minutes)

#### Istio Integration Patterns
```yaml
# Service mesh deployment with Istio
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    istio-injection: enabled
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservice-a
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: microservice-a
      version: v1
  template:
    metadata:
      labels:
        app: microservice-a
        version: v1
    spec:
      containers:
      - name: app
        image: microservice-a:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: microservice-a-vs
  namespace: production
spec:
  hosts:
  - microservice-a
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: microservice-a
        subset: v2
      weight: 100
  - route:
    - destination:
        host: microservice-a
        subset: v1
      weight: 90
    - destination:
        host: microservice-a
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: microservice-a-dr
  namespace: production
spec:
  host: microservice-a
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 2
    circuitBreaker:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

#### Linkerd Service Profile
```yaml
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: microservice-a.production.svc.cluster.local
  namespace: production
spec:
  routes:
  - name: health
    condition:
      method: GET
      pathRegex: /health
    timeout: 5s
  - name: api_v1
    condition:
      method: GET
      pathRegex: /api/v1/.*
    timeout: 30s
    retryBudget:
      retryRatio: 0.2
      minRetriesPerSecond: 10
      ttl: 10s
  - name: api_v1_mutations
    condition:
      method: POST
      pathRegex: /api/v1/.*
    timeout: 60s
    retryBudget:
      retryRatio: 0.1
      minRetriesPerSecond: 5
      ttl: 10s
```

---

## Part II: Autoscaling and Resource Management (90 minutes)

### 1. Horizontal Pod Autoscaler (HPA) (25 minutes)

#### Custom Metrics HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: microservice-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservice
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: messages_per_second
      target:
        type: AverageValue
        averageValue: "100"
  - type: External
    external:
      metric:
        name: queue_depth
        selector:
          matchLabels:
            queue: worker-queue
      target:
        type: AverageValue
        averageValue: "30"
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
        periodSeconds: 60
      - type: Pods
        value: 10
        periodSeconds: 60
      selectPolicy: Max
```

#### Prometheus Adapter for Custom Metrics
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: adapter-config
  namespace: monitoring
data:
  config.yaml: |
    rules:
    - seriesQuery: 'http_requests_per_second{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        matches: "^(.*)_per_second$"
        as: "${1}"
      metricsQuery: 'sum(<<.Series>>{<<.LabelMatchers>>}) by (<<.GroupBy>>)'
    - seriesQuery: 'queue_depth{namespace!="",deployment!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          deployment: {resource: "deployment"}
      name:
        as: "queue_depth"
      metricsQuery: 'avg(<<.Series>>{<<.LabelMatchers>>}) by (<<.GroupBy>>)'
```

### 2. Vertical Pod Autoscaler (VPA) (20 minutes)

#### VPA Configuration
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: microservice-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservice
  updatePolicy:
    updateMode: "Auto"  # Off, Initial, Recreation, Auto
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
      mode: Auto
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
    - containerName: sidecar
      mode: Off
```

#### VPA with PDB for Safe Updates
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: microservice-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: microservice
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: microservice-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservice
  updatePolicy:
    updateMode: "Recreation"
    minReplicas: 3  # Ensures PDB compliance
  resourcePolicy:
    containerPolicies:
    - containerName: app
      maxAllowed:
        cpu: 2
        memory: 4Gi
      controlledResources: ["memory"]  # Only scale memory
      controlledValues: RequestsAndLimits
```

### 3. Cluster Autoscaler (25 minutes)

#### Cluster Autoscaler Deployment
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
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
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
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --max-node-provision-time=15m
        - --scan-interval=10s
        env:
        - name: AWS_REGION
          value: us-west-2
```

#### Node Pool Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-status
  namespace: kube-system
data:
  nodes.max: "1000"
  nodes.min: "3"
  scale-down-delay-after-add: "10m"
  scale-down-unneeded-time: "10m"
  skip-nodes-with-local-storage: "false"
  skip-nodes-with-system-pods: "false"
---
# Node affinity for workload placement
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compute-intensive-workload
spec:
  template:
    spec:
      nodeSelector:
        node-type: compute-optimized
      tolerations:
      - key: compute-intensive
        operator: Equal
        value: "true"
        effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/arch
                operator: In
                values: ["amd64"]
              - key: node.kubernetes.io/instance-type
                operator: In
                values: ["c5.xlarge", "c5.2xlarge"]
```

### 4. Job and CronJob Patterns (20 minutes)

#### Parallel Processing Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-data-processing
spec:
  parallelism: 10
  completions: 100
  backoffLimit: 3
  activeDeadlineSeconds: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: processor
        image: data-processor:latest
        command:
        - /bin/sh
        - -c
        - |
          JOB_INDEX=${JOB_COMPLETION_INDEX:-0}
          echo "Processing batch $JOB_INDEX"
          ./process-data.sh --batch=$JOB_INDEX --total-batches=100
        env:
        - name: BATCH_SIZE
          value: "1000"
        - name: S3_BUCKET
          value: "data-processing-bucket"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2
            memory: 4Gi
        volumeMounts:
        - name: temp-storage
          mountPath: /tmp
      volumes:
      - name: temp-storage
        emptyDir:
          sizeLimit: 10Gi
```

#### Advanced CronJob with Monitoring
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-data-backup
spec:
  schedule: "0 2 * * *"
  timeZone: "UTC"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 7200
      template:
        metadata:
          annotations:
            prometheus.io/scrape: "true"
            prometheus.io/port: "8080"
        spec:
          restartPolicy: OnFailure
          serviceAccountName: backup-service-account
          containers:
          - name: backup
            image: backup-tool:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup at $(date)"
              # Export Prometheus metrics
              echo "backup_start_time $(date +%s)" | curl -X POST --data-binary @- http://pushgateway:9091/metrics/job/daily-backup/instance/$HOSTNAME
              
              # Perform backup
              if ./backup-script.sh; then
                echo "backup_success 1" | curl -X POST --data-binary @- http://pushgateway:9091/metrics/job/daily-backup/instance/$HOSTNAME
                echo "Backup completed successfully at $(date)"
              else
                echo "backup_success 0" | curl -X POST --data-binary @- http://pushgateway:9091/metrics/job/daily-backup/instance/$HOSTNAME
                echo "Backup failed at $(date)"
                exit 1
              fi
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-credentials
                  key: url
            - name: S3_BUCKET
              value: "backup-storage"
            resources:
              requests:
                cpu: 100m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 1Gi
```

---

## Part III: Production Case Studies (80 minutes)

### 1. Spotify's Kubernetes Migration (20 minutes)

#### Background
Spotify migrated from a traditional service-oriented architecture to Kubernetes, handling millions of users and petabytes of data across multiple regions.

#### Architecture Overview
```yaml
# Spotify's Service Architecture Pattern
apiVersion: v1
kind: Namespace
metadata:
  name: music-streaming
  labels:
    team: audio
    criticality: high
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audio-transcoding-service
  namespace: music-streaming
  annotations:
    spotify.com/team: "audio-platform"
    spotify.com/on-call: "audio-platform-oncall@spotify.com"
spec:
  replicas: 50
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
  selector:
    matchLabels:
      app: audio-transcoding
  template:
    metadata:
      labels:
        app: audio-transcoding
        version: v2.1.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: audio-transcoding-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: transcoding-service
        image: spotify/audio-transcoding:v2.1.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: grpc
        env:
        - name: SERVICE_NAME
          value: "audio-transcoding-service"
        - name: REGION
          valueFrom:
            fieldRef:
              fieldPath: metadata.labels['topology.kubernetes.io/region']
        - name: ZONE
          valueFrom:
            fieldRef:
              fieldPath: metadata.labels['topology.kubernetes.io/zone']
        resources:
          requests:
            cpu: 2
            memory: 4Gi
            ephemeral-storage: 5Gi
          limits:
            cpu: 4
            memory: 8Gi
            ephemeral-storage: 10Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: temp-storage
          mountPath: /tmp
        - name: config
          mountPath: /etc/config
          readOnly: true
      volumes:
      - name: temp-storage
        emptyDir:
          sizeLimit: 5Gi
      - name: config
        configMap:
          name: audio-transcoding-config
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values: ["audio-transcoding"]
              topologyKey: kubernetes.io/hostname
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values: ["compute-optimized"]
```

#### Spotify's Multi-Region Strategy
```yaml
# Cross-region service discovery
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: audio-transcoding-us-east
  namespace: music-streaming
spec:
  hosts:
  - audio-transcoding.us-east.spotify.internal
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  - number: 9090
    name: grpc
    protocol: GRPC
  resolution: DNS
  location: MESH_EXTERNAL
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: audio-transcoding-failover
  namespace: music-streaming
spec:
  hosts:
  - audio-transcoding
  http:
  - match:
    - headers:
        region:
          exact: us-west
    route:
    - destination:
        host: audio-transcoding
      weight: 100
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
    retries:
      attempts: 3
      perTryTimeout: 10s
      retryOn: gateway-error,connect-failure,refused-stream
  - route:
    - destination:
        host: audio-transcoding.us-east.spotify.internal
      weight: 10
    - destination:
        host: audio-transcoding
      weight: 90
```

#### Key Lessons from Spotify
1. **Gradual Migration**: Service-by-service migration with feature flags
2. **Team Autonomy**: Each team owns their Kubernetes configuration
3. **Observability**: Comprehensive monitoring and distributed tracing
4. **Cost Optimization**: Node right-sizing and resource bin-packing

### 2. Airbnb's Kubernetes Platform (20 minutes)

#### Airbnb's Service Mesh Architecture
```yaml
# Airbnb's service template pattern
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: airbnb-services
  namespace: argocd
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: production
  - list:
      elements:
      - service: booking-service
        team: booking
        replicas: 20
        cpu: 1
        memory: 2Gi
      - service: search-service
        team: search
        replicas: 50
        cpu: 2
        memory: 4Gi
      - service: payment-service
        team: payments
        replicas: 10
        cpu: 500m
        memory: 1Gi
  template:
    metadata:
      name: '{{service}}-{{name}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/airbnb/k8s-service-templates
        targetRevision: HEAD
        path: services/{{service}}
        helm:
          parameters:
          - name: service.name
            value: '{{service}}'
          - name: service.team
            value: '{{team}}'
          - name: deployment.replicas
            value: '{{replicas}}'
          - name: resources.cpu
            value: '{{cpu}}'
          - name: resources.memory
            value: '{{memory}}'
          - name: cluster.name
            value: '{{name}}'
      destination:
        server: '{{server}}'
        namespace: '{{service}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

#### Airbnb's Multi-Tenancy Model
```yaml
# Per-team namespace with strict resource limits
apiVersion: v1
kind: Namespace
metadata:
  name: team-booking
  labels:
    team: booking
    cost-center: engineering
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-booking-quota
  namespace: team-booking
spec:
  hard:
    requests.cpu: "500"
    requests.memory: 1000Gi
    limits.cpu: "1000"
    limits.memory: 2000Gi
    persistentvolumeclaims: "100"
    services: "50"
    secrets: "50"
    configmaps: "50"
    count/deployments.apps: "50"
    count/jobs.batch: "20"
---
# Network policy for team isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: team-booking-isolation
  namespace: team-booking
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    - namespaceSelector:
        matchLabels:
          team: booking
    - namespaceSelector:
        matchLabels:
          team: platform
    - namespaceSelector:
        matchLabels:
          name: monitoring
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - namespaceSelector: {}
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

### 3. Pinterest's Multi-Region Kubernetes (20 minutes)

#### Pinterest's Regional Architecture
```yaml
# Pinterest's cross-region deployment strategy
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: pinterest-ads-service-us-west
  namespace: argocd
spec:
  project: ads-platform
  source:
    repoURL: https://github.com/pinterest/kubernetes-manifests
    targetRevision: HEAD
    path: services/ads-service
    helm:
      parameters:
      - name: global.region
        value: us-west-2
      - name: global.datacenter
        value: pdx
      - name: service.replicas
        value: "100"
      - name: service.resources.cpu
        value: "2"
      - name: service.resources.memory
        value: "4Gi"
      - name: database.region
        value: us-west-2
      - name: redis.cluster
        value: ads-redis-pdx
  destination:
    server: https://k8s-us-west-2.pinterest.com
    namespace: ads-service
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
  revisionHistoryLimit: 10
---
# Cross-region service mesh configuration
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: ads-service-cross-region
  namespace: ads-service
spec:
  hosts:
  - ads-service.us-east-1.pinterest.internal
  - ads-service.eu-west-1.pinterest.internal
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_EXTERNAL
```

#### Pinterest's Data Locality Strategy
```yaml
# Data-aware pod scheduling
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ads-ml-training
  namespace: ads-service
spec:
  replicas: 20
  selector:
    matchLabels:
      app: ads-ml-training
  template:
    metadata:
      labels:
        app: ads-ml-training
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values: ["us-west-2a", "us-west-2b"]  # Same AZ as data
              - key: node-type
                operator: In
                values: ["ml-optimized"]
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values: ["ads-ml-training"]
              topologyKey: kubernetes.io/hostname
      containers:
      - name: ml-trainer
        image: pinterest/ads-ml-trainer:latest
        resources:
          requests:
            cpu: 8
            memory: 32Gi
            nvidia.com/gpu: 1
          limits:
            cpu: 16
            memory: 64Gi
            nvidia.com/gpu: 1
        volumeMounts:
        - name: training-data
          mountPath: /data
          readOnly: true
        - name: model-output
          mountPath: /models
      volumes:
      - name: training-data
        persistentVolumeClaim:
          claimName: ads-training-data-pvc
      - name: model-output
        persistentVolumeClaim:
          claimName: ads-model-output-pvc
```

### 4. Shopify's Black Friday Scaling (20 minutes)

#### Shopify's Auto-scaling Strategy
```yaml
# Shopify's predictive scaling for Black Friday
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: checkout-service-hpa
  namespace: commerce
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: checkout-service
  minReplicas: 50  # Pre-scaled for Black Friday
  maxReplicas: 1000
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Conservative during high-traffic
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: checkout_requests_per_second
      target:
        type: AverageValue
        averageValue: "50"  # Lower threshold for responsiveness
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 600  # Longer stabilization
      policies:
      - type: Percent
        value: 5  # Very conservative scale-down
        periodSeconds: 120
    scaleUp:
      stabilizationWindowSeconds: 30  # Fast scale-up
      policies:
      - type: Percent
        value: 100  # Aggressive scale-up
        periodSeconds: 30
      - type: Pods
        value: 50  # Add many pods quickly
        periodSeconds: 30
---
# Pre-warmed node pools
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-config
  namespace: kube-system
data:
  black-friday.yaml: |
    # Special scaling configuration for Black Friday
    scale-down-enabled: false  # Disable scale-down during event
    max-node-provision-time: 5m
    scale-down-delay-after-add: 30m
    nodes.min: 200  # Pre-warmed minimum
    nodes.max: 2000  # Increased maximum
```

#### Shopify's Circuit Breaker Pattern
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service-circuit-breaker
  namespace: commerce
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 500
        maxRequestsPerConnection: 10
        consecutiveGatewayErrors: 5
        interval: 10s
        baseEjectionTime: 30s
        maxEjectionPercent: 50
    outlierDetection:
      consecutive5xxErrors: 3
      consecutiveGatewayErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
```

---

## Part IV: Security and Compliance (60 minutes)

### 1. Pod Security Standards and OPA Gatekeeper (25 minutes)

#### Pod Security Standards
```yaml
# Restricted Pod Security Standard
apiVersion: v1
kind: Namespace
metadata:
  name: secure-workloads
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
---
# Compliant deployment under restricted standard
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: secure-workloads
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
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: app
        image: secure-app:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        ports:
        - containerPort: 8080
          name: http
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
```

#### OPA Gatekeeper Policies
```yaml
# Gatekeeper constraint template
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredsecuritycontext
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredSecurityContext
      validation:
        type: object
        properties:
          runAsNonRoot:
            type: boolean
          runAsUser:
            type: object
            properties:
              rule:
                type: string
                enum: ["MustRunAs", "MustRunAsNonRoot", "RunAsAny"]
              ranges:
                type: array
                items:
                  type: object
                  properties:
                    min:
                      type: integer
                    max:
                      type: integer
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredsecuritycontext
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.securityContext.runAsNonRoot
        msg := "Container must run as non-root user"
      }
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        container.securityContext.runAsUser == 0
        msg := "Container must not run as root (UID 0)"
      }
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        container.securityContext.allowPrivilegeEscalation != false
        msg := "Container must not allow privilege escalation"
      }
---
# Apply the constraint
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredSecurityContext
metadata:
  name: must-run-as-nonroot
spec:
  match:
    kinds:
    - apiGroups: ["apps"]
      kinds: ["Deployment", "StatefulSet", "DaemonSet"]
    excludedNamespaces: ["kube-system", "gatekeeper-system"]
  parameters:
    runAsNonRoot: true
    runAsUser:
      rule: "MustRunAsNonRoot"
```

#### Advanced OPA Policy for Resource Limits
```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredresources
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredResources
      validation:
        type: object
        properties:
          limits:
            type: object
            properties:
              cpu:
                type: string
              memory:
                type: string
          requests:
            type: object
            properties:
              cpu:
                type: string
              memory:
                type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredresources
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.requests.cpu
        msg := sprintf("Container '%v' must specify CPU requests", [container.name])
      }
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.requests.memory
        msg := sprintf("Container '%v' must specify memory requests", [container.name])
      }
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.limits.cpu
        msg := sprintf("Container '%v' must specify CPU limits", [container.name])
      }
      
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.limits.memory
        msg := sprintf("Container '%v' must specify memory limits", [container.name])
      }
```

### 2. Network Policies for Zero-Trust (20 minutes)

#### Comprehensive Network Policy Strategy
```yaml
# Default deny all ingress and egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# Allow specific ingress to web tier
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-tier-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Metrics
---
# Allow web tier to communicate with app tier
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-to-app-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 8080
  - to: []  # Allow DNS
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
---
# Allow app tier ingress from web tier
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-tier-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Metrics
---
# Allow app tier to communicate with database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-to-db-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []  # Allow DNS and external HTTPS
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
    - protocol: TCP
      port: 443
---
# Database tier - only allow ingress from app tier
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-tier-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 5432
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Metrics
  egress:
  - to: []  # Allow DNS only
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

#### Calico Global Network Policy
```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-high-risk-egress
spec:
  order: 100
  selector: all()
  types:
  - Egress
  egress:
  # Deny access to cloud metadata services
  - action: Deny
    destination:
      nets:
      - 169.254.169.254/32  # AWS metadata service
      - 169.254.169.253/32  # AWS metadata service v2
    protocol: TCP
  # Deny access to private networks (except cluster networks)
  - action: Deny
    destination:
      nets:
      - 10.0.0.0/8
      - 172.16.0.0/12
      - 192.168.0.0/16
    notSelector: k8s-app == "kube-dns"
---
# Allow specific egress for applications
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: allow-external-apis
  namespace: production
spec:
  order: 200
  selector: app == "external-integrations"
  types:
  - Egress
  egress:
  - action: Allow
    destination:
      domains:
      - "api.stripe.com"
      - "api.twilio.com"
      - "*.amazonaws.com"
    protocol: TCP
    destination:
      ports: [443]
```

### 3. Admission Controllers and Image Security (15 minutes)

#### Custom Admission Controller for Image Scanning
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionWebhook
metadata:
  name: image-security-webhook
webhooks:
- name: image-security.security.company.com
  clientConfig:
    service:
      name: image-security-webhook
      namespace: security-system
      path: "/validate"
  rules:
  - operations: ["CREATE", "UPDATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  - operations: ["CREATE", "UPDATE"]
    apiGroups: ["apps"]
    apiVersions: ["v1"]
    resources: ["deployments", "statefulsets", "daemonsets"]
  admissionReviewVersions: ["v1", "v1beta1"]
  sideEffects: None
  failurePolicy: Fail
---
# Image security webhook service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-security-webhook
  namespace: security-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: image-security-webhook
  template:
    metadata:
      labels:
        app: image-security-webhook
    spec:
      serviceAccountName: image-security-webhook
      containers:
      - name: webhook
        image: security/image-webhook:v1.0.0
        ports:
        - containerPort: 8443
        env:
        - name: TLS_CERT_FILE
          value: "/etc/certs/tls.crt"
        - name: TLS_KEY_FILE
          value: "/etc/certs/tls.key"
        - name: REGISTRY_WHITELIST
          value: "gcr.io/company,registry.company.com"
        - name: SCAN_TIMEOUT
          value: "30s"
        volumeMounts:
        - name: certs
          mountPath: "/etc/certs"
          readOnly: true
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: certs
        secret:
          secretName: image-security-webhook-certs
```

#### Falco Runtime Security Rules
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules
  namespace: falco-system
data:
  custom_rules.yaml: |
    # Detect privilege escalation attempts
    - rule: Detect Privilege Escalation
      desc: Detect attempts to escalate privileges
      condition: >
        spawned_process and
        (proc.name in (su, sudo, doas) or
         proc.cmdline contains "chmod +s" or
         proc.cmdline contains "setuid")
      output: >
        Privilege escalation attempt detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: WARNING
      tags: [process, privilege_escalation]
    
    # Detect container escape attempts
    - rule: Container Escape Attempt
      desc: Detect attempts to escape container
      condition: >
        spawned_process and
        (proc.cmdline contains "docker" or
         proc.cmdline contains "runc" or
         proc.cmdline contains "kubectl" or
         proc.name in (nsenter, chroot))
      output: >
        Container escape attempt detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [process, container_escape]
    
    # Detect crypto mining
    - rule: Crypto Mining Activity
      desc: Detect cryptocurrency mining activity
      condition: >
        spawned_process and
        (proc.name in (xmrig, t-rex, claymore, cgminer, bfgminer) or
         proc.cmdline contains "stratum" or
         proc.cmdline contains "mining" or
         proc.cmdline contains "hashrate")
      output: >
        Cryptocurrency mining detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL
      tags: [process, crypto_mining]
```

---

## Part V: Troubleshooting and Monitoring (50 minutes)

### 1. Advanced Debugging Techniques (25 minutes)

#### Debug Pod for Network Troubleshooting
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: netshoot-debug
  namespace: production
spec:
  serviceAccountName: debug-pod-sa
  containers:
  - name: netshoot
    image: nicolaka/netshoot:latest
    command: ["/bin/bash"]
    args: ["-c", "sleep 3600"]
    securityContext:
      capabilities:
        add: ["NET_ADMIN", "NET_RAW"]
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi
    volumeMounts:
    - name: debug-scripts
      mountPath: /debug-scripts
  volumes:
  - name: debug-scripts
    configMap:
      name: debug-scripts
      defaultMode: 0755
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: debug-scripts
data:
  network-debug.sh: |
    #!/bin/bash
    echo "=== Network Debug Script ==="
    echo "Pod IP: $(hostname -i)"
    echo "DNS Resolution:"
    nslookup kubernetes.default.svc.cluster.local
    echo "Connectivity Tests:"
    curl -v telnet://kubernetes.default.svc.cluster.local:443
    echo "Network Interfaces:"
    ip addr show
    echo "Routing Table:"
    ip route show
    echo "IPTables Rules:"
    iptables -L -n
  
  resource-debug.sh: |
    #!/bin/bash
    echo "=== Resource Debug Script ==="
    echo "CPU Usage:"
    cat /proc/loadavg
    echo "Memory Usage:"
    free -h
    echo "Disk Usage:"
    df -h
    echo "Running Processes:"
    ps aux
```

#### Application Debug Sidecar Pattern
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-debug-sidecar
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      shareProcessNamespace: true
      containers:
      - name: main-app
        image: myapp:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1
            memory: 2Gi
        volumeMounts:
        - name: shared-data
          mountPath: /shared
      - name: debug-sidecar
        image: debug-tools:latest
        command: ["/bin/bash"]
        args: ["-c", "sleep infinity"]
        securityContext:
          capabilities:
            add: ["SYS_PTRACE"]
        env:
        - name: TARGET_PID
          value: "1"  # PID of main container
        volumeMounts:
        - name: shared-data
          mountPath: /shared
        - name: debug-tools
          mountPath: /debug-tools
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: shared-data
        emptyDir: {}
      - name: debug-tools
        configMap:
          name: debug-tools-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: debug-tools-config
data:
  profile-app.sh: |
    #!/bin/bash
    # Profile the main application
    echo "Starting application profiling..."
    
    # Get process info
    ps aux | grep -v grep | grep java
    
    # CPU profiling with perf
    perf record -p $(pgrep java) -g -o /shared/perf.data sleep 30
    
    # Memory dump
    jmap -dump:live,format=b,file=/shared/heap.hprof $(pgrep java)
    
    # Thread dump
    jstack $(pgrep java) > /shared/threads.dump
    
    echo "Profiling complete. Files saved to /shared/"
```

### 2. Distributed Tracing and Observability (25 minutes)

#### Jaeger Distributed Tracing Setup
```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: production-jaeger
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      redundancyPolicy: SingleRedundancy
      resources:
        requests:
          cpu: 1
          memory: 2Gi
        limits:
          cpu: 2
          memory: 4Gi
      storage:
        size: 100Gi
        storageClassName: fast-ssd
    options:
      es:
        server-urls: http://elasticsearch:9200
        index-prefix: jaeger
  collector:
    replicas: 3
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1
        memory: 2Gi
    options:
      collector:
        queue-size: 5000
        num-workers: 100
  query:
    replicas: 2
    resources:
      requests:
        cpu: 200m
        memory: 512Mi
      limits:
        cpu: 500m
        memory: 1Gi
  agent:
    strategy: DaemonSet
    daemonset:
      useHostNetwork: true
      useHostPort: true
```

#### OpenTelemetry Collector Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      jaeger:
        protocols:
          grpc:
            endpoint: 0.0.0.0:14250
          thrift_http:
            endpoint: 0.0.0.0:14268
          thrift_compact:
            endpoint: 0.0.0.0:6831
          thrift_binary:
            endpoint: 0.0.0.0:6832
      prometheus:
        config:
          scrape_configs:
            - job_name: 'kubernetes-pods'
              kubernetes_sd_configs:
                - role: pod
              relabel_configs:
                - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                  action: keep
                  regex: true
    
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        limit_mib: 512
      resource:
        attributes:
          - key: cluster.name
            value: production
            action: upsert
          - key: k8s.cluster.name
            from_attribute: cluster.name
            action: insert
      k8sattributes:
        auth_type: "serviceAccount"
        passthrough: false
        filter:
          node_from_env_var: KUBE_NODE_NAME
        extract:
          metadata:
            - k8s.pod.name
            - k8s.pod.uid
            - k8s.deployment.name
            - k8s.namespace.name
            - k8s.node.name
            - k8s.service.name
        pod_association:
          - sources:
            - from: resource_attribute
              name: k8s.pod.ip
          - sources:
            - from: resource_attribute
              name: k8s.pod.uid
          - sources:
            - from: connection
    
    exporters:
      jaeger:
        endpoint: jaeger-collector:14250
        tls:
          insecure: true
      prometheus:
        endpoint: "0.0.0.0:8889"
        metric_relabeling_configs:
          - source_labels: [__name__]
            regex: 'otelcol_.*'
            action: drop
      logging:
        loglevel: info
    
    service:
      pipelines:
        traces:
          receivers: [otlp, jaeger]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [jaeger, logging]
        metrics:
          receivers: [otlp, prometheus]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [prometheus, logging]
        logs:
          receivers: [otlp]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [logging]
      extensions: [health_check, pprof, zpages]
```

#### Service Monitoring with Prometheus
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: microservices-monitoring
  namespace: monitoring
  labels:
    app: microservices
spec:
  selector:
    matchLabels:
      monitoring: "enabled"
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
    scrapeTimeout: 10s
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'go_.*|process_.*'
      action: drop  # Drop Go runtime metrics
    - sourceLabels: [__name__]
      regex: 'http_request_duration_seconds_.*'
      targetLabel: __name__
      replacement: 'http_request_duration_seconds'
  - port: health
    interval: 15s
    path: /health
    scrapeTimeout: 5s
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: microservice-alerts
  namespace: monitoring
spec:
  groups:
  - name: microservice.rules
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        (
          rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m])
        ) > 0.05
      for: 5m
      labels:
        severity: warning
        team: platform
      annotations:
        summary: "High error rate detected"
        description: "Service {{ $labels.service }} has error rate of {{ $value | humanizePercentage }}"
        runbook: "https://runbooks.company.com/high-error-rate"
    
    - alert: HighLatency
      expr: |
        histogram_quantile(0.95,
          rate(http_request_duration_seconds_bucket[5m])
        ) > 1
      for: 10m
      labels:
        severity: warning
        team: platform
      annotations:
        summary: "High latency detected"
        description: "Service {{ $labels.service }} 95th percentile latency is {{ $value }}s"
    
    - alert: PodCrashLooping
      expr: |
        rate(kube_pod_container_status_restarts_total[5m]) * 300 > 0
      for: 5m
      labels:
        severity: critical
        team: platform
      annotations:
        summary: "Pod is crash looping"
        description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"
```

---

## Hands-On Scenarios and Exercises

### Scenario 1: Production Incident Response (30 minutes)

#### Problem Statement
A critical microservice is experiencing:
- High latency (95th percentile > 5 seconds)
- Increased error rate (10% 5xx responses)
- Memory usage approaching limits
- Intermittent connection timeouts

#### Investigation Steps

1. **Initial Assessment:**
```bash
# Check pod status and events
kubectl get pods -l app=critical-service -o wide
kubectl describe pods -l app=critical-service

# Check service endpoints
kubectl get endpoints critical-service

# Check recent deployments
kubectl rollout history deployment/critical-service
```

2. **Resource Analysis:**
```bash
# Check resource usage
kubectl top pods -l app=critical-service
kubectl top nodes

# Check HPA status
kubectl get hpa critical-service-hpa -o yaml

# Check for resource constraints
kubectl describe nodes | grep -A 5 "Allocated resources"
```

3. **Network Troubleshooting:**
```bash
# Deploy debug pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: debug-critical-service
spec:
  containers:
  - name: debug
    image: nicolaka/netshoot
    command: ['sleep', '3600']
EOF

# Test connectivity
kubectl exec debug-critical-service -- nslookup critical-service
kubectl exec debug-critical-service -- curl -v http://critical-service:8080/health
```

4. **Log Analysis:**
```bash
# Check application logs
kubectl logs -l app=critical-service --tail=100 --since=10m

# Check for errors
kubectl logs -l app=critical-service --since=1h | grep -i error

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Resolution Strategy

```yaml
# Emergency scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: critical-service-emergency-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: critical-service
  minReplicas: 10  # Increased from 3
  maxReplicas: 50  # Increased from 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # Lowered from 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 60  # Lowered from 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30  # Faster scale-up
      policies:
      - type: Pods
        value: 5  # Add 5 pods at once
        periodSeconds: 30
```

### Scenario 2: Multi-Region Disaster Recovery (45 minutes)

#### Scenario Setup
Primary region (us-west-2) experiences a complete outage. Implement disaster recovery to secondary region (us-east-1).

#### Pre-requisites
```yaml
# Cross-region service mesh configuration
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: critical-service-dr
  namespace: production
spec:
  hosts:
  - critical-service.us-east-1.company.internal
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_EXTERNAL
---
# Disaster recovery virtual service
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: critical-service-dr
  namespace: production
spec:
  hosts:
  - critical-service
  http:
  - match:
    - headers:
        region:
          exact: us-east-1
    route:
    - destination:
        host: critical-service.us-east-1.company.internal
      weight: 100
  - fault:
      abort:
        percentage:
          value: 100
        httpStatus: 503
    route:
    - destination:
        host: critical-service
      weight: 100
```

#### Disaster Recovery Automation
```bash
#!/bin/bash
# dr-failover.sh - Automated disaster recovery script

set -euo pipefail

PRIMARY_REGION="us-west-2"
DR_REGION="us-east-1"
NAMESPACE="production"
SERVICE="critical-service"

echo "Starting disaster recovery failover..."

# 1. Scale up DR region
kubectl --context=$DR_REGION patch hpa $SERVICE-hpa -n $NAMESPACE -p '{"spec":{"minReplicas":10}}'

# 2. Update DNS to point to DR region
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.company.com",
      "Type": "CNAME",
      "TTL": 60,
      "ResourceRecords": [{"Value": "api-dr.us-east-1.company.com"}]
    }
  }]
}'

# 3. Update service mesh configuration
kubectl --context=$DR_REGION apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: critical-service-active
  namespace: $NAMESPACE
spec:
  hosts:
  - critical-service
  http:
  - route:
    - destination:
        host: critical-service
      weight: 100
EOF

# 4. Verify DR readiness
echo "Verifying DR region health..."
kubectl --context=$DR_REGION get pods -l app=$SERVICE -n $NAMESPACE
kubectl --context=$DR_REGION get svc $SERVICE -n $NAMESPACE

# 5. Update monitoring
curl -X POST https://monitoring.company.com/api/incidents \
  -H "Authorization: Bearer $MONITORING_TOKEN" \
  -d '{
    "title": "DR Failover Activated",
    "description": "Primary region outage, failed over to DR region",
    "status": "investigating",
    "priority": "high"
  }'

echo "Disaster recovery failover completed"
```

### Scenario 3: Cost Optimization Challenge (40 minutes)

#### Challenge
Reduce Kubernetes cluster costs by 40% while maintaining performance and reliability.

#### Analysis Tools
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-analysis-scripts
data:
  resource-usage.sh: |
    #!/bin/bash
    echo "=== Resource Usage Analysis ==="
    
    # Get resource requests vs limits
    kubectl get pods --all-namespaces -o json | jq -r '
      .items[] | 
      select(.status.phase == "Running") |
      {
        namespace: .metadata.namespace,
        name: .metadata.name,
        containers: [
          .spec.containers[] | {
            name: .name,
            requests: .resources.requests // {},
            limits: .resources.limits // {},
            image: .image
          }
        ]
      }
    ' | jq -s '
      group_by(.namespace) | 
      map({
        namespace: .[0].namespace,
        pods: length,
        total_cpu_requests: [.[].containers[].requests.cpu // "0"] | map(gsub("m"; "") | tonumber) | add,
        total_memory_requests: [.[].containers[].requests.memory // "0"] | map(gsub("Mi|Gi"; "") | tonumber) | add,
        containers: [.[].containers[]] | length
      })
    '
  
  node-utilization.sh: |
    #!/bin/bash
    echo "=== Node Utilization Analysis ==="
    
    # Check node utilization
    kubectl top nodes | awk 'NR>1 {
      cpu_usage = $3;
      mem_usage = $5;
      gsub(/%/, "", cpu_usage);
      gsub(/%/, "", mem_usage);
      if (cpu_usage < 50 && mem_usage < 50) {
        print $1 " - Low utilization: CPU " cpu_usage "%, Memory " mem_usage "%"
      }
    }'
    
    # Check for over-provisioned pods
    kubectl get pods --all-namespaces -o json | jq -r '
      .items[] |
      select(.status.phase == "Running") |
      .spec.containers[] |
      select((.resources.requests.cpu // "0m" | gsub("m"; "") | tonumber) > 1000) |
      "Over-provisioned CPU: " + .name
    '
```

#### Optimization Strategies

1. **Right-sizing Containers:**
```yaml
# VPA recommendations for right-sizing
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: cost-optimization-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: over-provisioned-service
  updatePolicy:
    updateMode: "Off"  # Recommendation only
  resourcePolicy:
    containerPolicies:
    - containerName: main
      maxAllowed:
        cpu: 2
        memory: 4Gi
      minAllowed:
        cpu: 100m
        memory: 128Mi
```

2. **Spot Instance Integration:**
```yaml
apiVersion: v1
kind: Node
metadata:
  name: spot-node-template
  labels:
    node-type: spot
    kubernetes.io/arch: amd64
spec:
  taints:
  - key: spot-instance
    value: "true"
    effect: NoSchedule
---
# Deployment for spot-tolerant workloads
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-processor-spot
spec:
  replicas: 5
  selector:
    matchLabels:
      app: batch-processor
  template:
    spec:
      tolerations:
      - key: spot-instance
        operator: Equal
        value: "true"
        effect: NoSchedule
      nodeSelector:
        node-type: spot
      containers:
      - name: processor
        image: batch-processor:latest
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi
```

3. **Cluster Autoscaler Optimization:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-config
data:
  cluster-autoscaler-config.yaml: |
    # Cost-optimized cluster autoscaler configuration
    scale-down-enabled: true
    scale-down-delay-after-add: 2m  # Faster scale-down
    scale-down-unneeded-time: 2m    # Aggressive scale-down
    skip-nodes-with-local-storage: false
    skip-nodes-with-system-pods: false
    expander: least-waste           # Cost-optimized expansion
    max-node-provision-time: 5m
    nodes-per-zone: 10
    balance-similar-node-groups: true
```

---

## Advanced Topics and Future Patterns

### Serverless Kubernetes with Knative

```yaml
# Knative service for event-driven workloads
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: event-processor
  namespace: serverless
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "100"
        autoscaling.knative.dev/target: "10"
        autoscaling.knative.dev/scaleDownDelay: "30s"
        autoscaling.knative.dev/window: "60s"
    spec:
      containerConcurrency: 10
      timeoutSeconds: 300
      containers:
      - image: event-processor:latest
        env:
        - name: TARGET
          value: "Event Processing Service"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        ports:
        - containerPort: 8080
          protocol: TCP
```

### Edge Computing with K3s

```yaml
# Edge deployment configuration
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: edge-data-collector
  namespace: edge-computing
spec:
  selector:
    matchLabels:
      app: edge-data-collector
  template:
    metadata:
      labels:
        app: edge-data-collector
    spec:
      hostNetwork: true
      hostPID: true
      tolerations:
      - key: node-role.kubernetes.io/edge
        operator: Exists
        effect: NoSchedule
      nodeSelector:
        node-type: edge
      containers:
      - name: collector
        image: edge-collector:latest
        securityContext:
          privileged: true
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: CLUSTER_ENDPOINT
          value: "https://central-cluster.company.com"
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
```

### Machine Learning Workloads

```yaml
# ML training job with GPU resources
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-training-job
  namespace: ml-platform
spec:
  parallelism: 4
  completions: 1
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      nodeSelector:
        accelerator: nvidia-tesla-v100
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      containers:
      - name: ml-trainer
        image: ml-training:latest
        command:
        - python
        - train.py
        - --epochs=100
        - --batch-size=32
        - --model-dir=/models
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0,1,2,3"
        - name: NCCL_DEBUG
          value: "INFO"
        resources:
          requests:
            nvidia.com/gpu: 4
            cpu: 16
            memory: 64Gi
          limits:
            nvidia.com/gpu: 4
            cpu: 32
            memory: 128Gi
        volumeMounts:
        - name: dataset
          mountPath: /data
        - name: models
          mountPath: /models
        - name: shm
          mountPath: /dev/shm
      volumes:
      - name: dataset
        persistentVolumeClaim:
          claimName: ml-dataset-pvc
      - name: models
        persistentVolumeClaim:
          claimName: ml-models-pvc
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: 8Gi
```

## Module Summary and Best Practices

### Production Readiness Checklist

- [ ] Resource requests and limits defined for all containers
- [ ] Liveness and readiness probes configured
- [ ] Pod disruption budgets in place
- [ ] Network policies implemented for zero-trust
- [ ] Security contexts configured (non-root, read-only filesystem)
- [ ] Secrets properly managed (external secret management)
- [ ] Monitoring and alerting configured
- [ ] Distributed tracing implemented
- [ ] Disaster recovery procedures tested
- [ ] Cost optimization measures implemented
- [ ] Compliance requirements met (PSS, OPA policies)
- [ ] Documentation and runbooks updated

### Key Performance Metrics

1. **Reliability Metrics:**
   - Service availability (99.9%+)
   - Mean time to recovery (MTTR < 15 minutes)
   - Error rate (<0.1%)

2. **Performance Metrics:**
   - Response time (p95 < 100ms for APIs)
   - Throughput (requests/second)
   - Resource utilization (60-80% CPU/Memory)

3. **Cost Metrics:**
   - Cost per request
   - Resource efficiency
   - Spot instance utilization

### Advanced Patterns Summary

This module covered enterprise-grade Kubernetes patterns essential for production deployments at scale. Key takeaways include:

1. **StatefulSets** for distributed databases with persistent storage and ordered deployment
2. **Operators** for managing complex applications with custom logic
3. **Multi-tenancy** strategies using namespaces, RBAC, and resource quotas
4. **Service mesh** integration for advanced traffic management and security
5. **Comprehensive autoscaling** with HPA, VPA, and cluster autoscaler
6. **Production case studies** from industry leaders showing real-world implementations
7. **Security best practices** with PSS, OPA, and network policies
8. **Observability** with distributed tracing and comprehensive monitoring
9. **Cost optimization** techniques for efficient resource utilization
10. **Disaster recovery** strategies for multi-region deployments

These patterns form the foundation for running Kubernetes at enterprise scale, handling thousands of nodes and mission-critical workloads.

---

*Total learning time: 350+ minutes*
*Target audience: Senior DevOps Engineers, Platform Engineers, Cloud Architects*
*Certification preparation: CKA, CKAD, CKS*