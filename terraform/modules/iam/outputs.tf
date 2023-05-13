output "email" {
  description = "Service Account email"
  value       = google_service_account.function_sa.email
}

output "id" {
  description = "Service Account ID"
  value       = google_service_account.function_sa.account_id
}

output "name" {
  description = "Service Account name"
  value       = google_service_account.function_sa.name
}
