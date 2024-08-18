import hashlib
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from enum import Enum
from datetime import datetime
from database import Base

class DBClass(Enum):
    UNCLASSIFIED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class DBInfo(Base):
    __tablename__ = 'db_info'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    db_name : Mapped[str] = mapped_column(String, nullable=False)
    owner_id : Mapped[int] = mapped_column(Integer, ForeignKey('employee.user_id'), nullable=False)
    classification : Mapped[DBClass] = mapped_column(Integer, nullable=False)

    #relationships
    is_owned : Mapped['Employee'] = relationship('Employee',  back_populates='owns')

    def __init__(self, db_name, owner_id, classification : DBClass):
        super().__init__()
        # if db_name is empty, create it using hash of: (timestamp;owner_id;classification), all non-None values
        if db_name == '':
            db_hash = f"{0};{1};{2}".format(int(datetime.timestamp(datetime.now())), owner_id, classification.value)
            self.db_name = str(hashlib.sha256(db_hash.encode('utf-8')).hexdigest())
        else:
            self.db_name = db_name
        self.owner_id = owner_id if owner_id is not None else 0
        self.classification = classification.value if classification is not None else DBClass.UNCLASSIFIED.value

    def __repr__(self):
        return f"<DBInfo(id={self.id}, db_name={self.db_name}, owner_id={self.owner_id}, classification={DBClass(self.classification).name})>"

