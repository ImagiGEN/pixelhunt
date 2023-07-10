import glob
import os
import io
import json
from utils import azure
import PIL.Image as Image


JSON_DIR = os.path.join(os.environ.get("DATA_DIR"), "json")
IMAGES_DIR = os.path.join(os.environ.get("DATA_DIR"), "fashion")

glob.glob(JSON_DIR + "/*.json")

def _read_all_images():
    image_files = glob.glob(IMAGES_DIR + "/*")

    print("Directory of images:", IMAGES_DIR)
    print("Total number of catalog images =", "{:,}".format(len(image_files)))
    return image_files

def _get_image_analysis(image_file):
    result = azure.describe_image_with_AzureCV4(image_file)
    return result