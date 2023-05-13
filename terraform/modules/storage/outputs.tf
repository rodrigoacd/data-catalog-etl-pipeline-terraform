output "bucket_name" {
  description = "Bucket name"
  value       = google_storage_bucket.csv_bucket.name
}

output "bucket_url" {
  description = "Bucket URL"
  value       = google_storage_bucket.csv_bucket.url
}

output "bucket_id" {
  description = "Bucket ID"
  value       = google_storage_bucket.csv_bucket.id
}
