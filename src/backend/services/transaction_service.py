import io
import os
import re
import json
import pdfplumber
import csv
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schemas.transaction_schema import TransactionList, TransactionCreate
from database.models.transaction_model import Transactions
from services.category_service import CategoryService
from fastapi import UploadFile
from google import genai
from dotenv import load_dotenv
from collections.abc import Iterable
from database.models.categories_model import DEFAULT_CATEGORIES
from typing import Union
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY2")
client = genai.Client(api_key=API_KEY)

class TransactionService:
    async def create_transaction(
        self,
         db: AsyncSession,
        transaction_in: TransactionCreate,
        user_id: str,
    ) -> Transactions:
        category_in = transaction_in.category.strip().title()
        cat_id = await CategoryService().get_category_by_name(db, category_in, user_id)
        if not cat_id:
            category = await CategoryService().create_user_category(db, user_id, category_in)
            cat_id = await CategoryService().get_category_by_name(db, category, user_id)
        return Transactions(
            transaction_id=str(uuid4()),
            user_id=user_id,
            date=transaction_in.date,
            amount = transaction_in.amount,
            transaction_type=transaction_in.transaction_type,
            category_id=cat_id,
            to_from=transaction_in.to_from,
            description=transaction_in.description,
        )

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

                STRICT RULES:
                - Return ONLY valid JSON (no markdown, no commentary).
                - Dates MUST be in ISO 8601 format: YYYY-MM-DD (4-digit year required).
                - Do NOT use 2-digit years.
                - If the statement shows a 2-digit year, infer the correct 4-digit year.
                - Normalize amounts: remove ₦ and commas.
                - amount MUST be a NUMBER (no currency symbols, no commas).
                - transaction_type MUST be either "INCOME" or "EXPENSE".
                - Use "INCOME" AS input for transaction_type when money is entering the account.
                - Use "EXPENSE" AS input for transaction_type when money is leaving the account.
                - category must be one of the following: {', '.join(DEFAULT_CATEGORIES)}
                - Do NOT include summary lines or balances outside transactions.
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
        raw_json = response.text
        raw_json = re.sub(r"^```(?:json)?|```$", "", raw_json, flags=re.MULTILINE)
        payload = json.loads(raw_json)

        transactions = TransactionList.model_validate(payload).root

        return transactions
    
    async def write_transactions_to_db(self,db:AsyncSession, transactions_list: List[Transactions], user_id: str) -> bool:
        for transaction_in in transactions_list:
            db.add(transaction_in)
        await db.commit()
        return True


    async def get_transactions_by_user(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(Transactions)
            .options(selectinload(Transactions.category))
            .where(Transactions.user_id == user_id))
        return [
        {
            "description": tx.description,
            "date": tx.date,
            "amount": tx.amount,
            "transaction_type": tx.transaction_type,
            "category": tx.category.category_name,
        }
        for tx in result.scalars()
    ]
    
    async def get_income_summary(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(Transactions)
            .where(
                Transactions.user_id == user_id,
                Transactions.transaction_type == "INCOME"
            )
        )
        total_income = sum(tx.amount for tx in result.scalars())
        return {"total_income": total_income}
    
    async def get_expense_summary(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(Transactions)
            .where(
                Transactions.user_id == user_id,
                Transactions.transaction_type == "EXPENSE"
            )
        )
        total_expense = sum(tx.amount for tx in result.scalars())
        return {"total_expense": total_expense}
    
    async def get_spending_category_summary(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(Transactions)
            .options(selectinload(Transactions.category))
            .where(
                Transactions.user_id == user_id,
                Transactions.transaction_type == "EXPENSE"
            )
        )
        category_summary = {}
        for tx in result.scalars():
            category_name = tx.category.category_name
            if category_name not in category_summary:
                category_summary[category_name] = 0.0
            category_summary[category_name] += tx.amount
        return category_summary


transaction_service = TransactionService()
