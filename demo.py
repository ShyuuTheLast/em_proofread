import numpy as np
import glob
import re
import os
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
    image_paths = [['../../' + path.replace('\\', '/')] for path in image_paths]

    return image_paths

if __name__ == "__main__":
    output_folder = "./hydra_testing/"
    color_labels = ["undefined", "DV", "CV", "DVH"]

    folder_directory = "data/testing_predictions"
    image_paths = get_image_paths_from_folder(folder_directory)
    image_labels = np.random.randint(0, len(color_labels), len(image_paths))

    num_user = 1  # number of users
    num_per_page = 100  # number of images per page

    html = HtmlGenerator(output_folder, num_user=num_user, num_per_page=num_per_page, num_column = 2)
    html.create_html(image_paths, None, color_labels)
