# Deployment Guide

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (minikube, EKS, GKE, etc.)
- kubectl configured
- Docker images built and pushed to registry

### Build and Push Images
```bash
# Build backend
docker build -t your-registry/drug-discovery-backend:latest ./backend
docker push your-registry/drug-discovery-backend:latest

# Build frontend
docker build -t your-registry/drug-discovery-frontend:latest ./frontend
docker push your-registry/drug-discovery-frontend:latest
```

### Deploy to Kubernetes

1. Create namespace:
```bash
kubectl create namespace drug-discovery
```

2. Create secrets:
```bash
kubectl create secret generic app-secrets \
  --from-literal=secret-key=your-secret-key \
  --from-literal=db-password=your-db-password \
  -n drug-discovery
```

3. Apply manifests:
```bash
kubectl apply -f k8s/ -n drug-discovery
```

## AWS EKS Deployment

1. Create EKS cluster:
```bash
eksctl create cluster --name drug-discovery --region us-east-1
```

2. Configure kubectl:
```bash
aws eks update-kubeconfig --name drug-discovery --region us-east-1
```

3. Deploy using Helm (if using Helm charts):
```bash
helm install drug-discovery ./helm-chart
```

## GCP GKE Deployment

1. Create GKE cluster:
```bash
gcloud container clusters create drug-discovery \
  --num-nodes=3 \
  --zone=us-central1-a
```

2. Get credentials:
```bash
gcloud container clusters get-credentials drug-discovery --zone us-central1-a
```

3. Deploy:
```bash
kubectl apply -f k8s/
```

## Production Considerations

### Security
- Use strong SECRET_KEY
- Enable HTTPS/TLS
- Use managed database services (RDS, Cloud SQL)
- Implement rate limiting
- Use secrets management (AWS Secrets Manager, GCP Secret Manager)
- Enable firewall rules
- Regular security updates

### Scalability
- Horizontal pod autoscaling
- Database connection pooling
- Redis caching
- CDN for static assets
- Load balancing

### Monitoring
- Set up Prometheus and Grafana
- Configure alerting
- Log aggregation (ELK stack)
- Application performance monitoring (APM)

### Backup
- Database backups (automated)
- MLflow artifact backups
- Disaster recovery plan
