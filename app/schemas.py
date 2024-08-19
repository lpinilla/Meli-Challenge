from models.db_info import DBClass
from pydantic import BaseModel, ConfigDict

class EmployeeBase(BaseModel):
    user_id: int
    user_state: bool
    user_manger: int
    user_mail: str

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    user_id: int
    user_state: bool
    user_manger: int
    user_mail: str
    created_at: int

    class ConfigDict:
        from_attributes=True

class DBInfoBase(BaseModel):
    db_name: str
    owner_id: int
    classification: int

class DBInfoCreate(DBInfoBase):
    pass

class DBInfo(DBInfoBase):
    id: int
    db_name: str
    owner_id: int
    classification: int

    class ConfigDict:
        from_attributes=True
