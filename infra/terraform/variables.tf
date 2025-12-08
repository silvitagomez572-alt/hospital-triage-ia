variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "cluster_name" {
  description = "Nombre del clúster GKE"
  type        = string
  default     = "ml-dev-autoscaling"
}

variable "region" {
  description = "Región de GCP"
  type        = string
  default     = "southamerica-east1"
}

variable "zone" {
  description = "Zona donde se crea el clúster"
  type        = string
  default     = "southamerica-east1-b"
}

variable "machine_type" {
  description = "Tipo de máquina para los nodos"
  type        = string
  default     = "e2-medium"
}

variable "disk_size_gb" {
  description = "Tamaño del disco de cada nodo"
  type        = number
  default     = 30
}

variable "initial_node_count" {
  description = "Cantidad inicial de nodos"
  type        = number
  default     = 1
}

variable "min_node_count" {
  description = "Cantidad mínima de nodos del autoscaler"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Cantidad máxima de nodos del autoscaler"
  type        = number
  default     = 3
}

