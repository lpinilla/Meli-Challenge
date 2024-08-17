import pytest
import csv
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from models.employee import Employee
from database import Base, engine
from crud import *
from io import StringIO

Session = sessionmaker(bind=engine)

@pytest.fixture(scope='module')
def db_session():
    Base.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='module')
def valid_employee_raw_string():
    return """row_id,user_id,user_state,user_manager,user_mail
1000,1000,True,1000,crystal21@company.com
"""

@pytest.fixture(scope='module')
def valid_multiple_employees_raw_string():
    return """row_id,user_id,user_state,user_manager,user_mail
2000,2000,True,2000,crystal21@company.com
2001,2001,False,2000,crystal22@company.com
2002,2002,True,2000,crystal23@company.com
"""


class TestCrud:

    def test_crud_create_employee_from_raw(self, db_session, valid_employee_raw_string):
        crud_created_user = create_employee_from_raw(db_session, valid_employee_raw_string)
        employee = db_session.query(Employee).filter_by(user_id=1000).first()
        assert crud_created_user == employee
        assert employee.user_id == 1000
        assert employee.user_state == True
        assert employee.user_mail == 'crystal21@company.com'
        assert employee.user_manager == 1000


    def test_crud_create_multiple_employees_from_raw(self, db_session, valid_multiple_employees_raw_string):
        create_multiple_employees_from_raw(db_session, valid_multiple_employees_raw_string)
        #get manager
        manager = db_session.query(Employee).filter_by(user_id=2000).first()
        assert manager.user_id == 2000
        assert manager.user_state == True
        assert manager.user_mail == 'crystal21@company.com'
        assert manager.user_manager == 2000
        employee_1 = db_session.query(Employee).filter_by(user_id=2001).first()
        assert employee_1.user_id == 2001
        assert employee_1.user_state == False
        assert employee_1.user_mail == 'crystal22@company.com'
        assert employee_1.user_manager == 2000
        assert employee_1.managed_by == manager
        assert employee_1 in manager.manages
        employee_2 = db_session.query(Employee).filter_by(user_id=2002).first()
        assert employee_2.user_id == 2002
        assert employee_2.user_state == True
        assert employee_2.user_mail == 'crystal23@company.com'
        assert employee_2.user_manager == 2000
        assert employee_2.managed_by == manager
        assert employee_2 in manager.manages


