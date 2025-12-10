import io
import os
import pdfplumber
import csv
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.transaction_schema import TransactionList, TransactionCreate
from database.models.transaction_model import Transactions
from fastapi import UploadFile
from google import genai
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

class TransactionService:
    async def create_transaction(self, db: AsyncSession, transaction_in: TransactionCreate, user_id: str):
        transaction = Transactions(
            transaction_id=str(uuid4()),
            user_id=user_id,
            date=transaction_in.date,
            time=transaction_in.time,
            money_in=transaction_in.money_in,
            money_out=transaction_in.money_out,
            category=transaction_in.category,
            to_from=transaction_in.to_from,
            description=transaction_in.description,
            balance=transaction_in.balance,
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    async def upload_transactions(self, db: AsyncSession, file: UploadFile):
        filename = file.filename.lower()
        file_bytes = await file.read()

        # Case 1: .txt file
        if filename.endswith(".txt"):
            return file_bytes.decode("utf-8")

        # Case 2: .pdf file
        if filename.endswith(".pdf"):
            file_stream = io.BytesIO(file_bytes)
            with pdfplumber.open(file_stream) as pdf:
                # pages_text = [
                #     page.extract_text() or "" 
                #     for page in pdf.pages
                # ]
                # return "\n".join(pages_text)
                first_page = pdf.pages[0]
                return first_page.extract_text() or ""
    
    async def extraction_transactions_from_text(self,raw_text: str) -> List[dict]:
        prompt = f"""
                Extract ALL financial transactions from the following bank statement text.

                Rules:
                - Return ONLY JSON using the provided schema.
                - Normalize amounts: remove ₦ and commas.
                - If money_in or money_out is missing, set to 0.
                - If time is missing in a wrapped line, infer it if provided.
                - Don't include summary text or non-transaction lines.

                Text to parse:
                -------------------------
                {raw_text}
                -------------------------
                """
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
        "response_mime_type": "application/json",
        "response_json_schema": TransactionList.model_json_schema()},
        )  
        return response.text

    async def get_transactions_by_user(self, db: AsyncSession, user_id: str):
        result = await db.execute(select(Transactions).where(Transactions.user_id == user_id))
        return result.scalars().all()
    
    


transaction_service = TransactionService()
