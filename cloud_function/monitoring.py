"""Módulo de monitoreo y métricas"""
import logging

logger = logging.getLogger(__name__)

def log_processing_metrics(metadata):
    """Registra métricas de procesamiento"""
    logger.info(f"Metrics - Rows: {metadata['row_count']}, Columns: {metadata['column_count']}")
    logger.info(f"Metrics - Size: {metadata['file_size']} bytes")
    logger.info(f"Metrics - Table: {metadata['table_name']}")
