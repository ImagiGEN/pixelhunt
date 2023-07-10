import streamlit as st
from utils import analysis

@st.cache_data
def get_image_files():
    image_files = analysis._read_all_images()
    return image_files

def get_analysis():
    result = analysis._get_image_analysis(selected_image)
    return result
    
st.title('Image Analysis')

image_files = get_image_files()

selected_image = st.selectbox("Select image", image_files)

if selected_image:
    st.image(selected_image, width=250)

if st.button("Analyze"):
    analysis = get_analysis()
    st.write(analysis)
