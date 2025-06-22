# main.py (FastAPI Backend)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import uuid
from rag import extract_text_from_pdfs, chunk_text, save_vectors, answer_question,delete_vectors
from db import init_db, add_file, get_files, delete_file as remove_file

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("faiss_index", exist_ok=True)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        add_file(unique_name, file_path)

        with open(file_path, "rb") as f:
            text = extract_text_from_pdfs([f])
        chunks = chunk_text(text)
        save_vectors(chunks, file_id=unique_name)

    return {"message": "Files processed successfully"}

@app.get("/files/")
async def list_files():
    rows = get_files()
    return {"files": [{"id": row[0], "filename": row[1]} for row in rows]}


@app.delete("/delete/{file_id}")
async def delete_file(file_id: int):
    filepath = remove_file(file_id)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found in DB")

    if os.path.exists(filepath):
        os.remove(filepath)

    # Remove associated vectors
    delete_vectors(os.path.basename(filepath))

    return {"message": "File and its vectors deleted successfully"}


@app.get("/answer/")
async def get_answer(question: str):
    try:
        answer = answer_question(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
