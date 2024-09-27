import numpy as np
import glob
import re
import os
import h5py
from generate_html import HtmlGenerator

# Function to extract numbers from a string
def extract_number(string):
    numbers = re.findall(r'\d+', string)  # Find all numeric substrings
    return int(numbers[-1]) if numbers else -1  # Return the last number if found, otherwise return -1

def get_image_paths_from_folder(folder_dir):
    # Get all .png files in the folder and subfolders
    image_paths = glob.glob(os.path.join(folder_dir, '**', '*.png'), recursive=True)

    # Sort image paths numerically based on the number in the filename
    image_paths.sort(key=extract_number)

    # Convert backslashes to forward slashes for HTML compatibility and add '../../' before the path
    image_paths = [['../../../' + path.replace('\\', '/')] for path in image_paths]

    return image_paths

if __name__ == "__main__":
    # Main input folder containing subfolders (CV, DV, DVH)
    input_folder = "data/testing_predictions"
    output_folder = "./hydra_testing/"
    color_labels = ["undefined", "CV", "DV", "DVH"]
    pred_file_name = "testing_results"

    # Get all subfolders (CV, DV, DVH)
    subfolders = [f.path for f in os.scandir(input_folder) if f.is_dir()]

    num_user = 1  # number of users
    num_per_page = 100  # number of images per page

    # Loop through each subfolder (CV, DV, DVH)
    for subfolder in subfolders:
        # Get the name of the subfolder (e.g., CV, DV, DVH)
        category = os.path.basename(subfolder)

        # Generate the image paths from the subfolder
        image_paths = get_image_paths_from_folder(subfolder)

        # Construct the HDF5 label file name with category behind pred_file_name
        label_file = os.path.join(subfolder, f'{pred_file_name}_{category}.h5')

        # Open the HDF5 file to get image labels
        dataset_name = "main"
        with h5py.File(label_file, 'r') as f:
            image_labels = np.array(f[dataset_name])

        # Create output subfolder within the main output folder
        category_output_folder = os.path.join(output_folder, category)
        os.makedirs(category_output_folder, exist_ok=True)

        # Generate HTML for this category using HtmlGenerator
        html = HtmlGenerator(category_output_folder, num_user=num_user, num_per_page=num_per_page, num_column=2)
        html.create_html(image_paths, image_labels, color_labels)