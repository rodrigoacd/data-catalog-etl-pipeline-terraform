"""Tests de validación Terraform"""
import unittest
import re

class TestTerraformValidation(unittest.TestCase):
    
    def test_project_id_format(self):
        """TEST 1: Valida formato project_id"""
        valid_ids = ['my-project-123', 'test-project', 'prod-env-001']
        pattern = r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$'
        
        for project_id in valid_ids:
            self.assertIsNotNone(re.match(pattern, project_id))
    
    def test_bucket_name_format(self):
        """TEST 2: Valida formato bucket name"""
        valid_names = ['my-bucket', 'data-bucket-123']
        pattern = r'^[a-z0-9][a-z0-9-_.]{1,61}[a-z0-9]$'
        
        for name in valid_names:
            self.assertIsNotNone(re.match(pattern, name))
    
    def test_service_account_id_format(self):
        """TEST 3: Valida formato service account"""
        valid_ids = ['my-sa', 'function-sa', 'datacatalog-sa']
        pattern = r'^[a-z][a-z0-9-]{5,29}$'
        
        for sa_id in valid_ids:
            self.assertIsNotNone(re.match(pattern, sa_id))

if __name__ == '__main__':
    unittest.main(verbosity=2)
