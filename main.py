import os
import csv
import json
from types import SimpleNamespace
from models import ModelBase as Base
from models.employee import Employee
from models.db_info import DBInfo, DBClass
from fastapi import Depends, FastAPI, HTTPException

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
app = FastAPI()
#session = Session()                                                          
                                                                              
employees = []                                                                
db_info = []                                                                  
                                                                              
#read csv                                                                     
with open('employee_data.csv', encoding='utf-8') as f:                        
    csvReader = csv.DictReader(f)
    for r in csvReader:
        employees.append(Employee(int(r['user_id']), bool(r['user_state']), str(r['user_mail']), int(r['user_manager'])))

session.add_all(employees)

def validate_db_data(db_info):
    required_fields = {'db_name': str, 'owner_id': int, 'classification': int}
    for key, expected_type in required_fields.items():
        if key not in db_info or not isinstance(db_info[key], expected_type):
            return False
    return True

raw_data = json.load(open('dbs_data.json', encoding='utf-8'))
valid_entries = []
invalid_entries = []
for rd in raw_data:
    if validate_db_data(rd):
        valid_entries.append(
                DBInfo(
                    str(rd['db_name']),
                    int(rd['owner_id']),
                    DBClass(rd['classification'])
                )
        )
    else:
        invalid_entries.append(rd)

session.add_all(valid_entries)
session.commit()
session.close()

