# Kubernetes Deployment Guide for OpenManus

This guide provides detailed instructions for deploying the OpenManus Appliance Repair Business Automation System on Kubernetes. It covers setting up all necessary components, configuration, scaling, and maintenance.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Kubernetes Architecture](#kubernetes-architecture)
4. [Deployment Overview](#deployment-overview)
5. [Namespace Setup](#namespace-setup)
6. [Secrets Management](#secrets-management)
7. [ConfigMaps](#configmaps)
8. [Database Deployment](#database-deployment)
9. [Cache Deployment](#cache-deployment)
10. [Backend API Deployment](#backend-api-deployment)
11. [Frontend Deployment](#frontend-deployment)
12. [Agent System Deployment](#agent-system-deployment)
13. [Ingress Configuration](#ingress-configuration)
14. [Persistence Configuration](#persistence-configuration)
15. [Scaling](#scaling)
16. [Monitoring](#monitoring)
17. [Maintenance](#maintenance)
18. [Troubleshooting](#troubleshooting)

## Introduction

Kubernetes provides a scalable, resilient platform for deploying OpenManus. This guide will help you set up a production-ready Kubernetes deployment with high availability and scalability.

### Benefits of Kubernetes Deployment

- **Scalability**: Easily scale components up or down based on demand
- **High Availability**: Run multiple replicas across different nodes for fault tolerance
- **Resource Efficiency**: Optimize resource usage with container orchestration
- **Self-Healing**: Automatic recovery from failures
- **Rolling Updates**: Zero-downtime deployments and updates
- **Monitoring and Logging**: Built-in support for monitoring and logging

## Prerequisites

Before you begin, ensure you have:

- A Kubernetes cluster (version 1.24+)
- `kubectl` installed and configured to access your cluster
- Helm 3 installed
- Persistent storage provider (e.g., AWS EBS, Google Persistent Disk, etc.)
- Ingress controller installed (e.g., Nginx Ingress, Traefik, etc.)
- Domain name configured for your OpenManus installation
- TLS certificate or cert-manager configured for SSL

### Resource Requirements

For a production deployment, we recommend:

- **Control Plane**:
  - At least 3 control plane nodes for high availability
  - 2 vCPUs per node
  - 4 GB RAM per node
- **Worker Nodes** (minimum 3):
  - 4 vCPUs per node
  - 8 GB RAM per node
  - 100 GB storage per node

## Kubernetes Architecture

OpenManus on Kubernetes consists of the following components:

![OpenManus Kubernetes Architecture](images/kubernetes-architecture.png)

- **Backend API**: FastAPI application running as a Deployment
- **Frontend**: React application served by Nginx as a Deployment
- **Agent System**: Agent Manager and worker nodes as Deployments
- **Databases**: PostgreSQL and MongoDB as StatefulSets
- **Redis**: For caching and task queue as a StatefulSet
- **Ingress**: For routing external traffic to services

## Deployment Overview

Here's an overview of the deployment process:

1. Create a namespace for OpenManus
2. Set up Secrets and ConfigMaps
3. Deploy databases (PostgreSQL and MongoDB)
4. Deploy Redis cache
5. Deploy the backend API
6. Deploy the frontend
7. Deploy the agent system
8. Configure Ingress
9. Set up persistence
10. Configure monitoring

## Namespace Setup

Start by creating a dedicated namespace for OpenManus:

```bash
kubectl create namespace openmanus
```

Set this namespace as the default for subsequent commands:

```bash
kubectl config set-context --current --namespace=openmanus
```

## Secrets Management

Create secrets for database credentials, API keys, and other sensitive information:

### Database Credentials

```bash
kubectl create secret generic openmanus-db-credentials \
  --from-literal=postgresql-password=<POSTGRESQL_PASSWORD> \
  --from-literal=postgresql-username=openmanus \
  --from-literal=mongodb-password=<MONGODB_PASSWORD> \
  --from-literal=mongodb-username=openmanus \
  --from-literal=redis-password=<REDIS_PASSWORD>
```

### API Keys and Tokens

```bash
kubectl create secret generic openmanus-api-keys \
  --from-literal=secret-key=<SECRET_KEY> \
  --from-literal=encryption-key=<ENCRYPTION_KEY> \
  --from-literal=anthropic-api-key=<ANTHROPIC_API_KEY> \
  --from-literal=openai-api-key=<OPENAI_API_KEY> \
  --from-literal=ghl-api-key=<GHL_API_KEY> \
  --from-literal=ghl-location-id=<GHL_LOCATION_ID> \
  --from-literal=kickserv-api-key=<KICKSERV_API_KEY> \
  --from-literal=kickserv-account=<KICKSERV_ACCOUNT>
```

### TLS Certificate

If you're not using cert-manager, create a secret for your TLS certificate:

```bash
kubectl create secret tls openmanus-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

## ConfigMaps

Create ConfigMaps for non-sensitive configuration:

### Backend Configuration

```bash
cat > backend-config.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: openmanus-backend-config
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  SERVER_HOST: "0.0.0.0"
  SERVER_PORT: "8000"
  API_V1_STR: "/api"
  BACKEND_CORS_ORIGINS: '["https://app.openmanus.io"]'
  DATABASE_POOL_SIZE: "10"
  DATABASE_MAX_OVERFLOW: "20"
  MONGODB_DATABASE: "openmanus"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  ACCESS_TOKEN_EXPIRE_MINUTES: "60"
  ENABLE_METRICS: "true"
  METRICS_PREFIX: "openmanus_"
  ENABLE_HEALTH_CHECK: "true"
  HEALTH_CHECK_PATH: "/health"
EOF

kubectl apply -f backend-config.yaml
```

### Frontend Configuration

```bash
cat > frontend-config.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: openmanus-frontend-config
data:
  VITE_API_URL: "https://app.openmanus.io/api"
  VITE_APP_TITLE: "OpenManus"
  VITE_DEFAULT_LOCALE: "en"
EOF

kubectl apply -f frontend-config.yaml
```

## Database Deployment

### PostgreSQL Deployment

Use Helm to deploy PostgreSQL:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install postgresql bitnami/postgresql \
  --set global.postgresql.auth.username=openmanus \
  --set global.postgresql.auth.password=$(kubectl get secret openmanus-db-credentials -o jsonpath="{.data.postgresql-password}" | base64 --decode) \
  --set global.postgresql.auth.database=openmanus \
  --set primary.persistence.size=20Gi \
  --set primary.resources.requests.memory=2Gi \
  --set primary.resources.requests.cpu=1 \
  --set primary.resources.limits.memory=4Gi \
  --set primary.resources.limits.cpu=2
```

### MongoDB Deployment

Use Helm to deploy MongoDB:

```bash
helm install mongodb bitnami/mongodb \
  --set auth.rootPassword=$(kubectl get secret openmanus-db-credentials -o jsonpath="{.data.mongodb-password}" | base64 --decode) \
  --set auth.username=openmanus \
  --set auth.password=$(kubectl get secret openmanus-db-credentials -o jsonpath="{.data.mongodb-password}" | base64 --decode) \
  --set auth.database=openmanus \
  --set persistence.size=20Gi \
  --set resources.requests.memory=2Gi \
  --set resources.requests.cpu=1 \
  --set resources.limits.memory=4Gi \
  --set resources.limits.cpu=2
```

## Cache Deployment

Deploy Redis for caching and task queue:

```bash
helm install redis bitnami/redis \
  --set auth.password=$(kubectl get secret openmanus-db-credentials -o jsonpath="{.data.redis-password}" | base64 --decode) \
  --set architecture=standalone \
  --set master.persistence.size=5Gi \
  --set master.resources.requests.memory=1Gi \
  --set master.resources.requests.cpu=0.5 \
  --set master.resources.limits.memory=2Gi \
  --set master.resources.limits.cpu=1
```

## Backend API Deployment

Create a deployment YAML file for the backend API:

```bash
cat > backend-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmanus-backend
  labels:
    app: openmanus
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openmanus
      component: backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: openmanus
        component: backend
    spec:
      containers:
      - name: api
        image: openmanus/backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: openmanus-backend-config
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: secret-key
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: encryption-key
        - name: DATABASE_URL
          value: "postgresql://openmanus:$(POSTGRESQL_PASSWORD)@postgresql/openmanus"
        - name: POSTGRESQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: postgresql-password
        - name: MONGODB_URL
          value: "mongodb://openmanus:$(MONGODB_PASSWORD)@mongodb/openmanus"
        - name: MONGODB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: mongodb-password
        - name: REDIS_URL
          value: "redis://:$(REDIS_PASSWORD)@redis-master:6379/0"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: redis-password
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: anthropic-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: openai-api-key
        - name: GHL_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: ghl-api-key
        - name: GHL_LOCATION_ID
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: ghl-location-id
        - name: KICKSERV_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: kickserv-api-key
        - name: KICKSERV_ACCOUNT
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: kickserv-account
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: storage
          mountPath: /app/uploads
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: openmanus-storage-pvc
EOF

kubectl apply -f backend-deployment.yaml
```

Create a service for the backend API:

```bash
cat > backend-service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: openmanus-backend
  labels:
    app: openmanus
    component: backend
spec:
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: openmanus
    component: backend
EOF

kubectl apply -f backend-service.yaml
```

## Frontend Deployment

Create a deployment YAML file for the frontend:

```bash
cat > frontend-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmanus-frontend
  labels:
    app: openmanus
    component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openmanus
      component: frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: openmanus
        component: frontend
    spec:
      containers:
      - name: frontend
        image: openmanus/frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: openmanus-frontend-config
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
EOF

kubectl apply -f frontend-deployment.yaml
```

Create a service for the frontend:

```bash
cat > frontend-service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: openmanus-frontend
  labels:
    app: openmanus
    component: frontend
spec:
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  selector:
    app: openmanus
    component: frontend
EOF

kubectl apply -f frontend-service.yaml
```

## Agent System Deployment

Create a deployment YAML file for the agent system:

```bash
cat > agent-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmanus-agent
  labels:
    app: openmanus
    component: agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openmanus
      component: agent
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: openmanus
        component: agent
    spec:
      containers:
      - name: agent
        image: openmanus/agent:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: openmanus-backend-config
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: secret-key
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: encryption-key
        - name: DATABASE_URL
          value: "postgresql://openmanus:$(POSTGRESQL_PASSWORD)@postgresql/openmanus"
        - name: POSTGRESQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: postgresql-password
        - name: MONGODB_URL
          value: "mongodb://openmanus:$(MONGODB_PASSWORD)@mongodb/openmanus"
        - name: MONGODB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: mongodb-password
        - name: REDIS_URL
          value: "redis://:$(REDIS_PASSWORD)@redis-master:6379/0"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: redis-password
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: anthropic-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openmanus-api-keys
              key: openai-api-key
        - name: AGENT_SYSTEM_ENABLED
          value: "true"
        - name: AGENT_MAX_THINKING_TOKENS
          value: "2000"
        - name: AGENT_MAX_CONVERSATIONS
          value: "10"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2
            memory: 4Gi
EOF

kubectl apply -f agent-deployment.yaml
```

## Ingress Configuration

Create an Ingress resource for external access:

```bash
cat > ingress.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openmanus-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - app.openmanus.io
    secretName: openmanus-tls
  rules:
  - host: app.openmanus.io
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: openmanus-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openmanus-frontend
            port:
              number: 80
EOF

kubectl apply -f ingress.yaml
```

## Persistence Configuration

Create Persistent Volume Claims for storage:

```bash
cat > storage-pvc.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openmanus-storage-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
EOF

kubectl apply -f storage-pvc.yaml
```

## Scaling

### Horizontal Pod Autoscaler (HPA)

Create HPAs for automatic scaling based on resource usage:

```bash
cat > hpa.yaml << EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openmanus-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openmanus-backend
  minReplicas: 3
  maxReplicas: 10
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
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openmanus-frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openmanus-frontend
  minReplicas: 2
  maxReplicas: 5
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
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openmanus-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openmanus-agent
  minReplicas: 2
  maxReplicas: 10
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
EOF

kubectl apply -f hpa.yaml
```

### Manual Scaling

You can manually scale deployments:

```bash
kubectl scale deployment openmanus-backend --replicas=5
kubectl scale deployment openmanus-frontend --replicas=3
kubectl scale deployment openmanus-agent --replicas=5
```

## Monitoring

### Prometheus and Grafana

See the [Monitoring Guide](monitoring.md) for detailed instructions on setting up Prometheus and Grafana for monitoring OpenManus.

### Liveness and Readiness Probes

Liveness and readiness probes are already configured in the deployment YAML files. They use the `/health` endpoint to check if the application is responsive.

## Maintenance

### Updates and Upgrades

To update the OpenManus components:

```bash
# Update the backend
kubectl set image deployment/openmanus-backend api=openmanus/backend:new-version

# Update the frontend
kubectl set image deployment/openmanus-frontend frontend=openmanus/frontend:new-version

# Update the agent system
kubectl set image deployment/openmanus-agent agent=openmanus/agent:new-version
```

### Database Migrations

Run database migrations as a Kubernetes Job:

```bash
cat > migration-job.yaml << EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: openmanus-migration
spec:
  ttlSecondsAfterFinished: 100
  template:
    spec:
      containers:
      - name: migration
        image: openmanus/backend:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
        - configMapRef:
            name: openmanus-backend-config
        env:
        - name: DATABASE_URL
          value: "postgresql://openmanus:$(POSTGRESQL_PASSWORD)@postgresql/openmanus"
        - name: POSTGRESQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: openmanus-db-credentials
              key: postgresql-password
      restartPolicy: Never
  backoffLimit: 4
EOF

kubectl apply -f migration-job.yaml
```

### Backup and Restore

See the [Backup and Recovery Guide](backup.md) for detailed instructions on backing up and restoring OpenManus.

## Troubleshooting

### Viewing Logs

```bash
# Backend logs
kubectl logs -l app=openmanus,component=backend

# Frontend logs
kubectl logs -l app=openmanus,component=frontend

# Agent system logs
kubectl logs -l app=openmanus,component=agent

# PostgreSQL logs
kubectl logs -l app=postgresql

# MongoDB logs
kubectl logs -l app=mongodb

# Redis logs
kubectl logs -l app=redis
```

### Common Issues

#### Pods Not Starting

If pods are not starting, check the events:

```bash
kubectl describe pod <pod-name>
```

#### Database Connection Issues

If the application cannot connect to the database:

1. Check the database service:
   ```bash
   kubectl get svc postgresql
   kubectl get svc mongodb
   ```

2. Check database credentials:
   ```bash
   kubectl get secret openmanus-db-credentials -o yaml
   ```

3. Check database pod status:
   ```bash
   kubectl get pods -l app=postgresql
   kubectl get pods -l app=mongodb
   ```

#### API Errors

If the API returns errors:

1. Check the backend logs:
   ```bash
   kubectl logs -l app=openmanus,component=backend
   ```

2. Check if the API is running:
   ```bash
   kubectl get pods -l app=openmanus,component=backend
   ```

3. Check the health endpoint:
   ```bash
   kubectl port-forward svc/openmanus-backend 8000:8000
   curl http://localhost:8000/health
   ```

#### Ingress Issues

If the Ingress is not working:

1. Check the Ingress resource:
   ```bash
   kubectl get ingress openmanus-ingress
   kubectl describe ingress openmanus-ingress
   ```

2. Check the Ingress controller logs:
   ```bash
   kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
   ```

3. Verify the TLS certificate:
   ```bash
   kubectl get secret openmanus-tls -o yaml
   ```

### Restarting Components

If you need to restart components:

```bash
# Restart the backend
kubectl rollout restart deployment openmanus-backend

# Restart the frontend
kubectl rollout restart deployment openmanus-frontend

# Restart the agent system
kubectl rollout restart deployment openmanus-agent
``` 