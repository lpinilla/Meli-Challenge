from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from database import Base

class Employee(Base):
    __tablename__ = 'employee'

    id : Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id : Mapped[int] = mapped_column(Integer, unique=True)
    user_state : Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_manager : Mapped[int] = mapped_column(Integer, ForeignKey('employee.user_id'), nullable=True)
    user_mail : Mapped[str] = mapped_column(String(100), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, nullable=False)

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

