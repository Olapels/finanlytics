import io
from datetime import date

import pytest
from fastapi import UploadFile

from backend.schemas.transaction_schema import TransactionCreate
from backend.services.transaction_service import transaction_service


def test_create_transaction_populates_all_fields():
    tx_in = TransactionCreate(
        date=date(2024, 1, 1),
        money_in=100.0,
        money_out=0.0,
        category="Salary",
        to_from="Employer",
        description="January pay",
        balance=500.0,
    )

    tx = transaction_service.create_transaction(tx_in, user_id="user-123")

    assert tx.user_id == "user-123"
    assert tx.date == tx_in.date
    assert tx.money_in == tx_in.money_in
    assert tx.money_out == tx_in.money_out
    assert tx.category == tx_in.category
    assert tx.to_from == tx_in.to_from
    assert tx.description == tx_in.description
    assert tx.balance == tx_in.balance
    assert tx.transaction_id  # generated uuid


@pytest.mark.asyncio
async def test_upload_transactions_reads_plain_text():
    file = UploadFile(filename="statement.txt", file=io.BytesIO(b"hello world"))

    content = await transaction_service.upload_transactions(db=None, file=file)

    assert content == "hello world"


@pytest.mark.asyncio
async def test_extraction_transactions_from_text_parses_response(monkeypatch):
    sample_json = """
    ```json
    [{"date":"2024-02-01","money_in":1500,"money_out":0,"category":"Salary","to_from":"Employer","description":"Feb pay","balance":2000}]
    ```
    """

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModels:
        def __init__(self):
            self.called_with = None

        def generate_content(self, **kwargs):
            self.called_with = kwargs
            return FakeResponse(sample_json)

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    fake_client = FakeClient()
    monkeypatch.setattr(transaction_service, "client", fake_client)

    transactions = await transaction_service.extraction_transactions_from_text("statement text")

    assert len(transactions) == 1
    tx = transactions[0]
    assert tx.date.isoformat() == "2024-02-01"
    assert tx.money_in == 1500
    assert tx.money_out == 0
    assert tx.category == "Salary"
    assert tx.to_from == "Employer"
    assert tx.description == "Feb pay"
    assert tx.balance == 2000
    assert fake_client.models.called_with["model"] == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_write_transactions_to_db_persists_and_commits(monkeypatch):
    tx_in = TransactionCreate(
        date=date(2024, 3, 1),
        money_in=0.0,
        money_out=50.0,
        category="Groceries",
        to_from="Store",
        description="Weekly groceries",
        balance=450.0,
    )

    class DummyAsyncSession:
        def __init__(self):
            self.added = None
            self.committed = False
            self.refreshed = []
            self.rollback_called = False

        def add_all(self, objs):
            self.added = objs

        async def commit(self):
            self.committed = True

        async def rollback(self):
            self.rollback_called = True

        async def refresh(self, obj):
            self.refreshed.append(obj)

    db = DummyAsyncSession()

    result = await transaction_service.write_transactions_to_db(
        db=db,
        transactions=[tx_in],
        user_id="user-123",
    )

    assert db.committed is True
    assert db.rollback_called is False
    assert len(db.added) == 1
    assert len(db.refreshed) == 1
    saved_tx = result[0]
    assert saved_tx.user_id == "user-123"
    assert saved_tx.category == "Groceries"
    assert saved_tx.money_out == 50.0
    assert saved_tx.balance == 450.0
