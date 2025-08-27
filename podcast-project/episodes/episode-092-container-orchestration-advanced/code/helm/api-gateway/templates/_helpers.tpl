{{/*
Helm template helpers for Indian E-commerce API Gateway
Episode 092: Container Orchestration - Helm Helpers
*/}}

{{/*
Expand the name of the chart.
*/}}
{{- define "api-gateway.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "api-gateway.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "api-gateway.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels for all resources
*/}}
{{- define "api-gateway.labels" -}}
helm.sh/chart: {{ include "api-gateway.chart" . }}
{{ include "api-gateway.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: flipkart-api-gateway
{{- with .Values.global.region }}
app.kubernetes.io/region: {{ . }}
{{- end }}
{{- with .Values.global.environment }}
app.kubernetes.io/environment: {{ . }}
{{- end }}
# Indian specific labels
indian.ecommerce/platform: "flipkart"
indian.compliance/rbi: "{{ .Values.global.compliance.rbi }}"
indian.compliance/pci-dss: "{{ .Values.global.compliance.pciDss }}"
indian.optimization/timezone: "{{ .Values.global.indianOptimization.timezone }}"
cost.optimization/enabled: "{{ .Values.costOptimization.spotInstances.enabled }}"
{{- end }}

{{/*
Selector labels
*/}}
{{- define "api-gateway.selectorLabels" -}}
app.kubernetes.io/name: {{ include "api-gateway.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "api-gateway.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "api-gateway.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified PostgreSQL name.
*/}}
{{- define "api-gateway.postgresql.fullname" -}}
{{- if .Values.postgresql.fullnameOverride }}
{{- .Values.postgresql.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default "postgresql" .Values.postgresql.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified Redis name.
*/}}
{{- define "api-gateway.redis.fullname" -}}
{{- if .Values.redis.fullnameOverride }}
{{- .Values.redis.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default "redis" .Values.redis.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create Kong database connection string
*/}}
{{- define "api-gateway.kong.databaseUrl" -}}
{{- if .Values.kong.env.database -}}
{{- if eq .Values.kong.env.database "postgres" -}}
postgresql://{{ .Values.kong.env.pg_user }}:{{ .Values.kong.env.pg_password }}@{{ .Values.kong.env.pg_host }}:{{ .Values.kong.env.pg_port }}/{{ .Values.kong.env.pg_database }}
{{- end -}}
{{- end -}}
{{- end }}

{{/*
Create Redis connection string
*/}}
{{- define "api-gateway.redis.connectionString" -}}
{{- if .Values.redis.enabled -}}
redis://{{ include "api-gateway.redis.fullname" . }}-master:6379
{{- end -}}
{{- end }}

{{/*
Generate Indian region-specific node selector
*/}}
{{- define "api-gateway.nodeSelector" -}}
topology.kubernetes.io/region: {{ .Values.global.region }}
{{- range $zone := .Values.global.zones }}
topology.kubernetes.io/zone: {{ $zone }}
{{- end }}
node.kubernetes.io/instance-type: {{ .Values.nodeSelector.instanceType | default "c5.xlarge" }}
{{- if .Values.global.compliance.rbi }}
compliance.rbi/enabled: "true"
{{- end }}
{{- if .Values.global.compliance.pciDss }}
compliance.pci-dss/enabled: "true"
{{- end }}
{{- end }}

{{/*
Generate pod anti-affinity rules for high availability
*/}}
{{- define "api-gateway.podAntiAffinity" -}}
podAntiAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values:
          - {{ include "api-gateway.name" . }}
        - key: app.kubernetes.io/instance
          operator: In
          values:
          - {{ .Release.Name }}
      topologyKey: kubernetes.io/hostname
  - weight: 50
    podAffinityTerm:
      labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values:
          - {{ include "api-gateway.name" . }}
      topologyKey: topology.kubernetes.io/zone
{{- end }}

{{/*
Generate resource requirements based on Indian infrastructure optimization
*/}}
{{- define "api-gateway.resources" -}}
{{- $component := . -}}
{{- if eq $component "kong" }}
requests:
  cpu: {{ .Values.kong.resources.requests.cpu | quote }}
  memory: {{ .Values.kong.resources.requests.memory | quote }}
limits:
  cpu: {{ .Values.kong.resources.limits.cpu | quote }}
  memory: {{ .Values.kong.resources.limits.memory | quote }}
{{- else if eq $component "nginx" }}
requests:
  cpu: {{ .Values.nginx.controller.resources.requests.cpu | quote }}
  memory: {{ .Values.nginx.controller.resources.requests.memory | quote }}
limits:
  cpu: {{ .Values.nginx.controller.resources.limits.cpu | quote }}
  memory: {{ .Values.nginx.controller.resources.limits.memory | quote }}
{{- end }}
{{- end }}

{{/*
Generate tolerations for spot instances
*/}}
{{- define "api-gateway.spotInstanceTolerations" -}}
{{- if .Values.costOptimization.spotInstances.enabled }}
tolerations:
- key: "spot-instance"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
- key: "node.kubernetes.io/spot"
  operator: "Exists"
  effect: "NoSchedule"
- key: "kubernetes.aws.com/spot"
  operator: "Exists"
  effect: "NoSchedule"
{{- end }}
{{- end }}

{{/*
Generate security context for Indian compliance
*/}}
{{- define "api-gateway.securityContext" -}}
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  {{- if .Values.global.compliance.pciDss }}
  seccompProfile:
    type: RuntimeDefault
  {{- end }}
{{- end }}

{{/*
Generate container security context
*/}}
{{- define "api-gateway.containerSecurityContext" -}}
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
    {{- if .needsNetBindService }}
    add:
    - NET_BIND_SERVICE
    {{- end }}
  {{- if .Values.global.compliance.pciDss }}
  seccompProfile:
    type: RuntimeDefault
  {{- end }}
{{- end }}

{{/*
Generate Indian timezone environment variable
*/}}
{{- define "api-gateway.timezoneEnv" -}}
- name: TZ
  value: {{ .Values.global.indianOptimization.timezone | quote }}
{{- end }}

{{/*
Generate monitoring annotations
*/}}
{{- define "api-gateway.monitoringAnnotations" -}}
{{- if .Values.monitoring.prometheus.enabled }}
prometheus.io/scrape: "true"
prometheus.io/path: "/metrics"
{{- if .port }}
prometheus.io/port: {{ .port | quote }}
{{- end }}
{{- end }}
{{- if .Values.monitoring.jaeger.enabled }}
jaeger.io/trace: "true"
{{- end }}
{{- end }}

{{/*
Generate network policy selectors
*/}}
{{- define "api-gateway.networkPolicySelectors" -}}
{{- if .Values.security.networkPolicies.enabled }}
podSelector:
  matchLabels:
    {{- include "api-gateway.selectorLabels" . | nindent 4 }}
{{- end }}
{{- end }}

{{/*
Generate backup annotations
*/}}
{{- define "api-gateway.backupAnnotations" -}}
{{- if .Values.backup.enabled }}
backup.velero.io/backup-volumes: "data,logs"
backup.velero.io/backup-volumes-excludes: "tmp"
backup.velero.io/schedule: {{ .Values.backup.schedule | quote }}
backup.velero.io/retention: {{ .Values.backup.retention | quote }}
{{- end }}
{{- end }}

{{/*
Generate cost optimization labels
*/}}
{{- define "api-gateway.costOptimizationLabels" -}}
cost.optimization/spot-instances: "{{ .Values.costOptimization.spotInstances.enabled }}"
cost.optimization/budget: "{{ .Values.costOptimization.resourceQuotas.limits.cpu }}-cpu-{{ .Values.costOptimization.resourceQuotas.limits.memory }}-memory"
cost.optimization/scaling: "auto"
{{- if .Values.costOptimization.scheduledScaling.enabled }}
cost.optimization/scheduled-scaling: "enabled"
{{- end }}
{{- end }}

{{/*
Generate Indian compliance labels
*/}}
{{- define "api-gateway.complianceLabels" -}}
compliance.indian/rbi: "{{ .Values.global.compliance.rbi }}"
compliance.indian/pci-dss: "{{ .Values.global.compliance.pciDss }}"
compliance.indian/data-localization: "{{ .Values.global.compliance.dataLocalization }}"
{{- if .Values.indian.compliance.itAct2000 }}
compliance.indian/it-act-2000: "true"
{{- end }}
{{- if .Values.indian.compliance.digitalIndia }}
compliance.indian/digital-india: "true"
{{- end }}
{{- end }}

{{/*
Generate payment gateway integration labels
*/}}
{{- define "api-gateway.paymentGatewayLabels" -}}
{{- if .Values.indian.paymentGateways.razorpay.enabled }}
payment.gateway/razorpay: "enabled"
{{- end }}
{{- if .Values.indian.paymentGateways.paytm.enabled }}
payment.gateway/paytm: "enabled"
{{- end }}
{{- if .Values.indian.paymentGateways.phonepe.enabled }}
payment.gateway/phonepe: "enabled"
{{- end }}
{{- if .Values.indian.paymentGateways.upi.enabled }}
payment.gateway/upi: "enabled"
{{- end }}
{{- end }}

{{/*
Generate health check configuration
*/}}
{{- define "api-gateway.healthCheck" -}}
{{- $component := .component }}
{{- $values := .values }}
{{- if eq $component "kong" }}
livenessProbe:
  httpGet:
    path: /status
    port: 8100
    scheme: HTTP
  initialDelaySeconds: 60
  periodSeconds: 15
  timeoutSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /status/ready
    port: 8100
    scheme: HTTP
  initialDelaySeconds: 30
  periodSeconds: 5
  timeoutSeconds: 5
  failureThreshold: 3
startupProbe:
  httpGet:
    path: /status
    port: 8100
    scheme: HTTP
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 10
  failureThreshold: 18
{{- else if eq $component "nginx" }}
livenessProbe:
  httpGet:
    path: /healthz
    port: 10254
    scheme: HTTP
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 5
readinessProbe:
  httpGet:
    path: /healthz
    port: 10254
    scheme: HTTP
  initialDelaySeconds: 10
  periodSeconds: 1
  timeoutSeconds: 1
  failureThreshold: 3
{{- end }}
{{- end }}

{{/*
Generate lifecycle hooks for graceful shutdown
*/}}
{{- define "api-gateway.lifecycle" -}}
lifecycle:
  preStop:
    exec:
      command:
      - /bin/sh
      - -c
      - |
        sleep {{ .gracePeriod | default 30 }}
        {{- if .customCommand }}
        {{ .customCommand }}
        {{- end }}
{{- end }}

{{/*
Generate environment variables for Indian optimizations
*/}}
{{- define "api-gateway.indianOptimizationEnv" -}}
- name: INDIAN_REGION
  value: {{ .Values.global.region | quote }}
- name: INDIAN_TIMEZONE
  value: {{ .Values.global.indianOptimization.timezone | quote }}
- name: INDIAN_LOCALE
  value: {{ .Values.global.indianOptimization.locale | quote }}
- name: INDIAN_CURRENCY
  value: {{ .Values.global.indianOptimization.currency | quote }}
- name: INDIAN_PEAK_HOURS
  value: {{ .Values.global.indianOptimization.peakHours | quote }}
{{- if .Values.indian.businessMetrics.festivalScaling }}
- name: FESTIVAL_SCALING_ENABLED
  value: "true"
{{- end }}
{{- if .Values.indian.businessMetrics.gstIntegration }}
- name: GST_INTEGRATION_ENABLED
  value: "true"
{{- end }}
{{- end }}