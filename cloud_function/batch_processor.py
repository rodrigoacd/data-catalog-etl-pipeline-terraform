"""Procesamiento por lotes de múltiples CSVs"""

def process_batch(bucket_name, file_pattern):
    """Procesa múltiples archivos CSV en lote"""
    from google.cloud import storage
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix=file_pattern)
    
    results = []
    for blob in blobs:
        if blob.name.endswith('.csv'):
            # Procesar cada archivo
            results.append({
                'file': blob.name,
                'status': 'queued'
            })
    
    return results
