# ShopSphere Monitoring

## Overview

ShopSphere uses Prometheus and Grafana for application and Kubernetes monitoring.

The monitoring stack runs through Docker Compose on the EC2 instance.

## Prometheus

Configuration: `prometheus.yml`

### Scrape Targets

| Target | Endpoint | Purpose |
|---|---|---|
| User Service | user-service:8000/metrics | Application metrics |
| Product Service | product-service:8000/metrics | Application metrics |
| Order Service | order-service:8000/metrics | Application metrics |
| Payment Service | payment-service:8000/metrics | Application metrics |
| Kubernetes API Server | Private K3s API endpoint | Control-plane metrics |
| kube-state-metrics | 172.18.0.1:18080/metrics | Kubernetes object-state metrics |

### Configuration

- Application scrape interval: 15 seconds
- Kubernetes scrape interval: 30 seconds
- Metrics path: `/metrics`
- Three Prometheus alert rules are configured in `alerts.yml`.

## Kubernetes Monitoring

### kube-state-metrics

Installed in the `kube-system` namespace using the Prometheus Community Helm chart.

It exposes Kubernetes object-state metrics, including:

- Pod information and status
- Deployment replica status
- StatefulSet status
- Container restart counters
- Namespace and node information

### Private Connectivity

A systemd service forwards kube-state-metrics through the Docker bridge.

- Bind address: `172.18.0.1`
- Forwarded port: `18080`
- Kubernetes service port: `8080`
- Service: `shopsphere-kube-state-metrics-forward.service`

The service automatically restarts and is not exposed through a public IP or Kubernetes NodePort.

### Kubernetes API Server Security

Prometheus accesses the Kubernetes API metrics endpoint over HTTPS.

- Dedicated service account with permission to access only `/metrics`
- Kubernetes CA certificate for TLS verification
- Automatic token refresh every 30 minutes using a systemd timer
- Credentials mounted into the Prometheus container read-only

## Grafana

Grafana runs as part of the Docker Compose monitoring stack and is intended to visualize application and Kubernetes metrics.

## Validation

Check Prometheus configuration:

```bash
docker exec shopsphere-prometheus promtool check config /etc/prometheus/prometheus.yml
```

## Grafana Dashboard

Grafana is available locally on port 3000 and is bound to 127.0.0.1.

Access Grafana securely from a local computer using an SSH tunnel:

```bash
ssh -i "your-key.pem" -L 3000:127.0.0.1:3000 ubuntu@your-ec2-public-ip
```

Dashboard: `ShopSphere Kubernetes Monitoring`

The dashboard includes:
- Total Kubernetes pods
- Pod distribution by namespace
- Ready pods by namespace
- Container restart counts
- Desired versus available deployment replicas
- Kubernetes node readiness
- Database StatefulSet ready replicas

Dashboard refresh interval: 30 seconds.

## Metrics Scope

kube-state-metrics exposes Kubernetes object-state metrics. CPU and memory usage are checked separately through the Kubernetes Metrics Server using `kubectl top`.

## Validation Results

- Prometheus configuration validated successfully using promtool.
- Six Prometheus scrape targets verified as UP.
- Kubernetes pod metrics successfully queried from Prometheus.
- Grafana Prometheus data source successfully tested.
- Grafana dashboard saved and persistence verified.
