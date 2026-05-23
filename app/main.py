from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import Account, Transaction

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
    transaction = Transaction(account_id=account.id, amount=amount, type="deposit")
    db.add(transaction)
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
    transaction = Transaction(account_id=account.id, amount=amount, type="deposit")
    db.add(transaction)
    db.commit()
    return {"id": account.id, "owner": account.owner, "balance": account.balance}


@app.post("/accounts/transfer", tags=["Transactions"])
def transfer_to_someone(from_id: int, to_id: int, amount: float, db: Session = Depends(get_db)):
    sender = db.query(Account).filter(Account.id == from_id).first()
    receiver = db.query(Account).filter(Account.id == to_id).first()

    if not sender or not receiver:
        return {"error": "Account not found"}

    if amount <= 0:
        return {"error": "Amount must be positive"}

    if amount > sender.balance:
        return {"error": "Not enough balance"}

   
    
    sender.balance -= amount
    receiver.balance += amount
    sender_transaction = Transaction(account_id=sender.id, amount=amount, type="transfer_out")
    receiver_transaction = Transaction(account_id=receiver.id, amount=amount, type="transfer_in")
    db.add(sender_transaction)
    db.add(receiver_transaction)
    db.commit()
    return {"sender_id": sender.id, "sender_balance": sender.balance, "receiver_id": receiver.id, "receiver_balance": receiver.balance, "amount_sent": amount}

@app.get("/accounts/{account_id}/transactions", tags=["Transactions"])
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.account_id == account_id).all()
    return [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "timestamp": str(t.timestamp)
        }
        for t in transactions
    ]