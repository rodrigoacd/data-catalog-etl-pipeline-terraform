output "function_name" {
  description = "Function name"
  value       = google_cloudfunctions2_function.function.name
}

output "function_url" {
  description = "Function URL"
  value       = google_cloudfunctions2_function.function.url
}

output "function_id" {
  description = "Function ID"
  value       = google_cloudfunctions2_function.function.id
}
