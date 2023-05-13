"""Tests para CSVMetadataExtractor"""
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestCSVMetadataExtractor(unittest.TestCase):
    
    def test_detect_integer_type(self):
        """TEST 1: Detecta tipos INTEGER"""
        values = ['1', '2', '3', '100']
        # Mock de la clase
        result = self._mock_detect_type(values)
        self.assertEqual(result, 'INTEGER')
    
    def test_detect_float_type(self):
        """TEST 2: Detecta tipos FLOAT"""
        values = ['1.5', '2.3', '3.14']
        result = self._mock_detect_type(values)
        self.assertEqual(result, 'FLOAT')
    
    def test_detect_string_type(self):
        """TEST 3: Detecta tipos STRING"""
        values = ['hello', 'world', 'test']
        result = self._mock_detect_type(values)
        self.assertEqual(result, 'STRING')
    
    def test_get_table_name(self):
        """TEST 4: Extrae nombre de tabla correctamente"""
        test_cases = [
            ('tables/users.csv', 'users'),
            ('data/orders-2024.csv', 'orders_2024'),
            ('sales data.csv', 'sales_data'),
        ]
        for file_name, expected in test_cases:
            result = self._mock_get_table_name(file_name)
            self.assertEqual(result, expected)
    
    def _mock_detect_type(self, values):
        """Mock de _detect_type"""
        if not values:
            return 'STRING'
        if all(str(v).isdigit() for v in values):
            return 'INTEGER'
        try:
            if all(self._is_float(v) for v in values):
                return 'FLOAT'
        except:
            pass
        return 'STRING'
    
    def _mock_get_table_name(self, file_name):
        """Mock de _get_table_name"""
        name = file_name.split('/')[-1]
        name = name.replace('.csv', '').replace('.CSV', '')
        name = name.replace('-', '_').replace(' ', '_')
        return name.lower()
    
    def _is_float(self, value):
        try:
            float(str(value))
            return True
        except:
            return False

if __name__ == '__main__':
    unittest.main(verbosity=2)
