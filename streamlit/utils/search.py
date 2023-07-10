import glob
import os
import io
import json
from utils import azure
import PIL.Image as Image


JSON_DIR = os.path.join(os.environ.get("DATA_DIR"), "json")
IMAGES_DIR = os.path.join(os.environ.get("DATA_DIR"), "fashion")

glob.glob(JSON_DIR + "/*.json")

def _import_embeddings():
    print("Importing vectors embeddings...")

    jsonfiles = [entry.name for entry in os.scandir(JSON_DIR) if entry.is_file()]
    jsonfiles = [f for f in jsonfiles if os.path.isfile(os.path.join(JSON_DIR, f))]

    # Get the most recent file
    modification_times = [
        (f, os.path.getmtime(os.path.join(JSON_DIR, f))) for f in jsonfiles
    ]
    modification_times.sort(key=lambda x: x[1], reverse=True)
    most_recent_file = JSON_DIR + "/" + modification_times[0][0]

    # Loading the most recent file
    print(f"Loading the most recent file of the vector embeddings: {most_recent_file}")

    with open(most_recent_file) as f:
        list_emb = json.load(f)

    print(f"\nDone: number of imported vector embeddings = {len(list_emb):,}")
    return list_emb

def _read_all_images():
    image_files = glob.glob(IMAGES_DIR + "/*")

    print("Directory of images:", IMAGES_DIR)
    print("Total number of catalog images =", "{:,}".format(len(image_files)))
    return image_files

def get_similar_images_using_image(reference_image, topn=6):
    image = Image.open(reference_image)
    image.save("/tmp/reference_image.jpg")
    reference_image = "/tmp/reference_image.jpg"
    list_emb = _import_embeddings()
    image_files = _read_all_images()
    nobackground_image = azure.remove_background(reference_image)
    df = azure.get_results_using_image(
        reference_image, nobackground_image, image_files, list_emb, topn=topn, disp=False
    )
    return df

def get_similar_images_using_prompt(prompt, topn=6):
    list_emb = _import_embeddings()
    image_files = _read_all_images()
    df = azure.get_results_using_prompt(prompt, image_files, list_emb, topn, disp=False)
    return df