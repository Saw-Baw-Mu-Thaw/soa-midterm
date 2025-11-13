from ..repository import config as cfg
from sqlmodel import Session, create_engine, select
from ..models.Transaction import Transactions_DTO
from datetime import datetime
from ..repository import Debt_Repo, Cust_Repo
from ..models.Tuition_Debt import Tuition_Debt_DTO

engine = create_engine(cfg.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        return session
    
def create_new_transaction(payer_id : int, receiver_id : str, debt_id : int) -> int:
    # create a new transaction record in database and return the transaction id
    # if failed, returns -1
    new_transaction = Transactions_DTO(
        payer_id=payer_id,
        receiver_id=receiver_id,
        debt_id=debt_id,
        amount=0,
        initiated_at=datetime.now()
    )
    session = get_session()
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)
    session.close()

    if new_transaction.transaction_id:
        return new_transaction.transaction_id
    return -1

def get_pending_transaction(username : str) -> Transactions_DTO:
    # get the transaction that the user with username is currently performing
    cust = Cust_Repo.get_cust_info_by_username(username)

    if cust is None:
        return None
    
    session = get_session()
    statement = select(Transactions_DTO).where(Transactions_DTO.status == "PENDING").where(Transactions_DTO.payer_id == cust.customer_id)
    results = session.exec(statement)
    transaction = results.first()

    session.close()

    return transaction

def check_pending_transaction(receiver_id : str) -> bool:
    # to check if someone else has already stated a transaction for the receiver
    session = get_session()

    statement = select(Transactions_DTO).where(Transactions_DTO.receiver_id == receiver_id).where(Transactions_DTO.status == "PENDING")
    results = session.exec(statement)
    transaction = results.first()
    session.close()
    if transaction:
        return True
    else:
        return False
    
def get_transaction(transaction_id : int) -> Transactions_DTO:
    # get the transaction record with the transaction id
    session = get_session()
    statement = select(Transactions_DTO).where(Transactions_DTO.transaction_id == transaction_id)
    results = session.exec(statement)
    
    transaction = results.first()

    session.close()

    return transaction

def complete_transaction(transaction_id : int):
    transaction = get_transaction(transaction_id)

    # Update receiver debt record
    receiver_id = transaction.receiver_id
    

    receiver = Cust_Repo.get_cust_info_by_id(receiver_id)
    if receiver is None:
        return False
    
    receiver_debt = Debt_Repo.get_debt(receiver.student_id)
    tuition_amount = receiver_debt.amount
    Debt_Repo.set_debt_paid(receiver.student_id)

    # reduce payer's balance
    payer_id = transaction.payer_id
    payer = Cust_Repo.get_cust_info_by_cust_id(payer_id)
    if payer is None:
        return False
    Cust_Repo.reduce_balance(payer.username, tuition_amount)

    # Mark transaction as complete
    session = get_session()

    transaction.amount = tuition_amount
    transaction.status = "SUCCESS"
    transaction.completed_at = datetime.now()
    session.add(transaction)
    session.commit()
    session.close()
    
    return True

def fail_transaction(transaction_id : int, reason : str = None):
    # fails a transaction(after a set amount of time has passed)
    transaction = get_transaction(transaction_id)

    if transaction is None:
        return False
    
    if(transaction.status == "PENDING"):
        session = get_session()
        transaction.status = "FAILED"
        if(reason):
            transaction.failure_reason = reason
        session.add(transaction)
        session.commit()
        session.close()
        return True
    return True 
    
def get_all_transaction(username : str):
    # get all transactions where user is a payer
    cust = Cust_Repo.get_cust_info_by_username(username)
    if cust is None:
        return None
    
    
    session = get_session()

    statement = select(Transactions_DTO).where(
        (Transactions_DTO.payer_id == cust.customer_id)
        ).distinct()
    
    results = session.exec(statement)

    transactions = results.all()

    session.close()

    return transactions
