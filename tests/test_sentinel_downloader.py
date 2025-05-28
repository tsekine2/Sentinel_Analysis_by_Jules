import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from collections import OrderedDict
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from sentinel_downloader import download_sentinel_imagery

class TestSentinelDownloader(unittest.TestCase):

    @patch('sentinel_downloader.SentinelAPI')
    @patch('sentinel_downloader.os.makedirs')
    @patch('sentinel_downloader.os.path.exists')
    def test_download_successful(self, mock_exists, mock_makedirs, MockSentinelAPI):
        # Mock os.path.exists to simulate directory not existing initially, then existing
        mock_exists.side_effect = [False, True] # First call for output_path, second for downloaded file

        # Setup mock API
        mock_api_instance = MockSentinelAPI.return_value
        
        # Mock products
        mock_product_id_1 = 'prod1_id'
        mock_product_info_1 = {
            'title': 'S2_Product_1',
            'ingestiondate': '20230101T100000Z',
            'cloudcoverpercentage': 10,
            'uuid': mock_product_id_1
        }
        mock_product_id_2 = 'prod2_id'
        mock_product_info_2 = {
            'title': 'S2_Product_2',
            'ingestiondate': '20230102T100000Z', # More recent
            'cloudcoverpercentage': 5,
            'uuid': mock_product_id_2
        }
        mock_products = OrderedDict([
            (mock_product_id_1, mock_product_info_1),
            (mock_product_id_2, mock_product_info_2)
        ])
        mock_api_instance.query.return_value = mock_products
        
        # Mock download
        mock_download_path = '/fake/path/to/S2_Product_2.zip'
        mock_api_instance.download.return_value = {
            'id': mock_product_id_2,
            'title': 'S2_Product_2',
            'path': mock_download_path
        }

        # Parameters for the function call
        user = 'testuser'
        password = 'testpassword'
        footprint_wkt = 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
        date_start = '20230101'
        date_end = '20230110'
        cloud_cover = (0, 20)
        output_path = './test_output'

        # Call the function
        result_path = download_sentinel_imagery(user, password, footprint_wkt, date_start, date_end, cloud_cover, output_path)

        # Assertions
        mock_exists.assert_any_call(output_path) # Check if output dir exists
        mock_makedirs.assert_called_once_with(output_path) # Check if makedirs was called

        MockSentinelAPI.assert_called_once_with(user, password, 'https://apihub.copernicus.eu/apihub')
        
        mock_api_instance.query.assert_called_once_with(
            footprint_wkt,
            platformname='Sentinel-2',
            producttype='S2MSI2A',
            date=(date_start, date_end),
            cloudcoverpercentage=cloud_cover
        )
        
        # Should download the most recent product (prod2_id)
        mock_api_instance.download.assert_called_once_with(mock_product_id_2, directory_path=output_path)
        self.assertEqual(result_path, mock_download_path)

    @patch('sentinel_downloader.SentinelAPI')
    @patch('sentinel_downloader.os.path.exists', return_value=True) # Assume directory exists
    def test_no_products_found(self, mock_exists, MockSentinelAPI):
        mock_api_instance = MockSentinelAPI.return_value
        mock_api_instance.query.return_value = OrderedDict() # Empty products

        result_path = download_sentinel_imagery('u', 'p', 'wkt', 'd1', 'd2', (0,10), './out')

        self.assertIsNone(result_path)
        mock_api_instance.download.assert_not_called()

    @patch('sentinel_downloader.SentinelAPI')
    @patch('sentinel_downloader.os.path.exists')
    def test_download_failed_offline_then_success_no_checksum(self, mock_exists, MockSentinelAPI):
        mock_exists.side_effect = [False, True, True] # output dir, first download check, second download check

        mock_api_instance = MockSentinelAPI.return_value
        mock_product_id = 'prod_offline_id'
        mock_products = OrderedDict([(mock_product_id, {'title': 'OfflineProduct', 'ingestiondate': '20230101', 'uuid': mock_product_id})])
        mock_api_instance.query.return_value = mock_products

        # Simulate first download failing (e.g. product offline, path not existing)
        mock_api_instance.download.side_effect = [
            {'id': mock_product_id, 'title': 'OfflineProduct', 'path': '/non/existent/path.zip'}, # First attempt
            {'id': mock_product_id, 'title': 'OfflineProduct', 'path': '/successful/path_no_checksum.zip'} # Second attempt
        ]
        
        output_path = './test_output_offline'
        result_path = download_sentinel_imagery('u', 'p', 'wkt', 'd1', 'd2', (0,10), output_path)

        self.assertEqual(result_path, '/successful/path_no_checksum.zip')
        self.assertEqual(mock_api_instance.download.call_count, 2)
        mock_api_instance.download.assert_any_call(mock_product_id, directory_path=output_path) # First call
        mock_api_instance.download.assert_any_call(mock_product_id, directory_path=output_path, checksum=False) # Second call with checksum=False

    @patch('sentinel_downloader.SentinelAPI')
    @patch('sentinel_downloader.os.path.exists', return_value=True)
    def test_api_exception(self, mock_exists, MockSentinelAPI):
        MockSentinelAPI.side_effect = Exception("API Connection Error")

        result_path = download_sentinel_imagery('u', 'p', 'wkt', 'd1', 'd2', (0,10), './out')
        self.assertIsNone(result_path)

if __name__ == '__main__':
    unittest.main()
