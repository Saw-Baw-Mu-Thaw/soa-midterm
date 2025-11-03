from ..repository import config as cfg
from sqlmodel import Session, create_engine, select
from ..models.Tuition_Debt import Tuition_Debt_DTO
from datetime import datetime

engine = create_engine(cfg.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        return session
    
def get_debt(cust_id : int) -> Tuition_Debt_DTO:
    # get the tution_debt row that is UNPAID associated with customer Id
    session = get_session()

    statement = select(Tuition_Debt_DTO).where(Tuition_Debt_DTO.customer_id == cust_id).where(Tuition_Debt_DTO.status == "UNPAID")
    results = session.exec(statement)
    debt = results.first()
    
    session.close()

    return debt

def set_debt_paid(cust_id : int) -> None:
    # update the debt row of customer id
    debt = get_debt(cust_id)
    debt.status = "PAID"
    debt.paid_date = datetime.now()
    debt.updated_at = datetime.now()

    session = get_session()

    session.add(debt)
    session.commit()
    session.close()