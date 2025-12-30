from pydantic import BaseModel, EmailStr, Field, RootModel,field_validator, ConfigDict
from typing import Optional, List
import datetime
from enum import Enum

class TransactionTypeEnum(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

#transaction input from user
class TransactionCreate(BaseModel):
    date: datetime.date = Field(description="Transaction date in ISO 8601 format (YYYY-MM-DD).")
    amount: float = Field(description="Amount of money entering or leaving the account, numeric only.")
    category: str = Field(description="Transaction category.")
    transaction_type: TransactionTypeEnum = Field(description="Type of transaction: income or expense.")
    to_from: str = Field(description="Person or merchant involved.")
    description: str = Field(description="Description of the transaction.")

    #extra validation for date field to ensure correct format and not future date
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        # Case 1: Already a date object
        if isinstance(value, datetime.date):
            parsed_date = value

        # Case 2: String date → parse manually
        else:
            parsed_date = None
            for fmt in (
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d/%m/%y",
                "%d-%m-%y",
            ):
                try:
                    parsed_date = datetime.datetime.strptime(value, fmt).date()
                    break
                except ValueError:
                    continue

            if parsed_date is None:
                raise ValueError(f"Invalid date format: {value}")

        # normalize bad centuries
        if parsed_date.year < 1900:
            parsed_date = parsed_date.replace(year=parsed_date.year + 2000)

        if parsed_date > datetime.date.today():
            raise ValueError("Date cannot be in the future.")

        return parsed_date

        
class TransactionRead(BaseModel):
    transaction_id: str
    date: datetime.date
    amount: float
    transaction_type: str
    category_id: int
    to_from: str | None
    description: str | None

    model_config = ConfigDict(from_attributes=True)


#transaction schema for post response which is sent to db. matches transaction model
class Transaction(TransactionCreate):
    user_id: str = Field(description="Identifier for the user associated with the transaction.")
    transaction_id: str = Field(description="Unique identifier for the transaction.")

#extracted transaction list schema -using rootmodel since input is a list of transactions
class TransactionList(RootModel[list[TransactionCreate]]):
    pass

class ExtractedTransactionList(BaseModel):
    transactions: List[TransactionCreate] = Field(
        description="List of transactions extracted from a bank statement before persistence."
    )

class ExtractTransactionsRequest(BaseModel):
    email: EmailStr = Field(description="Email of the user uploading the statement.")
    text: str = Field(description="Full text content extracted from the uploaded PDF.")
