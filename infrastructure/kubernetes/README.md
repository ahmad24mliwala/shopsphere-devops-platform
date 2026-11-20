
# ShopSphere Kubernetes Deployment

## Overview

ShopSphere is a microservices-based e-commerce application prepared for deployment on Kubernetes.

The Kubernetes configuration runs four FastAPI microservices and a PostgreSQL database inside a dedicated Kubernetes namespace.

### Architecture Components

| Component | Kubernetes Resource | Purpose |
|---|---|---|
| ShopSphere | Namespace | Application isolation |
| User Service | Deployment + Service | User management |
| Product Service | Deployment + Service | Product management |
| Order Service | Deployment + Service | Order management |
| Payment Service | Deployment + Service | Simulated payment processing |
| PostgreSQL | StatefulSet + Service | Persistent relational database |
| Database initialization | ConfigMap | Database schema initialization |
| Database credentials | Secret | Secure database configuration |

### Kubernetes Namespace

All application resources are configured in the `shopsphere` namespace.

### Container Images

The application uses four Docker images:

- `shopsphere-devops-platform-user-service:latest`
- `shopsphere-devops-platform-product-service:latest`
- `shopsphere-devops-platform-order-service:latest`
- `shopsphere-devops-platform-payment-service:latest`

The manifests currently reference locally available image names. A Kubernetes cluster must have access to these images through a container registry or an appropriate image-loading mechanism.


## Kubernetes Resource Configuration

### Application Deployments

Each microservice is configured with:

- One replica.
- Container port `8000`.
- Database connection through the Kubernetes Secret `shopsphere-db-secret`.
- CPU and memory requests and limits.
- Startup, readiness, and liveness probes.

### Health Probes

| Probe | Configuration | Purpose |
|---|---|---|
| Startup | TCP port 8000 | Allows application startup |
| Readiness | HTTP `/health` | Checks application and database readiness |
| Liveness | TCP port 8000 | Checks whether the application process is responding |

The readiness probe prevents traffic from being sent to an application that cannot connect to its database.

The liveness probe uses TCP so a temporary database outage does not automatically restart the application.

### PostgreSQL StatefulSet

PostgreSQL is configured using:

- PostgreSQL 16 image.
- One replica.
- PersistentVolumeClaim requesting 2Gi storage.
- Headless Service named `db`.
- ConfigMap for database initialization.
- Startup, readiness, and liveness probes.

The database uses persistent storage so its data can survive normal container restarts.

### Resource Management

Application resource configuration:

| Resource | Request | Limit |
|---|---:|---:|
| CPU | 100m | 500m |
| Memory | 128Mi | 256Mi |

PostgreSQL resource configuration:

| Resource | Request | Limit |
|---|---:|---:|
| CPU | 100m | 500m |
| Memory | 128Mi | 384Mi |


## Database Secrets

Database credentials are not stored directly in Kubernetes Deployment manifests.

The application Deployments reference a Kubernetes Secret named:

`shopsphere-db-secret`

The Secret must contain the following keys:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DATABASE_URL`

The PostgreSQL StatefulSet uses the first three keys. The four application services use `DATABASE_URL`.

### Creating the Secret

Assuming database variables are securely loaded into the shell:

```bash
export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}"
kubectl create secret generic shopsphere-db-secret --namespace shopsphere --from-literal=DB_NAME="$DB_NAME" --from-literal=DB_USER="$DB_USER" --from-literal=DB_PASSWORD="$DB_PASSWORD" --from-literal=DATABASE_URL="$DATABASE_URL"
unset DB_NAME DB_USER DB_PASSWORD DATABASE_URL
```

Do not commit actual credentials or Kubernetes Secret manifests containing real credentials.

## Deployment Workflow

The following steps describe the intended deployment order when a Kubernetes cluster is available.

### 1. Verify Kubernetes Cluster Access

```bash
kubectl cluster-info
kubectl get nodes
```

### 2. Create the Namespace

```bash
kubectl apply -f infrastructure/kubernetes/namespace.yaml
```

### 3. Create Database Credentials

Prepare the required environment variables securely and create the `shopsphere-db-secret` Secret in the `shopsphere` namespace.

Refer to the Database Secrets section.

### 4. Create Database Resources

```bash
kubectl apply -f infrastructure/kubernetes/db-service.yaml
kubectl apply -f infrastructure/kubernetes/db-init-configmap.yaml
kubectl apply -f infrastructure/kubernetes/db-statefulset.yaml
```

### 5. Deploy Application Services

```bash
kubectl apply -f infrastructure/kubernetes/user-service-deployment.yaml
kubectl apply -f infrastructure/kubernetes/user-service-service.yaml

kubectl apply -f infrastructure/kubernetes/product-service-deployment.yaml
kubectl apply -f infrastructure/kubernetes/product-service-service.yaml

kubectl apply -f infrastructure/kubernetes/order-service-deployment.yaml
kubectl apply -f infrastructure/kubernetes/order-service-service.yaml

kubectl apply -f infrastructure/kubernetes/payment-service-deployment.yaml
kubectl apply -f infrastructure/kubernetes/payment-service-service.yaml
```

### 6. Verify Deployment

```bash
kubectl get all -n shopsphere
kubectl get pods -n shopsphere
kubectl get pvc -n shopsphere
kubectl get services -n shopsphere
```

Check application logs:

```bash
kubectl logs deployment/user-service -n shopsphere
kubectl logs deployment/product-service -n shopsphere
kubectl logs deployment/order-service -n shopsphere
kubectl logs deployment/payment-service -n shopsphere
```


## Manifest Validation

Kubernetes manifests are validated using Kubeconform.

Install Kubeconform and run:

```bash
kubeconform -strict -summary infrastructure/kubernetes/
```

Validation result:

- Resources found: 12
- Valid resources: 12
- Invalid resources: 0
- Errors: 0

All 12 Kubernetes resources passed strict schema validation.

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n shopsphere
```

### Describe a Pod

```bash
kubectl describe pod <pod-name> -n shopsphere
```

### Check Application Logs

```bash
kubectl logs <pod-name> -n shopsphere
```

### Check Database Status

```bash
kubectl get statefulset -n shopsphere
kubectl get pvc -n shopsphere
kubectl logs shopsphere-db-0 -n shopsphere
```

### Common Issues

| Problem | Possible Cause |
|---|---|
| ImagePullBackOff | Image unavailable in the cluster |
| CrashLoopBackOff | Application startup or configuration failure |
| Pod not Ready | Health probe failure or database unavailable |
| PVC Pending | Storage provisioner or StorageClass issue |
| Database connection failure | Incorrect Secret or database service configuration |

## Current Implementation Status

| Area | Status |
|---|---|
| Kubernetes manifests | Prepared |
| YAML syntax validation | Passed |
| Strict schema validation | Passed |
| Kubernetes cluster | Not deployed |
| Application deployment | Not performed |
| Database Secret | Not created |
| Container registry integration | Pending |

## Important Notes

- These manifests are currently deployment-ready templates, not a verified live Kubernetes deployment.
- Application images must be accessible to the target Kubernetes cluster.
- Persistent storage requires a suitable storage provisioner.
- Database credentials must be created securely.
- Actual deployment and runtime testing are pending.

## Repository Structure

```text
infrastructure/
└── kubernetes/
    ├── namespace.yaml
    ├── user-service-deployment.yaml
    ├── user-service-service.yaml
    ├── product-service-deployment.yaml
    ├── product-service-service.yaml
    ├── order-service-deployment.yaml
    ├── order-service-service.yaml
    ├── payment-service-deployment.yaml
    ├── payment-service-service.yaml
    ├── db-service.yaml
    ├── db-statefulset.yaml
    ├── db-init-configmap.yaml
    └── README.md
```

