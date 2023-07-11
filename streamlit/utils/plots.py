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