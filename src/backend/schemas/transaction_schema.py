from pydantic import BaseModel, EmailStr, Field, RootModel,field_validator
from typing import Optional, List
import datetime

#transaction input from user
class TransactionCreate(BaseModel):
    date: datetime.date = Field(description="Date of the transaction in dd/mm/yy format.")
    money_in: float = Field(description="Amount of money entering the account, numeric only.")
    money_out: float = Field(description="Amount of money leaving the account, numeric only.")
    category: str = Field(description="Transaction category.")
    to_from: str = Field(description="Person or merchant involved.")
    description: str = Field(description="Description of the transaction.")
    balance: float = Field(description="Resulting account balance.")

    #extra validation for date field to ensure correct format and not future date
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, datetime.date):
            parsed_date = value
        else:
            for format in ("%d/%m/%Y","%d-%m-%Y","%Y-%m-%d","%Y/%m/%d","%d/%m/%y","%d-%m-%y"):
                try:
                    parsed_date = datetime.datetime.strptime(value, format).date()
                    break
                except ValueError:
                    parsed_date = None
            if parsed_date is None:
                raise ValueError(f"Invalid date format: {value}")
        
        if parsed_date > datetime.date.today():
            raise ValueError("Date cannot be in the future.")
        
        return parsed_date
        


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
