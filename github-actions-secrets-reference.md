# GitHub Actions Secrets Reference Guide

This document outlines all the secrets you need to configure in your GitHub repository for the OpenManus CI/CD pipeline to work properly.

## How to Add Secrets to Your GitHub Repository

1. Go to your repository on GitHub
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each secret with its corresponding value

## Required GitHub Secrets

### Docker Hub Credentials
```
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```
Note: For DOCKERHUB_TOKEN, create an access token in Docker Hub settings, not your regular password.

### Kubernetes Configuration
```
KUBE_CONFIG_STAGING
KUBE_CONFIG_PRODUCTION
```
These should be base64-encoded versions of your kubeconfig files:
```bash
cat ~/.kube/config | base64
```

### Notification Service
```
SLACK_WEBHOOK
```
Get this URL from Slack when configuring incoming webhooks.

### Database Credentials
```
DB_PASSWORD
MONGODB_URI
```

### API Keys and Service Credentials
```
ANTHROPIC_API_KEY
OPENAI_API_KEY
KICKSERV_API_TOKEN
GHL_API_KEY
```

### Authentication Secrets
```
JWT_SECRET
SECRET_KEY
```

### S3 Storage
```
S3_ACCESS_KEY
S3_SECRET_KEY
```

### Monitoring Credentials
```
PROMETHEUS_PASSWORD
GRAFANA_ADMIN_PASSWORD
```

### Messaging Services
```
SMTP_PASSWORD
TWILIO_AUTH_TOKEN
```

## Environment-specific Variables

The workflow can access environment variables configured at the Environment level in GitHub. Configure these in:
Settings > Environments > [environment name] > Environment secrets

### Staging Environment
```
DATABASE_URL_STAGING
REDIS_URL_STAGING
FRONTEND_URL_STAGING
```

### Production Environment
```
DATABASE_URL_PRODUCTION
REDIS_URL_PRODUCTION
FRONTEND_URL_PRODUCTION
```

## Security Notes

- Never commit the actual values of these secrets to your repository
- Regularly rotate API keys and tokens
- Use roles with minimum required permissions
- Consider using GitHub's secret scanning feature to detect accidentally committed credentials 