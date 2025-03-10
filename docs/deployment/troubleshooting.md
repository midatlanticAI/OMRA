# OpenManus Troubleshooting Guide

This guide provides solutions to common issues you might encounter when deploying and running the OpenManus Appliance Repair Business Automation System.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Connection Issues](#database-connection-issues)
3. [API Issues](#api-issues)
4. [Frontend Issues](#frontend-issues)
5. [Authentication Issues](#authentication-issues)
6. [Integration Issues](#integration-issues)
7. [Performance Issues](#performance-issues)
8. [Agent System Issues](#agent-system-issues)
9. [Kubernetes-Specific Issues](#kubernetes-specific-issues)
10. [Docker-Specific Issues](#docker-specific-issues)
11. [Logging and Monitoring](#logging-and-monitoring)
12. [Common Error Codes](#common-error-codes)

## Installation Issues

### Environment Setup Failures

**Issue**: The installation script fails to set up the environment.

**Solutions**:

1. **Verify System Requirements**:
   ```bash
   # Check Python version
   python --version  # Should be 3.10 or higher
   
   # Check Node.js version
   node --version  # Should be 18 or higher
   
   # Check Docker version
   docker --version  # Should be 20.10 or higher
   docker-compose --version  # Should be 2.0 or higher
   ```

2. **Dependency Issues**:
   ```bash
   # Verify Python dependencies
   pip install -r requirements.txt --no-cache-dir
   
   # Verify Node.js dependencies
   npm ci
   ```

3. **File Permissions**:
   ```bash
   # Fix permissions on the installation directory
   chmod -R 755 /path/to/openmanus
   ```

### Database Initialization Failures

**Issue**: Database initialization fails during installation.

**Solutions**:

1. **Check Database Connection**:
   ```bash
   # PostgreSQL
   psql -h <DB_HOST> -U <DB_USER> -d postgres -c "SELECT 1"
   
   # MongoDB
   mongo --host <DB_HOST> --port <DB_PORT> --eval "db.stats()"
   ```

2. **Verify Database Credentials**:
   - Check if the database credentials in `.env` are correct
   - Try connecting to the database manually

3. **Database Permission Issues**:
   - Ensure the database user has sufficient privileges

4. **Reset Database**:
   ```bash
   # PostgreSQL
   dropdb openmanus
   createdb openmanus
   
   # MongoDB
   mongo --host <DB_HOST> --port <DB_PORT> --eval "db.dropDatabase()" openmanus
   ```

## Database Connection Issues

### PostgreSQL Connection Issues

**Issue**: The application cannot connect to PostgreSQL.

**Solutions**:

1. **Check Connection String**:
   - Verify the `DATABASE_URL` in `.env`
   - Ensure the format is correct: `postgresql://user:password@host:port/database`

2. **Check Network Connectivity**:
   ```bash
   # Test connection to PostgreSQL
   nc -zv <DB_HOST> <DB_PORT>
   
   # Check if PostgreSQL is running
   ps aux | grep postgres
   ```

3. **Check PostgreSQL Logs**:
   ```bash
   # View PostgreSQL logs
   tail -f /var/log/postgresql/postgresql-<version>-main.log
   
   # Docker PostgreSQL logs
   docker logs <postgres_container_id>
   ```

4. **Verify PostgreSQL Configuration**:
   - Check `pg_hba.conf` for correct client authentication settings
   - Ensure PostgreSQL is configured to accept remote connections

### MongoDB Connection Issues

**Issue**: The application cannot connect to MongoDB.

**Solutions**:

1. **Check Connection String**:
   - Verify the `MONGODB_URL` in `.env`
   - Ensure the format is correct: `mongodb://user:password@host:port/database`

2. **Check Network Connectivity**:
   ```bash
   # Test connection to MongoDB
   nc -zv <DB_HOST> <DB_PORT>
   
   # Check if MongoDB is running
   ps aux | grep mongod
   ```

3. **Check MongoDB Logs**:
   ```bash
   # View MongoDB logs
   tail -f /var/log/mongodb/mongod.log
   
   # Docker MongoDB logs
   docker logs <mongodb_container_id>
   ```

4. **Verify MongoDB Authentication**:
   ```bash
   # Connect to MongoDB and verify authentication
   mongo --host <DB_HOST> --port <DB_PORT> -u <DB_USER> -p <DB_PASSWORD> --authenticationDatabase admin
   ```

## API Issues

### API Not Starting

**Issue**: The backend API does not start or crashes immediately.

**Solutions**:

1. **Check API Logs**:
   ```bash
   # View API logs
   tail -f /path/to/logs/api.log
   
   # Docker API logs
   docker logs <api_container_id>
   ```

2. **Verify Environment Variables**:
   - Check if all required environment variables are set
   - Validate the values of critical variables like `SECRET_KEY` and connection strings

3. **Check Dependencies**:
   ```bash
   # Verify Python dependencies
   pip install -r requirements.txt --no-cache-dir
   ```

4. **Port Conflicts**:
   ```bash
   # Check if port 8000 is already in use
   netstat -tuln | grep 8000
   
   # Kill process using port 8000
   kill -9 $(lsof -t -i:8000)
   ```

### API Endpoints Returning Errors

**Issue**: API endpoints return errors like 404, 500, etc.

**Solutions**:

1. **Check API Logs for Errors**:
   ```bash
   # View API logs
   tail -f /path/to/logs/api.log
   ```

2. **Test API with curl**:
   ```bash
   # Test a simple endpoint
   curl -v http://localhost:8000/health
   
   # Test with authentication
   curl -v -H "Authorization: Bearer <token>" http://localhost:8000/api/customers
   ```

3. **Verify Database Connectivity**:
   - Check if the API can connect to the database
   - Ensure database migrations have been applied

4. **Restart API Service**:
   ```bash
   # Restart API service
   systemctl restart openmanus-api
   
   # Docker Compose
   docker-compose restart api
   ```

## Frontend Issues

### Frontend Not Loading

**Issue**: The frontend application does not load or shows a blank page.

**Solutions**:

1. **Check Browser Console for Errors**:
   - Open browser developer tools and check console for errors

2. **Verify Build Process**:
   ```bash
   # Rebuild frontend
   cd frontend
   npm run build
   ```

3. **Check Web Server Configuration**:
   - Ensure Nginx or other web server is properly configured
   - Verify that the web server is pointing to the correct build directory

4. **Check API Connectivity**:
   ```bash
   # Test API connectivity from browser
   curl -v http://localhost:8000/health
   ```

### Frontend Missing Assets

**Issue**: Frontend assets (images, CSS, JS) are not loading.

**Solutions**:

1. **Check Browser Network Tab**:
   - Open browser developer tools and check network tab for 404 errors

2. **Verify Asset Paths**:
   - Check if asset paths are correctly configured
   - Ensure assets are correctly included in the build

3. **Check Web Server MIME Types**:
   - Verify that the web server is configured with the correct MIME types

4. **Clear Browser Cache**:
   - Try clearing browser cache or using incognito/private browsing mode

## Authentication Issues

### Login Failures

**Issue**: Users cannot log in to the system.

**Solutions**:

1. **Check Credentials**:
   - Verify that the username and password are correct
   - Check if the user account exists and is active

2. **Check API Logs for Authentication Errors**:
   ```bash
   # View API logs
   tail -f /path/to/logs/api.log | grep -i "auth"
   ```

3. **Verify JWT Configuration**:
   - Check `SECRET_KEY` in the environment variables
   - Ensure JWT expiration time is set correctly

4. **Reset User Password**:
   ```bash
   # Use CLI tool to reset password
   python -m backend.utils.reset_password --email user@example.com --password newpassword
   ```

### Token Expiration

**Issue**: Users are frequently logged out or get "token expired" errors.

**Solutions**:

1. **Increase Token Expiration Time**:
   - Set `ACCESS_TOKEN_EXPIRE_MINUTES` to a higher value in `.env`

2. **Check Client-Server Time Synchronization**:
   - Ensure the server and client times are synchronized
   - Check for significant time drifts

3. **Implement Token Refresh**:
   - Verify that token refresh functionality is working correctly

## Integration Issues

### Go High Level (GHL) Integration Issues

**Issue**: Integration with GHL is not working.

**Solutions**:

1. **Verify API Key and Location ID**:
   - Check that `GHL_API_KEY` and `GHL_LOCATION_ID` are set correctly
   - Verify that the API key has the necessary permissions

2. **Check API Logs for GHL Requests**:
   ```bash
   # View API logs for GHL interactions
   tail -f /path/to/logs/api.log | grep -i "ghl"
   ```

3. **Test GHL API Connection**:
   ```bash
   # Test connection to GHL API
   curl -v -H "Authorization: Bearer <GHL_API_KEY>" https://services.leadconnectorhq.com/locations/<GHL_LOCATION_ID>
   ```

4. **Check GHL Webhook Configuration**:
   - Verify that webhooks are correctly configured in GHL
   - Ensure the webhook URL is accessible from GHL servers

### Kickserv Integration Issues

**Issue**: Integration with Kickserv is not working.

**Solutions**:

1. **Verify API Key and Account**:
   - Check that `KICKSERV_API_KEY` and `KICKSERV_ACCOUNT` are set correctly
   - Verify that the API key has the necessary permissions

2. **Check API Logs for Kickserv Requests**:
   ```bash
   # View API logs for Kickserv interactions
   tail -f /path/to/logs/api.log | grep -i "kickserv"
   ```

3. **Test Kickserv API Connection**:
   ```bash
   # Test connection to Kickserv API
   curl -v -H "Authorization: Basic <KICKSERV_API_KEY>" https://api.kickserv.com/<KICKSERV_ACCOUNT>/customers.xml
   ```

4. **Check Kickserv Webhook Configuration**:
   - Verify that webhooks are correctly configured in Kickserv
   - Ensure the webhook URL is accessible from Kickserv servers

## Performance Issues

### Slow API Response Times

**Issue**: API endpoints respond slowly.

**Solutions**:

1. **Check Database Performance**:
   ```bash
   # PostgreSQL slow queries
   SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   
   # MongoDB slow queries
   db.setProfilingLevel(2)
   db.system.profile.find({millis: {$gt: 100}}).sort({ts: -1})
   ```

2. **Check API Resource Usage**:
   ```bash
   # Check CPU and memory usage
   top -c | grep <api_process>
   
   # For Docker
   docker stats <api_container_id>
   ```

3. **Optimize Database Queries**:
   - Review and optimize slow database queries
   - Add appropriate indexes

4. **Scale API Horizontally**:
   - Increase the number of API instances
   - Implement load balancing

### Memory Leaks

**Issue**: Memory usage continuously increases over time.

**Solutions**:

1. **Monitor Memory Usage**:
   ```bash
   # Check memory usage trends
   ps -p <process_id> -o %mem,%cpu,cmd
   
   # For Docker
   docker stats <container_id>
   ```

2. **Restart Periodically**:
   - Implement scheduled restarts of services
   - Set up a cron job or systemd timer

3. **Debug Memory Usage**:
   ```bash
   # Use memory profiling tools
   python -m memory_profiler <script.py>
   ```

4. **Check for Memory Leaks in Dependencies**:
   - Update dependencies to latest versions
   - Check if known memory leak issues exist in dependencies

## Agent System Issues

### Agents Not Starting

**Issue**: The agent system does not start or crashes immediately.

**Solutions**:

1. **Check Agent Logs**:
   ```bash
   # View agent logs
   tail -f /path/to/logs/agent.log
   
   # Docker agent logs
   docker logs <agent_container_id>
   ```

2. **Verify Environment Variables**:
   - Check if agent-specific environment variables like `AGENT_SYSTEM_ENABLED` are set correctly
   - Verify AI service API keys like `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

3. **Check Dependencies**:
   ```bash
   # Verify Python dependencies
   pip install -r requirements.txt --no-cache-dir
   ```

4. **Restart Agent System**:
   ```bash
   # Restart agent service
   systemctl restart openmanus-agent
   
   # Docker Compose
   docker-compose restart agent
   ```

### Agent Execution Failures

**Issue**: Agents fail to execute tasks or workflows.

**Solutions**:

1. **Check Agent Logs for Errors**:
   ```bash
   # View agent logs
   tail -f /path/to/logs/agent.log | grep -i "error"
   ```

2. **Verify AI Service Connectivity**:
   ```bash
   # Test Anthropic API connectivity
   curl -v -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
   
   # Test OpenAI API connectivity
   curl -v -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

3. **Check Tool Registry Configuration**:
   - Verify that all required tools are correctly registered
   - Check if tool implementations are working correctly

4. **Monitor Agent Metrics**:
   - Check agent performance metrics in Prometheus/Grafana
   - Look for patterns in failed executions

## Kubernetes-Specific Issues

### Pod Scheduling Issues

**Issue**: Pods are not being scheduled or remain in Pending state.

**Solutions**:

1. **Check Pod Status and Events**:
   ```bash
   # Check pod status
   kubectl get pods
   
   # Describe the problematic pod
   kubectl describe pod <pod_name>
   ```

2. **Verify Resource Availability**:
   ```bash
   # Check node resources
   kubectl describe nodes
   
   # Check resource quotas
   kubectl describe resourcequota
   ```

3. **Check Node Taints and Pod Tolerations**:
   ```bash
   # List node taints
   kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
   ```

4. **Review Pod Resource Requests and Limits**:
   - Adjust CPU and memory requests/limits to match cluster capacity

### Service Discovery Issues

**Issue**: Services cannot discover or communicate with each other.

**Solutions**:

1. **Check Service and Endpoint Status**:
   ```bash
   # Check service
   kubectl get svc <service_name>
   
   # Check endpoints
   kubectl get endpoints <service_name>
   ```

2. **Verify Service Selectors and Pod Labels**:
   ```bash
   # Check service selectors
   kubectl describe svc <service_name>
   
   # Check pod labels
   kubectl get pods --show-labels
   ```

3. **Test Service DNS Resolution**:
   ```bash
   # Run a temporary pod to test DNS
   kubectl run -it --rm debug --image=busybox -- nslookup <service_name>
   ```

4. **Check Network Policies**:
   ```bash
   # List network policies
   kubectl get networkpolicies
   
   # Describe network policy
   kubectl describe networkpolicy <policy_name>
   ```

## Docker-Specific Issues

### Container Startup Issues

**Issue**: Containers fail to start or exit immediately.

**Solutions**:

1. **Check Container Logs**:
   ```bash
   # View container logs
   docker logs <container_id>
   
   # Follow container logs
   docker logs -f <container_id>
   ```

2. **Check Container Status**:
   ```bash
   # List all containers
   docker ps -a
   
   # Inspect container
   docker inspect <container_id>
   ```

3. **Verify Docker Compose File**:
   - Check for syntax errors in `docker-compose.yml`
   - Ensure all required services are defined

4. **Check Volume Mounts and Permissions**:
   ```bash
   # Check volume mounts
   docker inspect -f '{{ .Mounts }}' <container_id>
   
   # Fix permissions
   chmod -R 755 /path/to/volume
   ```

### Network Issues in Docker

**Issue**: Containers cannot communicate with each other.

**Solutions**:

1. **Inspect Docker Networks**:
   ```bash
   # List networks
   docker network ls
   
   # Inspect network
   docker network inspect <network_name>
   ```

2. **Check Container Network Configuration**:
   ```bash
   # Check container network settings
   docker inspect -f '{{.NetworkSettings.Networks}}' <container_id>
   ```

3. **Test Inter-Container Communication**:
   ```bash
   # Start a shell in a container
   docker exec -it <container_id> sh
   
   # Ping another container
   ping <container_name>
   ```

4. **Recreate the Docker Network**:
   ```bash
   # Remove and recreate the network
   docker-compose down
   docker network prune
   docker-compose up -d
   ```

## Logging and Monitoring

### Missing or Incomplete Logs

**Issue**: Logs are not being generated or are incomplete.

**Solutions**:

1. **Check Log Configuration**:
   - Verify log settings in configuration files
   - Check if log paths exist and are writable

2. **Set Appropriate Log Levels**:
   - Set `LOG_LEVEL` environment variable to a more verbose level like `DEBUG`

3. **Check Log Rotation**:
   - Ensure log rotation is correctly configured
   - Check if logs are being rotated correctly

4. **Verify Log Aggregation**:
   - Check if log aggregation tools like Fluentd or Logstash are correctly configured

### Monitoring System Issues

**Issue**: Prometheus or Grafana not working correctly.

**Solutions**:

1. **Check Prometheus Target Status**:
   - Open Prometheus UI at `http://<prometheus-host>:9090/targets`
   - Verify that all targets are `UP`

2. **Verify Metrics Endpoint**:
   ```bash
   # Check metrics endpoint
   curl http://localhost:8000/metrics
   ```

3. **Check Grafana Dashboard Configuration**:
   - Verify Grafana datasource configuration
   - Check if dashboard JSON is valid

4. **Restart Monitoring Stack**:
   ```bash
   # Restart Prometheus and Grafana
   docker-compose -f monitoring-docker-compose.yml restart
   ```

## Common Error Codes

### HTTP Status Codes

| Status Code | Description | Possible Causes | Solutions |
|-------------|-------------|-----------------|-----------|
| 400 | Bad Request | Invalid input data | Check request payload and parameters |
| 401 | Unauthorized | Missing or invalid authentication | Verify authentication token |
| 403 | Forbidden | Insufficient permissions | Check user roles and permissions |
| 404 | Not Found | Resource does not exist | Verify resource ID and URL |
| 422 | Unprocessable Entity | Validation error | Check input data format |
| 429 | Too Many Requests | Rate limit exceeded | Implement request throttling |
| 500 | Internal Server Error | Server-side error | Check API logs for details |
| 502 | Bad Gateway | Proxy or gateway error | Check network configuration |
| 503 | Service Unavailable | Service is down or overloaded | Check service status and resources |
| 504 | Gateway Timeout | Request timeout | Check service response times |

### Application-Specific Error Codes

| Error Code | Description | Possible Causes | Solutions |
|------------|-------------|-----------------|-----------|
| `AUTH001` | Authentication failed | Invalid credentials | Verify username and password |
| `AUTH002` | Token expired | JWT token has expired | Refresh token or login again |
| `AUTH003` | Invalid token | Token is malformed or tampered | Login again to get a new token |
| `DB001` | Database connection error | Database is down or unreachable | Check database status |
| `DB002` | Query error | SQL syntax error or invalid query | Check query and parameters |
| `API001` | External API error | Third-party API is down or returned an error | Check external API status |
| `INT001` | Integration error | Error in GHL or Kickserv integration | Verify integration configuration |
| `AGT001` | Agent execution error | Agent failed to execute a task | Check agent logs and configuration | 