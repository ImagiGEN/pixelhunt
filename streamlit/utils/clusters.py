import glob
import os
import io
import json
from utils import azure
import PIL.Image as Image
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd
from umap import UMAP
import plotly.express as px


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

def form_clusters(nb_clusters=17):
    list_emb = _import_embeddings()
    image_files = _read_all_images()
    kmeans = KMeans(n_clusters=nb_clusters, 
                    random_state=123456)

    kmeans.fit(list_emb)
    labels = kmeans.labels_

    print("Cluster labels:\n", labels)
    print("\nCluster centers:\n", kmeans.cluster_centers_)
    print("\nWithin-cluster sum of squares (inertia) =", kmeans.inertia_)

    df_clusters = pd.DataFrame(
        {"image_file": image_files, "vector": list_emb, "cluster": labels}
    )

    
    cluster_labels = _get_cluster_labels()
    cluster_ids = [int(cluster_labels[i]) for i in range(0, len(cluster_labels), 2)]
    category_names = [cluster_labels[i + 1] for i in range(0, len(cluster_labels), 2)]

    cluster_ids_series = pd.Series(cluster_ids, name="cluster")
    cluster_names_series = pd.Series(category_names, name="cluster_label")
    cluster_labels_df = pd.concat([cluster_ids_series, cluster_names_series], axis=1)
    df_results = pd.merge(df_clusters, cluster_labels_df, on="cluster", how="left")
    df_results["cluster"] = df_results["cluster"].astype(str)
    df_results["Cluster and Label"] = (
        "Cluster " + df_results["cluster"] + " = " + df_results["cluster_label"]
    )

    return df_results

def _get_cluster_labels():
    cluster_labels = [
        "0", "Shoes",
        "1", "Shorts",
        "2", "Woman clothes",
        "3", "Sheets",
        "4", "Colored Woman shirts",
        "5", "Woman T shirts",
        "6", "Accessories",
        "7", "Coats",
        "8", "Jumpers",
        "9", "Sportwear shirts",
        "10", "Lingerie",
        "11", "Colored shirts",
        "12", "Dresses",
        "13", "Trousers",
        "14", "Shirts",
        "15", "Glasses and caps",
        "16", "Fancy clothes",
    ]
    return cluster_labels

def _get_3d_umap():
    list_emb = _import_embeddings()
    print("Running Umap on the images vectors embeddings...")

    umap_3d = UMAP(n_components=3, init="random", random_state=0)
    proj_3d = umap_3d.fit_transform(list_emb)

    print("Done")
    return proj_3d

def get_3d_cluster_plot(df_results):
    proj_3d = _get_3d_umap()
    clusterlabel = df_results["cluster_label"].tolist()
    fig_3d = px.scatter_3d(
            proj_3d,
            x=0,
            y=1,
            z=2,
            color=clusterlabel,
            labels={"color": "Cluster"},
            custom_data=[df_results["image_file"].tolist(), df_results["Cluster and Label"].tolist()],
            title="Images Vectors Embeddings UMAP Projections",
            height=860,
        )
    return fig_3d

def get_cluster_freq_plot(df_results):
    ax = (
        df_results["Cluster and Label"]
        .value_counts()
        .plot(
            kind="barh",
            figsize=(10, 7),
            title="Number of images per cluster",
            color="purple",
        )
    )

    ax.set_xlabel("cluster")
    ax.set_ylabel("Frequency")
    return ax.figure