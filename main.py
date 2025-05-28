import argparse
import os

# Attempt to import project-specific modules
try:
    from sentinel_downloader import download_sentinel_imagery
    from scene_classifier import generate_scene_classification_map
    from visualizer import visualize_scl_map
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure sentinel_downloader.py, scene_classifier.py, and visualizer.py are in the same directory or accessible in PYTHONPATH.")
    exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download Sentinel-2 imagery, generate SCL map, and visualize it.")

    # Copernicus Hub Credentials
    parser.add_argument("--user", type=str, required=True, help="Username for Copernicus Open Access Hub.")
    parser.add_argument("--password", type=str, required=True, help="Password for Copernicus Open Access Hub.")

    # AOI and Date Range
    parser.add_argument("--footprint", type=str, required=True,
                        help="Well-Known Text (WKT) string defining the Area of Interest (AOI). "
                             "Example: 'POLYGON((lon1 lat1, lon2 lat2, lon3 lat3, lon1 lat1))'")
    parser.add_argument("--date_start", type=str, required=True,
                        help="Start date for imagery search (format: YYYYMMDD).")
    parser.add_argument("--date_end", type=str, required=True,
                        help="End date for imagery search (format: YYYYMMDD).")

    # Search and Download Parameters
    parser.add_argument("--cloud_cover", type=int, default=30,
                        help="Maximum cloud cover percentage (0-100). Default: 30 (meaning 0-30%%).")
    parser.add_argument("--download_path", type=str, default="./sentinel_downloads",
                        help="Directory to save downloaded Sentinel products. Default: './sentinel_downloads'.")

    # Visualization Parameters
    parser.add_argument("--output_viz_path", type=str, default="./scl_visualization.png",
                        help="Path to save the visualized SCL map image (e.g., 'map.png'). "
                             "If not provided, the script will attempt to display interactively. Default: './scl_visualization.png'.")
    
    args = parser.parse_args()

    # Create download directory if it doesn't exist
    if not os.path.exists(args.download_path):
        os.makedirs(args.download_path, exist_ok=True)
        print(f"Created download directory: {args.download_path}")

    print("Step 1: Downloading Sentinel imagery...")
    downloaded_product_path = download_sentinel_imagery(
        user=args.user,
        password=args.password,
        footprint=args.footprint,
        date_start=args.date_start,
        date_end=args.date_end,
        cloud_cover_percentage=(0, args.cloud_cover), # Sentinelsat expects a tuple
        output_path=args.download_path
    )

    if downloaded_product_path:
        print(f"Successfully downloaded product to: {downloaded_product_path}")
        print("\nStep 2: Generating Scene Classification (SCL) map...")
        
        scl_data, scl_meta = generate_scene_classification_map(product_path=downloaded_product_path)

        if scl_data is not None and scl_meta is not None:
            print("Successfully generated SCL map data.")
            print(f"SCL data shape: {scl_data.shape}, Metadata keys: {scl_meta.keys()}")
            
            print("\nStep 3: Visualizing SCL map...")
            visualize_scl_map(
                scl_data=scl_data,
                scl_meta=scl_meta,
                output_image_path=args.output_viz_path  # Will save if path is provided, else show
            )
            if args.output_viz_path:
                 print(f"Visualization saved to {args.output_viz_path}")
            else:
                print("Visualization displayed interactively.")
            
            print("\nProcessing complete.")

        else:
            print("Failed to generate SCL map.")
            print("Please check the logs from scene_classifier.py for more details.")
    else:
        print("Failed to download Sentinel imagery.")
        print("Please check your credentials, AOI, date range, and logs from sentinel_downloader.py.")

if __name__ == '__main__':
    # Note: To run this script, you need to provide actual Copernicus Hub credentials
    # and a valid WKT footprint.
    # Example command (replace placeholders with actual values):
    # python main.py --user YOUR_USER --password YOUR_PASSWORD \
    # --footprint "POLYGON((5.0 52.0, 5.1 52.0, 5.1 52.1, 5.0 52.1, 5.0 52.0))" \
    # --date_start "20231001" --date_end "20231010" \
    # --cloud_cover 20 \
    # --download_path "./my_sentinel_data" \
    # --output_viz_path "./my_scl_map.png"

    # Due to the lack of live credentials in this environment, the script
    # cannot be fully executed here. The main() function is called to ensure
    # it's syntactically correct and follows the logic.
    main()
