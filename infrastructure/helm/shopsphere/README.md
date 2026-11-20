# ShopSphere Helm Chart

## Overview

This Helm chart deploys the ShopSphere microservices e-commerce
application and PostgreSQL database on Kubernetes.

## Components

- User Service
- Product Service
- Order Service
- Payment Service
- PostgreSQL StatefulSet
- Database headless Service
- Database initialization ConfigMap
- Four application ClusterIP Services
- Kubernetes Namespace

## Prerequisites

- Kubernetes cluster
- kubectl
- Helm 3 or later
- Application container images available to the cluster
- Database Kubernetes Secret

## Configuration

Application and database configuration is maintained in values.yaml.

Configurable settings include:

- Application image names and tags
- Replica counts
- Container ports
- CPU and memory requests and limits
- Database storage size
- Database Secret name
- Image pull policy

## Database Secret

The chart does not contain actual credentials.

Create the shopsphere-db-secret Secret before deploying the chart.

Required keys:

- DB_NAME
- DB_USER
- DB_PASSWORD
- DATABASE_URL

The PostgreSQL StatefulSet uses the first three keys.
Application Deployments use DATABASE_URL.

Never commit real credentials or Kubernetes Secret manifests
containing real credentials.

## Validate the Chart

Run:

    helm lint infrastructure/helm/shopsphere

Render Kubernetes manifests:

    helm template shopsphere infrastructure/helm/shopsphere \
      --namespace shopsphere

Validate rendered manifests:

    helm template shopsphere infrastructure/helm/shopsphere \
      --namespace shopsphere > /tmp/shopsphere-rendered.yaml

    kubeconform -strict -summary /tmp/shopsphere-rendered.yaml

## Install

After preparing the Kubernetes cluster, container images
and database Secret:

    helm install shopsphere infrastructure/helm/shopsphere \
      --namespace shopsphere

The chart includes a Namespace resource.

## Upgrade

    helm upgrade shopsphere infrastructure/helm/shopsphere \
      --namespace shopsphere

## Rollback

    helm rollback shopsphere 1 --namespace shopsphere

## Uninstall

    helm uninstall shopsphere --namespace shopsphere

Note: Uninstalling the chart does not automatically guarantee
deletion of persistent volume data. Review PVC and storage
retention before removing database resources.

## Current Implementation Status

- Helm chart created.
- Configurable values implemented.
- PostgreSQL StatefulSet and persistent storage configured.
- Application Deployments and Services templated.
- Database initialization SQL packaged.
- Kubernetes Secret references configured.
- Helm lint passed.
- 12 rendered Kubernetes resources validated with kubeconform.

Actual Kubernetes cluster deployment has not yet been performed.

## Repository Structure

    shopsphere/
    ├── Chart.yaml
    ├── values.yaml
    ├── README.md
    ├── files/
    │   └── db-init.sql
    └── templates/
        ├── namespace.yaml
        ├── deployments.yaml
        ├── services.yaml
        ├── db-configmap.yaml
        ├── db-service.yaml
        └── db-statefulset.yaml
