import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Home Page",
    page_icon="👋",
)

st.title("Image Processing with Azure CV")

st.markdown(
    """
    Application for searching through apparels image database using image and prompt search.
"""
)

# Run the app
# streamlit run main.py