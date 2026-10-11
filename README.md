# Banking Transaction Processing System

**Cloud Engineer Portfolio Project**

**Engineer:** Shaik Ahamed Eshak Nowfal

---

## Overview

A cloud-based banking transaction application built to demonstrate AWS infrastructure, REST API development, database integration, event-driven processing, containerisation, orchestration, and operational monitoring.

The project brings together a multi-tier web application and asynchronous transaction-processing components to explore practical cloud engineering concepts.

### Key Capabilities

- Multi-tier application architecture
- REST API development using Python and Flask
- Amazon RDS MySQL database integration
- Application deployment using Nginx and Gunicorn
- Event-driven processing with Amazon SNS, SQS, and Lambda
- CloudWatch dashboards, alarms, and SNS notifications
- Docker containerisation and Kubernetes deployment using Minikube
- Helm-based application packaging and release management

---

## Architecture

### Core Application

```text
                         Internet
                            |
                            v
                Application Load Balancer
                            |
                            v
                     Amazon EC2
                            |
                     Nginx Reverse Proxy
                            |
                       Gunicorn
                            |
                      Flask App
                            |
                            v
                    Amazon RDS MySQL
                     (Private Subnet)
```

### Event-Driven Transaction Processing

```text
                Banking Application
                         |
                         v
                Amazon SNS Topic
              (ahamed-payment-events)
                         |
                  Fan-out Messaging
                    /          \
                   v            v
          Amazon SQS          Amazon SQS
     (transaction-processing)  (audit-log)
                   |            |
                   v            v
             AWS Lambda     AWS Lambda
             (processor)    (audit logger)
                                |
                                v
                           Amazon S3
```

The event-driven components support asynchronous processing and audit-log storage. The exact integration between the web application and the messaging pipeline depends on the deployed implementation.

---

## AWS Services Used

| AWS Service | Purpose |
|---|---|
| Amazon EC2 | Hosts the Flask web application |
| Amazon VPC | Provides network isolation |
| Application Load Balancer | Routes incoming application traffic and performs health checks |
| Amazon RDS for MySQL | Stores banking transaction data |
| AWS IAM | Manages access permissions and instance roles |
| Amazon CloudWatch | Collects metrics, logs, dashboards, and alarms |
| Amazon SNS | Distributes events and sends alarm notifications |
| Amazon SQS | Provides queues for asynchronous transaction and audit processing |
| AWS Lambda | Executes transaction-processing and audit-logging functions |
| Amazon S3 | Stores audit-log output |
| Amazon ECR | Stores container images and supports image vulnerability scanning |

---

## Application Features

- Banking dashboard
- Transaction history
- REST API endpoints
- Transaction validation
- Application health endpoint
- MySQL database integration
- Nginx reverse proxy
- Gunicorn application server
- Systemd service management
- Cloud infrastructure monitoring

---

## REST API

### Retrieve Transactions

**Method:** `GET`

```http
GET /api/transactions
```

Retrieves transaction records from the application.

### Create a Transaction

**Method:** `POST`

```http
POST /api/transactions
Content-Type: application/json
```

Example request body:

```json
{
  "amount": 500.00,
  "transaction_type": "credit",
  "description": "Portfolio project transaction"
}
```

The actual request fields and validation rules depend on the application's implementation.

### Application Health Check

```http
GET /health
```

Returns the application's health status.

---

## Security

The project demonstrates the following security practices:

- Amazon RDS deployed in a private subnet.
- Security groups restrict communication between application and database tiers.
- IAM roles are used for AWS permissions where configured.
- Database configuration is supplied through environment variables.
- Kubernetes configuration and secret-management mechanisms are explored for containerised deployments.

**Planned security enhancement:** Integrate AWS Secrets Manager or an appropriate external secrets-management solution for sensitive application configuration.

Never commit real credentials, database passwords, access keys, or production banking data to the repository.

---

## Containerisation & Kubernetes

### Docker

- Multi-stage Dockerfile for building the application image.
- Docker Compose configuration for running the application with Redis.
- Container image publication to Amazon ECR.
- Image vulnerability scanning to identify potential security issues.

### Kubernetes — Minikube

- Deployment resources for application workloads.
- Services for application networking.
- ConfigMaps for non-sensitive configuration.
- Secrets for sensitive configuration in the development environment.
- NGINX Ingress for HTTP routing.
- Local Kubernetes deployment and validation using Minikube.

### Helm

- Helm chart for packaging Kubernetes resources.
- Installation and upgrade of application releases.
- Rollback to a previous release when required.

These capabilities describe the containerisation and orchestration work associated with the project. Refer to the repository's actual manifests, Docker files, Helm chart, and test evidence for implementation details.

---

## Monitoring

**CloudWatch dashboard:** `ahamed-banking-production`

The dashboard is designed to provide visibility across the application's AWS components.

### Metrics and Operational Visibility

- EC2 CPU utilisation
- RDS connections and storage
- Lambda invocations and errors for both functions
- SQS queue depths for both queues
- API Gateway request count and latency, where API Gateway is integrated
- Recent Lambda log events through CloudWatch Logs Insights or the configured log-query mechanism

### Configured Alarms

| Alarm condition | Action |
|---|---|
| EC2 CPU utilisation above 70% | SNS email notification |
| RDS CPU utilisation above 50% | SNS email notification |
| Lambda errors greater than or equal to 1 | SNS email notification |

Alarm thresholds and notification actions should match the actual CloudWatch configuration in the AWS account.

---

## Proactive Alerting & Incident Response

### Lambda Pipeline Monitoring

A CloudWatch alarm named `Lambda-Errors-Banking-Pipeline` monitors Lambda execution failures.

### Automated Notifications

The alarm is connected to the Amazon SNS topic `ahamed-alerts`, which sends email notifications when the configured alarm state changes.

### Operational Validation

Alarm state transitions, including `INSUFFICIENT_DATA` to `OK`, have been used to validate monitoring behaviour and notification delivery.

This demonstrates basic cloud monitoring, alerting, and operational troubleshooting practices.

---

## Technologies

**Languages & Frameworks**
- Python
- Flask
- SQL
- MySQL

**Web & Application Servers**
- Nginx
- Gunicorn
- Systemd

**Cloud & Infrastructure**
- AWS EC2
- Amazon VPC
- IAM
- Application Load Balancer
- Amazon RDS
- Amazon S3
- Amazon CloudWatch
- Amazon SNS
- Amazon SQS
- AWS Lambda
- Amazon ECR

**Containers & Orchestration**
- Docker
- Docker Compose
- Kubernetes
- Minikube
- Helm
- NGINX Ingress

**Operating System & Tools**
- Ubuntu
- Git
- GitHub

---

## Project Structure

```text
banking-app/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
└── screenshots/
```

The repository may also contain Docker, Kubernetes, Helm, and infrastructure configuration files as those components are added.

---

## Screenshots

### Application Health Endpoint

![Health Endpoint Response](https://github.com/user-attachments/assets/27071d17-6bb6-4ea2-88d3-82a8ef29f970)

### Banking Dashboard

![Banking Dashboard](https://github.com/user-attachments/assets/7434804d-e719-49bc-b4d4-3ad6d708d25c)

---

## Future Improvements

- Deploy the containerised application to Amazon EKS.
- Provision cloud infrastructure using Terraform.
- Implement CI/CD pipelines using GitHub Actions.
- Integrate AWS Secrets Manager or External Secrets Operator.
- Configure Auto Scaling for application workloads.
- Improve automated testing and deployment validation.
- Strengthen application logging, auditability, and failure handling.

---

## Engineer

**Shaik Ahamed Eshak Nowfal**

Product Support Engineer | Transitioning into Cloud Engineering

Bengaluru, India
