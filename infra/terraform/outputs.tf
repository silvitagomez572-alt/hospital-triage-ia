output "cluster_name" {
  description = "Nombre del clúster creado"
  value       = google_container_cluster.dev_autoscaling.name
}

output "endpoint" {
  description = "Endpoint del clúster Kubernetes"
  value       = google_container_cluster.dev_autoscaling.endpoint
}

output "location" {
  description = "Zona donde se creó el clúster"
  value       = google_container_cluster.dev_autoscaling.location
}

output "node_pool_name" {
  description = "Nombre del node pool"
  value       = google_container_node_pool.dev_autoscaling_nodes.name
}
