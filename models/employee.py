from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, Boolean, event
from sqlalchemy.orm import relationship, sessionmaker, mapped_column, Mapped
from datetime import datetime
from . import ModelBase as Base

#Base = declarative_base()

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
        return f"<Employee(id={self.id}, user_id={self.user_id}, user_state={self.user_state}, user_mail={self.user_mail}, user_manager={self.user_manager})>"

