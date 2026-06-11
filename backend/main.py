from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File
import os
from dotenv import load_dotenv
from google.genai.errors import ClientError, ServerError
from PyPDF2 import PdfReader
from google import genai
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse


load_dotenv()

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")


app = FastAPI(title="Data Summarizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=f"""
                Act as an expert analyst. Read the provided text and produce a structured, accurate summary.
                
                Follow these rules strictly:
                1. Open with 1-2 concise paragraphs covering the core narrative or purpose of the document with a heading using ###.
                2. Use ### headers to separate distinct major sections only — do not create headers for minor points.
                3. Use bullet points (-) only for concrete data, metrics, or lists of items. Never bullet prose.
                4. Do not use em dashes (—). Use commas or restructure the sentence instead.
                5. Do not pad or over-summarise. If the document is short, keep the summary short.
                6. Never include filler phrases like "In conclusion" or "Overall".
                7. Start immediately with the first word of the summary. No intro, no outro.
                ---
                TEXT TO SUMMARIZE:
                {total_pages}
                ---
            """
        )

        with open("response.txt", "w") as txt_file:
            txt_file.write(response.text)
        return PlainTextResponse(response.text)
    except ClientError as e:
        if e.code == 429:
            return "Rate limit hit! Google's free tier is cooling down. Please wait 30 seconds and try again."
        return f"An error occurred: {e}"
    except ServerError as e:
        if e.code == 503:
            return "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later."
        return f"An error occurred: {e}"