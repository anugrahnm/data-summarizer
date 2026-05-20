import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

uploaded_file = st.file_uploader("Choose a file")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/summarize/")

print(type(uploaded_file))
if uploaded_file is not None:
    if st.button("Generate Summary"):
        st.toast("File Uploaded!", icon="✅")
        with st.spinner("Summarizing...", show_time=True):
            files={"file":(uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(API_URL, files=files)
            try:
                st.success("Done!")
                st.markdown(response.json())
            except requests.JSONDecodeError as e:
                st.exception(e)
                print(str(e))
            except Exception as e:
                st.error(f"Something went wrong! Error details: {e}", icon="🚨")