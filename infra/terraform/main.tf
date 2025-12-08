########################################
# Red y subred para el clúster de ML
########################################

resource "google_compute_network" "vpc" {
  name                    = "ml-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "ml-subnet"
  region        = var.region          # Ej: "southamerica-east1"
  ip_cidr_range = "10.0.0.0/16"
  network       = google_compute_network.vpc.id
}

########################################
# Clúster de Kubernetes con autoscaling
########################################

resource "google_container_cluster" "dev_autoscaling" {
  name     = var.cluster_name         # Ej: "ml-dev-autoscaling"
  location = var.zone                 # Ej: "southamerica-east1-b"

  remove_default_node_pool = true
  initial_node_count       = 1

  # 👇 Ahora usamos la VPC y subred que definimos arriba
  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id

  release_channel {
    channel = "REGULAR"
  }
}

########################################
# Node pool con autoscaling
########################################

resource "google_container_node_pool" "dev_autoscaling_nodes" {
  name     = "${var.cluster_name}-pool"
  cluster  = google_container_cluster.dev_autoscaling.name
  location = var.zone

  node_count = var.initial_node_count

  node_config {
    machine_type = var.machine_type   # Ej: "e2-medium"
    disk_size_gb = var.disk_size_gb   # Ej: 30

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }
}

