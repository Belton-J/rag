# 📄 RAG PDF Question Answering App

This is a simple full-stack application that allows users to upload PDF files, ask questions about their content, and get accurate answers using LangChain + Gemini (Google Generative AI). It uses:

* **FastAPI** as the backend API
* **Streamlit** for the frontend UI
* **LangChain** + **FAISS** for vector storage and retrieval
* **Gemini** for LLM-based question answering

---

## 📜 Project Structure

```
rag-pdf-qa/
├── app.py            # Streamlit frontend UI
├── main.py           # FastAPI backend API
├── rag.py            # Core RAG logic (text extraction, embedding, answering)
├── requirements.txt  # Python dependencies
├── .env              # Gemini API key (not to be shared)
└── .gitignore        # Ignored files/folders
```

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Belton-J/rag.git
cd rag
```

### 2. Install Dependencies

Make sure you have Python 3.9+ and pip installed. Then run:

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variable

Create a `.env` file in the root folder and add your Gemini API key:

```
GOOGLE_API_KEY=your-api-key-here
```

---

### 4. Run the FastAPI Backend

```bash
uvicorn main:app --reload
```

---

### 5. Run the Streamlit Frontend

In another terminal/tab:

```bash
streamlit run app.py
```

---

## 🧠 How It Works

1. **Upload PDFs**: PDFs are read and converted into text.
2. **Text Chunking**: The text is chunked into manageable pieces.
3. **Embedding**: Each chunk is embedded using Google Generative AI embeddings.
4. **Store in FAISS**: The embeddings are stored locally using FAISS.
5. **Answering**: When a user asks a question, similar chunks are retrieved and passed to Gemini for answering.

---

## 📦 Dependencies

Some key libraries used:

* `streamlit`
* `fastapi`
* `langchain`
* `PyPDF2`
* `google-generativeai`
* `python-dotenv`
* `faiss-cpu`

---

## 🛡️ .gitignore (Important)

Make sure your `.env`, temp folders, and vector index files are ignored from Git commits.

```
__pycache__/
faiss_index/
temp_uploads/
.env
```

---

## 📬 License

MIT License – feel free to use and modify.
