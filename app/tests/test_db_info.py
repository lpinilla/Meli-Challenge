import pytest
from models.db_info import DBInfo, DBClass
from models.employee import Employee
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from database import Base, engine

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
def valid_db_entry():
    valid_entry = DBInfo(
        db_name='test_db',
        owner_id=1000,
        classification=DBClass.LOW
    )
    return valid_entry

@pytest.fixture(scope="module")
def valid_employee():
    valid_employee = Employee(
            user_id=1000,
            user_state=True,
            user_mail='test@gmail.com',
            user_manager=1000
    )
    return valid_employee

#Testing DBInfo, assuming Employee model works
class TestDBInfo:

    def test_valid_entry(self, db_session, valid_employee, valid_db_entry):
        db_session.add(valid_employee)
        db_session.add(valid_db_entry)
        db_session.commit()
        db_info = db_session.query(DBInfo).filter_by(owner_id=1000).first()
        assert db_info.db_name == 'test_db'
        assert db_info.owner_id == 1000
        assert DBClass(db_info.classification) == DBClass.LOW
