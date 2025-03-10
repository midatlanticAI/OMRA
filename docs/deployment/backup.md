# OpenManus Backup and Recovery Guide

This guide outlines procedures for backing up and recovering the OpenManus Appliance Repair Business Automation System. Following these procedures will help you maintain data integrity and enable recovery in case of a system failure.

## Table of Contents

1. [Introduction](#introduction)
2. [Backup Components](#backup-components)
3. [Backup Strategies](#backup-strategies)
4. [PostgreSQL Database Backup](#postgresql-database-backup)
5. [MongoDB Database Backup](#mongodb-database-backup)
6. [File Storage Backup](#file-storage-backup)
7. [Configuration Backup](#configuration-backup)
8. [Automated Backup](#automated-backup)
9. [Backup Verification](#backup-verification)
10. [Recovery Procedures](#recovery-procedures)
11. [Disaster Recovery Planning](#disaster-recovery-planning)

## Introduction

A robust backup and recovery strategy is essential for any production system. OpenManus stores data in multiple locations:

- **PostgreSQL**: Primary database for structured data (customers, service requests, etc.)
- **MongoDB**: Database for unstructured data (agent states, documents, etc.)
- **File Storage**: Uploaded files and documents
- **Configuration**: Environment variables and configuration files

This guide provides instructions for backing up and recovering each of these components.

## Backup Components

A complete OpenManus backup includes:

1. **PostgreSQL Database**: All tables and data in the PostgreSQL database
2. **MongoDB Database**: All collections and documents in the MongoDB database
3. **File Storage**: All uploaded files and documents (local or S3)
4. **Configuration**: Environment variables, secrets, and configuration files
5. **Custom Code**: Any custom code or modifications to the standard OpenManus codebase

## Backup Strategies

There are several strategies for backing up OpenManus:

### Full Backup

A full backup includes all data and configurations. This is the simplest approach and recommended for smaller deployments.

### Incremental Backup

Incremental backups only store changes since the last backup. This reduces storage requirements but adds complexity to the recovery process.

### Point-in-Time Recovery

Using database transaction logs, you can recover the system to a specific point in time. This is useful for recovering from data corruption or user errors.

### Hot vs. Cold Backup

- **Hot Backup**: Taken while the system is running. This is the preferred approach for production systems.
- **Cold Backup**: Taken while the system is stopped. This ensures complete consistency but requires system downtime.

## PostgreSQL Database Backup

PostgreSQL can be backed up using the `pg_dump` tool.

### Full Database Backup

```bash
pg_dump -h <DB_HOST> -U <DB_USER> -d openmanus -F c -f openmanus_$(date +"%Y%m%d_%H%M%S").dump
```

This creates a compressed binary dump of the entire database.

### Schema-Only Backup

```bash
pg_dump -h <DB_HOST> -U <DB_USER> -d openmanus --schema-only -f openmanus_schema_$(date +"%Y%m%d_%H%M%S").sql
```

This backs up only the database schema without data.

### Incremental Backup with WAL Archiving

For point-in-time recovery, configure WAL (Write-Ahead Log) archiving in `postgresql.conf`:

```
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

### Backup with Docker

If you're running PostgreSQL in Docker:

```bash
docker exec -t postgres pg_dump -U openmanus -d openmanus -F c > openmanus_$(date +"%Y%m%d_%H%M%S").dump
```

### Backup with Kubernetes

If you're running PostgreSQL in Kubernetes:

```bash
kubectl exec -n <NAMESPACE> <POSTGRES_POD> -- pg_dump -U openmanus -d openmanus -F c > openmanus_$(date +"%Y%m%d_%H%M%S").dump
```

## MongoDB Database Backup

MongoDB can be backed up using the `mongodump` tool.

### Full Database Backup

```bash
mongodump --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus --out /path/to/backup/mongodb_$(date +"%Y%m%d_%H%M%S")
```

This creates a backup of the entire MongoDB database.

### Collection-Specific Backup

```bash
mongodump --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus --collection <COLLECTION_NAME> --out /path/to/backup/mongodb_$(date +"%Y%m%d_%H%M%S")
```

This backs up a specific collection.

### Backup with Docker

If you're running MongoDB in Docker:

```bash
docker exec -t mongodb mongodump --username <DB_USER> --password <DB_PASSWORD> --db openmanus --out /dump
docker cp mongodb:/dump /path/to/backup/mongodb_$(date +"%Y%m%d_%H%M%S")
```

### Backup with Kubernetes

If you're running MongoDB in Kubernetes:

```bash
kubectl exec -n <NAMESPACE> <MONGODB_POD> -- mongodump --username <DB_USER> --password <DB_PASSWORD> --db openmanus --out /dump
kubectl cp <NAMESPACE>/<MONGODB_POD>:/dump /path/to/backup/mongodb_$(date +"%Y%m%d_%H%M%S")
```

## File Storage Backup

OpenManus stores uploaded files either locally or in S3-compatible storage.

### Local Storage Backup

If you're using local storage, you can back up the files using standard file system tools:

```bash
tar -czf openmanus_files_$(date +"%Y%m%d_%H%M%S").tar.gz /path/to/storage
```

### S3 Storage Backup

If you're using S3 storage, you can use the AWS CLI to back up the files:

```bash
aws s3 sync s3://your-bucket/openmanus /path/to/backup/s3_$(date +"%Y%m%d_%H%M%S")
```

For incremental backups, you can use the `--delete` flag:

```bash
aws s3 sync s3://your-bucket/openmanus /path/to/backup/s3 --delete
```

### Cross-Region Replication

For S3 storage, you can also set up cross-region replication for automatic backup:

```bash
aws s3api put-bucket-replication --bucket your-bucket --replication-configuration file://replication-config.json
```

Where `replication-config.json` contains:

```json
{
  "Role": "arn:aws:iam::account-id:role/replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": { "Status": "Enabled" },
      "Filter": {
        "Prefix": "openmanus/"
      },
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
        "StorageClass": "STANDARD"
      }
    }
  ]
}
```

## Configuration Backup

Configuration files and environment variables should be backed up separately.

### Environment Variables

Back up the `.env` file:

```bash
cp .env .env.backup_$(date +"%Y%m%d_%H%M%S")
```

### Docker Compose Configuration

Back up the Docker Compose configuration:

```bash
cp docker-compose.yml docker-compose.yml.backup_$(date +"%Y%m%d_%H%M%S")
```

### Kubernetes Configuration

Back up Kubernetes configurations:

```bash
kubectl get -n <NAMESPACE> configmap,secret -o yaml > k8s_config_$(date +"%Y%m%d_%H%M%S").yaml
```

## Automated Backup

Automated backups can be set up using cron jobs or Kubernetes CronJobs.

### Cron Job Example

Create a backup script:

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/path/to/backups"
PG_HOST="localhost"
PG_USER="openmanus"
PG_DB="openmanus"
MONGO_HOST="localhost"
MONGO_PORT="27017"
MONGO_USER="openmanus"
MONGO_PASSWORD="password"
MONGO_DB="openmanus"
S3_BUCKET="your-bucket"
S3_PREFIX="openmanus"
RETENTION_DAYS=30

# Create timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"
mkdir -p "${BACKUP_PATH}"

# PostgreSQL backup
pg_dump -h ${PG_HOST} -U ${PG_USER} -d ${PG_DB} -F c -f "${BACKUP_PATH}/postgresql.dump"

# MongoDB backup
mongodump --host ${MONGO_HOST} --port ${MONGO_PORT} --username ${MONGO_USER} --password ${MONGO_PASSWORD} --db ${MONGO_DB} --out "${BACKUP_PATH}/mongodb"

# S3 backup (if using S3)
if [ ! -z "${S3_BUCKET}" ]; then
  aws s3 sync s3://${S3_BUCKET}/${S3_PREFIX} "${BACKUP_PATH}/s3"
fi

# Configuration backup
cp .env "${BACKUP_PATH}/env"
cp docker-compose.yml "${BACKUP_PATH}/docker-compose.yml"

# Compress backup
tar -czf "${BACKUP_DIR}/openmanus_backup_${TIMESTAMP}.tar.gz" -C "${BACKUP_DIR}" "${TIMESTAMP}"
rm -rf "${BACKUP_PATH}"

# Delete old backups
find "${BACKUP_DIR}" -name "openmanus_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
```

Make the script executable:

```bash
chmod +x backup.sh
```

Add a cron job:

```bash
0 1 * * * /path/to/backup.sh
```

This runs the backup daily at 1:00 AM.

### Kubernetes CronJob Example

Create a CronJob YAML file:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: openmanus-backup
  namespace: openmanus
spec:
  schedule: "0 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: openmanus/backup:latest
            env:
            - name: PG_HOST
              value: postgresql
            - name: PG_USER
              valueFrom:
                secretKeyRef:
                  name: openmanus-db-credentials
                  key: username
            - name: PG_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: openmanus-db-credentials
                  key: password
            - name: PG_DB
              value: openmanus
            - name: MONGO_HOST
              value: mongodb
            - name: MONGO_PORT
              value: "27017"
            - name: MONGO_USER
              valueFrom:
                secretKeyRef:
                  name: openmanus-mongodb-credentials
                  key: username
            - name: MONGO_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: openmanus-mongodb-credentials
                  key: password
            - name: MONGO_DB
              value: openmanus
            - name: S3_BUCKET
              value: your-bucket
            - name: S3_PREFIX
              value: openmanus
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: openmanus-s3-credentials
                  key: access-key
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: openmanus-s3-credentials
                  key: secret-key
            - name: RETENTION_DAYS
              value: "30"
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: openmanus-backup-pvc
          restartPolicy: OnFailure
```

Apply the CronJob:

```bash
kubectl apply -f openmanus-backup-cronjob.yaml
```

## Backup Verification

Regularly verify your backups to ensure they are valid and can be restored if needed.

### PostgreSQL Backup Verification

```bash
pg_restore -l openmanus.dump
```

This lists the contents of the backup file without restoring it.

### MongoDB Backup Verification

```bash
cd mongodb_backup
mongorestore --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus_verify --drop --dryRun .
```

This does a dry run of the restoration to verify the backup.

### Regular Testing

Schedule regular test restorations to a separate environment to ensure your backup and recovery procedures work as expected.

## Recovery Procedures

### PostgreSQL Recovery

```bash
pg_restore -h <DB_HOST> -U <DB_USER> -d openmanus -c openmanus.dump
```

The `-c` flag drops existing objects before creating them.

### MongoDB Recovery

```bash
mongorestore --host <DB_HOST> --port <DB_PORT> --username <DB_USER> --password <DB_PASSWORD> --db openmanus --drop mongodb_backup
```

The `--drop` flag drops existing collections before importing.

### File Storage Recovery

#### Local Storage Recovery

```bash
tar -xzf openmanus_files.tar.gz -C /path/to/storage
```

#### S3 Storage Recovery

```bash
aws s3 sync /path/to/backup/s3 s3://your-bucket/openmanus
```

### Configuration Recovery

Restore environment variables:

```bash
cp .env.backup .env
```

Restore Docker Compose configuration:

```bash
cp docker-compose.yml.backup docker-compose.yml
```

Restore Kubernetes configurations:

```bash
kubectl apply -f k8s_config.yaml
```

### Full System Recovery

1. Set up a new environment if necessary
2. Restore the configuration files
3. Restore the PostgreSQL database
4. Restore the MongoDB database
5. Restore the file storage
6. Restart all services
7. Verify system functionality

```bash
# Example Docker Compose restart
docker-compose down
docker-compose up -d

# Example Kubernetes restart
kubectl rollout restart deployment -n openmanus
```

## Disaster Recovery Planning

### Recovery Time Objective (RTO)

Define your RTO - the maximum tolerable time for recovery after a disaster. This will guide your backup strategy.

### Recovery Point Objective (RPO)

Define your RPO - the maximum data loss you can tolerate. This will guide your backup frequency.

### Disaster Recovery Plan

1. **Preparation**:
   - Document all backup procedures
   - Ensure all team members know their roles in the recovery process
   - Regularly test the recovery procedures

2. **Response**:
   - Assess the extent of the disaster
   - Communicate with all stakeholders
   - Begin recovery based on predefined procedures

3. **Recovery**:
   - Restore systems in order of priority
   - Verify data integrity
   - Test system functionality

4. **Post-Recovery**:
   - Analyze the cause of the disaster
   - Improve backup and recovery procedures
   - Document lessons learned

### Geographical Redundancy

For critical deployments, consider implementing geographical redundancy:

1. **Multi-Region Deployment**: Deploy OpenManus in multiple regions or data centers
2. **Database Replication**: Set up PostgreSQL and MongoDB replication across regions
3. **Content Delivery Network**: Use a CDN for file storage to distribute content globally

### Backup Storage Best Practices

1. **3-2-1 Rule**: Maintain at least 3 copies of data, on 2 different media types, with 1 copy offsite
2. **Encryption**: Encrypt all backup data, especially offsite backups
3. **Access Control**: Limit access to backup data to authorized personnel
4. **Regular Rotation**: Regularly rotate backup media to prevent degradation
5. **Monitoring**: Monitor backup jobs and alert on failures 