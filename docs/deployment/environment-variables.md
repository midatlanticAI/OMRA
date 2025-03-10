# OpenManus Environment Variables Reference

This document provides a complete reference for all environment variables used by the OpenManus system. Environment variables are used to configure various aspects of the system, including database connections, API settings, security, and third-party integrations.

## Core Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `ENVIRONMENT` | Deployment environment | Yes | `development` | `production` |
| `DEBUG` | Enable debug mode | No | `false` | `true` |
| `SECRET_KEY` | Secret key for JWT tokens | Yes | - | `your-secret-key-here` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration in minutes | No | `60` | `1440` |
| `ENCRYPTION_KEY` | Key for encrypting sensitive data | Yes | - | `your-encryption-key` |
| `LOG_LEVEL` | Logging level | No | `INFO` | `DEBUG` |
| `LOG_FORMAT` | Logging format | No | `json` | `text` |

## Database Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Yes | - | `postgresql://user:password@localhost:5432/openmanus` |
| `DATABASE_POOL_SIZE` | Database connection pool size | No | `5` | `10` |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | No | `10` | `20` |
| `MONGODB_URL` | MongoDB connection URL | Yes | - | `mongodb://user:password@localhost:27017/openmanus` |
| `MONGODB_DATABASE` | MongoDB database name | No | `openmanus` | `openmanus_prod` |
| `REDIS_URL` | Redis connection URL | No | - | `redis://localhost:6379/0` |

## API Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `API_V1_STR` | API prefix | No | `/api` | `/api/v1` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | No | `[]` | `["http://localhost:3000", "https://app.openmanus.com"]` |
| `MAX_REQUESTS_PER_MINUTE` | Rate limit for API requests | No | `60` | `100` |
| `SERVER_HOST` | Server host | No | `0.0.0.0` | `localhost` |
| `SERVER_PORT` | Server port | No | `8000` | `5000` |

## Security Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `SSL_CERT_PATH` | Path to SSL certificate | No | - | `/etc/ssl/certs/openmanus.crt` |
| `SSL_KEY_PATH` | Path to SSL key | No | - | `/etc/ssl/private/openmanus.key` |
| `ENABLE_HTTPS` | Enable HTTPS | No | `false` | `true` |
| `SECURE_COOKIES` | Require secure cookies | No | `false` | `true` |
| `SESSION_COOKIE_NAME` | Session cookie name | No | `openmanus_session` | `om_session` |
| `CSRF_SECRET` | CSRF protection secret | No | - | `your-csrf-secret` |

## AI Services Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | No | - | `your-anthropic-api-key` |
| `OPENAI_API_KEY` | OpenAI API key | No | - | `your-openai-api-key` |
| `AI_MODEL_VERSION` | AI model version to use | No | `claude-3-opus-20240229` | `gpt-4` |
| `AI_SERVICE_TIMEOUT` | Timeout for AI service requests (seconds) | No | `30` | `60` |
| `AI_MAX_TOKENS` | Maximum tokens for AI responses | No | `4000` | `8000` |

## Third-Party Integration Configuration

### Go High Level (GHL)

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `GHL_API_KEY` | Go High Level API key | No* | - | `your-ghl-api-key` |
| `GHL_LOCATION_ID` | Go High Level location ID | No* | - | `your-ghl-location-id` |
| `GHL_AGENCY_ID` | Go High Level agency ID | No | - | `your-ghl-agency-id` |
| `GHL_API_BASE_URL` | Go High Level API base URL | No | `https://services.leadconnectorhq.com` | `https://api.gohighlevel.com` |
| `GHL_WEBHOOK_SECRET` | Secret for GHL webhooks | No | - | `your-ghl-webhook-secret` |

*Required if GHL integration is enabled

### Kickserv

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `KICKSERV_API_KEY` | Kickserv API key | No* | - | `your-kickserv-api-key` |
| `KICKSERV_ACCOUNT` | Kickserv account name | No* | - | `your-kickserv-account` |
| `KICKSERV_API_BASE_URL` | Kickserv API base URL | No | `https://api.kickserv.com` | `https://api.kickserv.com/v1` |
| `KICKSERV_WEBHOOK_SECRET` | Secret for Kickserv webhooks | No | - | `your-kickserv-webhook-secret` |

*Required if Kickserv integration is enabled

## Email Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `SMTP_SERVER` | SMTP server | No | - | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | No | `587` | `465` |
| `SMTP_USERNAME` | SMTP username | No | - | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password | No | - | `your-smtp-password` |
| `SMTP_FROM_EMAIL` | From email address | No | `noreply@openmanus.com` | `support@yourdomain.com` |
| `SMTP_FROM_NAME` | From name | No | `OpenManus` | `Your Company Name` |
| `SMTP_TLS` | Use TLS | No | `true` | `false` |

## File Storage Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `STORAGE_TYPE` | Storage type (local, s3) | No | `local` | `s3` |
| `STORAGE_LOCAL_PATH` | Local storage path | No | `./uploads` | `/var/www/uploads` |
| `AWS_ACCESS_KEY_ID` | AWS access key ID | No* | - | `your-aws-access-key-id` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | No* | - | `your-aws-secret-access-key` |
| `AWS_REGION` | AWS region | No* | `us-east-1` | `eu-west-1` |
| `AWS_S3_BUCKET` | AWS S3 bucket | No* | - | `your-s3-bucket` |
| `AWS_S3_PREFIX` | AWS S3 prefix | No | - | `openmanus/uploads` |

*Required if `STORAGE_TYPE` is `s3`

## Agent System Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `AGENT_SYSTEM_ENABLED` | Enable agent system | No | `true` | `false` |
| `AGENT_MAX_THINKING_TOKENS` | Maximum thinking tokens | No | `2000` | `4000` |
| `AGENT_MAX_CONVERSATIONS` | Maximum concurrent conversations | No | `10` | `20` |
| `AGENT_DEFAULT_TIMEOUT` | Default timeout for agent tasks (seconds) | No | `60` | `120` |
| `AGENT_METRICS_ENABLED` | Enable agent metrics | No | `true` | `false` |

## Monitoring Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `ENABLE_METRICS` | Enable Prometheus metrics | No | `true` | `false` |
| `METRICS_PREFIX` | Prefix for metrics | No | `openmanus_` | `om_` |
| `ENABLE_HEALTH_CHECK` | Enable health check endpoint | No | `true` | `false` |
| `HEALTH_CHECK_PATH` | Path for health check | No | `/health` | `/healthz` |
| `ENABLE_TRACING` | Enable distributed tracing | No | `false` | `true` |
| `JAEGER_AGENT_HOST` | Jaeger agent host | No | `localhost` | `jaeger` |
| `JAEGER_AGENT_PORT` | Jaeger agent port | No | `6831` | `6832` |

## Frontend Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `VITE_API_URL` | API URL for frontend | No | `/api` | `https://api.openmanus.com` |
| `VITE_APP_TITLE` | Application title | No | `OpenManus` | `Your Company Name` |
| `VITE_DEFAULT_LOCALE` | Default locale | No | `en` | `es` |
| `VITE_ENABLE_MOCK_API` | Enable mock API | No | `false` | `true` |
| `VITE_ANALYTICS_ID` | Google Analytics ID | No | - | `UA-XXXXXXXXX-X` |
| `VITE_SENTRY_DSN` | Sentry DSN | No | - | `your-sentry-dsn` |

## Task Queue Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|:--------:|---------|---------|
| `CELERY_BROKER_URL` | Celery broker URL | No | - | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend | No | - | `redis://localhost:6379/2` |
| `CELERY_TASK_SERIALIZER` | Celery task serializer | No | `json` | `pickle` |
| `CELERY_RESULT_SERIALIZER` | Celery result serializer | No | `json` | `pickle` |
| `CELERY_ACCEPT_CONTENT` | Celery accept content | No | `["json"]` | `["json", "pickle"]` |
| `CELERY_TIMEZONE` | Celery timezone | No | `UTC` | `America/New_York` |
| `CELERY_TASK_SOFT_TIME_LIMIT` | Soft time limit for tasks (seconds) | No | `300` | `600` |
| `CELERY_WORKER_CONCURRENCY` | Worker concurrency | No | `2` | `4` |

## Environment-Specific Variables

### Development Environment

For development, you can use the following environment variables to simplify your setup:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEV_SKIP_AUTH` | Skip authentication in development | `false` |
| `DEV_MOCK_INTEGRATIONS` | Use mock integrations in development | `false` |
| `DEV_AUTO_MIGRATE` | Automatically apply migrations on startup | `true` |
| `DEV_POPULATE_DB` | Populate database with sample data | `false` |

### Testing Environment

For testing, you can use the following environment variables to configure your tests:

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_DATABASE_URL` | Test database URL | `postgresql://postgres:postgres@localhost:5432/openmanus_test` |
| `TEST_MONGODB_URL` | Test MongoDB URL | `mongodb://mongodb:mongodb@localhost:27017/openmanus_test` |
| `TEST_REDIS_URL` | Test Redis URL | `redis://localhost:6379/3` |
| `TEST_MOCK_EXTERNAL_APIS` | Mock external APIs in tests | `true` |

## Using Environment Variables

### Loading Environment Variables

OpenManus provides several ways to load environment variables:

1. **Environment File**: Create a `.env` file in the root directory of the project.
2. **System Environment**: Set environment variables at the system level.
3. **Kubernetes Secrets**: Store sensitive information in Kubernetes secrets.
4. **Docker Compose**: Define environment variables in `docker-compose.yml`.

### Sample .env File

```env
# Core Configuration
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENCRYPTION_KEY=your-encryption-key

# Database Configuration
DATABASE_URL=postgresql://openmanus:password@localhost:5432/openmanus
MONGODB_URL=mongodb://openmanus:password@localhost:27017/openmanus
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_V1_STR=/api
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
SERVER_PORT=8000

# Third-Party Integration Configuration
GHL_API_KEY=your-ghl-api-key
GHL_LOCATION_ID=your-ghl-location-id
KICKSERV_API_KEY=your-kickserv-api-key
KICKSERV_ACCOUNT=your-kickserv-account

# AI Services Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@openmanus.com
```

### Environment Variable Precedence

OpenManus follows the following precedence order for environment variables:

1. System environment variables
2. Kubernetes secrets (if deployed on Kubernetes)
3. `.env` file in the root directory
4. Default values

This allows you to override specific variables without modifying the `.env` file. 