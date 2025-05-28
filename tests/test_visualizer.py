import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from visualizer import visualize_scl_map, SCL_CLASSES

class TestVisualizer(unittest.TestCase):

    @patch('visualizer.plt.savefig')
    @patch('visualizer.plt.show')
    @patch('visualizer.plt.legend')
    @patch('visualizer.plt.subplots') # To control the fig and ax objects
    def test_visualize_scl_map_saves_file(self, mock_subplots, mock_legend, mock_show, mock_savefig):
        # Mock subplots to return a mock figure and axes
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        dummy_scl_data = np.random.randint(0, 12, size=(10, 10), dtype=np.uint8)
        output_path = "test_scl_map.png"

        visualize_scl_map(dummy_scl_data, output_image_path=output_path)

        mock_subplots.assert_called_once() # Check that a figure and axes were created
        mock_ax.imshow.assert_called_once() # Check that imshow was called
        
        # Check that legend was called. The specific handles might be complex to check deeply without more work.
        mock_legend.assert_called_once() 
        self.assertTrue(len(mock_legend.call_args[1]['handles']) == len(SCL_CLASSES))


        mock_savefig.assert_called_once_with(output_path, bbox_inches='tight')
        mock_show.assert_not_called()
        mock_fig.clf # Check if figure is cleared if using older matplotlib, or close for newer
        mock_fig.close.assert_called_once()


    @patch('visualizer.plt.savefig')
    @patch('visualizer.plt.show')
    @patch('visualizer.plt.legend')
    @patch('visualizer.plt.subplots')
    def test_visualize_scl_map_shows_plot(self, mock_subplots, mock_legend, mock_show, mock_savefig):
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        dummy_scl_data = np.random.randint(0, 12, size=(10, 10), dtype=np.uint8)

        visualize_scl_map(dummy_scl_data, output_image_path=None) # No output path

        mock_subplots.assert_called_once()
        mock_ax.imshow.assert_called_once()
        mock_legend.assert_called_once()

        mock_show.assert_called_once()
        mock_savefig.assert_not_called()
        mock_fig.close.assert_called_once()

    def test_visualize_scl_map_invalid_data(self):
        # Test with non-numpy array data to ensure it handles it gracefully
        with patch('builtins.print') as mock_print: # Capture print output
            visualize_scl_map("not_an_array")
            mock_print.assert_called_with("Error: scl_data must be a NumPy array.")

if __name__ == '__main__':
    unittest.main()
