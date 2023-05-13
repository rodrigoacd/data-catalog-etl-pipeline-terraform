variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "csv_bucket_name" {
  description = "Bucket name for CSV files"
  type        = string
}

variable "service_account_id" {
  description = "Service Account ID"
  type        = string
  default     = "datacatalog-function-sa"
}

variable "function_name" {
  description = "Cloud Function name"
  type        = string
  default     = "csv-to-datacatalog"
}

variable "entry_group_id" {
  description = "Data Catalog Entry Group ID"
  type        = string
  default     = "csv-tables-group"
}

variable "tag_template_id" {
  description = "Data Catalog Tag Template ID"
  type        = string
  default     = "csv-table-metadata"
}
