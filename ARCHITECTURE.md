cat > /home/ubuntu/banking-app/ARCHITECTURE.md << 'ARCHEOF'
# Banking Transaction System — Architecture Document

## Overview
Multi-tier, event-driven banking application on AWS.
Demonstrates production-grade cloud engineering patterns.

## Network Architecture
VPC: 10.0.0.0/16 (ap-south-1, Mumbai)
├── Public Subnet 10.0.1.0/24 (ap-south-1a) — EC2, ALB
├── Public Subnet 10.0.2.0/24 (ap-south-1b) — ALB second AZ
├── Private Subnet 10.0.3.0/24 (ap-south-1a) — App servers
 └── Private Subnet 10.0.4.0/24 (ap-south-1a) — RDS MySQL


## Request Flow

User Browser
│ HTTP/HTTPS
▼
Application Load Balancer (ahamed-banking-alb)
│ HTTP port 80
▼
EC2: t3.micro Ubuntu 22.04 (ahamed-banking-app)
│ nginx → gunicorn → Flask (port 5000)
├── READ/WRITE ──────────────▶ RDS MySQL (ahamed-banking-db)
│ private subnet, port 3306
└── PUBLISH ─────────────────▶ SNS Topic (ahamed-payment-events)
│
┌───────────────────┤
▼ ▼
SQS Queue: SQS Queue:
transaction- audit-log-
processing queue
│ │
▼ ▼
Lambda: Lambda:
transaction- audit-logger
processor │
│ ▼
▼ S3: audit-logs/
CloudWatch YYYY/MM/DD/
Logs txn-{id}.json


## Security Architecture

Layer Protection 
Network VPC with public/private subnet separation
EC2 → RDSSecurity group allows only EC2 SG on port 3306
 ALB → EC2 Security group allows only ALB SG on port 80
IAM EC2 role: S3 read + SNS publish only (least privilege)
Lambda rolesSeparate roles per function, minimum permissions
AuditS3 versioning + CloudTrail on all actions 


## AWS Services Inventory

Service Resource NamePurpose
VPCahamed-production-vpcNetwork isolation
EC2ahamed-banking-app (t3.micro) Application server
RDSahamed-banking-db (db.t3.micro MySQL 8.0) Transaction data
ALBahamed-banking-alb Load balancing
SNSahamed-payment-eventsEvent broadcasting
SQS ahamed-transaction-processing-queueProcessing buffer
SQSahamed-audit-log-queueAudit buffer
Lambda ahamed-transaction-processorTransaction validation
Lambdaahamed-audit-loggerCompliance logging
S3ahamed-learning-2026/audit-logs/Immutable audit trail
CloudWatchahamed-banking-production dashboardMonitoring
IAMEC2-S3-ReadOnly-Role + SNS publishLeast privilege
CloudTrailahamed-learning-trailAPI audit logging


## Design Decisions

### Why event-driven (SNS/SQS) instead of synchronous processing?
Transaction storage (RDS write) and event processing (Lambda) are separated. If Lambda is unavailable, transactions still save.
If traffic spikes, SQS absorbs the burst without overloading Lambda. This is the standard pattern for banking transaction pipelines.

### Why two SQS queues instead of one?
Fan-out to separate queues provides fault isolation.
Audit logger failure does not affect transaction processor.
Each queue has independent retry logic, DLQ, and scaling.

### Why S3 for audit logs instead of RDS?
RDS data is mutable — records can be deleted by DBAs.
S3 with versioning provides immutability — deleted objects are recoverable. 
Combined with CloudTrail, provides a tamper-evident audit trail required by banking regulations.

### Why nginx + gunicorn instead of Flask dev server?
Flask's built-in server is single-threaded, not production-safe.
Gunicorn handles concurrent requests with multiple workers.
Nginx handles slow clients, static files, and acts as a buffer.
