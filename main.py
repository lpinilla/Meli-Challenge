import csv
import json
from io import StringIO
from types import SimpleNamespace
from models.employee import Employee
from models.db_info import DBInfo, DBClass
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from database import Base, Session, engine

Base.metadata.create_all(engine)
app = FastAPI()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

#Endpoint to upload csv of employees
@app.post('/csv')
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    #assumes this file is correct
    content = await file.read()
    csv_raw = StringIO(content.decode('utf-8'))
    csvReader = csv.DictReader(csv_raw)
    employees = []
    for r in csvReader:
        employees.append(Employee(int(r['user_id']), bool(r['user_state']), str(r['user_mail']), int(r['user_manager'])))
    db.add_all(employees)
    db.commit()

#basic validation: all fields are correct
def validate_db_data(db_info):
    required_fields = {'db_name': str, 'owner_id': int, 'classification': int}
    for key, expected_type in required_fields.items():
        if key not in db_info or not isinstance(db_info[key], expected_type):
            return False
    return True


#Endpoint to upload json with db data, data *can* be corrupted
@app.post('/json')
async def upload_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    json_raw = json.loads(content)
    valid_entries = []
    invalid_entries = []
    for rd in json_raw:
        if validate_db_data(rd):
            valid_entries.append(
                    DBInfo(str(rd['db_name']),int(rd['owner_id']),DBClass(rd['classification']))
            )
        else:
            invalid_entries.append(rd)
    db.add_all(valid_entries)
    db.commit()
    db.close()
    return invalid_entries

