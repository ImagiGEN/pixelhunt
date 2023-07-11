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

if st.button("Search"):
    
# Get list of clusters in DataFrame
    clusters = df_clusters["cluster"].unique()
    cols = st.columns(grid_width)
# Sorted list
    clusters = np.sort(clusters)

# Create figure with subplots
    num_rows = len(clusters)

    cluster_rows = df_clusters[df_clusters["cluster_label"] == selected_cluster].head(top_n)
    view_images= cluster_rows['image_file']
# Display the images in a single row
    # for j, row in enumerate(cluster_rows.itertuples(index=False)):
    #     cols[0].write(f"Cluster: {row.cluster_label}")
    #     cols[0].image(row.image_file)
    st.write(view_images)
    groups = []
    for i in range(0, len(view_images), grid_width):
        groups.append(view_images[i:i+grid_width])
    
    cols = st.columns(grid_width)
    count = 0
    for group in groups:
        for i, image_details in enumerate(group):
            count += 1
            # cols[i].write(f"Top {count}")
            # cols[i].write(f"Score: {image_details[1]}")
            cols[i].image(image_details)
    