terraform {
  backend "gcs" {
    bucket = "REEMPLAZAR_POR_TU_BUCKET"
    prefix = "hospital-triage-ia/terraform/state"
  }
}
