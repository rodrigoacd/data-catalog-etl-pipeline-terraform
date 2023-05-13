terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Habilitar APIs necesarias
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "datacatalog.googleapis.com",
    "eventarc.googleapis.com",
    "run.googleapis.com",
    "iam.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# Módulo: Service Account
module "service_account" {
  source = "./modules/iam"
  
  project_id         = var.project_id
  service_account_id = var.service_account_id
  
  depends_on = [google_project_service.apis]
}

# Módulo: Cloud Storage
module "storage" {
  source = "./modules/storage"
  
  project_id  = var.project_id
  bucket_name = var.csv_bucket_name
  location    = var.region
  
  depends_on = [google_project_service.apis]
}

# Módulo: Data Catalog
module "datacatalog" {
  source = "./modules/datacatalog"
  
  project_id      = var.project_id
  location        = var.region
  entry_group_id  = var.entry_group_id
  tag_template_id = var.tag_template_id
  
  depends_on = [google_project_service.apis]
}

# Módulo: Cloud Function
module "cloud_function" {
  source = "./modules/function"
  
  project_id            = var.project_id
  region                = var.region
  function_name         = var.function_name
  service_account_email = module.service_account.email
  trigger_bucket        = module.storage.bucket_name
  
  environment_variables = {
    GCP_PROJECT     = var.project_id
    GCP_LOCATION    = var.region
    ENTRY_GROUP_ID  = var.entry_group_id
    TAG_TEMPLATE_ID = var.tag_template_id
  }
  
  depends_on = [
    google_project_service.apis,
    module.service_account,
    module.storage,
    module.datacatalog
  ]
}
