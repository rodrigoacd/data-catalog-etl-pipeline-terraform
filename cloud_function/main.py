"""
Cloud Function: CSV to Data Catalog
Trigger: Cloud Storage (finalize)
Descripción: Lee archivos CSV del bucket y carga metadata a Data Catalog
"""
import os
import csv
import json
import logging
from datetime import datetime
from io import StringIO

from google.cloud import datacatalog_v1
from google.cloud import storage
import functions_framework

# Configuración
PROJECT_ID = os.environ.get('GCP_PROJECT')
LOCATION = os.environ.get('GCP_LOCATION', 'us-central1')
ENTRY_GROUP_ID = os.environ.get('ENTRY_GROUP_ID', 'csv-tables-group')
TAG_TEMPLATE_ID = os.environ.get('TAG_TEMPLATE_ID', 'csv-table-metadata')

# Clientes
storage_client = storage.Client()
datacatalog_client = datacatalog_v1.DataCatalogClient()

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVMetadataExtractor:
    """Extrae metadata de archivos CSV"""
    
    def __init__(self, bucket_name, file_name):
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.metadata = {}
    
    def extract(self):
        """Extrae metadata del CSV"""
        try:
            # Descargar archivo
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {self.file_name}")
            
            # Leer contenido
            content = blob.download_as_text()
            
            # Analizar CSV
            csv_file = StringIO(content)
            reader = csv.DictReader(csv_file)
            
            # Obtener columnas
            columns = reader.fieldnames or []
            
            # Contar filas
            rows = list(reader)
            row_count = len(rows)
            
            # Inferir tipos de datos
            column_types = self._infer_types(rows, columns)
            
            # Metadata del blob
            self.metadata = {
                'file_name': self.file_name,
                'bucket_name': self.bucket_name,
                'table_name': self._get_table_name(self.file_name),
                'columns': columns,
                'column_count': len(columns),
                'row_count': row_count,
                'column_types': column_types,
                'file_size': blob.size,
                'created_time': blob.time_created.isoformat() if blob.time_created else None,
                'updated_time': blob.updated.isoformat() if blob.updated else None,
                'gcs_uri': f"gs://{self.bucket_name}/{self.file_name}"
            }
            
            logger.info(f"Metadata extraído: {json.dumps(self.metadata, indent=2, default=str)}")
            return self.metadata
            
        except Exception as e:
            logger.error(f"Error extrayendo metadata: {str(e)}")
            raise
    
    def _get_table_name(self, file_name):
        """Obtiene nombre de tabla desde el nombre del archivo"""
        # Remover extensión y path
        name = file_name.split('/')[-1]
        name = name.replace('.csv', '').replace('.CSV', '')
        # Limpiar caracteres especiales
        name = name.replace('-', '_').replace(' ', '_')
        return name.lower()
    
    def _infer_types(self, rows, columns):
        """Infiere tipos de datos de las columnas"""
        column_types = {}
        
        if not rows or not columns:
            return column_types
        
        for col in columns:
            # Tomar muestra de valores (máximo 100)
            sample = [row.get(col, '') for row in rows[:100] if row.get(col)]
            column_types[col] = self._detect_type(sample)
        
        return column_types
    
    def _detect_type(self, values):
        """Detecta tipo de dato de una lista de valores"""
        if not values:
            return 'STRING'
        
        # Intentar INTEGER
        if all(str(v).strip().isdigit() for v in values if v):
            return 'INTEGER'
        
        # Intentar FLOAT
        try:
            if all(self._is_float(v) for v in values if v):
                return 'FLOAT'
        except:
            pass
        
        # Intentar DATE
        if all(self._is_date(v) for v in values if v):
            return 'DATE'
        
        # Intentar BOOLEAN
        bool_values = {'true', 'false', 't', 'f', '1', '0', 'yes', 'no'}
        if all(str(v).lower() in bool_values for v in values if v):
            return 'BOOLEAN'
        
        return 'STRING'
    
    def _is_float(self, value):
        """Verifica si es número decimal"""
        try:
            float(str(value))
            return True
        except ValueError:
            return False
    
    def _is_date(self, value):
        """Verifica si es fecha"""
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(str(value), fmt)
                return True
            except ValueError:
                continue
        
        return False


class DataCatalogLoader:
    """Carga metadata a Data Catalog"""
    
    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.entry_group_id = ENTRY_GROUP_ID
        self.tag_template_id = TAG_TEMPLATE_ID
    
    def load(self, metadata):
        """Carga metadata a Data Catalog"""
        try:
            # 1. Asegurar Entry Group existe
            entry_group_name = self._ensure_entry_group()
            
            # 2. Asegurar Tag Template existe
            tag_template_name = self._ensure_tag_template()
            
            # 3. Crear/actualizar Entry
            entry_name = self._create_or_update_entry(entry_group_name, metadata)
            
            # 4. Crear/actualizar Tag
            self._create_or_update_tag(entry_name, tag_template_name, metadata)
            
            logger.info(f"✓ Metadata cargado exitosamente a Data Catalog: {entry_name}")
            return entry_name
            
        except Exception as e:
            logger.error(f"Error cargando a Data Catalog: {str(e)}")
            raise
    
    def _ensure_entry_group(self):
        """Crea Entry Group si no existe"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        entry_group_name = f"{parent}/entryGroups/{self.entry_group_id}"
        
        try:
            datacatalog_client.get_entry_group(name=entry_group_name)
            logger.info(f"Entry Group existe: {entry_group_name}")
        except Exception:
            logger.info(f"Creando Entry Group: {entry_group_name}")
            
            entry_group = datacatalog_v1.EntryGroup()
            entry_group.display_name = "CSV Tables Entry Group"
            entry_group.description = "Tablas CSV importadas automáticamente"
            
            datacatalog_client.create_entry_group(
                parent=parent,
                entry_group_id=self.entry_group_id,
                entry_group=entry_group
            )
        
        return entry_group_name
    
    def _ensure_tag_template(self):
        """Crea Tag Template si no existe"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        tag_template_name = f"{parent}/tagTemplates/{self.tag_template_id}"
        
        try:
            datacatalog_client.get_tag_template(name=tag_template_name)
            logger.info(f"Tag Template existe: {tag_template_name}")
        except Exception:
            logger.info(f"Creando Tag Template: {tag_template_name}")
            
            tag_template = datacatalog_v1.TagTemplate()
            tag_template.display_name = "CSV Table Metadata"
            
            # Campos del template
            tag_template.fields["source_file"] = datacatalog_v1.TagTemplateField(
                display_name="Source File",
                type_=datacatalog_v1.FieldType(primitive_type=datacatalog_v1.FieldType.PrimitiveType.STRING)
            )
            
            tag_template.fields["row_count"] = datacatalog_v1.TagTemplateField(
                display_name="Row Count",
                type_=datacatalog_v1.FieldType(primitive_type=datacatalog_v1.FieldType.PrimitiveType.DOUBLE)
            )
            
            tag_template.fields["column_count"] = datacatalog_v1.TagTemplateField(
                display_name="Column Count",
                type_=datacatalog_v1.FieldType(primitive_type=datacatalog_v1.FieldType.PrimitiveType.DOUBLE)
            )
            
            tag_template.fields["file_size_bytes"] = datacatalog_v1.TagTemplateField(
                display_name="File Size (bytes)",
                type_=datacatalog_v1.FieldType(primitive_type=datacatalog_v1.FieldType.PrimitiveType.DOUBLE)
            )
            
            tag_template.fields["last_updated"] = datacatalog_v1.TagTemplateField(
                display_name="Last Updated",
                type_=datacatalog_v1.FieldType(primitive_type=datacatalog_v1.FieldType.PrimitiveType.TIMESTAMP)
            )
            
            datacatalog_client.create_tag_template(
                parent=parent,
                tag_template_id=self.tag_template_id,
                tag_template=tag_template
            )
        
        return tag_template_name
    
    def _create_or_update_entry(self, entry_group_name, metadata):
        """Crea o actualiza Entry en Data Catalog"""
        entry_id = metadata['table_name'].replace('/', '_').replace('.', '_')
        entry_name = f"{entry_group_name}/entries/{entry_id}"
        
        # Crear Entry
        entry = datacatalog_v1.Entry()
        entry.display_name = metadata['table_name']
        entry.description = f"CSV table: {metadata['file_name']} ({metadata['row_count']} rows)"
        entry.type_ = datacatalog_v1.EntryType.FILESET
        
        # GCS fileset
        entry.gcs_fileset_spec = datacatalog_v1.GcsFilesetSpec(
            file_patterns=[metadata['gcs_uri']]
        )
        
        # Schema
        schema = datacatalog_v1.Schema()
        for col_name in metadata['columns']:
            column = datacatalog_v1.ColumnSchema()
            column.column = col_name
            column.type_ = metadata['column_types'].get(col_name, 'STRING')
            column.description = f"Type: {metadata['column_types'].get(col_name, 'STRING')}"
            schema.columns.append(column)
        
        entry.schema = schema
        
        # Crear o actualizar
        try:
            existing = datacatalog_client.get_entry(name=entry_name)
            logger.info(f"Actualizando Entry: {entry_name}")
            
            entry.name = entry_name
            update_mask = {"paths": ["display_name", "description", "schema"]}
            datacatalog_client.update_entry(entry=entry, update_mask=update_mask)
        except Exception:
            logger.info(f"Creando Entry: {entry_name}")
            datacatalog_client.create_entry(
                parent=entry_group_name,
                entry_id=entry_id,
                entry=entry
            )
        
        return entry_name
    
    def _create_or_update_tag(self, entry_name, tag_template_name, metadata):
        """Crea o actualiza Tag con metadata"""
        # Eliminar tags existentes
        try:
            tags = datacatalog_client.list_tags(parent=entry_name)
            for tag in tags:
                datacatalog_client.delete_tag(name=tag.name)
        except Exception:
            pass
        
        # Crear nuevo tag
        tag = datacatalog_v1.Tag()
        tag.template = tag_template_name
        
        tag.fields["source_file"] = datacatalog_v1.TagField(
            string_value=metadata['file_name']
        )
        tag.fields["row_count"] = datacatalog_v1.TagField(
            double_value=float(metadata['row_count'])
        )
        tag.fields["column_count"] = datacatalog_v1.TagField(
            double_value=float(metadata['column_count'])
        )
        tag.fields["file_size_bytes"] = datacatalog_v1.TagField(
            double_value=float(metadata['file_size'])
        )
        
        if metadata.get('updated_time'):
            from google.protobuf.timestamp_pb2 import Timestamp
            from dateutil import parser
            
            dt = parser.parse(metadata['updated_time'])
            timestamp = Timestamp()
            timestamp.FromDatetime(dt)
            
            tag.fields["last_updated"] = datacatalog_v1.TagField(
                timestamp_value=timestamp
            )
        
        datacatalog_client.create_tag(parent=entry_name, tag=tag)
        logger.info(f"Tag creado para: {entry_name}")


@functions_framework.cloud_event
def process_csv_to_catalog(cloud_event):
    """
    Cloud Function Principal
    Trigger: Cloud Storage (finalize)
    """
    data = cloud_event.data
    
    bucket_name = data['bucket']
    file_name = data['name']
    
    logger.info(f"▶ Evento recibido: gs://{bucket_name}/{file_name}")
    
    # Validar que sea CSV
    if not file_name.lower().endswith('.csv'):
        logger.info(f"Archivo ignorado (no es CSV): {file_name}")
        return {'status': 'ignored', 'reason': 'not_csv'}
    
    try:
        # 1. Extraer metadata
        logger.info("1. Extrayendo metadata del CSV...")
        extractor = CSVMetadataExtractor(bucket_name, file_name)
        metadata = extractor.extract()
        
        # 2. Cargar a Data Catalog
        logger.info("2. Cargando metadata a Data Catalog...")
        loader = DataCatalogLoader()
        entry_name = loader.load(metadata)
        
        logger.info(f"✓ Procesamiento completado exitosamente")
        
        return {
            'status': 'success',
            'entry_name': entry_name,
            'table_name': metadata['table_name'],
            'rows': metadata['row_count'],
            'columns': metadata['column_count']
        }
        
    except Exception as e:
        logger.error(f"✗ Error procesando archivo: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'status': 'error',
            'error': str(e),
            'file': file_name
        }
