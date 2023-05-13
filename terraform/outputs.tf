output "bucket_name" {
  description = "CSV bucket name"
  value       = module.storage.bucket_name
}

output "bucket_url" {
  description = "CSV bucket URL"
  value       = module.storage.bucket_url
}

output "function_name" {
  description = "Cloud Function name"
  value       = module.cloud_function.function_name
}

output "function_url" {
  description = "Cloud Function URL"
  value       = module.cloud_function.function_url
}

output "service_account_email" {
  description = "Service Account email"
  value       = module.service_account.email
}

output "entry_group_name" {
  description = "Data Catalog Entry Group name"
  value       = module.datacatalog.entry_group_name
}

output "tag_template_name" {
  description = "Data Catalog Tag Template name"
  value       = module.datacatalog.tag_template_name
}
