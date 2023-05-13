variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "function_name" {
  description = "Function name"
  type        = string
}

variable "service_account_email" {
  description = "Service Account email"
  type        = string
}

variable "trigger_bucket" {
  description = "Bucket that triggers the function"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables"
  type        = map(string)
  default     = {}
}
