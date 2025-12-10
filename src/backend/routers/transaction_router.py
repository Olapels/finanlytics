from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from database.database_connection.database_client import get_db
from schemas.transaction_schema import (
    ExtractTransactionsRequest,
    Transaction,
    TransactionList,
)

from services.transaction_service import transaction_service

transaction_router = APIRouter()


@transaction_router.post("/upload")
async def upload_file(file: UploadFile, db: AsyncSession = Depends(get_db)):
    text_content = await transaction_service.upload_transactions(db, file)
    return {"text": text_content}

@transaction_router.post("/extract")
async def extract_transactions(text, db: AsyncSession = Depends(get_db)):
    transactions_data = await transaction_service.extraction_transactions_from_text(text)
    return transactions_data

