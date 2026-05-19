from fastapi import FastAPI
import os
from dotenv import load_dotenv
from datetime import date, datetime
from pydantic import BaseModel, field_validator

load_dotenv()

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")


app = FastAPI(title="Data Summarizer")


@app.post("/summarize/")
async def upload_file():
    pass