# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from rag import extract_text_from_pdfs, chunk_text, save_vectors, answer_question

app = FastAPI()

# Allow CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_path)

    try:
        with open(file_path, "rb") as f:
            text = extract_text_from_pdfs([f])
        chunks = chunk_text(text)
        save_vectors(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

    return {"message": "Files processed successfully"}

@app.get("/answer/")
async def get_answer(question: str):
    try:
        answer = answer_question(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
