import streamlit as st
from utils import search

st.title('Query Transcripts')

def display_image_grid(images):
    pass

search_by = st.selectbox(label='Search by', options=["", "Image", "Prompt"])

if search_by == "Image":
    file = st.file_uploader("Upload an image", type=["png", "jpg"])
    
if search_by == "Prompt":
    prompt = st.text_input('Enter a prompt')

if st.button("Search"):
    with st.spinner(text="Loading..."):
        if prompt:
            df = search.get_similar_images_using_prompt(prompt)
        else:
            df = search.get_similar_images_using_image(file)
        st.write(df)