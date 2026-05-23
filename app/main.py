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


@app.post("/accounts")
def create_account(owner: str, balance: float = 0.0, db: Session = Depends(get_db)):
    account = Account(owner=owner, balance=balance)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@app.get("/accounts/{account_id}")
def get_accounts(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return {"error": "Account not found"}

    return {"id": account.id, "owner": account.owner, "balance": account.balance}