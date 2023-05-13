# Data Catalog ETL System

Sistema automatizado para cargar metadata de archivos CSV a Google Cloud Data Catalog.

## 📊 Arquitectura

```
CSV Upload → Cloud Storage → Cloud Function → Data Catalog
```

### Componentes:

1. **Cloud Storage**: Bucket para archivos CSV (directorio `/tables/`)
2. **Cloud Function**: Procesa CSVs y extrae metadata
3. **Data Catalog**: Almacena metadata de tablas
4. **Service Account**: Permisos aislados por seguridad

## 🏗️ Infraestructura

### APIs habilitadas automáticamente:
- Cloud Functions API
- Cloud Build API
- Cloud Storage API
- Data Catalog API
- Eventarc API
- Cloud Run API
- IAM API

### Service Account con permisos:
- `roles/datacatalog.admin` - Gestión de Data Catalog
- `roles/storage.objectViewer` - Lectura de CSVs
- `roles/logging.logWriter` - Escritura de logs
- `roles/monitoring.metricWriter` - Métricas

## 📋 Prerequisitos

- Google Cloud SDK instalado
- Terraform >= 1.0
- Python 3.11
- Cuenta GCP con permisos de Owner/Editor

## 🚀 Deployment

### 1. Configurar variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Editar con tus valores:
```hcl
project_id      = "my-gcp-project"
region          = "us-central1"
csv_bucket_name = "my-project-csv-tables"
```

### 2. Preparar código de Cloud Function

```bash
cd ../cloud_function
zip -r ../terraform/function-source.zip .
cd ../terraform
```

### 3. Subir código a GCS

```bash
# Crear bucket temporal
gcloud storage buckets create gs://YOUR_PROJECT-function-source

# Subir ZIP
gcloud storage cp function-source.zip gs://YOUR_PROJECT-function-source/
```

### 4. Desplegar con Terraform

```bash
terraform init
terraform plan
terraform apply
```

## 📝 Uso

### Subir archivos CSV

Los archivos deben ir al directorio `/tables/` del bucket:

```bash
BUCKET=$(terraform output -raw bucket_name)

# Subir un CSV
gcloud storage cp my-table.csv gs://$BUCKET/tables/

# Subir múltiples
gcloud storage cp *.csv gs://$BUCKET/tables/ --recursive
```

### Verificar en Data Catalog

```bash
# CLI
gcloud data-catalog entries list --location=us-central1

# Web UI
# https://console.cloud.google.com/datacatalog
```

### Ver logs

```bash
gcloud functions logs read csv-to-datacatalog \
  --region=us-central1 \
  --limit=50
```

## 🔍 Metadata Extraído

Para cada CSV, el sistema extrae:

- **Nombre de tabla** (derivado del nombre del archivo)
- **Columnas** (nombres y tipos inferidos)
- **Número de filas**
- **Número de columnas**
- **Tamaño del archivo**
- **Fecha de creación/actualización**
- **URI de GCS**

### Tipos de datos detectados:

- `INTEGER` - Números enteros
- `FLOAT` - Números decimales
- `STRING` - Texto
- `DATE` - Fechas (varios formatos)
- `BOOLEAN` - true/false, yes/no, 1/0

## 🧪 Testing

```bash
cd tests
python test_metadata_extractor.py -v
python test_terraform_validation.py -v
```

## 🗑️ Limpieza

```bash
cd terraform
terraform destroy
```

## 📚 Estructura del Proyecto

```
.
├── cloud_function/          # Código Python
│   ├── main.py
│   └── requirements.txt
├── terraform/               # IaC
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── iam/            # Service Account
│       ├── storage/        # Buckets
│       ├── datacatalog/    # Entry Groups
│       └── function/       # Cloud Function
└── tests/                   # Tests unitarios
```

## 🔒 Seguridad

- Service Account dedicado (no usa default)
- Permisos mínimos necesarios (least privilege)
- Bucket con versionamiento habilitado
- Lifecycle policies para optimizar costos

## 💰 Costos Estimados

| Servicio | Costo/mes |
|----------|-----------|
| Cloud Functions (100K invocaciones) | ~$0.04 |
| Cloud Storage (10GB) | ~$0.50 |
| Data Catalog | Gratis* |
| **Total** | **~$0.54/mes** |

*El almacenamiento de metadata es gratuito

## 👤 Autor

Rodrigo ACD - rodrigo.acd@gmail.com
