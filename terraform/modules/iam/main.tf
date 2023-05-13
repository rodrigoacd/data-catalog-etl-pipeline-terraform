# Service Account para Cloud Function
resource "google_service_account" "function_sa" {
  account_id   = var.service_account_id
  display_name = "Data Catalog Function SA"
  description  = "Service Account for Cloud Function - Data Catalog ETL"
  project      = var.project_id
}

# Roles necesarios
resource "google_project_iam_member" "datacatalog_admin" {
  project = var.project_id
  role    = "roles/datacatalog.admin"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_project_iam_member" "storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_project_iam_member" "logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_project_iam_member" "monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}
