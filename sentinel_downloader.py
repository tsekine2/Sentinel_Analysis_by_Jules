import os
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from collections import OrderedDict

def download_sentinel_imagery(user, password, footprint, date_start, date_end, cloud_cover_percentage, output_path='./sentinel_images'):
    """
    Downloads Sentinel-2 imagery for a given area of interest (AOI) and time range.

    Args:
        user (str): Username for Copernicus Open Access Hub.
        password (str): Password for Copernicus Open Access Hub.
        footprint (str): Well-Known Text (WKT) string defining the AOI.
        date_start (str): Start date for the imagery search (e.g., 'YYYYMMDD').
        date_end (str): End date for the imagery search (e.g., 'YYYYMMDD').
        cloud_cover_percentage (tuple): Maximum cloud cover percentage (e.g., (0, 30)).
        output_path (str, optional): Directory where the downloaded imagery should be saved.
                                     Defaults to './sentinel_images'.

    Returns:
        str or None: Path to the downloaded product, or None if no products were found or an error occurred.
    """
    try:
        # Initialize SentinelsatAPI
        api = SentinelAPI(user, password, 'https://apihub.copernicus.eu/apihub')

        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Construct query
        query_kwargs = {
            'platformname': 'Sentinel-2',
            'producttype': 'S2MSI2A',  # Level-2A products
            'date': (date_start, date_end),
            'cloudcoverpercentage': cloud_cover_percentage
        }

        # Execute query
        products = api.query(footprint, **query_kwargs)

        if products:
            # Convert products to an OrderedDict, sort by ingestiondate
            products_sorted = OrderedDict(sorted(products.items(), key=lambda x: x[1]['ingestiondate'], reverse=True))
            
            # Select the first product (most recent)
            product_id = list(products_sorted.keys())[0]
            product_info = products_sorted[product_id]

            print(f"Found product: {product_info['title']}")
            print(f"Ingestion date: {product_info['ingestiondate']}")
            print(f"Cloud cover: {product_info['cloudcoverpercentage']}%")

            # Download the product
            print(f"Downloading product {product_id}...")
            download_info = api.download(product_id, directory_path=output_path)
            
            # Check if download was successful and return path
            if download_info and 'path' in download_info and os.path.exists(download_info['path']):
                print(f"Product downloaded to: {download_info['path']}")
                return download_info['path']
            else:
                # This case might occur if the product is offline or other download issues
                print(f"Failed to download product {product_id}. Product might be offline or an error occurred.")
                # Attempt to download without checksum verification if it failed (common issue)
                print("Attempting download without checksum verification...")
                download_info_no_checksum = api.download(product_id, directory_path=output_path, checksum=False)
                if download_info_no_checksum and 'path' in download_info_no_checksum and os.path.exists(download_info_no_checksum['path']):
                    print(f"Product downloaded (without checksum) to: {download_info_no_checksum['path']}")
                    return download_info_no_checksum['path']
                else:
                    print(f"Download failed even without checksum for product {product_id}.")
                    return None

        else:
            print("No products found for the given criteria.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    # Example usage (replace with your actual credentials and parameters)
    # NOTE: This part is for testing and will require actual credentials and a valid WKT.
    # For the purpose of this task, this block will be commented out or removed before submission
    # if it cannot be tested in the environment.
    
    # user = "your_username"  # Replace with your Copernicus Hub username
    # password = "your_password"  # Replace with your Copernicus Hub password
    # wkt_footprint = "POLYGON((10.0 50.0, 10.0 50.5, 10.5 50.5, 10.5 50.0, 10.0 50.0))" # Example WKT
    # start_date = "20230101"
    # end_date = "20230110"
    # cloud_cover = (0, 10)
    # output_dir = "./downloaded_sentinel_images"

    # print(f"Attempting to download imagery for footprint: {wkt_footprint}")
    # print(f"Date range: {start_date} to {end_date}")
    # print(f"Max cloud cover: {cloud_cover[1]}%")
    
    # downloaded_file_path = download_sentinel_imagery(user, password, wkt_footprint, start_date, end_date, cloud_cover, output_dir)

    # if downloaded_file_path:
    #     print(f"Script finished. Downloaded file: {downloaded_file_path}")
    # else:
    #     print("Script finished. No file was downloaded.")
    pass
