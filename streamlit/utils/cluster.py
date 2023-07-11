import glob
import os
import io
import json
from utils import azure
import PIL.Image as Image
from sklearn.cluster import KMeans
import pandas as pd


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

def cluster_images(nb_clusters=17):
    list_emb = _import_embeddings()
    image_files = _read_all_images()
    kmeans = KMeans(n_clusters=nb_clusters, 
                random_state=123456)

    kmeans.fit(list_emb)
    labels = kmeans.labels_
    print("Cluster labels:\n", labels)
    df_clusters = pd.DataFrame({"image_file": image_files, "vector": list_emb, "cluster": labels})
    cluster_labels = [
        "0", "Accessories",
        "1", "Women clothes",
        "2", "Women Sweatshirts",
        "3", "Baby clothes",
        "4", "Printed Tshirts",
        "5", "Trousers",
        "6", "Shoes",
        "7", "Full sleeved Tshirts",
        "8", "Sweatshirts",
        "9", "Coats",
        "10", "Fancy Clothes",
        "11", "Lingerie",
        "12", "Shorts",
        "13", "Trousers",
        "14", "Women's Tshirts",
        "15", "Dresses",
        "16", "Jumpers",
    ]
    cluster_ids = [int(cluster_labels[i]) for i in range(0, len(cluster_labels), 2)]
    category_names = [cluster_labels[i + 1] for i in range(0, len(cluster_labels), 2)]

    cluster_ids_series = pd.Series(cluster_ids, name="cluster")
    cluster_names_series = pd.Series(category_names, name="cluster_label")
    cluster_labels_df = pd.concat([cluster_ids_series, cluster_names_series], axis=1)
    df_results = pd.merge(df_clusters, cluster_labels_df, on="cluster", how="left")
    # Adding 1 to avoid the number 0
    df_results["cluster"] = df_results["cluster"].apply(lambda x: int(x) + 1)
    # Numbers in 2 characters
    df_results["cluster"] = df_results["cluster"].apply(
        lambda x: f"0{x}" if int(x) < 10 else x
    )
    #  Adding some text
    df_results["cluster"] = df_results["cluster"].astype(str)
    df_results["Cluster and Label"] = (
        "Cluster " + df_results["cluster"] + " = " + df_results["cluster_label"]
    )
    return df_results