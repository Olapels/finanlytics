from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from database.database_connection.database_client import get_db
from services.transaction_service import transaction_service
from services.user_service import user_service
from database.models.user_model import User
from schemas.transaction_schema import TransactionList


transaction_router = APIRouter()


@transaction_router.post("/upload",response_model=TransactionList)
async def upload_tx_and_save(file: UploadFile,db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    raw_text = await transaction_service.upload_transactions(db, file)
    extracted_transactions = await transaction_service.extraction_transactions_from_text(raw_text)
    saved_transactions = await transaction_service.write_transactions_to_db(db, extracted_transactions, user_id)
    return saved_transactions
