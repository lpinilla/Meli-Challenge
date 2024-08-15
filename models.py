import os
from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, Boolean, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, mapped_column, Mapped
from sqlalchemy.exc import IntegrityError
from enum import Enum
from datetime import datetime
import pytest

DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

db = create_engine("postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME))
Session = sessionmaker(bind=db)
Base = declarative_base()

# Modelo empleado
class Employee(Base):
    __tablename__ = 'employee'

    id : Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id = Column(Integer, unique=True)
    user_state = Column(Boolean, nullable=False)
    user_manager = Column(Integer, ForeignKey('employee.user_id'), nullable=True)
    user_mail = Column(String(100), nullable=False)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)

    #relationships
    managed_by : Mapped['Employee'] = relationship('Employee', remote_side='Employee.user_id', back_populates='manages')
    manages : Mapped[list['Employee']] = relationship('Employee', back_populates='managed_by')
    owns :  Mapped[list['DBInfo']] = relationship('DBInfo', back_populates='is_owned')



    def __init__(self, user_id, user_state, user_mail, user_manager):
        super().__init__()
        self.user_id = user_id
        self.user_state = user_state
        self.user_mail = user_mail
        self.user_manager = user_manager

    def __repr__(self):
        return f"<Employee(id={self.id}, user_id={self.user_id}, user_state={user_state}, user_mail={self.user_mail}, user_manager={self.user_manager})>"

class DBClass(Enum):
    UNCLASSIFIED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class DBInfo(Base):
    __tablename__ = 'db_info'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    db_name : Mapped[str] = mapped_column(String, nullable=False)
    owner_id : Mapped[int] = mapped_column(Integer, ForeignKey('employee.user_id'), nullable=False)
    classification : Mapped[DBClass] = mapped_column(Integer, nullable=False)

    #relationships
    is_owned : Mapped['Employee'] = relationship('Employee',  back_populates='owns')

    def __init__(self, db_name, owner_id, classification : DBClass):
        super().__init__()
        self.db_name = db_name
        self.owner_id = owner_id
        self.classification = classification.value

    def __repr__(self):
        return f"<DBInfo(row_id={self.id}, user_id={self.db_name}, owner_id={self.owner_id}, classification={DBClass(self.classification).name})>"

# Creando modelos
#Base.metadata.create_all(db)

#with Session.begin() as session:
#    manager = Employee(1, True, 'pepito@gmail.com', 1)
#    employee1 = Employee(2, True, 'manolito@gmail.com', 1)
#    employee2 = Employee(3, True, 'fulanito@gmail.com', 1)
#    db_info = DBInfo('test_db', employee1.user_id, 1)
#    session.add_all([manager, employee1, employee2, db_info])
#    db_info = DBInfo('test_db3', 1, DBClass.LOW)
#    session.add(db_info)
#    print(session.query(DBInfo).filter_by(db_name='test_db2').first())
#    session.commit()

###########
#  TESTS  #
###########

@pytest.fixture(scope='session')
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
