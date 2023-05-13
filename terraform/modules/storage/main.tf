resource "google_storage_bucket" "csv_bucket" {
  name          = var.bucket_name
  location      = var.location
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
  force_destroy               = false
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Directorio predeterminado para tablas (metadata)
resource "google_storage_bucket_object" "tables_dir" {
  name    = "tables/.keep"
  content = "CSV table files directory"
  bucket  = google_storage_bucket.csv_bucket.name
}
