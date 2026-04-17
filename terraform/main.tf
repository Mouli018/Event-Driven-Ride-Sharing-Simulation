terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0.0"
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

resource "kubernetes_namespace" "ride_share" {
  metadata {
    name = "ride-share-prod"
  }
}

resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

# Install ArgoCD via Helm
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
  version    = "5.46.0"

  set {
    name  = "server.service.type"
    value = "LoadBalancer"
  }
}

# Install Prometheus/Grafana Stack via Helm
resource "helm_release" "kube-prometheus" {
  name       = "kube-prometheus-stack"
  namespace  = "monitoring"
  create_namespace = true
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  
  set {
    name  = "grafana.service.type"
    value = "LoadBalancer"
  }
}
