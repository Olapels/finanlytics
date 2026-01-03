from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, Query
from backend.database.database_connection.database_client import get_db
from backend.services.transaction_service import transaction_service
from backend.services.user_service import user_service
from backend.database.models import User
from backend.schemas.transaction_schema import TransactionCreate, TransactionList, TransactionRead


transaction_router = APIRouter()


@transaction_router.post("/upload")
async def upload_tx_and_save(file: UploadFile,db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    """Upload a statement, extract transactions, and persist them for the user.

    Args:
        file (UploadFile): Statement file (txt/pdf).
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Confirmation message.
    """
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
async def get_user_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """List transactions for the current user with pagination.

    Args:
        limit (int): Page size (default 20, max 100).
        offset (int): Records to skip (default 0).
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Items plus pagination metadata.
    """
    user_id = current_user.user_id
    items, total = await transaction_service.list_transactions(db, user_id, limit, offset)
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "total": total,
        "has_more": offset + len(items) < total,
    }

@transaction_router.get("/income_summary")
async def get_income_summary(db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    """Return total income for the current user.

    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Total income.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_income_summary(db, user_id)
    return summary

@transaction_router.get("/expense_summary")
async def get_expense_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Return total expenses for the current user.

    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Total expenses.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_expense_summary(db, user_id)
    return summary

@transaction_router.get("/monthly_income_summary")
async def get_monthly_income_summary(month_input:int,year_input:int,db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Return income total for a specific month/year for the current user.

    Args:
        month_input (int): Target month (1-12).
        year_input (int): Target year.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Monthly income total.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_income_by_month(db, user_id,month=month_input,year=year_input)
    return summary

@transaction_router.get("/monthly_expense_summary")
async def get_monthly_expense_summary(month_input:int, year_input:int, db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Return expense total for a specific month/year for the current user.

    Args:
        month_input (int): Target month (1-12).
        year_input (int): Target year.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Monthly expense total.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_expense_by_month(db, user_id, month=month_input, year=year_input)
    return summary

@transaction_router.post("/input_transactions")
async def write_transactions(transaction_in: TransactionCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(user_service.get_current_user)):
    """Manually insert a single transaction for the current user.

    Args:
        transaction_in (TransactionCreate): Transaction payload.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        str: Status message.
    """
    user_id = current_user.user_id
    saved_transaction = await transaction_service.create_transaction(db, transaction_in, user_id)
    success_code = await transaction_service.write_transactions_to_db(db, [saved_transaction], user_id)
    if success_code is True:    
        return "Transaction saved successfully"
    else:
        return "Failed to save transaction"
    
@transaction_router.get("/spending_category_summary")
async def get_spending_category_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Return expense totals grouped by category for the current user.

    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Spend totals per category.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_spending_category_summary(db, user_id)
    return summary

@transaction_router.get("/monthly_summary")
async def get_monthly_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Return income/expense totals grouped by month for the current user.

    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        list[dict]: Monthly income/expense totals.
    """
    user_id = current_user.user_id
    summary = await transaction_service.get_monthly_summary(db, user_id)
    return summary
