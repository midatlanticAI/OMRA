# OpenManus Deployment Guide

Welcome to the OpenManus Deployment Guide. This guide provides comprehensive instructions for deploying the OpenManus Appliance Repair Business Automation System in various environments.

## Table of Contents

1. [Introduction](#introduction)
2. [Deployment Options](#deployment-options)
3. [System Requirements](#system-requirements)
4. [Environment Setup](#environment-setup)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Database Setup](#database-setup)
8. [Configuration](#configuration)
9. [Security Considerations](#security-considerations)
10. [Monitoring](#monitoring)
11. [Backup and Recovery](#backup-and-recovery)
12. [Scaling](#scaling)
13. [Upgrades](#upgrades)
14. [Troubleshooting](#troubleshooting)

## Introduction

OpenManus can be deployed in various environments, from single-server setups to distributed cloud deployments. This guide covers all aspects of deploying OpenManus, including environment setup, configuration, security, monitoring, backup, and scaling.

The deployment process is designed to be flexible, allowing you to choose the approach that best fits your organization's needs and technical capabilities.

## Deployment Options

OpenManus offers several deployment options:

1. **Docker Compose**: Simple, single-server deployment using Docker Compose.
2. **Kubernetes**: Scalable, distributed deployment using Kubernetes.
3. **Manual Installation**: Traditional deployment on physical or virtual servers.
4. **Cloud-Managed Services**: Deployment using cloud-managed services like AWS ECS, Azure App Service, or Google Cloud Run.

Each option has its own advantages and considerations, which are outlined in the respective sections.

## System Requirements

### Docker Compose Deployment

- **CPU**: 4 cores (minimum), 8 cores (recommended)
- **RAM**: 8 GB (minimum), 16 GB (recommended)
- **Storage**: 100 GB (minimum), SSD recommended
- **Operating System**: Linux (Ubuntu 20.04+ or similar)
- **Software**: Docker 20.10+, Docker Compose 2.0+

### Kubernetes Deployment

- **Control Plane**:
  - **CPU**: 2 cores per node
  - **RAM**: 4 GB per node
  - **Storage**: 50 GB per node, SSD recommended
- **Worker Nodes** (minimum 3):
  - **CPU**: 4 cores per node
  - **RAM**: 8 GB per node
  - **Storage**: 100 GB per node, SSD recommended
- **Kubernetes Version**: 1.24+
- **Required Tools**: kubectl, Helm 3+

### Manual Installation

- **CPU**: 4 cores (minimum), 8 cores (recommended)
- **RAM**: 8 GB (minimum), 16 GB (recommended)
- **Storage**: 100 GB (minimum), SSD recommended
- **Operating System**: Linux (Ubuntu 20.04+ or similar)
- **Software**:
  - Python 3.10+
  - Node.js 18+
  - PostgreSQL 14+
  - MongoDB 6+
  - Redis 7+
  - Nginx or similar web server

## Environment Setup

This section covers the basic environment setup for all deployment options. Specific instructions for each deployment option are provided in their respective sections.

### Clone the Repository

```bash
git clone https://github.com/openmanus/openmanus.git
cd openmanus
```

### Set Up Environment Variables

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to set the required environment variables, including:

- Database connection details
- API keys for third-party services
- Security settings
- Application configuration

See [Configuration](#configuration) for details on the available environment variables.

## Docker Deployment

Docker is the simplest way to deploy OpenManus. This section covers deployment using Docker Compose.

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Access to Docker Hub or a private Docker registry

### Deployment Steps

1. Clone the repository and set up environment variables as described in [Environment Setup](#environment-setup).

2. Build and start the containers:

```bash
docker-compose up -d
```

3. Initialize the database:

```bash
docker-compose exec api python -m backend.db.init_db
```

4. Create an admin user:

```bash
docker-compose exec api python -m backend.utils.create_admin \
  --email admin@example.com \
  --password secretpassword \
  --full-name "Admin User"
```

5. Access the application:
   - Web UI: http://localhost:80
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

See [docker-compose.yml](docker-compose.yml) for details on the container configuration.

## Kubernetes Deployment

Kubernetes provides a scalable, distributed deployment option for OpenManus. This section covers deployment using Kubernetes.

### Prerequisites

- Kubernetes 1.24+
- kubectl
- Helm 3+

### Deployment Steps

1. Clone the repository:

```bash
git clone https://github.com/openmanus/openmanus.git
cd openmanus
```

2. Create a namespace for OpenManus:

```bash
kubectl create namespace openmanus
```

3. Create a secret for environment variables:

```bash
kubectl create secret generic openmanus-env \
  --from-file=.env \
  -n openmanus
```

4. Deploy OpenManus using Helm:

```bash
helm install openmanus ./helm/openmanus \
  --namespace openmanus \
  --values ./helm/openmanus/values.yaml
```

5. Verify the deployment:

```bash
kubectl get pods -n openmanus
```

6. Access the application:
   - Get the external IP:
     ```bash
     kubectl get service openmanus-frontend -n openmanus
     ```
   - Web UI: http://<EXTERNAL_IP>
   - API: http://<EXTERNAL_IP>/api
   - API Documentation: http://<EXTERNAL_IP>/api/docs

See [Kubernetes Deployment](kubernetes.md) for detailed instructions, including configuration options and advanced scenarios.

## Database Setup

OpenManus uses PostgreSQL for structured data and MongoDB for unstructured data. This section covers database setup and configuration.

### PostgreSQL Setup

1. Create a PostgreSQL database:

```bash
createdb openmanus
```

2. Create a PostgreSQL user:

```bash
createuser -P openmanus
```

3. Grant privileges to the user:

```sql
GRANT ALL PRIVILEGES ON DATABASE openmanus TO openmanus;
```

4. Configure the connection in the `.env` file:

```
DATABASE_URL=postgresql://openmanus:password@localhost:5432/openmanus
```

### MongoDB Setup

1. Create a MongoDB database:

```javascript
use openmanus
```

2. Create a MongoDB user:

```javascript
db.createUser({
  user: "openmanus",
  pwd: "password",
  roles: [{ role: "readWrite", db: "openmanus" }]
})
```

3. Configure the connection in the `.env` file:

```
MONGODB_URL=mongodb://openmanus:password@localhost:27017/openmanus
```

## Configuration

OpenManus is configured using environment variables. This section covers the available configuration options.

### Core Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development, staging, production) | `development` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Secret key for JWT tokens | *Required* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration in minutes | `60` |
| `ENCRYPTION_KEY` | Key for encrypting sensitive data | *Required* |

### Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | *Required* |
| `MONGODB_URL` | MongoDB connection URL | *Required* |
| `MONGODB_DATABASE` | MongoDB database name | `openmanus` |

### API Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_V1_STR` | API prefix | `/api` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `[]` |

### AI Services Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | *Optional* |
| `OPENAI_API_KEY` | OpenAI API key | *Optional* |

### Third-Party Integration Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GHL_API_KEY` | Go High Level API key | *Optional* |
| `GHL_LOCATION_ID` | Go High Level location ID | *Optional* |
| `KICKSERV_API_KEY` | Kickserv API key | *Optional* |
| `KICKSERV_ACCOUNT` | Kickserv account name | *Optional* |

See [Environment Variables](environment-variables.md) for a complete list of available environment variables.

## Security Considerations

This section covers security considerations for deploying OpenManus.

### API Security

- **HTTPS**: Always use HTTPS in production
- **API Keys**: Secure storage of API keys
- **Rate Limiting**: Configure rate limiting to prevent abuse
- **Input Validation**: Ensure proper input validation
- **Authentication**: Secure JWT tokens

### Database Security

- **Connection Security**: Use SSL for database connections
- **Access Control**: Limit database access to necessary permissions
- **Data Encryption**: Encrypt sensitive data
- **Backup Security**: Secure database backups

### Network Security

- **Firewalls**: Configure firewalls to limit access
- **VPCs**: Use VPCs to isolate components
- **Load Balancers**: Configure security groups for load balancers

### Compliance

- **GDPR**: Ensure compliance with GDPR if applicable
- **HIPAA**: Ensure compliance with HIPAA if applicable
- **PCI DSS**: Ensure compliance with PCI DSS if applicable

See [Security Guide](security.md) for detailed security guidelines.

## Monitoring

OpenManus provides built-in monitoring capabilities. This section covers monitoring setup and configuration.

### Prometheus Integration

OpenManus exposes Prometheus metrics at `/metrics`. This section covers setting up Prometheus monitoring.

1. Deploy Prometheus using Helm:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace
```

2. Configure Prometheus to scrape OpenManus metrics:

```yaml
scrape_configs:
  - job_name: 'openmanus'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['openmanus-backend:8000']
```

### Grafana Dashboard

We provide a Grafana dashboard for visualizing OpenManus metrics. This section covers setting up the Grafana dashboard.

1. Deploy Grafana using Helm:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana \
  --namespace monitoring
```

2. Import the OpenManus dashboard:
   - Go to Grafana: http://<GRAFANA_IP>
   - Navigate to Dashboards > Import
   - Upload the dashboard JSON from `monitoring/grafana/dashboard.json`

See [Monitoring Guide](monitoring.md) for detailed monitoring instructions.

## Backup and Recovery

This section covers backup and recovery procedures for OpenManus.

### Database Backup

1. PostgreSQL backup:

```bash
pg_dump -h <DB_HOST> -U <DB_USER> -d openmanus -F c -f openmanus.dump
```

2. MongoDB backup:

```bash
mongodump --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus --out /path/to/backup
```

### Automated Backup

We provide a script for automated backup. This section covers setting up automated backups.

1. Set up a cron job to run the backup script:

```bash
0 1 * * * /path/to/openmanus/scripts/backup.sh
```

2. Configure backup retention:

```bash
# Keep backups for 30 days
BACKUP_RETENTION_DAYS=30
```

### Recovery

1. PostgreSQL recovery:

```bash
pg_restore -h <DB_HOST> -U <DB_USER> -d openmanus -c openmanus.dump
```

2. MongoDB recovery:

```bash
mongorestore --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus /path/to/backup/openmanus
```

See [Backup and Recovery Guide](backup.md) for detailed backup and recovery instructions.

## Scaling

This section covers scaling OpenManus for high availability and performance.

### Horizontal Scaling

1. Backend scaling:
   - Increase the number of backend replicas:
     ```bash
     kubectl scale deployment openmanus-backend --replicas=5 -n openmanus
     ```

2. Frontend scaling:
   - Increase the number of frontend replicas:
     ```bash
     kubectl scale deployment openmanus-frontend --replicas=3 -n openmanus
     ```

### Database Scaling

1. PostgreSQL scaling:
   - Set up PostgreSQL replication
   - Configure connection pooling with PgBouncer

2. MongoDB scaling:
   - Set up MongoDB replica set
   - Configure sharding for high volume data

### Caching

1. Redis caching:
   - Deploy Redis
   - Configure OpenManus to use Redis for caching

See [Scaling Guide](scaling.md) for detailed scaling instructions.

## Upgrades

This section covers upgrading OpenManus to newer versions.

### Upgrade Process

1. Back up the database:
   - Follow the backup procedure in [Backup and Recovery](#backup-and-recovery)

2. Update the repository:
   ```bash
   git pull origin main
   ```

3. Update dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. Apply database migrations:
   ```bash
   alembic upgrade head
   ```

5. Restart the application:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Version-Specific Upgrade Notes

See [Upgrade Guide](upgrade.md) for version-specific upgrade instructions.

## Troubleshooting

This section provides solutions to common issues you might encounter during deployment.

### Common Issues

1. **Database Connection Issues**:
   - Check database connection settings
   - Verify network connectivity
   - Check database user permissions

2. **API Connection Issues**:
   - Check API server status
   - Verify network connectivity
   - Check firewall settings

3. **Authentication Issues**:
   - Verify JWT secret key
   - Check token expiration settings
   - Verify user credentials

See [Troubleshooting Guide](troubleshooting.md) for detailed troubleshooting instructions.

## Complete Documentation Set

This guide is part of a complete documentation set for deploying and operating OpenManus. Here are all the available deployment guides:

| Guide | Description |
|-------|-------------|
| [README.md](README.md) | Main deployment guide (this file) |
| [environment-variables.md](environment-variables.md) | Complete reference for environment variables |
| [security.md](security.md) | Security best practices and configuration |
| [kubernetes.md](kubernetes.md) | Detailed Kubernetes deployment instructions |
| [monitoring.md](monitoring.md) | Setting up monitoring with Prometheus and Grafana |
| [backup.md](backup.md) | Backup and recovery procedures |
| [troubleshooting.md](troubleshooting.md) | Solutions to common deployment issues |

For other aspects of the OpenManus system, see:

- [API Documentation](../api/README.md): Reference for the OpenManus API
- [Developer Guide](../developer/README.md): Information for developers working with the codebase
- [User Manual](../user-manual/README.md): End-user documentation for using OpenManus 