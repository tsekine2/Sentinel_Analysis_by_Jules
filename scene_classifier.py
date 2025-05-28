import os
import glob
import zipfile
import rasterio
import numpy as np

def generate_scene_classification_map(product_path):
    """
    Generates a scene classification map from a Sentinel-2 product.

    Args:
        product_path (str): Path to the downloaded Sentinel product 
                             (either a .zip file or an unzipped .SAFE directory).

    Returns:
        tuple: A tuple containing:
            - scl_data (numpy.ndarray): The SCL data array.
            - scl_meta (dict): The metadata associated with the SCL file (from rasterio).
        Returns (None, None) if the SCL file cannot be found or an error occurs.
    """
    extracted_path = ""
    cleanup_extracted_path = False

    try:
        if not os.path.exists(product_path):
            print(f"Error: Product path does not exist: {product_path}")
            return None, None

        if product_path.lower().endswith(".zip"):
            # Create a directory for extraction named after the zip file
            base_name = os.path.splitext(os.path.basename(product_path))[0]
            extracted_path = os.path.join(os.path.dirname(product_path), base_name + "_extracted")
            
            if not os.path.exists(extracted_path):
                os.makedirs(extracted_path, exist_ok=True)
                print(f"Extracting {product_path} to {extracted_path}...")
                with zipfile.ZipFile(product_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)
                print("Extraction complete.")
                cleanup_extracted_path = True # Mark for potential cleanup if we created it
            else:
                print(f"Using existing extracted directory: {extracted_path}")
            
            # The actual .SAFE directory is usually inside this extracted folder
            # Look for the first .SAFE directory within the extracted path
            safe_dirs = glob.glob(os.path.join(extracted_path, '*.SAFE'))
            if not safe_dirs:
                print(f"Error: No .SAFE directory found in {extracted_path}")
                # Attempt to search from the root of extracted_path if no .SAFE found directly
                product_root_path = extracted_path 
            else:
                product_root_path = safe_dirs[0] # Use the first .SAFE dir found
        
        elif os.path.isdir(product_path) and product_path.lower().endswith(".safe"):
            product_root_path = product_path
        else:
            print(f"Error: Invalid product_path. It must be a .zip file or a .SAFE directory. Path: {product_path}")
            return None, None

        print(f"Searching for SCL file in: {product_root_path}")

        # Search for the SCL file
        # Common patterns: Txxxxx_YYYYMMDDTHHMMSS_SCL_20m.jp2 or similar within GRANULE/*/IMG_DATA/R20m/ or R60m/
        scl_file_patterns = [
            os.path.join(product_root_path, '**', '*_SCL_20m.jp2'), # L2A products typically have 20m SCL
            os.path.join(product_root_path, '**', '*_SCL_60m.jp2'), # Some products might have it at 60m
            os.path.join(product_root_path, '**', '*_SCL_*.jp2')    # Generic SCL file
        ]
        
        scl_file_path = None
        for pattern in scl_file_patterns:
            scl_files = glob.glob(pattern, recursive=True)
            if scl_files:
                scl_file_path = scl_files[0] # Take the first match
                print(f"Found SCL file: {scl_file_path}")
                break
        
        if not scl_file_path:
            print(f"Error: SCL file not found in {product_root_path} using patterns: {scl_file_patterns}")
            return None, None

        # Open the SCL file with rasterio and read the data
        with rasterio.open(scl_file_path) as src:
            scl_data = src.read(1)  # Read the first band
            scl_meta = src.meta.copy()
            
            # Update metadata if needed (e.g., ensure dtype is appropriate)
            scl_meta.update({
                "driver": "GTiff", # Often good to save as GeoTIFF if further processing
                "count": 1,
                "dtype": scl_data.dtype 
            })

        print(f"Successfully read SCL data from {scl_file_path}. Shape: {scl_data.shape}")
        return scl_data, scl_meta

    except Exception as e:
        print(f"An error occurred in generate_scene_classification_map: {e}")
        return None, None
    finally:
        # Optional: Cleanup the extracted directory if we created it and if it's desired.
        # For now, we'll leave it for inspection, but in a pipeline, you might want to remove it.
        # if cleanup_extracted_path and os.path.exists(extracted_path):
        #     print(f"Cleaning up extracted directory: {extracted_path}")
        #     import shutil
        #     shutil.rmtree(extracted_path)
        pass


if __name__ == '__main__':
    # This block is for example usage and testing.
    # You would need a sample Sentinel product (.zip or .SAFE folder) to test this.
    # For instance:
    # product_zip_path = "/path/to/your/S2A_MSIL2A_20230101TXXXXXX_NXXXX_RXXX_TXXXXX_20230101TXXXXXX.zip"
    # product_safe_path = "/path/to/your/S2A_MSIL2A_20230101TXXXXXX_NXXXX_RXXX_TXXXXX_20230101TXXXXXX.SAFE"

    # print("Testing with a dummy (non-existent) product path:")
    # data, meta = generate_scene_classification_map("dummy_product.zip")
    # if data is not None:
    #     print("SCL Data Max Value:", np.max(data))
    #     print("SCL Metadata:", meta)
    # else:
    #     print("Failed to process dummy product.")
    
    # To test this properly, you would need to:
    # 1. Download a Sentinel-2 L2A product.
    # 2. Update the `product_zip_path` or `product_safe_path` variable above.
    # 3. Run this script.
    
    # Example (requires a file to exist at the path):
    # test_safe_path = "./sample_data/S2A_MSIL2A_20230105T100351_N0509_R122_T32TQP_20230105T120730.SAFE"
    # if os.path.exists(test_safe_path):
    #     print(f"\nTesting with local SAFE product: {test_safe_path}")
    #     scl_array, scl_metadata = generate_scene_classification_map(test_safe_path)
    #     if scl_array is not None and scl_metadata is not None:
    #         print(f"SCL array shape: {scl_array.shape}, SCL metadata: {scl_metadata}")
    #     else:
    #         print("Could not process the SAFE product.")
    # else:
    #     print(f"Test SAFE product not found at {test_safe_path}, skipping example run.")
    pass
