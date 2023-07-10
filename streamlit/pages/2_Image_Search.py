import streamlit as st
from utils import search

st.title('Image Search')

def display_image_grid(images):
    pass

def search_images():
    if search_by == "Prompt":
        df = search.get_similar_images_using_prompt(prompt)
    else:
        df = search.get_similar_images_using_image(file)
    return df

top_n = st.number_input('How many relavant images?', min_value=3, max_value=60)

search_by = st.selectbox(label='Search by', options=["", "Image", "Prompt"])

if search_by == "Image":
    file = st.file_uploader("Upload an image", type=["png", "jpg"])
    
if search_by == "Prompt":
    prompt = st.text_input('Enter a prompt')

grid_width = 3

if st.button("Search"):
    with st.spinner(text="Loading..."):
        df = search_images()
    view_images = []    
    for index, row in df.head(top_n).iterrows():
        view_images.append((row["image_file"], row["similarity"]))

    groups = []
    for i in range(0, len(view_images), grid_width):
        groups.append(view_images[i:i+grid_width])
    
    cols = st.columns(grid_width)
    count = 0
    for group in groups:
        for i, image_details in enumerate(group):
            count += 1
            cols[i].write(f"Top {count}")
            cols[i].write(f"Score: {image_details[1]}")
            cols[i].image(image_details[0])
        
