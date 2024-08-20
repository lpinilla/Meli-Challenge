from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from database import Base, Session, engine
from crud import create_multiple_employees_from_raw, create_multiple_db_info_from_raw, get_unclassified_dbs, notify_db_owners_manager
from typing import List
import logging
from schemas import DBInfo

Base.metadata.create_all(engine)
app = FastAPI()
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#Method to yield db session
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
    """
    Upload a CSV file containing employee data.

    This endpoint allows the user to upload a CSV file with information about employees. 
    It assumes that the data in the file is correct and will directly attempt to process 
    and store the data in the database.

    Parameters:
    - **file**: The CSV file to upload. The content should be properly formatted according to the expected schema.

    Returns:
    - A dictionary with the result of the upload operation, including details such as the number of records added.

    Raises:
    - **HTTPException (409)**: If there was an error processing the file, an exception is raised with details about the issue.

    Example:
    - A successful response might look like:
      ```
      {
        "success": true,
      }
      ```
    - If an error occurs, the response might look like:
      ```
      {
        "success": false,
        "detail": "Key (user_id)=(1) already exists.\\n')"
      }
      ```
    """
    logger.debug('endpoint /employees/upload called, creating employees from csv')
    content = await file.read()
    result = create_multiple_employees_from_raw(db, content.decode('utf-8'))
    if not result['success']:
        raise HTTPException(status_code=409, detail=result['error'])
    return result

#Endpoint to upload json with db data, data *can* be corrupted
@app.post('/db_info/upload')
async def upload_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a JSON file containing database information.

    This endpoint allows the user to upload a JSON file that contains information about databases.
    The data in the file may contain corrupt entries. The endpoint will attempt to process as much valid data as possible.

    Parameters:
    - **file**: The JSON file to upload. Must be in a valid JSON format.

    Returns:
    - **number_of_records_added** (int): The number of valid database records successfully added to the database.
    - **invalid_entries** (int): The number of invalid entries in the JSON file that could not be processed.

    Raises:
    - **HTTPException (409)**: If there was an error processing the file, an exception is raised with details about the issue.

    Example:
    - A successful response might look like:
      ```
      {
        "success": true,
        "total": 10,
        "valid_entries": [...]
        "invalid_entries": []
      }
      ```
    - If an error occurs, the response might look like:
      ```
      {
        "success": false,
        "total": 0,
        "detail": "Key (owner_id)=(1) does not exist.\\n')"
      }

      ```
    """
    logger.debug('endpoint /db_info/upload called, creating db_info from json')
    content = await file.read()
    result = create_multiple_db_info_from_raw(db, content)
    if not result['success']:
        raise HTTPException(status_code=409, detail=result['error'])
    return {'number_of_records_added': result['total'], 'invalid_entries': result['invalid_entries']}

#Endpoint to get all unclassified dbs
@app.get('/db_info/unclassified', response_model=List[DBInfo])
def get_unclass_dbs(db: Session = Depends(get_db)):
    """
    Get all unclassified databases.

    This endpoint retrieves a list of all databases that are currently unclassified.
    It's useful for identifying databases that haven't been categorized yet.

    Returns:
    - A list of `DBInfo` objects representing unclassified databases.

    Example:
    - A successful response might look like:
      ```
      [
        {
          "id": 1,
          "owner_id": 21,
          "db_name": "example_db",
          "classification": 0,
        },
        ...
      ]
      ```
    """
    logger.debug('endpoint /db_info/unclassified called')
    return get_unclassified_dbs(db)

#Endpoint to notify high-classified-db owner's managers that they should review the db
@app.post('/notify')
def notify(db: Session = Depends(get_db)):
    """
    Notify high-classified database owner's managers to review the database.

    This endpoint sends notifications to the managers of owners of high-classified databases,
    prompting them to review the respective databases. If there are any issues with the emails sent,
    it returns a list of recipients with errors.

    Returns:
    - **success** (bool): Indicates whether all notifications were sent successfully.
    - **recipients_with_errors** (Optional[List[str]]): A list of email addresses that encountered errors during notification.

    Example:
    - A successful response: `{"success": true}`
    - A failure response with errors: `{"success": false, "recipients_with_errors": ["email1@example.com", "email2@example.com"]}`
    """
    logger.debug('endpoint /notify called')
    emails_with_errors = notify_db_owners_manager(db)
    if len(emails_with_errors) == 0:
        return {'success': True}
    else:
        return {'success': False, 'recipients_with_errors': emails_with_errors}
