# ============================================================================
# Terraform Configuration for Solar Facades GKE Deployment
# ============================================================================

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure for production
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "terraform/state"
  # }
}

# ============================================================================
# Variables
# ============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "cluster_name" {
  description = "GKE Cluster name"
  type        = string
  default     = "solar-facades-cluster"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "api.solar-facades.example.com"
}

# ============================================================================
# Provider Configuration
# ============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ============================================================================
# Locals
# ============================================================================

locals {
  namespace = "solar-facades-${var.environment}"
  labels = {
    environment = var.environment
    application = "solar-facades"
    managed-by  = "terraform"
  }
}

# ============================================================================
# VPC Network
# ============================================================================

resource "google_compute_network" "vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  project                 = var.project_id
}

resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }

  private_ip_google_access = true
}

# ============================================================================
# Cloud NAT for outbound internet access
# ============================================================================

resource "google_compute_router" "router" {
  name    = "${var.cluster_name}-router"
  region  = var.region
  network = google_compute_network.vpc.id
  project = var.project_id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${var.cluster_name}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  project                            = var.project_id

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ============================================================================
# Firewall Rules
# ============================================================================

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.cluster_name}-allow-internal"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/20", "10.4.0.0/14", "10.8.0.0/20"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "${var.cluster_name}-allow-health-checks"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  target_tags   = ["gke-node"]
}

# ============================================================================
# GKE Cluster
# ============================================================================

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region
  project  = var.project_id

  # Regional cluster for high availability
  node_locations = [
    "${var.region}-a",
    "${var.region}-b",
    "${var.region}-c"
  ]

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.gke_subnet.name

  # IP allocation for pods and services
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Network policy for pod-to-pod communication
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # Workload Identity for GCP service account integration
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Master authorized networks (restrict access to control plane)
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks"
    }
  }

  # Enable Shielded Nodes
  enable_shielded_nodes = true

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Cluster autoscaling
  cluster_autoscaling {
    enabled = true
    autoscaling_profile = "OPTIMIZE_UTILIZATION"
    
    resource_limits {
      resource_type = "cpu"
      minimum       = 4
      maximum       = 100
    }
    
    resource_limits {
      resource_type = "memory"
      minimum       = 16
      maximum       = 400
    }
  }

  # Release channel for automatic updates
  release_channel {
    channel = "REGULAR"
  }

  # Binary authorization for container security
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  resource_labels = local.labels

  depends_on = [
    google_compute_subnetwork.gke_subnet
  ]
}

# ============================================================================
# Node Pools
# ============================================================================

# General purpose node pool
resource "google_container_node_pool" "general" {
  name       = "general-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  project    = var.project_id

  # Autoscaling configuration
  autoscaling {
    min_node_count = 2
    max_node_count = 10
    location_policy = "BALANCED"
  }

  # Node management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 100
    disk_type    = "pd-standard"

    # Service account
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = merge(local.labels, {
      pool = "general"
    })

    tags = ["gke-node", "${var.cluster_name}-node"]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# Database workload node pool (for StatefulSets)
resource "google_container_node_pool" "database" {
  name       = "database-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  project    = var.project_id

  autoscaling {
    min_node_count = 1
    max_node_count = 3
    location_policy = "BALANCED"
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    machine_type = "n2-standard-4"
    disk_size_gb = 200
    disk_type    = "pd-ssd"

    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = merge(local.labels, {
      pool = "database"
    })

    tags = ["gke-node", "${var.cluster_name}-node"]

    taint {
      key    = "workload"
      value  = "database"
      effect = "NO_SCHEDULE"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ============================================================================
# Service Accounts
# ============================================================================

# GKE Node Service Account
resource "google_service_account" "gke_nodes" {
  account_id   = "${var.cluster_name}-node-sa"
  display_name = "GKE Node Service Account for ${var.cluster_name}"
  project      = var.project_id
}

resource "google_project_iam_member" "gke_nodes_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/storage.objectViewer",
    "roles/artifactregistry.reader"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

# Backend Service Account
resource "google_service_account" "backend" {
  account_id   = "backend-sa"
  display_name = "Service Account for Backend API"
  project      = var.project_id
}

# Ingestor Service Account
resource "google_service_account" "ingestor" {
  account_id   = "ingestor-sa"
  display_name = "Service Account for Ingestor"
  project      = var.project_id
}

# Alert Monitor Service Account
resource "google_service_account" "alert_monitor" {
  account_id   = "alert-monitor-sa"
  display_name = "Service Account for Alert Monitor"
  project      = var.project_id
}

# Frontend Service Account
resource "google_service_account" "frontend" {
  account_id   = "frontend-sa"
  display_name = "Service Account for Frontend"
  project      = var.project_id
}

# IAM bindings for service accounts
resource "google_service_account_iam_binding" "backend_workload_identity" {
  service_account_id = google_service_account.backend.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${local.namespace}/backend-sa]"
  ]
}

resource "google_service_account_iam_binding" "ingestor_workload_identity" {
  service_account_id = google_service_account.ingestor.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${local.namespace}/ingestor-sa]"
  ]
}

resource "google_service_account_iam_binding" "alert_monitor_workload_identity" {
  service_account_id = google_service_account.alert_monitor.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${local.namespace}/alert-monitor-sa]"
  ]
}

# ============================================================================
# Cloud Storage Bucket for exports
# ============================================================================

resource "google_storage_bucket" "exports" {
  name          = "${var.project_id}-solar-facades-exports"
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

# IAM for bucket access
resource "google_storage_bucket_iam_member" "backend_bucket_access" {
  bucket = google_storage_bucket.exports.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.backend.email}"
}

# ============================================================================
# Artifact Registry
# ============================================================================

resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "solar-facades"
  description   = "Docker repository for Solar Facades application"
  format        = "DOCKER"
  project       = var.project_id

  labels = local.labels
}

# ============================================================================
# Static IP Address for Ingress
# ============================================================================

resource "google_compute_global_address" "ingress_ip" {
  name    = "solar-facades-ip"
  project = var.project_id
}

resource "google_compute_global_address" "frontend_ip" {
  name    = "frontend-ip"
  project = var.project_id
}

# ============================================================================
# Secret Manager Secrets
# ============================================================================

resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = local.labels
}

resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = local.labels
}

# IAM for secret access
resource "google_secret_manager_secret_iam_member" "backend_secret_accessor_db" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "backend_secret_accessor_redis" {
  secret_id = google_secret_manager_secret.redis_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "ingestor_secret_accessor_db" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ingestor.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "ingestor_secret_accessor_redis" {
  secret_id = google_secret_manager_secret.redis_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ingestor.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "alert_monitor_secret_accessor" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.alert_monitor.email}"
  project   = var.project_id
}

# ============================================================================
# Outputs
# ============================================================================

output "cluster_name" {
  description = "GKE Cluster name"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "GKE Cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE Cluster CA certificate"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "ingress_ip" {
  description = "Static IP address for Backend Ingress"
  value       = google_compute_global_address.ingress_ip.address
}

output "frontend_ip" {
  description = "Static IP address for Frontend Ingress"
  value       = google_compute_global_address.frontend_ip.address
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "storage_bucket" {
  description = "Cloud Storage bucket for exports"
  value       = google_storage_bucket.exports.url
}

output "service_accounts" {
  description = "Service account emails"
  value = {
    backend       = google_service_account.backend.email
    ingestor      = google_service_account.ingestor.email
    alert_monitor = google_service_account.alert_monitor.email
    frontend      = google_service_account.frontend.email
  }
}
