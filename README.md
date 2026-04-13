# Event-Driven Ride-Sharing Simulation Backend

This project represents a complete end-to-end implementation of modern DevOps practices, fulfilling the requirements for the "Event-Driven Ride-Sharing Simulation Backend with Microservices, DevSecOps CI/CD Pipeline, and GitOps Automation."

## 1. Project Organization
This repository is broken down into the following key aspects:
- **`ride-request-service/`**: Python FastAPI Microservice. Validates requests, tracks basic state, exposes `/metrics` for Prometheus.
- **`Dockerfile`**: Follows multi-stage build best practices, building lightweight images and using a non-root user for execution to adhere to "Security-First" patterns.
- **`.github/workflows/devsecops.yml`**: Full CI Pipeline utilizing SonarQube (SAST) and Aquasecurity Trivy (SCA/Container Vulnerability scans). Fails build on CRITICAL vulnerabilities.
- **`terraform/`**: Infrastructure as Code simulating cluster deployment. Automates ArgoCD and Kube-Prometheus stack setup.
- **`k8s-manifests/`**: The "Source of Truth" GitOps folder. ArgoCD observes this repository and continually applies it to Kubernetes.

## 2. CI/CD Workflow & Deployment Mechanism
- **Code:** Changes are committed and pushed to GitHub.
- **CI Build:** GitHub Actions intercepts the Push/PR events. It lints the python code, runs basic Unit Tests, builds the Docker Image, and executes static and vulnerability scans.
- **GitOps CD:** Upon clean CI, image tags updating the `k8s-manifests` folder will trigger an automated Pull from **Argo CD**, ensuring absolute consistency between source control and active production cluster.

## 3. Operations & Observability
- **Prometheus**: Scrapes `/metrics` from services to ingest data points like active requests and memory footprints.
- **Grafana**: Creates the dashboards reading from Prometheus datastore. Highly available load balancer endpoints ensure dashboard reachability.
- **High-Availability (HPA)**: Handled directly within the Kubernetes deployment metrics tracking CPU/Memory threshold limits.
