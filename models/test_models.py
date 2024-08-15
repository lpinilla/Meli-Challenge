import os
import pytest
from .models import Employee, Base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, event

DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

db = create_engine("postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME))
Session = sessionmaker(bind=db)


@pytest.fixture(scope='module')
def db_session():
    Base.metadata.create_all(db)
    connection = db.connect()
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

@pytest.fixture(scope="module")
def valid_employee():
    valid_employee = Employee(
            user_id=1,
            user_state=True,
            user_mail='test@gmail.com',
            user_manager=1
    )
    return valid_employee


class TestEmployee:

    def test_valid_employee(self, db_session, valid_employee):
        db_session.add(valid_employee)
        db_session.commit()
        employee = db_session.query(Employee).filter_by(user_id=1).first()
        assert employee.user_id == 1
        assert employee.user_state == True
        assert employee.user_mail == 'test@gmail.com'
        assert employee.user_manager == 1

    @pytest.mark.xfail(raises=IntegrityError)
    def test_no_email(self,db_session):
        employee = Employee(
                user_id=1,
                user_state = True,
                user_mail = None,
                user_manager=1
                )
        db_session.add(employee)
        try:
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
