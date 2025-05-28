# Sentinel Imagery Downloader and Scene Classifier

## Overview

This project provides a command-line tool to download Sentinel-2 imagery for a specified Area of Interest (AOI) and time range. It then processes the downloaded imagery to generate a Scene Classification Layer (SCL) map and saves this map as a PNG image.

## Features

*   **Download Sentinel-2 Imagery**: Fetches Level-2A (S2MSI2A) products from the Copernicus Open Access Hub.
*   **Scene Classification Map Generation**: Extracts the SCL band from the downloaded product.
*   **Visualization**: Creates and saves a color-coded PNG image of the SCL map, with a legend detailing the different land cover/atmospheric classes.
*   **Customizable**: Allows users to specify AOI, date range, cloud cover, and output paths via command-line arguments.

## Setup

1.  **Clone the Repository (Optional)**
    If you haven't already, clone the repository to your local machine:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Virtual Environment (Recommended)**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    Install the required Python libraries using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Credentials

To download Sentinel imagery, you need an active account for the [Copernicus Open Access Hub](https://scihub.copernicus.eu/dhus/#/home).
You will need to provide your **username** and **password** as command-line arguments when running the script.

## Usage

The main script for this project is `main.py`. It is executed from the command line.

```bash
python main.py [ARGUMENTS]
```

### Command-Line Arguments

Below is a detailed explanation of all available command-line arguments:

*   `--user YOUR_USERNAME`
    *   **Required**. Your username for the Copernicus Open Access Hub.
*   `--password YOUR_PASSWORD`
    *   **Required**. Your password for the Copernicus Open Access Hub.
*   `--footprint "WKT_STRING"`
    *   **Required**. The Well-Known Text (WKT) string defining your Area of Interest (AOI).
    *   Example: `"POLYGON((5.0 52.0, 5.1 52.0, 5.1 52.1, 5.0 52.1, 5.0 52.0))"`
*   `--date_start YYYYMMDD`
    *   **Required**. The start date for your imagery search, in 'YYYYMMDD' format.
    *   Example: `20231001`
*   `--date_end YYYYMMDD`
    *   **Required**. The end date for your imagery search, in 'YYYYMMDD' format.
    *   Example: `20231010`
*   `--cloud_cover MAX_PERCENTAGE`
    *   Optional. Maximum cloud cover percentage allowed for the imagery. The script searches for imagery with cloud cover between 0% and this value.
    *   Default: `30` (meaning 0-30% cloud cover).
    *   Example: `20`
*   `--download_path ./path/to/downloads`
    *   Optional. Directory where the downloaded Sentinel product(s) (usually .zip or .SAFE files) will be saved.
    *   Default: `./sentinel_downloads`
*   `--output_viz_path ./path/to/image.png`
    *   Optional. Full path, including filename and extension (e.g., `.png`), where the generated SCL map visualization will be saved.
    *   Default: `./scl_visualization.png`

### Example Command

```bash
python main.py \
    --user "your_copernicus_username" \
    --password "your_copernicus_password" \
    --footprint "POLYGON((5.0 52.0, 5.1 52.0, 5.1 52.1, 5.0 52.1, 5.0 52.0))" \
    --date_start 20230101 \
    --date_end 20230115 \
    --cloud_cover 10 \
    --download_path "./my_sentinel_images" \
    --output_viz_path "./my_scl_map.png"
```
**Note:** Replace placeholder values (like `"your_copernicus_username"`, WKT coordinates, and dates) with your actual information.

## Output

The script will produce the following:

1.  **Downloaded Sentinel Product**: A Sentinel-2 product file (typically a `.zip` archive containing a `.SAFE` directory structure) saved in the directory specified by `--download_path`.
2.  **SCL Map Image**: A PNG image visualizing the Scene Classification Layer of the downloaded product, saved to the path specified by `--output_viz_path`. This image includes a legend for the different SCL classes.

## Modules

This project consists of the following Python scripts:

*   `main.py`: The main executable script that orchestrates the entire workflow, handling command-line arguments and calling other modules.
*   `sentinel_downloader.py`: Contains the `download_sentinel_imagery` function responsible for querying and downloading Sentinel-2 products from the Copernicus Hub.
*   `scene_classifier.py`: Contains the `generate_scene_classification_map` function, which extracts and processes the SCL data from a downloaded Sentinel product.
*   `visualizer.py`: Contains the `visualize_scl_map` function used to create and save a PNG image of the SCL map with appropriate colors and a legend.
*   `requirements.txt`: A text file listing all Python dependencies required for the project. This allows for easy installation of prerequisites using `pip`.
