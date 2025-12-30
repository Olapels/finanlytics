from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from database.database_connection.database_client import get_db
from services.transaction_service import transaction_service
from services.user_service import user_service
from database.models.user_model import User
from schemas.transaction_schema import TransactionCreate, TransactionList, TransactionRead


transaction_router = APIRouter()


@transaction_router.post("/upload")
async def upload_tx_and_save(file: UploadFile,db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    raw_text = await transaction_service.upload_transactions(db, file)
    extracted_transactions = await transaction_service.extraction_transactions_from_text(raw_text)
    saved_transactions = []
    for tx in extracted_transactions:
        saved_tx = await transaction_service.create_transaction(db, tx, user_id)
        saved_transactions.append(saved_tx)

    await transaction_service.write_transactions_to_db(db, saved_transactions, user_id)

    return {"message": "Transactions uploaded successfully"}



@transaction_router.get("/user_transactions")
async def get_user_transactions(db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    transactions = await transaction_service.get_transactions_by_user(db, user_id)
    return transactions

@transaction_router.get("/income_summary")
async def get_income_summary(db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    summary = await transaction_service.get_income_summary(db, user_id)
    return summary

@transaction_router.get("/expense_summary")
async def get_expense_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    summary = await transaction_service.get_expense_summary(db, user_id)
    return summary

@transaction_router.post("/input_transactions")
async def write_transactions(transaction_in: TransactionCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    saved_transaction = await transaction_service.create_transaction(db, transaction_in, user_id)
    success_code = await transaction_service.write_transactions_to_db(db, [saved_transaction], user_id)
    if success_code is True:    
        return "Transaction saved successfully"
    else:
        return "Failed to save transaction"
    
@transaction_router.get("/spending_category_summary")
async def get_spending_category_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    user_id = current_user.user_id
    summary = await transaction_service.get_spending_category_summary(db, user_id)
    return summary