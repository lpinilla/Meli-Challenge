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
#assumes this file is correct
@app.post('/csv')
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read(encoding='utf-8')
    crud.create_multiple_employees_from_raw(content)

#Endpoint to upload json with db data, data *can* be corrupted
@app.post('/json')
async def upload_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    create_multiple_db_info_from_raw(content)
    return {'invalid_entries': invalid_entries}

