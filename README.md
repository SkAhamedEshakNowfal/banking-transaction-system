# Banking Transaction Processing System

**Cloud Engineer Portfolio Project**

**Engineer:** Shaik Ahamed Eshak Nowfal

---

## Overview

A cloud-native banking transaction application deployed on AWS demonstrating:

- Multi-tier architecture
- REST API development
- Amazon RDS integration
- Production web server deployment
- Monitoring and health checks

---

# Architecture

```
Internet
      │
      ▼
Application Load Balancer
      │
      ▼
Amazon EC2
(Nginx → Gunicorn → Flask)
      │
      ▼
Amazon RDS MySQL
(Private Subnet)
```

---

# AWS Services Used

| Service | Purpose |
|---------|---------|
| Amazon EC2 | Hosts Flask application |
| Amazon RDS MySQL | Banking transaction database |
| Application Load Balancer | Load balancing & health checks |
| Amazon VPC | Network isolation |
| IAM | Secure service permissions |
| Amazon CloudWatch | Monitoring and alarms |
| Amazon SNS | Event notifications *(Lab completed)* |
| Amazon SQS | Message queue *(Lab completed)* |
| AWS Lambda | Transaction processing *(Lab completed)* |

---

# Features

- Banking dashboard
- Transaction history
- REST API
- Health endpoint
- MySQL database
- Nginx reverse proxy
- Gunicorn application server
- Systemd service
- Transaction validation

---

# REST API

GET

```
/api/transactions
```

POST

```
/api/transactions
```

Health

```
/health
```

---

# Security

- RDS deployed in private subnet
- Security Groups between EC2 and RDS
- IAM Role attached to EC2
- Environment variables for database configuration
- Planned migration to AWS Secrets Manager

---

# Technologies

- Python
- Flask
- Gunicorn
- Nginx
- MySQL
- Ubuntu
- AWS

---

# Project Structure

```
banking-app/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
└── screenshots/
```


## Screenshots

```
<img width="523" height="253" alt="health_Endpoint_Response" src="https://github.com/user-attachments/assets/27071d17-6bb6-4ea2-88d3-82a8ef29f970" />
<img width="1432" height="746" alt="Banking Dashboard" src="https://github.com/user-attachments/assets/7434804d-e719-49bc-b4d4-3ad6d708d25c" />


```

---

# Future Improvements

- AWS Secrets Manager
- Auto Scaling
- CloudFormation/Terraform
- CI/CD using GitHub Actions
- Docker
- ECS/Fargate

---

# Engineer

Shaik Ahamed Eshak Nowfal

Product Support Engineer

Transitioning into Cloud Engineering

Bengaluru, India
