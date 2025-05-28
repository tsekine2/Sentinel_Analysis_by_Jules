import unittest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import os
import sys
import zipfile

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scene_classifier import generate_scene_classification_map

class TestSceneClassifier(unittest.TestCase):

    @patch('scene_classifier.glob.glob')
    @patch('scene_classifier.rasterio.open')
    @patch('scene_classifier.os.path.exists', return_value=True) # Assume product path exists
    def test_generate_scl_map_unzipped_safe_directory(self, mock_exists, mock_rasterio_open, mock_glob):
        # Mock SCL file path
        mock_scl_file = '/path/to/product.SAFE/GRANULE/L2A_T123_N123_R123_V123/IMG_DATA/R20m/SCL_20m.jp2'
        mock_glob.side_effect = [[mock_scl_file], [], []] # First pattern finds the file

        # Mock rasterio.open().read() and .meta
        mock_scl_data = np.random.randint(0, 12, size=(100, 100), dtype=np.uint8)
        mock_scl_meta = {'driver': 'JP2OpenJPEG', 'width': 100, 'height': 100, 'count': 1, 'dtype': 'uint8'}
        
        mock_rasterio_context = MagicMock()
        mock_rasterio_context.__enter__.return_value.read.return_value = mock_scl_data
        mock_rasterio_context.__enter__.return_value.meta = mock_scl_meta
        mock_rasterio_open.return_value = mock_rasterio_context

        product_path = '/path/to/product.SAFE' # Unzipped .SAFE directory
        scl_data, scl_meta = generate_scene_classification_map(product_path)

        self.assertIsNotNone(scl_data)
        self.assertIsNotNone(scl_meta)
        np.testing.assert_array_equal(scl_data, mock_scl_data)
        self.assertEqual(scl_meta['width'], 100)
        mock_rasterio_open.assert_called_once_with(mock_scl_file)
        
        # Check that glob was called with expected patterns
        expected_glob_calls = [
            unittest.mock.call(os.path.join(product_path, '**', '*_SCL_20m.jp2'), recursive=True),
            # No need to check other patterns if the first one succeeded
        ]
        mock_glob.assert_has_calls(expected_glob_calls, any_order=False)


    @patch('scene_classifier.zipfile.ZipFile')
    @patch('scene_classifier.glob.glob')
    @patch('scene_classifier.rasterio.open')
    @patch('scene_classifier.os.path.exists')
    @patch('scene_classifier.os.makedirs')
    def test_generate_scl_map_zipped_product(self, mock_makedirs, mock_os_exists, mock_rasterio_open, mock_glob, mock_zipfile):
        # os.path.exists: True for zip, False for extracted dir, then True for extracted dir after creation
        mock_os_exists.side_effect = [True, False, True, True] 

        # Mock SCL file path within extracted structure
        extracted_dir_name = 'S2_Product_extracted'
        product_zip_path = '/path/to/S2_Product.zip'
        # The structure inside the zip might be just a .SAFE folder
        # So extracted_path/PRODUCT.SAFE/...
        mock_safe_dir_in_zip = os.path.join(os.path.dirname(product_zip_path), extracted_dir_name, 'S2_Product.SAFE')
        mock_scl_file = os.path.join(mock_safe_dir_in_zip, 'GRANULE/L2A_T123/IMG_DATA/R20m/SCL_20m.jp2')

        # Glob should find .SAFE dir first, then SCL file
        mock_glob.side_effect = [
            [mock_safe_dir_in_zip], # For finding *.SAFE in extracted_path
            [mock_scl_file],        # For finding SCL_20m.jp2
            [],                     # For SCL_60m.jp2
            []                      # For SCL_*.jp2
        ]

        # Mock rasterio
        mock_scl_data_zip = np.random.randint(0, 12, size=(50, 50), dtype=np.uint8)
        mock_scl_meta_zip = {'driver': 'JP2OpenJPEG', 'width': 50, 'height': 50, 'count': 1, 'dtype': 'uint8'}
        mock_rasterio_context_zip = MagicMock()
        mock_rasterio_context_zip.__enter__.return_value.read.return_value = mock_scl_data_zip
        mock_rasterio_context_zip.__enter__.return_value.meta = mock_scl_meta_zip
        mock_rasterio_open.return_value = mock_rasterio_context_zip

        # Mock ZipFile
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        scl_data, scl_meta = generate_scene_classification_map(product_zip_path)

        self.assertIsNotNone(scl_data)
        np.testing.assert_array_equal(scl_data, mock_scl_data_zip)
        self.assertEqual(scl_meta['width'], 50)

        expected_extraction_path = os.path.join(os.path.dirname(product_zip_path), extracted_dir_name)
        mock_os_exists.assert_any_call(product_zip_path) # Check if zip exists
        mock_os_exists.assert_any_call(expected_extraction_path) # Check if extraction dir exists
        mock_makedirs.assert_called_once_with(expected_extraction_path, exist_ok=True)
        mock_zipfile.assert_called_once_with(product_zip_path, 'r')
        mock_zip_instance.extractall.assert_called_once_with(expected_extraction_path)
        
        mock_rasterio_open.assert_called_once_with(mock_scl_file)

        # Check glob calls
        expected_glob_calls = [
            unittest.mock.call(os.path.join(expected_extraction_path, '*.SAFE'), recursive=True), # First to find .SAFE
            unittest.mock.call(os.path.join(mock_safe_dir_in_zip, '**', '*_SCL_20m.jp2'), recursive=True), # Then SCL
        ]
        mock_glob.assert_has_calls(expected_glob_calls, any_order=False)


    @patch('scene_classifier.glob.glob', return_value=[]) # No SCL files found
    @patch('scene_classifier.os.path.exists', return_value=True)
    def test_scl_file_not_found(self, mock_exists, mock_glob):
        product_path = '/path/to/product.SAFE'
        scl_data, scl_meta = generate_scene_classification_map(product_path)

        self.assertIsNone(scl_data)
        self.assertIsNone(scl_meta)
        # Check that glob was called with all patterns
        expected_glob_calls = [
            unittest.mock.call(os.path.join(product_path, '**', '*_SCL_20m.jp2'), recursive=True),
            unittest.mock.call(os.path.join(product_path, '**', '*_SCL_60m.jp2'), recursive=True),
            unittest.mock.call(os.path.join(product_path, '**', '*_SCL_*.jp2'), recursive=True),
        ]
        mock_glob.assert_has_calls(expected_glob_calls, any_order=False)


    @patch('scene_classifier.os.path.exists', return_value=False) # Product path does not exist
    def test_product_path_does_not_exist(self, mock_exists):
        product_path = '/non/existent/path.SAFE'
        scl_data, scl_meta = generate_scene_classification_map(product_path)
        self.assertIsNone(scl_data)
        self.assertIsNone(scl_meta)
        mock_exists.assert_called_once_with(product_path)

    @patch('scene_classifier.os.path.exists', return_value=True)
    @patch('scene_classifier.glob.glob')
    @patch('scene_classifier.rasterio.open')
    def test_rasterio_exception(self, mock_rasterio_open, mock_glob, mock_exists):
        mock_scl_file = '/path/to/product.SAFE/GRANULE/L2A_T123_N123_R123_V123/IMG_DATA/R20m/SCL_20m.jp2'
        mock_glob.side_effect = [[mock_scl_file], [], []] 
        mock_rasterio_open.side_effect = Exception("Rasterio failed to open")

        product_path = '/path/to/product.SAFE'
        scl_data, scl_meta = generate_scene_classification_map(product_path)
        self.assertIsNone(scl_data)
        self.assertIsNone(scl_meta)

if __name__ == '__main__':
    unittest.main()
