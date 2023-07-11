import streamlit as st
from utils import cluster
import numpy as np


st.title('Image Search')

def display_image_grid(images):
    pass

@st.cache_data
def search_images():
    df=cluster.cluster_images()
    return df

df_clusters = search_images()
selected_cluster = st.selectbox("Select cluster", df_clusters['cluster_label'].unique())

top_n = st.number_input('How many images per cluster?', min_value=3, max_value=60)

grid_width = 3

# Get list of clusters in DataFrame
clusters = df_clusters["cluster"].unique()
cols = st.columns(grid_width)
# Sorted list
cluster_rows = df_clusters[df_clusters["cluster_label"] == selected_cluster].head(top_n)
view_images= cluster_rows['image_file']
# Display the images in a single row
groups = []
for i in range(0, len(view_images), grid_width):
    groups.append(view_images[i:i+grid_width])

cols = st.columns(grid_width)
for group in groups:
    for i, image_details in enumerate(group):
        cols[i].image(image_details)
