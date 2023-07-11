import streamlit as st
from utils import cluster as cluster_utils
from utils import plots

@st.cache_data
def get_image_clusters():
    df = cluster_utils.cluster_images()
    return df

def get_umap_figure():
    plot = plots.get_3d_cluster_plot(clusters)
    return plot
   
st.title('Inventory Analysis')

clusters = get_image_clusters()

grid_width = 3

data = clusters.groupby("Cluster and Label").count().drop(columns=["vector", "cluster", "cluster_label"]).rename(columns={"image_file":"Count"})
st.bar_chart(data=data)

# figure = cluster_utils.get_cluster_freq_plot(clusters)
# st.pyplot(fig=figure)

figure = get_umap_figure()
st.plotly_chart(figure, use_container_width=False, sharing="streamlit", theme="streamlit")
