
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

def extract_text_from_pdfs(pdf_files):
    text = ""
    for file in pdf_files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_text(text)

def save_vectors(chunks, file_id):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    metadatas = [{"file_id": file_id} for _ in chunks]
    new_store = FAISS.from_texts(chunks, embedding=embeddings, metadatas=metadatas)

    index_path = "faiss_index"
    if os.path.exists(os.path.join(index_path, "index.faiss")):
        existing_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        existing_store.merge_from(new_store)
        existing_store.save_local(index_path)
    else:
        new_store.save_local(index_path)


def delete_vectors(file_id):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    index_path = "faiss_index"
    if not os.path.exists(os.path.join(index_path, "index.faiss")):
        return  # nothing to do

    store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    # Filter out docs from that file_id
    docs_with_file = [doc for doc in store.docstore._dict.values() if doc.metadata.get("file_id") == file_id]
    ids_to_delete = [doc.metadata["doc_id"] for doc in docs_with_file if "doc_id" in doc.metadata]

    # Remove manually
    for doc in docs_with_file:
        del store.docstore._dict[doc.metadata["doc_id"]]

    store.save_local(index_path)

def get_qa_chain():
    prompt = PromptTemplate(
        template="""
        Answer the question with the core points that gives the user a clear understanding about the concept they ask for,
        from the provided context.
        If the answer is not available in the context, say "Answer is not available in the context."
        Do not make up answers.

        Context:
        {context}

        Question:
        {question}

        Answer:""",
        input_variables=["context", "question"]
    )
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def answer_question(question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    index_path = "faiss_index"

    if not os.path.exists(os.path.join(index_path, "index.faiss")):
        raise ValueError("Vector index is empty")

    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(question)
    
    chain = get_qa_chain()
    result = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return result["output_text"]
