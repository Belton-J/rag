import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"
st.set_page_config(layout="wide")
st.title("RAG PDF QA App")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Layout: Left (1/3) for upload, Right (2/3) for Q&A
col1, col_space, col2 = st.columns([1, 0.5, 2])

# ===== Left: Upload Section =====
with col1:
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True, key="file_uploader")

    if uploaded_files and st.button("Upload & Process"):
        files = []
        for f in uploaded_files:
            files.append(("files", (f.name, f.read(), "application/pdf")))

        with st.spinner("Uploading and processing..."):
            res = requests.post(f"{API_URL}/upload/", files=files)
            if res.status_code == 200:
                st.success("Files processed successfully!")
                st.rerun()
            else:
                st.error(f"Error: {res.json()['detail']}")

# ===== Separator =====
with col_space:
    st.markdown("""
    <div style="border-left: 1px solid #ccc; height: 100%; margin-left: 10px;"></div>
    """, unsafe_allow_html=True)

# ===== Right: Q&A Chat Section =====
with col2:
    st.header("Ask a Question")
    question = st.text_input("Enter your question", key="user_question")

    if st.button("Send"):
        if question.strip():
            with st.spinner("Getting answer..."):
                res = requests.get(f"{API_URL}/answer/", params={"question": question})
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.session_state.chat_history.append({"question": question, "answer": answer})
                    st.session_state.user_question = ""  # Clear input
                    st.rerun()
                else:
                    st.error(f"Error: {res.json()['detail']}")
        else:
            st.warning("Please enter a question.")

    # Display chat history like ChatGPT
    st.markdown("---")
    for chat in reversed(st.session_state.chat_history):  # newest at top
        with st.chat_message("user"):
            st.markdown(f"**You:** {chat['question']}")
        with st.chat_message("assistant"):
            st.markdown(f"**Answer:** {chat['answer']}")

# ===== Sidebar: File List =====
st.sidebar.title("📁 Uploaded Files")
res = requests.get(f"{API_URL}/files/")
if res.status_code == 200:
    files = res.json()["files"]
    for file in files:
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(file["filename"].split("_", 1)[-1])
        if col2.button("🗑️", key=f"del_{file['id']}"):
            del_res = requests.delete(f"{API_URL}/delete/{file['id']}")
            time.sleep(2)
            if del_res.status_code == 200:
                st.success("File deleted!")
                st.rerun()
            else:
                st.error("Failed to delete file")
