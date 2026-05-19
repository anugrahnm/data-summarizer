from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File
import os
from dotenv import load_dotenv
from datetime import date, datetime
from pydantic import BaseModel, field_validator
from PyPDF2 import PdfReader
from google import genai


load_dotenv()

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")


app = FastAPI(title="Data Summarizer")

client = genai.Client()


@app.post("/summarize/")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf","text/plain"}:
        raise HTTPException(415, "Unsupported file type")
    data = await file.read()
    total_pages = ""
    bytes_stream = BytesIO(data)
    if file.content_type == "application/pdf":
        reader = PdfReader(bytes_stream)

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            total_pages += page.extract_text()
            

    elif file.content_type == "text/plain":
        text= bytes_stream.read()
        total_pages = text.decode("utf-8")
        

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"""
Act as an expert data analyst. Read the provided text and extract a concise, structured summary using only basic plain-text formatting. 

Strict output constraints for your API-safe response:
1. Provide ONLY the final text summary. Do not use any Markdown formatting syntax (such as hashes, asterisks, or underscores).
2. Do not include any introductory text, pleasantries, conversational filler, or concluding remarks.
3. Do not reference the original document or use phrases like "According to the text".
4. Use standard capital letters for section headers, and simple spaces or dashes (-) for alignment and bullet items. Ensure it is perfectly readable inside a raw API payload. {total_pages} """
    )

    with open("response.txt", "w") as txt_file:
        txt_file.write(response.text)
    return {"Response in response.txt"}
    