from models.employee import Employee
from models.db_info import DBInfo, DBClass
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from database import Base, Session, engine
from crud import *
import schemas

Base.metadata.create_all(engine)
app = FastAPI()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

#Endpoint to upload csv of employees
#assumes this file's data is correct
@app.post('/employees/upload')
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    result = create_multiple_employees_from_raw(db, content.decode('utf-8'))
    if not result['success']:
        raise HTTPException(status_code=409, detail=result['error'])
    return result

#Endpoint to upload json with db data, data *can* be corrupted
@app.post('/db_info/upload')
async def upload_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    result = create_multiple_db_info_from_raw(db, content)
    if not result['success']:
        raise HTTPException(status_code=409, detail=result['error'])
    return {'number_of_records_added': result['total'], 'invalid_entries': result['invalid_entries']}

#Endpoint to get all unclassified dbs
@app.get('/db_info/unclassified')
def get_unclass_dbs(db: Session = Depends(get_db)):
    return get_unclassified_dbs(db)
