# OpenManus Security Guide

This guide outlines security best practices for deploying and operating the OpenManus system. Following these guidelines will help you maintain a secure environment for your OpenManus installation.

## Table of Contents

1. [Authentication and Authorization](#authentication-and-authorization)
2. [API Security](#api-security)
3. [Database Security](#database-security)
4. [Secret Management](#secret-management)
5. [Network Security](#network-security)
6. [Infrastructure Security](#infrastructure-security)
7. [Application Security](#application-security)
8. [Secure Configuration](#secure-configuration)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Incident Response](#incident-response)
11. [Compliance Considerations](#compliance-considerations)
12. [Security Checklist](#security-checklist)

## Authentication and Authorization

### JWT Implementation

OpenManus uses JSON Web Tokens (JWT) for authentication. To secure your JWT implementation:

1. Use a strong, unique `SECRET_KEY` for signing tokens.
2. Set an appropriate token expiration time (`ACCESS_TOKEN_EXPIRE_MINUTES`).
3. Store the refresh token securely, preferably in HttpOnly cookies.
4. Implement token rotation for refresh tokens.

Example secure JWT configuration:

```env
SECRET_KEY=your-randomly-generated-secure-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Password Security

1. Enforce strong password policies:
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, and special characters
   - Regular password rotation (every 90 days)
   - Password history (prevent reuse of the last 5 passwords)

2. Implement rate limiting for login attempts to prevent brute force attacks.

3. Use secure password hashing with Argon2 (default in OpenManus).

### Role-Based Access Control

OpenManus implements role-based access control (RBAC) with the following default roles:

- **Admin**: Full system access
- **Manager**: Access to most features except system configuration
- **Agent**: Access to customer and service management
- **Customer**: Limited access to their own data

Ensure that you assign the minimum necessary permissions to each user.

## API Security

### HTTPS Configuration

Always use HTTPS in production. Configure your environment variables:

```env
ENABLE_HTTPS=true
SSL_CERT_PATH=/path/to/certificate.crt
SSL_KEY_PATH=/path/to/private.key
```

For production deployments, use a properly signed certificate from a trusted certificate authority.

### API Authentication

All API endpoints (except authentication endpoints) require authentication. Secure your API:

1. Use API keys for service-to-service communication.
2. Implement OAuth2 for third-party integrations.
3. Include security headers in all responses.

### Rate Limiting

Configure rate limiting to prevent abuse:

```env
MAX_REQUESTS_PER_MINUTE=60
RATE_LIMITING_STRATEGY=ip
```

Adjust these values based on your expected traffic patterns.

### CORS Configuration

Restrict cross-origin requests to trusted domains:

```env
BACKEND_CORS_ORIGINS=["https://app.yourdomain.com", "https://admin.yourdomain.com"]
```

Never use `*` in production environments.

## Database Security

### Connection Security

Use SSL for database connections:

```env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
MONGODB_URL=mongodb://user:password@host:port/database?ssl=true
```

### Access Control

1. Create separate database users for different purposes (e.g., application, migration, backup).
2. Grant the minimum necessary permissions to each user.
3. Never use the database root/admin user for application connections.

Example PostgreSQL roles:

```sql
-- Application role (read/write)
CREATE ROLE openmanus_app WITH LOGIN PASSWORD 'secure-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO openmanus_app;

-- Read-only role (for reporting)
CREATE ROLE openmanus_readonly WITH LOGIN PASSWORD 'secure-password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO openmanus_readonly;
```

### Data Encryption

Encrypt sensitive data at rest:

1. Use column-level encryption for sensitive data (e.g., API keys, personal information).
2. Configure disk encryption for database servers.
3. Use the `ENCRYPTION_KEY` environment variable for application-level encryption.

### Database Backup Security

Secure your database backups:

1. Encrypt all database backups.
2. Store backups in a secure location with restricted access.
3. Regularly test backup restoration procedures.
4. Implement retention policies for backups.

## Secret Management

### Environment Variables

Never store secrets in your codebase. Use environment variables or a secret management service:

1. For development, use `.env` files (but exclude them from version control).
2. For production, use a secret management service like:
   - Kubernetes Secrets
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

### Secret Rotation

Implement regular rotation for all secrets:

1. Database credentials: Every 90 days
2. API keys: Every 90 days
3. JWT signing keys: Every 180 days
4. SSL certificates: Before expiration

### Secure CI/CD Pipeline

Protect secrets in your CI/CD pipeline:

1. Use sealed secrets or encrypted environment variables.
2. Avoid logging environment variables.
3. Implement least privilege for CI/CD service accounts.

## Network Security

### Firewall Configuration

Implement network-level security:

1. Allow only necessary inbound traffic:
   - HTTPS (443)
   - HTTP (80) - only to redirect to HTTPS
   - SSH (22) - restricted to specific IP ranges

2. Restrict outbound traffic to required services.

Example AWS Security Group configuration:

```
Inbound:
- HTTPS (443) from 0.0.0.0/0
- SSH (22) from your-office-ip-range

Outbound:
- HTTPS (443) to 0.0.0.0/0
- PostgreSQL (5432) to db-security-group
- MongoDB (27017) to db-security-group
```

### VPC Configuration

When deploying in cloud environments:

1. Place backend services in private subnets.
2. Use a load balancer in a public subnet to route traffic.
3. Implement network ACLs at the subnet level.
4. Use VPC endpoints for AWS services.

### Web Application Firewall (WAF)

Deploy a WAF to protect against common web attacks:

1. SQL injection
2. Cross-site scripting (XSS)
3. Cross-site request forgery (CSRF)
4. Distributed denial of service (DDoS)

AWS WAF sample rules:

```yaml
Rules:
  - Name: SQLInjectionRule
    Priority: 1
    Action: Block
    Statement:
      SqlInjectionMatchStatement:
        FieldToMatch:
          AllQueryArguments: {}
        TextTransformations:
          - Priority: 0
            Type: NONE
  - Name: XSSRule
    Priority: 2
    Action: Block
    Statement:
      XssMatchStatement:
        FieldToMatch:
          Body: {}
        TextTransformations:
          - Priority: 0
            Type: NONE
```

## Infrastructure Security

### Kubernetes Security

For Kubernetes deployments:

1. Enable Pod Security Policies (PSP) or Pod Security Standards (PSS).
2. Use Kubernetes Network Policies to restrict pod-to-pod communication.
3. Implement RBAC for Kubernetes API access.
4. Run containers as non-root users.
5. Use read-only file systems where possible.

Example Pod Security Context:

```yaml
securityContext:
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  readOnlyRootFilesystem: true
```

### Container Security

For Docker-based deployments:

1. Use minimal base images (e.g., Alpine Linux).
2. Regularly update base images.
3. Scan images for vulnerabilities before deployment.
4. Do not run containers as root.
5. Use Docker Content Trust for image signing.

Example Dockerfile security:

```dockerfile
FROM python:3.10-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Rest of Dockerfile...
```

### Infrastructure as Code Security

When using Infrastructure as Code (IaC):

1. Use version control for all IaC templates.
2. Implement code review for infrastructure changes.
3. Scan IaC templates for security issues.
4. Use principle of least privilege for all resources.

## Application Security

### Input Validation

Implement thorough input validation:

1. Validate input on both client and server sides.
2. Use schema validation for API requests.
3. Sanitize all user inputs to prevent injection attacks.
4. Implement content security policy (CSP) headers.

OpenManus uses Pydantic for input validation. Example schema:

```python
class CustomerCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., regex=r"^\+?[1-9]\d{1,14}$")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if re.search(r'[<>{}]', v):
            raise ValueError('Name contains invalid characters')
        return v
```

### XSS Prevention

Prevent Cross-Site Scripting (XSS) attacks:

1. Sanitize all user-generated content before display.
2. Implement Content Security Policy (CSP) headers.
3. Use automatic escaping in templates.

Example CSP header:

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self' api.openmanus.com;
```

### CSRF Protection

Implement CSRF protection for all state-changing operations:

1. Use CSRF tokens in forms.
2. Validate the Origin/Referer header.
3. Use SameSite cookies.

Example CSRF configuration:

```env
CSRF_SECRET=your-csrf-secret
COOKIE_SAMESITE=Lax
```

## Secure Configuration

### Security Headers

Implement security headers in all HTTP responses:

1. Strict-Transport-Security (HSTS)
2. Content-Security-Policy (CSP)
3. X-Content-Type-Options
4. X-Frame-Options
5. Referrer-Policy

Example NGINX configuration:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self';" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Dependency Management

Secure your dependencies:

1. Regularly update dependencies to patch security vulnerabilities.
2. Use tools like Dependabot or Snyk to monitor for vulnerable dependencies.
3. Pin dependency versions to avoid unexpected updates.
4. Scan dependencies for security issues before deployment.

### Security Hardening

Harden your production environment:

1. Disable debugging and development features in production.
2. Remove unnecessary services and packages.
3. Implement file integrity monitoring.
4. Apply the principle of least privilege across all systems.

## Monitoring and Logging

### Security Monitoring

Implement comprehensive security monitoring:

1. Log all authentication attempts (successful and failed).
2. Monitor API access patterns for anomalies.
3. Set up alerts for suspicious activities.
4. Implement user behavior analytics.

### Log Management

Secure your logs:

1. Centralize logs in a secure, tamper-proof store.
2. Implement log rotation and retention policies.
3. Ensure logs do not contain sensitive information.
4. Protect logs from unauthorized access.

Example logging configuration:

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=90
```

### Intrusion Detection

Implement intrusion detection systems:

1. Network-based intrusion detection (NIDS)
2. Host-based intrusion detection (HIDS)
3. Regular file integrity checks
4. Anomaly detection for system calls

## Incident Response

### Incident Response Plan

Develop an incident response plan:

1. Define roles and responsibilities.
2. Establish communication channels.
3. Document response procedures for different types of incidents.
4. Conduct regular drills and tabletop exercises.

### Security Incident Handling

Steps for handling security incidents:

1. **Identification**: Detect and confirm the incident.
2. **Containment**: Limit the damage and isolate affected systems.
3. **Eradication**: Remove the cause of the incident.
4. **Recovery**: Restore systems to normal operation.
5. **Lessons Learned**: Document findings and improve processes.

### Disclosure Policy

Establish a vulnerability disclosure policy:

1. Provide a secure channel for reporting vulnerabilities.
2. Define the response timeline.
3. Acknowledge and communicate vulnerability fixes.
4. Consider implementing a bug bounty program.

## Compliance Considerations

### GDPR Compliance

If you process data of EU residents:

1. Implement data minimization principles.
2. Provide mechanisms for data subject rights (access, correction, deletion).
3. Document data processing activities.
4. Implement appropriate technical and organizational measures.

### HIPAA Compliance

If you process protected health information (PHI):

1. Implement required technical safeguards.
2. Conduct regular risk assessments.
3. Maintain audit logs of all PHI access.
4. Encrypt PHI in transit and at rest.

### PCI DSS Compliance

If you process payment card data:

1. Implement required security controls.
2. Conduct regular vulnerability scans.
3. Maintain secure networks and systems.
4. Implement strong access control measures.

## Security Checklist

Use this checklist before deploying to production:

### Authentication and Authorization
- [ ] JWT signing key is strong and unique
- [ ] Password policy is enforced
- [ ] MFA is available for admin accounts
- [ ] Session timeout is configured appropriately

### API Security
- [ ] HTTPS is enforced for all endpoints
- [ ] API endpoints require proper authentication
- [ ] Rate limiting is configured
- [ ] CORS is restricted to specific origins

### Database Security
- [ ] Database connections use SSL
- [ ] Database users have minimal permissions
- [ ] Sensitive data is encrypted
- [ ] Database backup process is secure

### Network Security
- [ ] Firewalls restrict traffic to necessary ports
- [ ] Services are deployed in private networks where appropriate
- [ ] WAF is configured to block common attacks
- [ ] Network traffic is monitored for anomalies

### Application Security
- [ ] Input validation is implemented
- [ ] XSS protection is in place
- [ ] CSRF protection is enabled
- [ ] Content Security Policy is configured

### Configuration
- [ ] Debug mode is disabled in production
- [ ] Security headers are configured
- [ ] Sensitive environment variables are securely stored
- [ ] Dependencies are up to date

### Monitoring and Logging
- [ ] Authentication events are logged
- [ ] Security alerts are configured
- [ ] Logs are stored securely
- [ ] Regular security scans are scheduled

### Incident Response
- [ ] Incident response plan is documented
- [ ] Contact information is up to date
- [ ] Recovery procedures are tested
- [ ] Backup restoration is verified 