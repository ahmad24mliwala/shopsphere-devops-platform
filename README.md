
# ShopSphere — DevOps Microservices Platform

A hands-on DevOps portfolio project demonstrating a microservices-based e-commerce backend, containerization, automated testing, CI/CD, infrastructure management, deployment, metrics, and structured logging.

## 1. Project Overview

ShopSphere is a portfolio e-commerce platform with a React frontend, four independent FastAPI microservices, and PostgreSQL.

The application runs on AWS EC2 Ubuntu. Docker Compose manages the backend services and database, while Nginx serves the frontend and routes API requests.

### Key Features

- React 19 frontend with product browsing, search, category filters, cart, checkout, and order confirmation.
- Four independent FastAPI microservices.
- PostgreSQL relational database.
- Docker and Docker Compose containerization.
- Automated API and integration testing using pytest.
- GitHub Actions continuous integration.
- Jenkins CI/CD and automated deployment.
- Terraform-based read-only AWS infrastructure inspection.
- Ansible server configuration and auditing.
- Prometheus-compatible application metrics.
- Structured JSON application logging.

### Application Preview

![ShopSphere Homepage](docs/screenshots/homepage.png)

![Product Catalogue](docs/screenshots/products.png)

![Checkout and Order Confirmation](docs/screenshots/checkout.png)

![Grafana Monitoring Dashboard](docs/screenshots/grafana.png)

![Jenkins CI/CD Pipeline](docs/screenshots/jenkins.png)

## 2. Architecture

```mermaid
flowchart TB
    User["🌐 Customer Browser"]
    GH["GitHub Repository"]
    GHA["GitHub Actions CI"]

    subgraph AWS["☁️ AWS Cloud — EC2 Ubuntu"]
        subgraph HOST["EC2 Host"]
            NGINX["Nginx :80"]
            REACT["React 19 Static Frontend"]
            subgraph DOCKER["Docker Compose Network"]
                US["User API :8001"]
                PS["Product API :8002"]
                OS["Order API :8003"]
                PAY["Payment API :8004"]
                DB[("PostgreSQL :5432")]
                PROM["Prometheus :9090"]
                GRAF["Grafana :3000"]
            end
            JENKINS["Jenkins :8080"]
        end
    end

    User -->|"HTTP"| NGINX
    NGINX -->|"Serves static files"| REACT
    NGINX -->|"/api/users"| US
    NGINX -->|"/api/products"| PS
    NGINX -->|"/api/orders"| OS
    NGINX -->|"/api/payments"| PAY

    US --> DB
    PS --> DB
    OS --> DB
    PAY --> DB

    PROM -->|"Scrapes /metrics"| US
    PROM --> PS
    PROM --> OS
    PROM --> PAY
    GRAF --> PROM

    GH --> GHA
    GH -->|"SCM checkout / polling"| JENKINS

    classDef frontend fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef backend fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef ops fill:#fef3c7,stroke:#d97706,color:#78350f
    class REACT,NGINX frontend
    class US,PS,OS,PAY,DB backend
    class JENKINS,PROM,GRAF,GHA ops
```

## 3. Microservices

The application consists of a React frontend and four independent FastAPI services.

| Service | Responsibility | Host Port |
|---|---|---:|
| User Service | User management | 8001 |
| Product Service | Product management | 8002 |
| Order Service | Order management | 8003 |
| Payment Service | Simulated payment operations | 8004 |
| PostgreSQL | Persistent database | 5432 |

Each application service runs in its own Docker container. Services communicate over Docker's internal network. Application API ports are bound to localhost on the EC2 host.

## 4. Technology Stack

| Category | Technology |
|---|---|
| Programming | Python, FastAPI |
| Database | PostgreSQL 16 |
| Testing | Pytest, Requests |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |
| CI/CD | Jenkins |
| Cloud | AWS EC2 |
| Infrastructure as Code | Terraform |
| Configuration Management | Ansible |
| Metrics | Prometheus Client |
| Logging | Python Logging, JSON |
| Version Control | Git, GitHub |
| Operating System | Ubuntu Linux |

## 5. Containerization

Docker Compose manages the application services and PostgreSQL database.

Useful commands:

```bash
# View running containers
docker compose ps

# Build and start services
docker compose up -d --build

# View recent logs
docker compose logs --tail=100

# Stop containers
docker compose down
```

The PostgreSQL database uses a persistent Docker volume. Avoid `docker compose down -v` unless you intentionally want to delete the database volume and its data.

## 6. CI/CD Pipeline

The project uses GitHub Actions and Jenkins.

### GitHub Actions

The GitHub Actions workflow runs automatically on pushes and pull requests targeting the `main` branch.

The workflow performs these steps:

1. Checks out the repository and sets up Python 3.12.
2. Installs development and security dependencies.
3. Runs `pip-audit` against the requirements of all four microservices.
4. Builds and starts the application and PostgreSQL containers using Docker Compose.
5. Scans all four backend Docker images with Trivy for HIGH and CRITICAL vulnerabilities. Unfixed vulnerabilities are ignored by the configured scan.
6. Generates CycloneDX Software Bill of Materials (SBOM) files for all four images.
7. Uploads the SBOM files as GitHub Actions artifacts, retained for 30 days.
8. Checks the health endpoints of all four microservices.
9. Runs the automated pytest suite (13 tests).
10. Stops the CI containers, including when the workflow fails.

The workflow provides automated testing, dependency auditing, container image security checks, and software supply-chain visibility before changes are accepted.

### Jenkins

The Jenkins pipeline demonstrates:

1. Source code checkout.
2. Test dependency installation.
3. Automated test execution.
4. Connection to the EC2 host using a restricted SSH deployment key.
5. Application source code update.
6. Docker image builds.
7. Application container deployment.
8. Health verification of all four services.

**Automated Trigger:**

- Jenkins SCM polling is enabled at the job level.
- Schedule: `H/5 * * * *` (approximately every 5 minutes).
- Jenkins checks GitHub for new commits and automatically starts the pipeline when changes are detected.
- The pipeline deploys the application to the EC2 instance and verifies service health.

### CI/CD Workflow

```mermaid
flowchart TD
    A["Developer pushes code"] --> GH["GitHub Repository"]

    GH --> B["GitHub Actions CI"]
    B --> C["Checkout and Python 3.12 setup"]
    C --> D["Install test and security dependencies"]
    D --> E["pip-audit dependency scan"]
    E --> F["Docker Compose build and start"]
    F --> G["Trivy scans four Docker images"]
    G --> H["Generate four CycloneDX SBOMs"]
    H --> I["Upload SBOM artifacts"]
    I --> J["Check service health"]
    J --> K["Run 13 automated tests"]
    K --> L["Stop test containers"]

    GH --> M["Jenkins SCM polling"]
    M --> N["Checkout source and install dependencies"]
    N --> O["pip-audit and pytest"]
    O --> P["SSH deployment to EC2"]
    P --> Q["Build four backend images"]
    Q --> R["Recreate backend containers"]
    R --> S["Health checks"]
    S --> T["Generate and archive SBOM reports"]

    U["Frontend: npm build"] --> V["Copy dist to Nginx web root"]
    V --> W["React application served by Nginx"]

    classDef success fill:#dcfce7,stroke:#16a34a,color:#14532d
    class L,T,W success
```

### Deployment Safety

- Deployment uses a restricted SSH key and host-side script.
- Jenkins does not require direct access to the host Docker socket.
- The deployment script does not intentionally recreate PostgreSQL.
- Health checks verify the application services after deployment.
- Automatic rollback is not currently implemented.

## 7. Infrastructure Automation

### Terraform

Terraform inspects an existing AWS EC2 instance using a read-only data source.

The configuration reports:

- Instance ID
- Instance type
- Availability zone
- Instance state

The current configuration does not create or destroy AWS infrastructure.

### Ansible

Ansible demonstrates basic configuration management and server auditing.

Tasks include:

- Server connectivity validation.
- Installation of basic packages.
- Operating system information.
- CPU and memory information.
- Disk usage and uptime auditing.


## 8. Kubernetes and Helm

The project includes Kubernetes deployment configurations for the four FastAPI microservices and PostgreSQL.

**Kubernetes resources:**
- Namespace and service deployments.
- ClusterIP services for application networking.
- PostgreSQL StatefulSet with persistent volume claim.
- ConfigMap for database initialization.
- Kubernetes Secrets references for database credentials.
- Startup, readiness, and liveness probes.
- CPU and memory requests and limits.
- Non-root application containers and security contexts.

**Helm deployment:**

A reusable Helm chart is available at `infrastructure/helm/shopsphere/`.

The chart supports configurable container images, replica counts, resource limits, database settings, and Secret references.

**Validation performed:**

```bash
helm lint infrastructure/helm/shopsphere

helm template shopsphere infrastructure/helm/shopsphere \
  > /tmp/shopsphere-rendered.yaml

kubeconform -strict -summary /tmp/shopsphere-rendered.yaml
```

Validation result: 12 Kubernetes resources valid, zero invalid resources, and zero schema errors.

**Deployment status:** Kubernetes manifests and Helm templates are prepared and validated. Deployment to a live Kubernetes cluster has not yet been performed.

### Kubernetes Architecture (Design Only)

```mermaid
flowchart TB
    STATUS["Design validated with Helm lint and kubeconform — NOT deployed to a live cluster"]

    subgraph K8S["Kubernetes Namespace: shopsphere"]
        ING["Ingress / External Access (not configured)"]

        subgraph APPS["Application Deployments"]
            U["User Service Deployment"]
            P["Product Service Deployment"]
            O["Order Service Deployment"]
            PAY["Payment Service Deployment"]
        end

        subgraph SERVICES["ClusterIP Services"]
            US["user-service"]
            PS["product-service"]
            OS["order-service"]
            PAYS["payment-service"]
            DBS["db"]
        end

        DB["PostgreSQL StatefulSet"]
        PVC[("PersistentVolumeClaim")]
        SECRET["Secret: shopsphere-db-secret"]
        CM["ConfigMap: db-init-script"]
    end

    STATUS -.-> K8S
    ING --> US
    ING --> PS
    ING --> OS
    ING --> PAYS
    US --> U
    PS --> P
    OS --> O
    PAYS --> PAY

    U --> DBS
    P --> DBS
    O --> DBS
    PAY --> DBS
    DBS --> DB
    DB --> PVC
    SECRET -. "Database credentials" .-> DB
    CM -. "Initialization script" .-> DB
```


## 9. Monitoring and Logging

### Health Checks

Each microservice exposes a `/health` endpoint to report service health and database connectivity.

### Application Metrics

Each microservice exposes a `/metrics` endpoint with Prometheus-compatible metrics, including:

- HTTP request counters.
- HTTP request duration histograms.

### Prometheus Configuration

Prometheus configuration is available at `infrastructure/monitoring/prometheus.yml`.

It defines four application metrics targets:

- User Service
- Product Service
- Order Service
- Payment Service

The scrape interval is 15 seconds.

Prometheus and Grafana are running as Docker containers on the EC2 instance. Prometheus scrapes all four API services every 15 seconds. Grafana provides the ShopSphere DevOps Monitoring dashboard.

### Structured JSON Logging

Application request logs are emitted as structured JSON records containing information such as:

- Timestamp
- Service name
- HTTP method
- Request path
- Response status
- Request duration

Logs can be inspected using Docker Compose.

**Access:** Prometheus (port 9090) and Grafana (port 3000) are bound to localhost on the EC2 host and are not directly exposed to the public internet. Access them through an SSH tunnel.

### PostgreSQL Backup Verification

PostgreSQL database backups are created using `pg_dump` in custom archive format.

Backup verification performed:

- Created a database backup archive.
- Inspected the archive using `pg_restore --list`.
- Verified that all four database tables were included.
- Compared backup row counts with live database row counts.

The backup archive was verified successfully. A full database restore test has not yet been performed.

Backup files are stored outside the Git repository.

## 10. Automated Testing

The project currently includes 13 automated tests.

| Test Category | Tests |
|---|---:|
| Service health checks | 4 |
| Invalid request validation | 4 |
| End-to-end integration flow | 1 |
| Metrics endpoint validation | 4 |
| **Total** | **13** |

Run the tests after starting the application:

```bash
source .venv/bin/activate
pytest -v
```


## 11. Repository Structure

```text
shopsphere-devops-platform/
├── .github/workflows/ci.yml
├── database/init.sql
├── docs/
│   ├── diagrams/
│   │   ├── architecture.mmd
│   │   ├── ci-cd-pipeline.mmd
│   │   └── kubernetes-architecture.mmd
│   └── screenshots/
│       ├── checkout.png
│       ├── grafana.png
│       ├── homepage.png
│       ├── jenkins.png
│       └── products.png
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── infrastructure/
│   ├── ansible/
│   ├── helm/shopsphere/
│   ├── jenkins/
│   ├── kubernetes/
│   ├── monitoring/
│   └── terraform/main.tf
├── services/
│   ├── user-service/
│   ├── product-service/
│   ├── order-service/
│   └── payment-service/
├── shared/
│   ├── logging_config.py
│   └── metrics.py
├── tests/test_services.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Jenkinsfile
├── requirements-dev.txt
├── requirements-security.txt
└── README.md

```

## 12. Security and Limitations

### Container Security

- Application containers run as a dedicated non-root user.
- Docker images update operating system packages during builds.
- Docker build context excludes environment files, private keys, Terraform state, and unnecessary files.
- Application containers use restricted filesystem ownership.
- Jenkins deployment uses a restricted SSH key and host-side deployment script.

### Kubernetes Security

- Application pods use non-root execution with UID/GID 999.
- Privilege escalation is disabled.
- Linux capabilities are dropped for application containers.
- RuntimeDefault seccomp profile is configured.
- Database credentials are referenced through Kubernetes Secrets rather than hardcoded values.

### Vulnerability Scanning

Container images were scanned using Trivy.

The scan identified HIGH-severity operating system package findings and no CRITICAL findings in the recorded scan. No Python dependency vulnerabilities were reported.

Some operating system findings did not have an available fix at scan time. Therefore, the images should not be considered vulnerability-free.

### Limitations

- Kubernetes manifests and Helm templates are validated but have not been deployed to a live cluster.
- Payment operations are simulated; no real financial transactions occur.
- Terraform currently performs read-only infrastructure inspection.
- Automatic deployment rollback is not implemented.
- Application API ports are bound to localhost on the EC2 host.
- This is a learning and portfolio project, not a fully production-hardened platform.
- Environment files, passwords, tokens, private keys, and sensitive Terraform state must never be committed.


## 13. Future Improvements

- Improve monitoring dashboards and alerting.
- Implement automated deployment rollback.
- Expand automated test coverage.
- Improve authentication and application security.
- Explore Kubernetes-based deployment.
- Extend infrastructure automation.

## 14. Repository

GitHub: https://github.com/ahmad24mliwala/shopsphere-devops-platform
