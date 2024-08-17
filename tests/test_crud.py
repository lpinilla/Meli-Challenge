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

@pytest.fixture(scope='module')
def valid_db_info_raw_entry():
    return '[{"db_name": "Brown, Duncan and Munoz_db", "owner_id": 3000, "classification": 2}]'

@pytest.fixture(scope='module')
def valid_db_info_object():
    return { 'db_name': 'testDB', 'owner_id': 3000, 'classification': DBClass.LOW}



class TestCrud:

    def test_crud_create_employee_from_raw(self, db_session, valid_employee_raw_string):
        crud_created_user = create_employee_from_raw(db_session, valid_employee_raw_string)
        employee = db_session.query(Employee).filter_by(user_id=1000).first()
        assert crud_created_user == employee
        assert employee.user_id == 1000
        assert employee.user_state == True
        assert employee.user_mail == 'crystal21@company.com'
        assert employee.user_manager == 1000

    def test_crud_create_employee(self, db_session):
        create_employee(db_session, Employee(1001, True, 'db_owner@company.com', 1001))
        db_owner = db_session.query(Employee).filter_by(user_id=1001).first()
        assert db_owner.user_id == 1001
        assert db_owner.user_state == True
        assert db_owner.user_mail == 'db_owner@company.com'
        assert db_owner.user_manager == 1001


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

    def test_crud_create_multiple_db_info_from_raw(self, db_session, valid_db_info_raw_entry):
        #create employee owner of db
        create_employee(db_session, Employee(3000, True, 'db_owner@company.com', 3000))
        db_owner = db_session.query(Employee).filter_by(user_id=3000).first()
        valid_entries, invalid_entries = create_multiple_db_info_from_raw(db_session, valid_db_info_raw_entry)
        assert len(invalid_entries) == 0
        assert len(valid_entries) == 1
        db_info_from_db = db_session.query(DBInfo).filter_by(db_name='Brown, Duncan and Munoz_db').first()
        assert db_info_from_db.db_name == 'Brown, Duncan and Munoz_db'
        assert db_info_from_db.owner_id == db_owner.user_id
        assert DBClass(db_info_from_db.classification) == DBClass.MEDIUM

    def test_crud_aux_parse_db_info(self, db_session, valid_db_info_object):
        parsed = aux_parse_db_info(valid_db_info_object)
        assert parsed is not None
        assert parsed.db_name == valid_db_info_object['db_name']
        assert parsed.owner_id == valid_db_info_object['owner_id']
        assert DBClass(parsed.classification) == valid_db_info_object['classification']

