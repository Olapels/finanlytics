from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

#transaction input from user
class TransactionCreate(BaseModel):
    date: str = Field(description="Date of the transaction in dd/mm/yy format.")
    time: Optional[str] = Field(description="Time of the transaction, if available.")
    money_in: float = Field(description="Amount of money entering the account, numeric only.")
    money_out: float = Field(description="Amount of money leaving the account, numeric only.")
    category: str = Field(description="Transaction category.")
    to_from: str = Field(description="Person or merchant involved.")
    description: str = Field(description="Description of the transaction.")
    balance: float = Field(description="Resulting account balance.")


#transaction schema for post response which is sent to db. matches transaction model
class Transaction(TransactionCreate):
    user_id: str = Field(description="Identifier for the user associated with the transaction.")
    transaction_id: str = Field(description="Unique identifier for the transaction.")

class TransactionList(BaseModel):
    transactions: List[TransactionCreate] = Field(description="List of extracted financial transactions.")

class ExtractedTransactionList(BaseModel):
    transactions: List[TransactionCreate] = Field(
        description="List of transactions extracted from a bank statement before persistence."
    )

class ExtractTransactionsRequest(BaseModel):
    email: EmailStr = Field(description="Email of the user uploading the statement.")
    text: str = Field(description="Full text content extracted from the uploaded PDF.")
