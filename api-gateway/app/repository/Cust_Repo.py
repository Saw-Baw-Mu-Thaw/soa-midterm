from ..repository import config as cfg
from sqlmodel import Session, create_engine, select
from ..models.Customer import Customers_DTO
from ..models.Tuition_Debt import Tuition_Debt_DTO

engine = create_engine(cfg.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        return session

def get_cust_info_by_id(student_id : str) -> Tuition_Debt_DTO:
    # query DB for a specific customer's debt given student id
    session = get_session()

    statement = select(Tuition_Debt_DTO).where(Tuition_Debt_DTO.student_id == student_id)
    results = session.exec(statement)
    customer = results.first()

    session.close()

    return customer

def get_cust_info_by_username(username : str) -> Customers_DTO:
    # query DB for a specific customer given username
    session = get_session()

    statement = select(Customers_DTO).where(Customers_DTO.username == username)
    results = session.exec(statement)
    customer = results.first()

    session.close()

    return customer

def get_cust_info_by_cust_id(cust_id : int) -> Customers_DTO:
    # get the customer record with customer id
    session = get_session()

    statement = select(Customers_DTO).where(Customers_DTO.customer_id == cust_id)
    results = session.exec(statement)
    customer = results.first()

    session.close()

    return customer

def reduce_balance(username : str, amount : int):
    # reduce the balance of user by amount
    customer = get_cust_info_by_username(username)

    customer.available_balance -= amount

    session = get_session()
    session.add(customer)
    session.commit()
    session.close()
