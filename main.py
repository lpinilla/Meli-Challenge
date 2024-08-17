import json
from types import SimpleNamespace
from models.employee import Employee
from models.db_info import DBInfo, DBClass
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from database import Base, Session, engine
from crud import *

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
    content = await file.read(encoding='utf-8')
    crud.create_multiple_employees_from_raw(content)

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
    db.commit() # TODO: va a fallar si no hay datos de empleado
    db.close()
    return invalid_entries

