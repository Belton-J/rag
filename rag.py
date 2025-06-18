# rag.py

import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extract text from PDFs
def extract_text_from_pdfs(pdf_files):
    text = ""
    for file in pdf_files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

# Split into chunks
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_text(text)

# Embed and save
def save_vectors(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Load QA Chain
def get_qa_chain():
    prompt = PromptTemplate(
        template="""
        Answer the question as detailed as possible from the provided context.
        If the answer is not available in the context, say "Answer is not available in the context."
        Do not make up answers.

        Context:
        {context}

        Question:
        {question}

        Answer:""",
        input_variables=["context", "question"]
    )
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# Perform similarity search and answer
def answer_question(question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(question)
    chain = get_qa_chain()
    result = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return result["output_text"]
