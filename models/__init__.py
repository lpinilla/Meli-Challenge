from sqlalchemy.orm import DeclarativeBase

class ModelBase(DeclarativeBase):
    pass


from .employee import Employee
from .db_info import DBInfo, DBClass
