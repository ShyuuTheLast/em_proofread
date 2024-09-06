import numpy as np
from generate_html import HtmlGenerator


if __name__ == "__main__":
    Do = "./test/"
    color_labels = ["DV", "CV", "DVH"]
    # 50 images
    image_paths = [
        [f"data/cifar10/1_{x}.png"]
        for x in range(1, 11)
    ] * 5
    image_labels = np.random.randint(0, len(color_labels), len(image_paths))

    num_user = 1  # number of users
    num_per_page = 100  # number of images per page

    html = HtmlGenerator(Do, num_user=num_user, num_per_page=num_per_page)
    html.create_html(image_paths, image_labels, color_labels)
