from models import ModelBase as Base
from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, Boolean, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, mapped_column, Mapped
from enum import Enum
from datetime import datetime


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

