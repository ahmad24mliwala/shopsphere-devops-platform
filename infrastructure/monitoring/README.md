# ShopSphere Monitoring

## Prometheus

Prometheus collects application metrics from all four FastAPI microservices.

Configuration: `prometheus.yml`

### Scrape Targets

| Service | Metrics Endpoint |
|---|---|
| User | user-service:8000/metrics |
| Product | product-service:8000/metrics |
| Order | order-service:8000/metrics |
| Payment | payment-service:8000/metrics |

### Configuration

- Scrape interval: 15 seconds
- Metrics path: `/metrics`
- Service discovery: Docker Compose service DNS names

### Deployment

Prometheus is configured but not running on the current EC2 instance.

The EC2 instance has limited RAM and disk space, so Prometheus and Grafana should be deployed on a separate monitoring host or Kubernetes environment.

When deployed, ensure the monitoring environment can reach the application containers over the Docker network or an appropriately secured network connection.

### Validation

Check an application metrics endpoint:

```bash
curl http://localhost:8001/metrics
