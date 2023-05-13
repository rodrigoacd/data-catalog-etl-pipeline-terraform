output "entry_group_name" {
  description = "Entry Group name"
  value       = google_data_catalog_entry_group.csv_group.name
}

output "tag_template_name" {
  description = "Tag Template name"
  value       = google_data_catalog_tag_template.csv_template.name
}
