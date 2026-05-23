from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import Account

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyBank API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

@app.get('/')
def root():
    return {"message": "Welcome to MyBank API"}


@app.post("/accounts", tags=["Accounts"])
def create_account(owner: str, balance: float = 0.0, db: Session = Depends(get_db)):
    account = Account(owner=owner, balance=balance)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@app.get("/accounts/{account_id}", tags=["Accounts"])
def get_accounts(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return {"error": "Account not found"}

    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@app.post("/accounts/{account_id}/deposit", tags=["Transactions"])
def deposit_money(account_id: int, amount: float, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        return {"error": "Account not found"}

    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    account.balance += amount
    db.commit()
    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@app.post("/accounts/{account_id}/withdraw", tags=["Transactions"])
def withdraw_money(account_id: int, amount: float, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        return {"error": "Account not found"}

    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    if amount > account.balance:
        return {"error": "Not enough balance"}

    account.balance -= amount
    db.commit()
    return {"id": account.id, "owner": account.owner, "balance": account.balance}


@app.post("/accounts/transfer", tags=["Transactions"])
def transfer_to_someone(from_id: int, to_id: int, amount: float, db: Session = Depends(get_db)):
    sender = db.query(Account).filter(Account.id == from_id).first()
    receiver = db.query(Account).filter(Account.id == to_id).first()

    if amount <= 0:
        return {"error": "Amount must be positive"}

    if amount > sender.balance:
        return {"error": "Not enough balance"}

    if not sender or not receiver:
        return {"error": "Account not found"}
    
    sender.balance -= amount
    receiver.balance += amount
    db.commit()
    return {"sender_id": sender.id, "sender_balance": sender.balance, "receiver_id": receiver.id, "receiver_balance": receiver.balance, "amount_sent": amount}