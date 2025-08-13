# Episode 17: Container Orchestration (Kubernetes) - Part 2

**Duration**: 60 minutes | **Words**: 7,000+ | **Level**: Advanced
**Focus**: Advanced Kubernetes Concepts with Swiggy Production Deployment

---

## Chapter 4: Services और Networking - Mumbai Local Train की तरह Connectivity

### Kubernetes Services - Internal Communication का Magic

अब तक हमने देखा कि Pods कैसे बनते हैं, लेकिन एक fundamental question है - Pods आपस में कैसे communicate करते हैं? यह exactly वैसा ही है जैसे Mumbai की local trains में different coaches आपस में connected होती हैं।

Mumbai local train में सोचिए - आपके पास General compartment, Ladies compartment, First class, AC compartment हैं। हर compartment का अपना function है, लेकिन सब एक ही train का हिस्सा हैं और सब connected हैं। Kubernetes Services exactly यही काम करती हैं।

```python
# मान लेते हैं Swiggy का architecture
# Order Service -> Payment Service -> Delivery Service

# Traditional approach (बिना Kubernetes के)
order_service_ip = "192.168.1.10:8080"
payment_service_ip = "192.168.1.11:8081"
delivery_service_ip = "192.168.1.12:8082"

# Problem: IPs change होती रहती हैं
# Solution: Kubernetes Services
```

### Service Types - Different Communication Patterns

Kubernetes में चार main service types हैं:

#### 1. ClusterIP - Internal Communication Only
```yaml
# Swiggy का internal payment service
apiVersion: v1
kind: Service
metadata:
  name: swiggy-payment-service
  namespace: swiggy-prod
  labels:
    app: payment-service
    company: swiggy
spec:
  type: ClusterIP  # Default type
  selector:
    app: payment-service
  ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
```

यह service सिर्फ cluster के अंदर available है। External users directly access नहीं कर सकते। यह exactly वैसा है जैसे Mumbai local train का engine - passenger directly engine में नहीं जा सकते, लेकिन पूरी train engine के बिना चल नहीं सकती।

#### 2. NodePort - External Access के लिए
```yaml
# Swiggy का customer-facing API
apiVersion: v1
kind: Service
metadata:
  name: swiggy-api-service
  namespace: swiggy-prod
spec:
  type: NodePort
  selector:
    app: swiggy-api
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30001  # External port
```

NodePort service क्या करती है? यह हर Kubernetes node पर specified port (30001) को expose करती है। अब आप कोई भी node के IP से इस service को access कर सकते हैं।

#### 3. LoadBalancer - Production Grade External Access
```yaml
# Swiggy का production load balancer
apiVersion: v1
kind: Service
metadata:
  name: swiggy-public-api
  namespace: swiggy-prod
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  type: LoadBalancer
  selector:
    app: swiggy-api
  ports:
  - port: 443
    targetPort: 8080
    protocol: TCP
```

LoadBalancer service cloud provider के साथ integrate होकर एक external load balancer create करती है। AWS में यह ELB बनाती है, GCP में Google Load Balancer।

#### 4. ExternalName - External Services के लिए
```yaml
# External payment gateway integration
apiVersion: v1
kind: Service
metadata:
  name: razorpay-gateway
spec:
  type: ExternalName
  externalName: api.razorpay.com
```

### Service Discovery - DNS Magic in Kubernetes

अब सबसे interesting part आता है - Service Discovery। Kubernetes में automatic DNS resolution होती है। यह कुछ इस तरह काम करती है:

```python
# Swiggy के microservices में service discovery
import requests

class SwiggyOrderService:
    def __init__(self):
        # Kubernetes DNS resolution
        self.payment_service_url = "http://swiggy-payment-service.swiggy-prod.svc.cluster.local:8080"
        self.inventory_service_url = "http://swiggy-inventory-service.swiggy-prod.svc.cluster.local:8080"
        self.delivery_service_url = "http://swiggy-delivery-service.swiggy-prod.svc.cluster.local:8080"
    
    def process_order(self, order_data):
        """Complete order processing with microservices"""
        
        # Step 1: Check inventory
        inventory_response = requests.post(
            f"{self.inventory_service_url}/check-availability",
            json={"items": order_data["items"]}
        )
        
        if not inventory_response.json()["available"]:
            return {"status": "failed", "reason": "Items not available"}
        
        # Step 2: Process payment
        payment_response = requests.post(
            f"{self.payment_service_url}/process-payment",
            json={"amount": order_data["total"], "customer_id": order_data["customer_id"]}
        )
        
        if payment_response.json()["status"] != "success":
            return {"status": "failed", "reason": "Payment failed"}
        
        # Step 3: Assign delivery
        delivery_response = requests.post(
            f"{self.delivery_service_url}/assign-delivery",
            json={"order_id": order_data["order_id"], "location": order_data["delivery_address"]}
        )
        
        return {
            "status": "success",
            "order_id": order_data["order_id"],
            "delivery_eta": delivery_response.json()["eta"]
        }
```

### Ingress Controllers - Mumbai Traffic Police की तरह

अब जब आपके पास multiple services हैं, तो एक coordinator चाहिए जो traffic को सही direction में route करे। Mumbai में traffic police जैसे different lanes के traffic को manage करती है, वैसे ही Kubernetes में Ingress Controller काम करता है।

```yaml
# Swiggy का production Ingress configuration
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: swiggy-main-ingress
  namespace: swiggy-prod
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "1000"  # Rate limiting
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"  # Automatic SSL
spec:
  tls:
  - hosts:
    - api.swiggy.com
    - customer.swiggy.com
    - partner.swiggy.com
    secretName: swiggy-tls-secret
  
  rules:
  # Customer API
  - host: api.swiggy.com
    http:
      paths:
      - path: /orders
        pathType: Prefix
        backend:
          service:
            name: swiggy-order-service
            port:
              number: 8080
      - path: /restaurants
        pathType: Prefix
        backend:
          service:
            name: swiggy-restaurant-service
            port:
              number: 8080
      - path: /search
        pathType: Prefix
        backend:
          service:
            name: swiggy-search-service
            port:
              number: 8080
  
  # Customer Web App
  - host: customer.swiggy.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: swiggy-customer-web
            port:
              number: 80
  
  # Partner Portal
  - host: partner.swiggy.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: swiggy-partner-portal
            port:
              number: 80
```

Ingress Controller में कई powerful features होती हैं:

1. **SSL Termination**: Automatic HTTPS certificates
2. **Load Balancing**: Multiple backend pods में traffic distribution
3. **Rate Limiting**: DDoS protection
4. **Path-based Routing**: URL के basis पर different services
5. **Host-based Routing**: Different domains के लिए different services

---

## Chapter 5: ConfigMaps और Secrets - Configuration Management

### ConfigMaps - Environment-based Configuration

Real production में different environments के लिए different configurations होती हैं। Swiggy के development environment में test payment gateway use होती है, production में real Razorpay integration होती है।

```yaml
# Development environment ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: swiggy-config-dev
  namespace: swiggy-dev
data:
  app.yaml: |
    environment: development
    debug: true
    database:
      host: postgres-dev.swiggy.com
      port: 5432
      name: swiggy_dev
    payment:
      provider: razorpay_test
      webhook_url: https://dev-api.swiggy.com/webhooks/payment
    cache:
      redis_host: redis-dev.swiggy.com
      redis_port: 6379
      ttl: 300
    logging:
      level: DEBUG
    features:
      new_ui: true
      advanced_search: false
      premium_delivery: false

---
# Production environment ConfigMap  
apiVersion: v1
kind: ConfigMap
metadata:
  name: swiggy-config-prod
  namespace: swiggy-prod
data:
  app.yaml: |
    environment: production
    debug: false
    database:
      host: postgres-prod.swiggy.com
      port: 5432
      name: swiggy_prod
    payment:
      provider: razorpay_live
      webhook_url: https://api.swiggy.com/webhooks/payment
    cache:
      redis_host: redis-prod.swiggy.com
      redis_port: 6379
      ttl: 3600
    logging:
      level: INFO
    features:
      new_ui: true
      advanced_search: true
      premium_delivery: true
```

### Secrets - Sensitive Information की Security

Passwords, API keys, certificates जैसी sensitive information को ConfigMaps में store नहीं करना चाहिए। इसके लिए Kubernetes Secrets का use करते हैं।

```yaml
# Swiggy production secrets
apiVersion: v1
kind: Secret
metadata:
  name: swiggy-secrets
  namespace: swiggy-prod
type: Opaque
data:
  # Base64 encoded values
  database_password: cGFzc3dvcmQxMjM=
  razorpay_key_id: cnpwX2xpdmVfa2V5XzEyMzQ1Ng==
  razorpay_key_secret: c2VjcmV0XzEyMzQ1Ng==
  jwt_secret: and0X3NlY3JldF9rZXlf
  redis_password: cmVkaXNfcGFzc3dvcmQ=
```

Real production में आप vault जैसे tools use करते हैं secrets को manage करने के लिए:

```python
# Python application में secrets का usage
import os
import base64
from kubernetes import client, config

class SwiggyConfigManager:
    def __init__(self):
        # Load Kubernetes config (in-cluster या local kubeconfig)
        try:
            config.load_incluster_config()  # If running inside pod
        except:
            config.load_kube_config()  # If running locally
        
        self.v1 = client.CoreV1Api()
        self.namespace = os.getenv('POD_NAMESPACE', 'swiggy-prod')
    
    def get_config(self, config_name='swiggy-config-prod'):
        """Get configuration from ConfigMap"""
        try:
            configmap = self.v1.read_namespaced_config_map(
                name=config_name,
                namespace=self.namespace
            )
            return configmap.data
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def get_secret(self, secret_name='swiggy-secrets'):
        """Get secrets from Kubernetes Secret"""
        try:
            secret = self.v1.read_namespaced_secret(
                name=secret_name,
                namespace=self.namespace
            )
            
            # Decode base64 encoded secrets
            decoded_secrets = {}
            for key, value in secret.data.items():
                decoded_secrets[key] = base64.b64decode(value).decode('utf-8')
            
            return decoded_secrets
        except Exception as e:
            print(f"Error loading secrets: {e}")
            return {}
    
    def get_database_config(self):
        """Get complete database configuration"""
        config_data = self.get_config()
        secrets_data = self.get_secret()
        
        return {
            "host": config_data.get("database_host"),
            "port": int(config_data.get("database_port", 5432)),
            "database": config_data.get("database_name"),
            "username": config_data.get("database_username"),
            "password": secrets_data.get("database_password")
        }

# Usage in Swiggy application
config_manager = SwiggyConfigManager()
db_config = config_manager.get_database_config()
```

### Volume Mounts - ConfigMaps और Secrets को Pods में Use करना

```yaml
# Swiggy order service deployment with ConfigMaps and Secrets
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swiggy-order-service
  namespace: swiggy-prod
spec:
  replicas: 10
  selector:
    matchLabels:
      app: swiggy-order-service
  template:
    metadata:
      labels:
        app: swiggy-order-service
    spec:
      containers:
      - name: order-service
        image: swiggy/order-service:v2.1.0
        ports:
        - containerPort: 8080
        
        # Environment variables from ConfigMap
        env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: swiggy-config-prod
              key: environment
        - name: DEBUG_MODE
          valueFrom:
            configMapKeyRef:
              name: swiggy-config-prod
              key: debug
        
        # Environment variables from Secrets
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: swiggy-secrets
              key: database_password
        - name: RAZORPAY_KEY_SECRET
          valueFrom:
            secretKeyRef:
              name: swiggy-secrets
              key: razorpay_key_secret
        
        # Mount ConfigMap as file
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: secrets-volume
          mountPath: /app/secrets
          readOnly: true
        
        # Health checks
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
      - name: config-volume
        configMap:
          name: swiggy-config-prod
      - name: secrets-volume
        secret:
          secretName: swiggy-secrets
          defaultMode: 0400  # Read-only for owner only
```

---

## Chapter 6: Auto-scaling - Mumbai Rush Hour की तरह Dynamic Scaling

### Horizontal Pod Autoscaler (HPA) - Peak Traffic Handling

Mumbai में rush hour के time सब local trains crowded हो जाती हैं। Railway department extra trains चलाती है। Similarly, Kubernetes में HPA automatic scaling करती है जब load बढ़ता है।

Swiggy में typical traffic patterns कुछ इस तरह होते हैं:
- **Breakfast Rush**: 8 AM - 11 AM (2x normal traffic)
- **Lunch Rush**: 12 PM - 3 PM (4x normal traffic)  
- **Evening Snacks**: 4 PM - 6 PM (1.5x normal traffic)
- **Dinner Rush**: 7 PM - 11 PM (5x normal traffic)

```yaml
# Swiggy order service HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: swiggy-order-service-hpa
  namespace: swiggy-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: swiggy-order-service
  
  minReplicas: 5    # Minimum instances हमेशा चाहिए
  maxReplicas: 100  # Peak dinner time के लिए maximum capacity
  
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # 70% CPU usage पर scale up
  
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # 80% memory usage पर scale up
  
  # Custom metrics - Requests per second
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"  # 100 RPS per pod
  
  # Advanced scaling behavior
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60  # 1 minute wait before scaling up
      policies:
      - type: Percent
        value: 100    # Scale up by 100% (double the pods)
        periodSeconds: 15
      - type: Pods
        value: 4      # Or add maximum 4 pods at once
        periodSeconds: 15
      selectPolicy: Max  # Use the more aggressive policy
    
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutes wait before scaling down
      policies:
      - type: Percent
        value: 10     # Scale down by 10% only
        periodSeconds: 60
      selectPolicy: Min  # Use the more conservative policy
```

### Vertical Pod Autoscaler (VPA) - Resource Right-sizing

कभी-कभी problem horizontal scaling से solve नहीं होती। अगर आपके application में memory leak है या CPU-intensive operations हैं, तो आपको bigger instances चाहिए, more instances नहीं।

```yaml
# Swiggy search service VPA - Heavy computational workload के लिए
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: swiggy-search-service-vpa
  namespace: swiggy-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: swiggy-search-service
  
  updatePolicy:
    updateMode: "Auto"  # Automatically update pod resources
  
  resourcePolicy:
    containerPolicies:
    - containerName: search-service
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 8000m    # Maximum 8 CPU cores
        memory: 16Gi  # Maximum 16GB RAM
      controlledResources: ["cpu", "memory"]
```

### Custom Metrics Scaling - Business Logic based Scaling

Real production में आपको standard CPU/Memory metrics के अलावा business metrics के basis पर भी scale करना पड़ता है।

```python
# Custom metrics के लिए Python script
import time
import requests
import json
from kubernetes import client, config
from datetime import datetime

class SwiggyCustomMetricsCollector:
    """
    Swiggy के लिए custom metrics collection और scaling decisions
    """
    
    def __init__(self):
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.namespace = "swiggy-prod"
        
        # Business metrics thresholds
        self.metrics_config = {
            "orders_per_minute_threshold": 1000,     # 1000 orders/minute पर scale up
            "delivery_time_threshold": 45,           # 45 minutes average delivery time
            "customer_wait_time_threshold": 300,     # 5 minutes customer wait time
            "restaurant_capacity_threshold": 0.85,   # 85% restaurant capacity
            "delivery_partner_availability": 0.7     # 70% delivery partners available
        }
    
    def get_business_metrics(self):
        """
        Production में यह Prometheus/CloudWatch से आएगा
        अभी demo के लिए simulated metrics
        """
        current_hour = datetime.now().hour
        
        # Simulate realistic Swiggy metrics
        base_orders_per_minute = 200
        base_delivery_time = 30
        base_wait_time = 120
        
        # Peak hour multipliers
        if 12 <= current_hour <= 14:  # Lunch rush
            multiplier = 4.0
        elif 19 <= current_hour <= 22:  # Dinner rush
            multiplier = 5.0
        elif 8 <= current_hour <= 10:   # Breakfast
            multiplier = 2.0
        else:
            multiplier = 1.0
        
        return {
            "orders_per_minute": base_orders_per_minute * multiplier,
            "avg_delivery_time": base_delivery_time * (1 + (multiplier - 1) * 0.3),
            "customer_wait_time": base_wait_time * (1 + (multiplier - 1) * 0.5),
            "restaurant_capacity_utilization": min(0.95, 0.4 * multiplier),
            "delivery_partner_availability": max(0.3, 0.9 - (multiplier - 1) * 0.15)
        }
    
    def calculate_required_replicas(self, current_replicas, metrics):
        """
        Business metrics के basis पर required replicas calculate करना
        """
        scaling_factors = []
        
        # Orders per minute based scaling
        if metrics["orders_per_minute"] > self.metrics_config["orders_per_minute_threshold"]:
            orders_factor = metrics["orders_per_minute"] / self.metrics_config["orders_per_minute_threshold"]
            scaling_factors.append(orders_factor)
        
        # Delivery time based scaling
        if metrics["avg_delivery_time"] > self.metrics_config["delivery_time_threshold"]:
            delivery_factor = metrics["avg_delivery_time"] / self.metrics_config["delivery_time_threshold"]
            scaling_factors.append(delivery_factor)
        
        # Customer wait time based scaling
        if metrics["customer_wait_time"] > self.metrics_config["customer_wait_time_threshold"]:
            wait_factor = metrics["customer_wait_time"] / self.metrics_config["customer_wait_time_threshold"]
            scaling_factors.append(wait_factor)
        
        # Restaurant capacity based scaling
        if metrics["restaurant_capacity_utilization"] > self.metrics_config["restaurant_capacity_threshold"]:
            capacity_factor = metrics["restaurant_capacity_utilization"] / self.metrics_config["restaurant_capacity_threshold"]
            scaling_factors.append(capacity_factor)
        
        # Delivery partner availability based scaling
        if metrics["delivery_partner_availability"] < self.metrics_config["delivery_partner_availability"]:
            partner_factor = self.metrics_config["delivery_partner_availability"] / metrics["delivery_partner_availability"]
            scaling_factors.append(partner_factor)
        
        if scaling_factors:
            # Use the maximum scaling factor
            max_scaling_factor = max(scaling_factors)
            required_replicas = int(current_replicas * max_scaling_factor)
            return min(100, max(5, required_replicas))  # Between 5 and 100 replicas
        
        return current_replicas
    
    def scale_deployment(self, deployment_name, target_replicas):
        """
        Deployment को scale करना
        """
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace
            )
            
            current_replicas = deployment.spec.replicas
            
            if current_replicas != target_replicas:
                # Update replica count
                deployment.spec.replicas = target_replicas
                
                # Apply the change
                self.apps_v1.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=self.namespace,
                    body=deployment
                )
                
                print(f"✅ Scaled {deployment_name}: {current_replicas} → {target_replicas} replicas")
                return True
            else:
                print(f"ℹ️ {deployment_name} already at target replicas: {target_replicas}")
                return False
                
        except Exception as e:
            print(f"❌ Scaling failed for {deployment_name}: {str(e)}")
            return False
    
    def monitor_and_scale(self):
        """
        Continuous monitoring और scaling
        """
        deployments_to_monitor = [
            "swiggy-order-service",
            "swiggy-payment-service", 
            "swiggy-delivery-service",
            "swiggy-search-service"
        ]
        
        while True:
            try:
                # Get current business metrics
                metrics = self.get_business_metrics()
                
                print(f"📊 Business Metrics at {datetime.now().strftime('%H:%M:%S')}:")
                print(f"   Orders/min: {metrics['orders_per_minute']:.0f}")
                print(f"   Avg delivery time: {metrics['avg_delivery_time']:.1f} minutes")
                print(f"   Customer wait time: {metrics['customer_wait_time']:.0f} seconds")
                print(f"   Restaurant capacity: {metrics['restaurant_capacity_utilization']:.1%}")
                print(f"   Delivery partners available: {metrics['delivery_partner_availability']:.1%}")
                
                # Scale each deployment based on metrics
                for deployment_name in deployments_to_monitor:
                    try:
                        deployment = self.apps_v1.read_namespaced_deployment(
                            name=deployment_name,
                            namespace=self.namespace
                        )
                        current_replicas = deployment.spec.replicas
                        
                        required_replicas = self.calculate_required_replicas(current_replicas, metrics)
                        
                        if required_replicas != current_replicas:
                            self.scale_deployment(deployment_name, required_replicas)
                    
                    except Exception as e:
                        print(f"⚠️ Error monitoring {deployment_name}: {str(e)}")
                
                print("-" * 60)
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                print("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"⚠️ Monitoring error: {str(e)}")
                time.sleep(30)

# Usage
if __name__ == "__main__":
    collector = SwiggyCustomMetricsCollector()
    collector.monitor_and_scale()
```

---

## Chapter 7: Service Mesh - Delivery Network की तरह Advanced Networking

### Istio Introduction - Mumbai Dabbawala System 2.0

अब तक हमने देखा कि individual services कैसे work करती हैं। लेकिन जब आपके पास 50+ microservices हैं (जैसे Swiggy/Zomato में होती हैं), तो networking complexity बहुत बढ़ जाती है।

यहीं पर Service Mesh काम आती है। Service Mesh एक dedicated infrastructure layer है जो service-to-service communication को handle करती है। यह exactly Mumbai dabbawala system की तरह है, लेकिन बहुत advanced।

### Istio Architecture - Three Main Components

#### 1. Data Plane - Envoy Sidecars
```yaml
# Swiggy order service with Istio sidecar injection
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swiggy-order-service
  namespace: swiggy-prod
  labels:
    app: order-service
    version: v2
spec:
  replicas: 10
  selector:
    matchLabels:
      app: order-service
      version: v2
  template:
    metadata:
      labels:
        app: order-service
        version: v2
      annotations:
        sidecar.istio.io/inject: "true"  # Enable Istio sidecar injection
    spec:
      containers:
      - name: order-service
        image: swiggy/order-service:v2.1.0
        ports:
        - containerPort: 8080
```

#### 2. Control Plane - Istiod
```yaml
# Istio Gateway - External traffic के लिए
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: swiggy-gateway
  namespace: swiggy-prod
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: swiggy-tls-secret
    hosts:
    - api.swiggy.com
    - customer.swiggy.com
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - api.swiggy.com
    - customer.swiggy.com
    redirect:
      httpsRedirect: true
```

#### 3. Virtual Services - Traffic Management
```yaml
# Swiggy order service traffic management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: swiggy-order-service-vs
  namespace: swiggy-prod
spec:
  hosts:
  - api.swiggy.com
  gateways:
  - swiggy-gateway
  http:
  # Canary deployment - 90% traffic to v2, 10% to v3
  - match:
    - uri:
        prefix: /orders
    route:
    - destination:
        host: swiggy-order-service
        subset: v2
      weight: 90
    - destination:
        host: swiggy-order-service
        subset: v3
      weight: 10
    fault:
      delay:
        percentage:
          value: 0.1  # 0.1% requests में 5s delay (chaos engineering)
        fixedDelay: 5s
    retries:
      attempts: 3
      perTryTimeout: 10s
```

### DestinationRule - Load Balancing और Circuit Breaker
```yaml
# Advanced traffic policies for Swiggy services
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: swiggy-order-service-dr
  namespace: swiggy-prod
spec:
  host: swiggy-order-service
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpCookieName: "customer_id"  # Session affinity
        ttl: 3600s
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
        maxRetries: 3
        consecutiveGatewayErrors: 5
        interval: 30s
        baseEjectionTime: 30s
        maxEjectionPercent: 50
    circuitBreaker:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v2
    labels:
      version: v2
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 50
  - name: v3
    labels:
      version: v3
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 10  # Limited traffic for canary
```

### Observability with Istio - Complete Monitoring

Istio automatically instruments कर देती है सारी service communication को:

```python
# Python service के लिए Istio metrics और tracing
import time
import random
from flask import Flask, request, jsonify
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = Flask(__name__)

# Configure tracing for Istio
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Jaeger exporter for distributed tracing
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.istio-system.svc.cluster.local",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

class SwiggyOrderService:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    @app.route("/orders", methods=["POST"])
    def create_order(self):
        with self.tracer.start_as_current_span("create_order") as span:
            order_data = request.get_json()
            
            # Add custom attributes to span
            span.set_attribute("customer.id", order_data.get("customer_id"))
            span.set_attribute("restaurant.id", order_data.get("restaurant_id"))
            span.set_attribute("order.value", order_data.get("total_amount"))
            
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # Call other services with automatic tracing
            payment_result = self.process_payment(order_data)
            delivery_result = self.assign_delivery(order_data)
            
            span.set_attribute("order.status", "success")
            
            return jsonify({
                "order_id": f"ORD{random.randint(10000, 99999)}",
                "status": "confirmed",
                "payment": payment_result,
                "delivery": delivery_result
            })
    
    def process_payment(self, order_data):
        with self.tracer.start_as_current_span("process_payment") as span:
            # This call will be automatically traced by Istio
            import requests
            
            payment_service_url = "http://swiggy-payment-service.swiggy-prod.svc.cluster.local:8080"
            
            response = requests.post(
                f"{payment_service_url}/process",
                json=order_data,
                headers={
                    "x-request-id": request.headers.get("x-request-id"),
                    "x-b3-traceid": request.headers.get("x-b3-traceid"),
                    "x-b3-spanid": request.headers.get("x-b3-spanid")
                }
            )
            
            span.set_attribute("payment.status", response.json().get("status"))
            return response.json()
    
    def assign_delivery(self, order_data):
        with self.tracer.start_as_current_span("assign_delivery") as span:
            # Call delivery service
            import requests
            
            delivery_service_url = "http://swiggy-delivery-service.swiggy-prod.svc.cluster.local:8080"
            
            response = requests.post(
                f"{delivery_service_url}/assign",
                json=order_data,
                headers={
                    "x-request-id": request.headers.get("x-request-id"),
                    "x-b3-traceid": request.headers.get("x-b3-traceid"),
                    "x-b3-spanid": request.headers.get("x-b3-spanid")
                }
            )
            
            span.set_attribute("delivery.partner_id", response.json().get("partner_id"))
            span.set_attribute("delivery.eta", response.json().get("eta"))
            return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

---

## Chapter 8: Resource Management और Optimization

### Resource Requests और Limits - Efficient Resource Utilization

Production में हर container को proper resource allocation देना बहुत important है। यह Mumbai local train की तरह है - हर compartment की capacity limited है।

```yaml
# Swiggy services के लिए optimized resource allocation
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swiggy-order-service
  namespace: swiggy-prod
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: order-service
        image: swiggy/order-service:v2.1.0
        resources:
          requests:
            cpu: "500m"      # 0.5 CPU cores guaranteed
            memory: "512Mi"  # 512MB memory guaranteed
          limits:
            cpu: "2000m"     # Maximum 2 CPU cores
            memory: "2Gi"    # Maximum 2GB memory
        
        # JVM tuning for Java applications
        env:
        - name: JAVA_OPTS
          value: "-Xms512m -Xmx1536m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
        
        # Security context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        
        # Volume mounts for writable directories
        volumeMounts:
        - name: temp-volume
          mountPath: /tmp
        - name: logs-volume
          mountPath: /app/logs
      
      volumes:
      - name: temp-volume
        emptyDir: {}
      - name: logs-volume
        emptyDir: {}
```

### Quality of Service (QoS) Classes

Kubernetes में तीन QoS classes हैं:

1. **Guaranteed**: Resources requests = limits
2. **Burstable**: Resources requests < limits  
3. **BestEffort**: कोई resources specified नहीं

```python
# Python script to analyze और optimize resource usage
import json
import subprocess
from kubernetes import client, config

class SwiggyResourceOptimizer:
    """
    Swiggy के containers के लिए resource optimization
    """
    
    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.metrics_v1beta1 = client.CustomObjectsApi()
        self.namespace = "swiggy-prod"
    
    def get_pod_metrics(self):
        """Get current pod resource usage from metrics server"""
        try:
            # Get metrics from metrics-server
            metrics = self.metrics_v1beta1.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1", 
                namespace=self.namespace,
                plural="pods"
            )
            
            pod_metrics = {}
            for item in metrics["items"]:
                pod_name = item["metadata"]["name"]
                containers = item["containers"]
                
                pod_metrics[pod_name] = {
                    "cpu_usage": sum(self.parse_cpu(c["usage"]["cpu"]) for c in containers),
                    "memory_usage": sum(self.parse_memory(c["usage"]["memory"]) for c in containers)
                }
            
            return pod_metrics
            
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {}
    
    def parse_cpu(self, cpu_string):
        """Parse CPU string to numeric value (in millicores)"""
        if cpu_string.endswith("n"):
            return float(cpu_string[:-1]) / 1000000  # nanocores to millicores
        elif cpu_string.endswith("u"):
            return float(cpu_string[:-1]) / 1000     # microcores to millicores
        elif cpu_string.endswith("m"):
            return float(cpu_string[:-1])            # already in millicores
        else:
            return float(cpu_string) * 1000          # cores to millicores
    
    def parse_memory(self, memory_string):
        """Parse memory string to numeric value (in MiB)"""
        units = {"Ki": 1/1024, "Mi": 1, "Gi": 1024, "Ti": 1024*1024}
        
        for unit, multiplier in units.items():
            if memory_string.endswith(unit):
                return float(memory_string[:-2]) * multiplier
        
        # Assume bytes if no unit
        return float(memory_string) / (1024 * 1024)
    
    def analyze_resource_utilization(self):
        """Analyze और recommend resource optimization"""
        
        # Get all deployments in namespace
        deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
        pod_metrics = self.get_pod_metrics()
        
        recommendations = []
        
        for deployment in deployments.items:
            deployment_name = deployment.metadata.name
            containers = deployment.spec.template.spec.containers
            
            for container in containers:
                container_name = container.name
                
                # Get current resource allocation
                resources = container.resources
                current_requests = resources.requests if resources.requests else {}
                current_limits = resources.limits if resources.limits else {}
                
                current_cpu_request = self.parse_cpu(current_requests.get("cpu", "0"))
                current_memory_request = self.parse_memory(current_requests.get("memory", "0Mi"))
                current_cpu_limit = self.parse_cpu(current_limits.get("cpu", "0"))
                current_memory_limit = self.parse_memory(current_limits.get("memory", "0Mi"))
                
                # Find corresponding pods और get average usage
                matching_pods = [
                    pod for pod in pod_metrics.keys() 
                    if deployment_name in pod
                ]
                
                if matching_pods:
                    avg_cpu_usage = sum(pod_metrics[pod]["cpu_usage"] for pod in matching_pods) / len(matching_pods)
                    avg_memory_usage = sum(pod_metrics[pod]["memory_usage"] for pod in matching_pods) / len(matching_pods)
                    
                    # Calculate utilization percentages
                    cpu_utilization = (avg_cpu_usage / current_cpu_request * 100) if current_cpu_request > 0 else 0
                    memory_utilization = (avg_memory_usage / current_memory_request * 100) if current_memory_request > 0 else 0
                    
                    # Generate recommendations
                    recommendation = {
                        "deployment": deployment_name,
                        "container": container_name,
                        "current_cpu_request": f"{current_cpu_request}m",
                        "current_memory_request": f"{current_memory_request:.0f}Mi",
                        "actual_cpu_usage": f"{avg_cpu_usage:.0f}m",
                        "actual_memory_usage": f"{avg_memory_usage:.0f}Mi",
                        "cpu_utilization": f"{cpu_utilization:.1f}%",
                        "memory_utilization": f"{memory_utilization:.1f}%"
                    }
                    
                    # Resource optimization recommendations
                    if cpu_utilization < 30:
                        recommended_cpu = max(100, avg_cpu_usage * 1.5)  # 50% buffer
                        recommendation["cpu_recommendation"] = f"Reduce to {recommended_cpu:.0f}m (overprovisioned)"
                    elif cpu_utilization > 80:
                        recommended_cpu = avg_cpu_usage * 2  # 100% buffer
                        recommendation["cpu_recommendation"] = f"Increase to {recommended_cpu:.0f}m (underprovisioned)"
                    else:
                        recommendation["cpu_recommendation"] = "Optimal"
                    
                    if memory_utilization < 30:
                        recommended_memory = max(128, avg_memory_usage * 1.5)  # 50% buffer
                        recommendation["memory_recommendation"] = f"Reduce to {recommended_memory:.0f}Mi (overprovisioned)"
                    elif memory_utilization > 80:
                        recommended_memory = avg_memory_usage * 2  # 100% buffer
                        recommendation["memory_recommendation"] = f"Increase to {recommended_memory:.0f}Mi (underprovisioned)"
                    else:
                        recommendation["memory_recommendation"] = "Optimal"
                    
                    recommendations.append(recommendation)
        
        return recommendations
    
    def generate_cost_savings_report(self, recommendations):
        """Calculate potential cost savings from optimization"""
        
        # AWS EKS pricing (approximate)
        cpu_cost_per_hour = 0.0464  # $0.0464 per vCPU per hour
        memory_cost_per_hour = 0.0051  # $0.0051 per GB per hour
        hours_per_month = 24 * 30
        
        total_current_cpu = 0
        total_optimized_cpu = 0
        total_current_memory = 0
        total_optimized_memory = 0
        
        for rec in recommendations:
            current_cpu = float(rec["current_cpu_request"].replace("m", "")) / 1000
            current_memory = float(rec["current_memory_request"].replace("Mi", "")) / 1024
            
            total_current_cpu += current_cpu
            total_current_memory += current_memory
            
            # Calculate optimized resources
            if "Reduce to" in rec["cpu_recommendation"]:
                optimized_cpu = float(rec["cpu_recommendation"].split("Reduce to ")[1].split("m")[0]) / 1000
            elif "Increase to" in rec["cpu_recommendation"]:
                optimized_cpu = float(rec["cpu_recommendation"].split("Increase to ")[1].split("m")[0]) / 1000
            else:
                optimized_cpu = current_cpu
            
            if "Reduce to" in rec["memory_recommendation"]:
                optimized_memory = float(rec["memory_recommendation"].split("Reduce to ")[1].split("Mi")[0]) / 1024
            elif "Increase to" in rec["memory_recommendation"]:
                optimized_memory = float(rec["memory_recommendation"].split("Increase to ")[1].split("Mi")[0]) / 1024
            else:
                optimized_memory = current_memory
            
            total_optimized_cpu += optimized_cpu
            total_optimized_memory += optimized_memory
        
        # Calculate costs
        current_monthly_cost = (
            total_current_cpu * cpu_cost_per_hour * hours_per_month +
            total_current_memory * memory_cost_per_hour * hours_per_month
        )
        
        optimized_monthly_cost = (
            total_optimized_cpu * cpu_cost_per_hour * hours_per_month +
            total_optimized_memory * memory_cost_per_hour * hours_per_month
        )
        
        monthly_savings = current_monthly_cost - optimized_monthly_cost
        annual_savings = monthly_savings * 12
        
        return {
            "current_monthly_cost_usd": current_monthly_cost,
            "optimized_monthly_cost_usd": optimized_monthly_cost,
            "monthly_savings_usd": monthly_savings,
            "annual_savings_usd": annual_savings,
            "monthly_savings_inr": monthly_savings * 83,  # Approximate USD to INR
            "annual_savings_inr": annual_savings * 83,
            "total_current_cpu_cores": total_current_cpu,
            "total_optimized_cpu_cores": total_optimized_cpu,
            "total_current_memory_gb": total_current_memory,
            "total_optimized_memory_gb": total_optimized_memory
        }

# Usage demonstration
def main():
    print("🔍 Swiggy Resource Optimization Analysis")
    print("=" * 50)
    
    optimizer = SwiggyResourceOptimizer()
    
    # Analyze current resource utilization
    recommendations = optimizer.analyze_resource_utilization()
    
    print("📊 Resource Utilization Analysis:")
    for rec in recommendations:
        print(f"\\n🏭 {rec['deployment']} / {rec['container']}:")
        print(f"   CPU: {rec['current_cpu_request']} → {rec['actual_cpu_usage']} ({rec['cpu_utilization']})")
        print(f"   Memory: {rec['current_memory_request']} → {rec['actual_memory_usage']} ({rec['memory_utilization']})")
        print(f"   CPU Recommendation: {rec['cpu_recommendation']}")
        print(f"   Memory Recommendation: {rec['memory_recommendation']}")
    
    # Generate cost savings report
    cost_report = optimizer.generate_cost_savings_report(recommendations)
    
    print("\\n💰 Cost Savings Analysis:")
    print(f"   Current Monthly Cost: ${cost_report['current_monthly_cost_usd']:.2f} (₹{cost_report['current_monthly_cost_usd'] * 83:.0f})")
    print(f"   Optimized Monthly Cost: ${cost_report['optimized_monthly_cost_usd']:.2f} (₹{cost_report['optimized_monthly_cost_usd'] * 83:.0f})")
    print(f"   Monthly Savings: ${cost_report['monthly_savings_usd']:.2f} (₹{cost_report['monthly_savings_inr']:.0f})")
    print(f"   Annual Savings: ${cost_report['annual_savings_usd']:.2f} (₹{cost_report['annual_savings_inr']:.0f})")

if __name__ == "__main__":
    main()
```

---

## समापन - Part 2 का Conclusion

आज के Part 2 में हमने Kubernetes की advanced concepts देखीं जो production-grade applications के लिए बहुत important हैं:

### Key Learnings:
1. **Services और Networking**: Internal communication और external access
2. **ConfigMaps और Secrets**: Secure configuration management
3. **Auto-scaling**: Dynamic resource allocation based on demand
4. **Service Mesh**: Advanced networking और observability
5. **Resource Optimization**: Cost-effective resource utilization

### Swiggy/Zomato Production Reality:
- Peak hour traffic handling with HPA/VPA
- Multi-environment configuration management
- Secure secrets handling for payment integrations
- Service mesh for complex microservices communication
- Cost optimization through proper resource allocation

### Mumbai Metaphors की Learning:
- Services = Local train connectivity
- Auto-scaling = Extra trains during rush hour
- Service Mesh = Advanced dabbawala coordination system
- Resource optimization = Efficient compartment utilization

अगले Part 3 में हम देखेंगे:
- CI/CD pipelines for Kubernetes
- Monitoring और logging at scale
- Disaster recovery strategies
- Security best practices
- Multi-cloud deployment strategies

### Production Tips:
1. हमेशा resource requests और limits set करें
2. ConfigMaps का use करें hardcoded values के बजाय
3. Secrets को properly encrypt करें
4. Auto-scaling policies को realistic metrics के साथ configure करें
5. Service mesh use करें complex microservices के लिए

Total word count: 7,000+ words
Next episode focus: Complete DevOps pipeline और production deployment strategies

**Episode 17 Part 2 complete! 🚀**