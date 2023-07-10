import datetime
import glob
import json
from multiprocessing.pool import Pool
import multiprocessing
import os
import time
import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from PIL import Image
from tqdm import tqdm
from dotenv import load_dotenv
from utils import azure
load_dotenv("azure.env")
import requests
import wget
import zipfile
from airflow.models.baseoperator import chain
import requests, zipfile, io
from concurrent.futures import ThreadPoolExecutor

key = os.environ.get("azure_cv_key")
endpoint = os.environ.get("azure_cv_endpoint")
DATA_DIR = os.environ.get("DATA_DIR")
IMAGE_DIR = os.path.join(DATA_DIR, "fashion")
JSON_DIR = os.path.join(DATA_DIR, "json")
DATA_SOURCE=os.environ.get("DATA_SOURCE", 'https://www.dropbox.com/s/f5983zo3etaqap9/fashion_samples.zip')
pyfile = "azure.py"

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2023, 6, 19),
}

dag = DAG('compute_vector_embeddings', default_args=default_args, schedule_interval=None)

def fetch_images():
    import os
    print("Mkdirs:", os.system(f"mkdir -p {DATA_DIR}"))
    print("Mkdirs:", os.system(f"mkdir -p {JSON_DIR}"))
    print("Wget:", os.system(f"wget  -P {DATA_DIR} {DATA_SOURCE}"))
    print("Unzip:", os.system(f"unzip {os.path.join(DATA_DIR, 'fashion_samples.zip')} -d {DATA_DIR}"))

def process_image(image_file, max_retries=20):
    """
    Process image with error management
    """
    num_retries = 0

    while num_retries < max_retries:
        try:
            embedding, response = azure.image_embedding_batch(image_file)

            if response.status_code == 200:
                return embedding

            else:
                num_retries += 1
                print(
                    f"Error processing {image_file}: {response.status_code}.\
                Retrying... (attempt {num_retries} of {max_retries})"
                )

        except Exception as e:
            print(f"An error occurred while processing {image_file}: {e}")
            print(f"Retrying... (attempt {num_retries} of {max_retries})")
            num_retries += 1

    return None

def process_all_images(image_files, max_workers, max_retries):
    """
    Running the full process using pool
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        embeddings = list(
            tqdm(
                executor.map(lambda x: process_image(x, max_retries), image_files),
                total=len(image_files),
            )
        )

    return [emb for emb in embeddings if emb is not None]

def compute_vector_embeddings():
    IMAGE_PATH=os.path.join(IMAGE_DIR, '039*.jpg')
    image_files = glob.glob(IMAGE_PATH)
    print("image_files:")
    print(image_files)
    num_cores = multiprocessing.cpu_count()

    print("Number of CPU cores =", num_cores)

    print(
        datetime.datetime.today().strftime("%d-%b-%Y %H:%M:%S"),
        "Starting to compute vector embeddings for our",
        "{:,}".format(len(image_files)),
        "catalog images...",
    )
    start = time.time()

    # Running the images vector embeddings for all the images files
    list_emb = process_all_images(image_files, 4, 20)

    # End of job
    print(datetime.datetime.today().strftime("%d-%b-%Y %H:%M:%S"), "Done")
    elapsed = time.time() - start
    print(f"\nElapsed time: {int(elapsed / 60)} minutes, {int(elapsed % 60)} seconds")
    print("Number of processed images =", len(list_emb))
    # print(f"Processing time per image = {(elapsed / len(list_emb)):.5f} sec")

    print(f"Number of images files = {len(image_files)}")
    print(f"Number of vectors embeddings = {len(list_emb)}")

    

    os.makedirs(JSON_DIR, exist_ok=True)

    print("Exporting images vector embeddings")

    # Json filename
    current_dt = str(datetime.datetime.today().strftime("%d%b%Y_%H%M%S"))
    json_file = os.path.join(JSON_DIR, f"img_embed_{current_dt}.json")

    # Saving vectors embeddings into this Json file
    with open(json_file, "w") as f:
        json.dump(list_emb, f)

    print("Done. Vector embeddings have been saved in:", json_file)


with dag:
    fetch_data_task = PythonOperator(
        task_id='fetch_images',
        python_callable=fetch_images
    )
    compute_vector_embeddings_task = PythonOperator(
        task_id='compute_vector_embeddings',
        python_callable=compute_vector_embeddings,
        dag=dag,
    )
    chain(fetch_data_task, compute_vector_embeddings_task)
