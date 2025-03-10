# OpenManus Monitoring Guide

This guide provides detailed instructions for setting up monitoring for your OpenManus deployment. Proper monitoring is essential for maintaining system health, identifying performance bottlenecks, and ensuring optimal user experience.

## Table of Contents

1. [Introduction](#introduction)
2. [Metrics Collection](#metrics-collection)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Setup](#grafana-setup)
5. [Alert Configuration](#alert-configuration)
6. [Log Management](#log-management)
7. [Health Checks](#health-checks)
8. [Key Performance Indicators](#key-performance-indicators)
9. [Troubleshooting](#troubleshooting)

## Introduction

OpenManus provides built-in monitoring capabilities through a `/metrics` endpoint that exposes Prometheus-compatible metrics. These metrics cover various aspects of the system, including:

- HTTP request counts, latencies, and error rates
- Database connection pool status
- Cache hit/miss rates
- Task queue sizes and processing times
- Agent system performance metrics
- Business metrics (service requests, customers, etc.)

This guide explains how to set up a complete monitoring stack using:

- **Prometheus**: For metrics collection and storage
- **Grafana**: For visualization and dashboarding
- **Alertmanager**: For alert management
- **Loki**: For log aggregation and searching
- **Jaeger**: For distributed tracing (optional)

## Metrics Collection

### Available Metrics

OpenManus exposes the following metrics at the `/metrics` endpoint:

| Metric Name | Type | Description |
|-------------|------|-------------|
| `openmanus_http_requests_total` | Counter | Total number of HTTP requests |
| `openmanus_http_request_duration_seconds` | Histogram | HTTP request duration in seconds |
| `openmanus_http_requests_in_progress` | Gauge | Number of HTTP requests in progress |
| `openmanus_database_connections` | Gauge | Number of active database connections |
| `openmanus_database_pool_size` | Gauge | Size of the database connection pool |
| `openmanus_cache_hits_total` | Counter | Total number of cache hits |
| `openmanus_cache_misses_total` | Counter | Total number of cache misses |
| `openmanus_task_queue_size` | Gauge | Size of the task queue |
| `openmanus_task_processing_time_seconds` | Histogram | Task processing time in seconds |
| `openmanus_service_requests_total` | Counter | Total number of service requests |
| `openmanus_service_requests_by_status` | Gauge | Number of service requests by status |
| `openmanus_agent_executions_total` | Counter | Total number of agent executions |
| `openmanus_agent_execution_time_seconds` | Histogram | Agent execution time in seconds |

### Enabling Metrics

Metrics are enabled by default. You can configure the metrics behavior using the following environment variables:

```env
ENABLE_METRICS=true
METRICS_PREFIX=openmanus_
```

## Prometheus Setup

Prometheus is used to collect and store metrics from OpenManus.

### Using Helm (Kubernetes)

1. Add the Prometheus Helm repository:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

2. Create a values file for Prometheus configuration:

```bash
cat > prometheus-values.yaml << EOF
server:
  global:
    scrape_interval: 15s
    evaluation_interval: 15s
  
  extraScrapeConfigs: |
    - job_name: 'openmanus'
      metrics_path: '/metrics'
      scrape_interval: 5s
      static_configs:
        - targets: ['openmanus-backend:8000']
EOF
```

3. Install Prometheus using Helm:

```bash
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  --values prometheus-values.yaml
```

### Using Docker Compose

1. Add Prometheus to your Docker Compose file:

```yaml
services:
  # ... other services ...
  
  prometheus:
    image: prom/prometheus:v2.43.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped

volumes:
  prometheus_data:
```

2. Create a Prometheus configuration file:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'openmanus'
    metrics_path: '/metrics'
    scrape_interval: 5s
    static_configs:
      - targets: ['api:8000']
```

3. Start the services:

```bash
docker-compose up -d
```

### Manual Installation

1. Download Prometheus from the [official website](https://prometheus.io/download/).

2. Create a configuration file:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'openmanus'
    metrics_path: '/metrics'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:8000']
```

3. Start Prometheus:

```bash
./prometheus --config.file=prometheus.yml
```

## Grafana Setup

Grafana is used to visualize the metrics collected by Prometheus.

### Using Helm (Kubernetes)

1. Add the Grafana Helm repository:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Create a values file for Grafana configuration:

```bash
cat > grafana-values.yaml << EOF
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus-server
        access: proxy
        isDefault: true

dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default

dashboards:
  default:
    openmanus-dashboard:
      url: https://raw.githubusercontent.com/openmanus/openmanus/main/monitoring/grafana/dashboard.json
EOF
```

3. Install Grafana using Helm:

```bash
helm install grafana grafana/grafana \
  --namespace monitoring \
  --values grafana-values.yaml
```

4. Get the Grafana admin password:

```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

5. Access Grafana:

```bash
kubectl port-forward --namespace monitoring service/grafana 3000:80
```

Visit http://localhost:3000 and log in with username `admin` and the password from step 4.

### Using Docker Compose

1. Add Grafana to your Docker Compose file:

```yaml
services:
  # ... other services ...
  
  grafana:
    image: grafana/grafana:9.5.1
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  grafana_data:
```

2. Create a data source configuration:

```yaml
# ./grafana/provisioning/datasources/datasource.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

3. Copy the OpenManus dashboard to `./grafana/dashboards/openmanus-dashboard.json`

4. Create a dashboard provider configuration:

```yaml
# ./grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
```

5. Start the services:

```bash
docker-compose up -d
```

Visit http://localhost:3000 and log in with username `admin` and password `admin`.

## Alert Configuration

Alertmanager is used to manage alerts from Prometheus.

### Using Helm (Kubernetes)

When installing Prometheus with Helm, Alertmanager is included by default. To configure alerts:

1. Create a values file for Prometheus configuration with alerts:

```bash
cat > prometheus-values.yaml << EOF
server:
  global:
    scrape_interval: 15s
    evaluation_interval: 15s
  
  extraScrapeConfigs: |
    - job_name: 'openmanus'
      metrics_path: '/metrics'
      scrape_interval: 5s
      static_configs:
        - targets: ['openmanus-backend:8000']

  alerting:
    alertmanagers:
      - static_configs:
          - targets:
            - alertmanager:9093

alertmanager:
  config:
    global:
      resolve_timeout: 5m
    route:
      group_by: ['alertname', 'job']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'email'
    receivers:
    - name: 'email'
      email_configs:
      - to: 'alerts@example.com'
        from: 'prometheus@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'smtp_user'
        auth_password: 'smtp_password'

serverFiles:
  alerts:
    groups:
      - name: openmanus
        rules:
        - alert: HighRequestLatency
          expr: openmanus_http_request_duration_seconds{quantile="0.9"} > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High request latency"
            description: "90th percentile request latency is above 1 second for 5 minutes"
        - alert: HighErrorRate
          expr: rate(openmanus_http_requests_total{status_code=~"5.."}[5m]) / rate(openmanus_http_requests_total[5m]) > 0.1
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate"
            description: "Error rate is above 10% for 5 minutes"
        - alert: DatabaseConnectionsHigh
          expr: openmanus_database_connections / openmanus_database_pool_size > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Database connections high"
            description: "Database connections are above 80% of pool size for 5 minutes"
EOF
```

2. Update or install Prometheus with the new values:

```bash
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --values prometheus-values.yaml
```

### Using Docker Compose

1. Update your Prometheus configuration:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'openmanus'
    metrics_path: '/metrics'
    scrape_interval: 5s
    static_configs:
      - targets: ['api:8000']
```

2. Create an alerts configuration file:

```yaml
# alerts.yml
groups:
  - name: openmanus
    rules:
    - alert: HighRequestLatency
      expr: openmanus_http_request_duration_seconds{quantile="0.9"} > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High request latency"
        description: "90th percentile request latency is above 1 second for 5 minutes"
    - alert: HighErrorRate
      expr: rate(openmanus_http_requests_total{status_code=~"5.."}[5m]) / rate(openmanus_http_requests_total[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate"
        description: "Error rate is above 10% for 5 minutes"
    - alert: DatabaseConnectionsHigh
      expr: openmanus_database_connections / openmanus_database_pool_size > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Database connections high"
        description: "Database connections are above 80% of pool size for 5 minutes"
```

3. Add Alertmanager to your Docker Compose file:

```yaml
services:
  # ... other services ...
  
  alertmanager:
    image: prom/alertmanager:v0.25.0
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/config.yml
      - alertmanager_data:/alertmanager
    ports:
      - "9093:9093"
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped

volumes:
  alertmanager_data:
```

4. Create an Alertmanager configuration file:

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'job']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'email'

receivers:
- name: 'email'
  email_configs:
  - to: 'alerts@example.com'
    from: 'prometheus@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'smtp_user'
    auth_password: 'smtp_password'
```

5. Start the services:

```bash
docker-compose up -d
```

## Log Management

OpenManus logs are structured and can be collected and analyzed using various log management solutions.

### Using Loki with Grafana

[Loki](https://grafana.com/oss/loki/) is a horizontally-scalable, highly-available, multi-tenant log aggregation system designed to be cost-effective and easy to operate.

#### Kubernetes Setup

1. Add the Grafana Helm repository (if not already added):

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Install Loki and Promtail:

```bash
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi
```

3. Add Loki as a data source in Grafana:

```bash
cat > grafana-loki-datasource.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-loki-datasource
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  loki-datasource.yaml: |-
    apiVersion: 1
    datasources:
      - name: Loki
        type: loki
        url: http://loki:3100
        access: proxy
EOF

kubectl apply -f grafana-loki-datasource.yaml
```

#### Docker Compose Setup

1. Add Loki and Promtail to your Docker Compose file:

```yaml
services:
  # ... other services ...
  
  loki:
    image: grafana/loki:2.8.2
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    restart: unless-stopped
  
  promtail:
    image: grafana/promtail:2.8.2
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yaml
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers
    command: -config.file=/etc/promtail/config.yaml
    depends_on:
      - loki
    restart: unless-stopped

volumes:
  loki_data:
```

2. Create a Loki configuration file:

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /loki/index

  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

3. Create a Promtail configuration file:

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log

  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*.log
    pipeline_stages:
      - json:
          expressions:
            stream: stream
            attrs: attrs
            tag: attrs.tag
      - labels:
          stream:
          tag:
```

4. Add Loki as a data source in Grafana:

```yaml
# ./grafana/provisioning/datasources/loki.yml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
```

5. Start the services:

```bash
docker-compose up -d
```

## Health Checks

OpenManus provides a health check endpoint at `/health` that returns the status of various components of the system.

### Enabling Health Checks

Health checks are enabled by default. You can configure the health check behavior using the following environment variables:

```env
ENABLE_HEALTH_CHECK=true
HEALTH_CHECK_PATH=/health
```

### Health Check Response

The health check endpoint returns a JSON response with the status of various components:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2023-05-15T10:30:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "details": "Connected to PostgreSQL"
    },
    "mongodb": {
      "status": "healthy",
      "details": "Connected to MongoDB"
    },
    "redis": {
      "status": "healthy",
      "details": "Connected to Redis"
    },
    "task_queue": {
      "status": "healthy",
      "details": "Connected to task queue"
    }
  }
}
```

### Using Health Checks with Kubernetes

In Kubernetes, you can use the health check endpoint for liveness and readiness probes:

```yaml
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
```

## Key Performance Indicators

When monitoring OpenManus, focus on these key performance indicators (KPIs):

### System Health
- **Service Availability**: Percentage of time the service is available
- **Error Rate**: Number of errors per minute
- **Response Time**: 90th and 99th percentile response times

### Database Performance
- **Query Latency**: Time taken to execute database queries
- **Connection Pool Usage**: Percentage of database connections in use
- **Cache Hit Rate**: Percentage of cache hits vs. misses

### Application Performance
- **Request Rate**: Number of requests per second
- **Request Duration**: Time taken to process requests
- **Task Queue Size**: Number of tasks waiting in the queue
- **Task Processing Time**: Time taken to process tasks

### Business Metrics
- **Active Users**: Number of active users
- **Service Requests**: Number of service requests by status
- **Appointments**: Number of scheduled appointments
- **Agent Executions**: Number of agent executions and their duration

## Troubleshooting

### Common Issues

#### High Response Times

If you're experiencing high response times:

1. Check the database query latency
2. Check the cache hit rate
3. Check the CPU and memory usage
4. Check for slow endpoints using the request duration metrics

#### High Error Rate

If you're experiencing a high error rate:

1. Check the logs for error messages
2. Check the database connection status
3. Check the external service integrations
4. Check the memory usage and potential OOM events

#### Database Connection Issues

If you're experiencing database connection issues:

1. Check the database server status
2. Check the connection pool configuration
3. Check for connection leaks in the application
4. Check the network connectivity between the application and the database

### Useful Queries

Here are some useful Prometheus queries for troubleshooting:

#### Error Rate
```
sum(rate(openmanus_http_requests_total{status_code=~"5.."}[5m])) / sum(rate(openmanus_http_requests_total[5m]))
```

#### Slow Endpoints
```
topk(10, avg by (endpoint) (openmanus_http_request_duration_seconds{quantile="0.9"}))
```

#### Database Connection Usage
```
openmanus_database_connections / openmanus_database_pool_size
```

#### Cache Efficiency
```
sum(rate(openmanus_cache_hits_total[5m])) / (sum(rate(openmanus_cache_hits_total[5m])) + sum(rate(openmanus_cache_misses_total[5m])))
``` 