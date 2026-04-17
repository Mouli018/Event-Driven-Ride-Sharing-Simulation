variable "github_token" {
  description = "GitHub Token for GHCR authentication"
  type        = string
  sensitive   = true
}

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

# Example AWS EKS or DigitalOcean K8s Cluster provisioning would go here
# Using local kubernetes provider as a mock for the assignment standard

resource "kubernetes_namespace_v1" "ride_share" {
  metadata {
    name = "ride-share-prod"
  }
}

# Image Pull Secret for GHCR
resource "kubernetes_secret_v1" "ghcr_secret" {
  metadata {
    name      = "ghcr-login-secret"
    namespace = kubernetes_namespace_v1.ride_share.metadata[0].name
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "ghcr.io" = {
          auth = base64encode("token:${var.github_token}")
        }
      }
    })
  }
}

resource "kubernetes_namespace_v1" "argocd" {
  metadata {
    name = "argocd"
  }
}

# Install ArgoCD via Helm
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = kubernetes_namespace_v1.argocd.metadata[0].name
  version    = "5.46.0"
  wait       = false

  set {
    name  = "server.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "server.insecure"
    value = "true"
  }
}

# Install Prometheus/Grafana Stack via Helm
resource "helm_release" "kube-prometheus" {
  name       = "kube-prometheus-stack"
  namespace  = "monitoring"
  create_namespace = true
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  wait       = false
  
  set {
    name  = "grafana.service.type"
    value = "LoadBalancer"
  }
}
