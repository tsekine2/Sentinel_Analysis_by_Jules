import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np

# Define SCL classes and their visual properties
SCL_CLASSES = {
    0: ('No Data', 'black'),
    1: ('Saturated or Defective', 'red'),
    2: ('Dark Area Pixels', 'dimgray'), # Or a very dark gray
    3: ('Cloud Shadows', 'saddlebrown'), # Or a distinct brown
    4: ('Vegetation', 'green'),
    5: ('Not Vegetated', 'darkkhaki'), # Or 'tan'
    6: ('Water', 'blue'),
    7: ('Unclassified', 'gray'),
    8: ('Cloud Medium Probability', 'lightgray'),
    9: ('Cloud High Probability', 'whitesmoke'), # Almost white, but not pure white for visibility
    10: ('Thin Cirrus', 'cyan'),
    11: ('Snow / Ice', 'mediumpurple') # Or 'fuchsia' or 'darkviolet'
}

def visualize_scl_map(scl_data, scl_meta=None, output_image_path=None):
    """
    Visualizes a Sentinel-2 Scene Classification Layer (SCL) map.

    Args:
        scl_data (numpy.ndarray): The SCL data array (e.g., as returned by 
                                  `generate_scene_classification_map`).
        scl_meta (dict, optional): Metadata associated with the SCL data. 
                                   Currently not used for extent but can be in future.
        output_image_path (str, optional): Path to save the visualization image. 
                                           If None, the plot is displayed interactively.
    """
    if not isinstance(scl_data, np.ndarray):
        print("Error: scl_data must be a NumPy array.")
        return

    # Prepare colormap and legend
    # Ensure classes are sorted by their key for consistent color mapping
    sorted_classes = sorted(SCL_CLASSES.items())
    
    class_ids = [item[0] for item in sorted_classes]
    class_labels = [item[1][0] for item in sorted_classes]
    colors = [item[1][1] for item in sorted_classes]

    # Create a ListedColormap
    # BoundaryNorm ensures that the colors are mapped correctly to the discrete SCL values
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(np.arange(-0.5, len(colors)), cmap.N) # Centering bins around integers

    # Create legend patches
    patches = [mpatches.Patch(color=colors[i], label=f"{class_ids[i]}: {class_labels[i]}") 
               for i in range(len(colors))]

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10)) # Adjust size as needed
    
    # Display the SCL data
    # Using norm with imshow ensures correct color mapping for discrete integer values
    im = ax.imshow(scl_data, cmap=cmap, norm=norm, interpolation='none')

    ax.set_title("Scene Classification Map (SCL)", fontsize=15)
    ax.set_xlabel("Pixel Column")
    ax.set_ylabel("Pixel Row")

    # Add legend
    # Place legend outside the plot to avoid obscuring data
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., title="SCL Classes")

    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for the legend

    # Save or show the plot
    if output_image_path:
        try:
            plt.savefig(output_image_path, bbox_inches='tight')
            print(f"SCL map saved to {output_image_path}")
        except Exception as e:
            print(f"Error saving SCL map: {e}")
    else:
        plt.show()

    plt.close(fig) # Close the figure after saving/showing to free memory


if __name__ == '__main__':
    print("Running example visualization...")

    # Create dummy SCL data (e.g., 100x100 pixels)
    # This will create a gradient-like pattern for demonstration
    dummy_scl_array = np.zeros((100, 100), dtype=np.uint8)
    for i in range(12): # Number of SCL classes
        row_start = i * 8
        row_end = (i + 1) * 8
        if row_end > 100:
            row_end = 100
        if row_start < 100:
            dummy_scl_array[row_start:row_end, :] = i
    
    # Add some specific class blocks for better visual variety
    dummy_scl_array[20:40, 20:40] = SCL_CLASSES_KEYS['Vegetation'] # Vegetation
    dummy_scl_array[50:70, 50:70] = SCL_CLASSES_KEYS['Water']      # Water
    dummy_scl_array[80:95, 10:30] = SCL_CLASSES_KEYS['Cloud High Probability'] # Cloud High Prob

    # Create dummy metadata (optional, not heavily used in current viz)
    dummy_scl_meta = {
        'driver': 'GTiff',
        'dtype': 'uint8',
        'nodata': None,
        'width': 100,
        'height': 100,
        'count': 1,
        # transform and crs would typically be here
    }

    # Test 1: Display interactively
    print("\nDisplaying SCL map interactively (close window to continue)...")
    # To avoid issues in environments without a display, this might be commented out
    # or conditionalized if there's a way to check for display availability.
    # For now, we assume a display is available for testing.
    # visualize_scl_map(dummy_scl_array, dummy_scl_meta)


    # Test 2: Save to file
    output_file = "dummy_scl_map.png"
    print(f"\nSaving SCL map to {output_file}...")
    visualize_scl_map(dummy_scl_array, dummy_scl_meta, output_image_path=output_file)
    print(f"Please check for the file '{output_file}' in the current directory.")

    # Example with a more random SCL map
    random_scl_data = np.random.randint(0, 12, size=(150, 150), dtype=np.uint8)
    output_file_random = "dummy_scl_map_random.png"
    print(f"\nSaving random SCL map to {output_file_random}...")
    visualize_scl_map(random_scl_data, None, output_image_path=output_file_random)
    print(f"Please check for the file '{output_file_random}' in the current directory.")

    # For the dummy data, let's make SCL_CLASSES_KEYS accessible for the example
SCL_CLASSES_KEYS = {info[0]: val for val, info in SCL_CLASSES.items()}
# Re-run the part of __main__ that uses SCL_CLASSES_KEYS after its definition
if __name__ == '__main__':
    dummy_scl_array = np.zeros((100, 100), dtype=np.uint8)
    for i in range(12): # Number of SCL classes
        row_start = i * 8
        row_end = (i + 1) * 8
        if row_end > 100: row_end = 100
        if row_start < 100: dummy_scl_array[row_start:row_end, :] = i
    
    dummy_scl_array[20:40, 20:40] = SCL_CLASSES_KEYS['Vegetation']
    dummy_scl_array[50:70, 50:70] = SCL_CLASSES_KEYS['Water']
    dummy_scl_array[80:95, 10:30] = SCL_CLASSES_KEYS['Cloud High Probability']

    output_file_updated_dummy = "dummy_scl_map_specific_classes.png"
    print(f"\nSaving SCL map with specific classes to {output_file_updated_dummy}...")
    visualize_scl_map(dummy_scl_array, None, output_image_path=output_file_updated_dummy)
    print(f"Please check for the file '{output_file_updated_dummy}'.")

    # Interactive display call (can be uncommented for local testing)
    # print("\nDisplaying SCL map with specific classes interactively (close window to continue)...")
    # visualize_scl_map(dummy_scl_array, None)
