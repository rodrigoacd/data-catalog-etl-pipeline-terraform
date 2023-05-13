# Bucket para código fuente
resource "google_storage_bucket" "function_source" {
  name          = "${var.project_id}-function-source"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  force_destroy               = true
}

# Cloud Function Gen 2
resource "google_cloudfunctions2_function" "function" {
  name        = var.function_name
  location    = var.region
  description = "Process CSV files and load to Data Catalog"
  
  build_config {
    runtime     = "python311"
    entry_point = "process_csv_to_catalog"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = "function-source.zip"
      }
    }
  }
  
  service_config {
    max_instance_count    = 10
    min_instance_count    = 0
    available_memory      = "512M"
    timeout_seconds       = 540
    service_account_email = var.service_account_email
    
    environment_variables = var.environment_variables
  }
  
  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    retry_policy   = "RETRY_POLICY_RETRY"
    
    event_filters {
      attribute = "bucket"
      value     = var.trigger_bucket
    }
  }
}
