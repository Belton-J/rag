# app.py

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("📄 RAG PDF QA App")

# Layout: Left (1/3) for upload, Right (2/3) for Q&A
col1, col_space, col2 = st.columns([1, 0.5, 2])

with col1:
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files and st.button("Upload & Process"):
        files = [('files', (f.name, f.read(), 'application/pdf')) for f in uploaded_files]
        with st.spinner("Uploading and processing..."):
            res = requests.post(f"{API_URL}/upload/", files=files)
            if res.status_code == 200:
                st.success("✅ Files processed successfully!")
            else:
                st.error(f"❌ Error: {res.json()['detail']}")

# Add vertical line separator
with col_space:
    st.markdown(
        """
        <div style="border-left: 1px solid #ccc; height: 100%; margin-left: 10px;"></div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.header("Ask a Question")
    question = st.text_input("Enter your question")

    if st.button("Send"):
        if question.strip():
            with st.spinner("Getting answer..."):
                res = requests.get(f"{API_URL}/answer/", params={"question": question})
                if res.status_code == 200:
                    st.markdown("**Answer:**")
                    st.write(res.json()["answer"])
                else:
                    st.error(f"❌ Error: {res.json()['detail']}")
        else:
            st.warning("Please enter a question.")
