from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File
import os
from dotenv import load_dotenv
from datetime import date, datetime
from google.genai.errors import ClientError, ServerError
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
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
                Act as an expert data analyst. Read the provided text and extract a comprehensive yet concise summary. 

                Format your response using clean, native Markdown according to these structural rules:

                1. Use 1-2 short paragraphs of flowing sentences to synthesize the main narrative, background, or core summary of the text.
                2. Use standard Markdown headers (## or ###) to separate major concepts or sections.
                3. Use bullet points (-) strictly for high-impact key data points, specific technical skills, or clear metrics that are difficult to read in a paragraph, even then keep it short while still keeping it sensible. Do not bullet entire paragraphs of text.
                4. If the source text is short (e.g., less than 2-3 paragraphs), do not split it into different sections with headings; just provide the summary paragraphs cleanly.
                5. Start your response immediately with the first Markdown element. Do not include any conversational intro ("Here is the summary:") or outro remarks. 

                ---
                ### TEXT TO SUMMARIZE:
                {total_pages}
                ---
            """
        )

        with open("response.txt", "w") as txt_file:
            txt_file.write(response.text)
        return response.text
    except ClientError as e:
        if e.code == 429:
            return {"summary": "Rate limit hit! Google's free tier is cooling down. Please wait 30 seconds and try again."}
        return {"summary": f"An error occurred: {e}"}
    except ServerError as e:
        if e.code == 503:
            return {"summary": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later."}
        return {"summary": f"An error occurred: {e}"}