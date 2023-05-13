# Entry Group
resource "google_data_catalog_entry_group" "csv_group" {
  entry_group_id = var.entry_group_id
  display_name   = "CSV Tables"
  description    = "Tablas CSV importadas desde Cloud Storage"
  
  project = var.project_id
  region  = var.location
}

# Tag Template
resource "google_data_catalog_tag_template" "csv_template" {
  tag_template_id = var.tag_template_id
  display_name    = "CSV Table Metadata"
  
  project = var.project_id
  region  = var.location
  
  fields {
    field_id     = "source_file"
    display_name = "Source File"
    type {
      primitive_type = "STRING"
    }
    is_required = true
  }
  
  fields {
    field_id     = "row_count"
    display_name = "Row Count"
    type {
      primitive_type = "DOUBLE"
    }
  }
  
  fields {
    field_id     = "column_count"
    display_name = "Column Count"
    type {
      primitive_type = "DOUBLE"
    }
  }
  
  fields {
    field_id     = "file_size_bytes"
    display_name = "File Size (bytes)"
    type {
      primitive_type = "DOUBLE"
    }
  }
  
  fields {
    field_id     = "last_updated"
    display_name = "Last Updated"
    type {
      primitive_type = "TIMESTAMP"
    }
  }
}
