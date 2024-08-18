import json
import csv
from io import StringIO
from database import Session
from sqlalchemy.exc import IntegrityError
from models.db_info import DBInfo, DBClass
from models.employee import Employee
import schemas
import logging

logger = logging.getLogger(__name__)

#for testing only
def create_employee(db:Session, employee: schemas.EmployeeCreate):
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as e:
        logger.error(f"Integrity Error creating employee: {repr(e)}")
        return False
    logger.debug('employee created')
    return True

def parse_employee_from_raw(raw_employee):
    return Employee(
                int(raw_employee['user_id']),
                raw_employee['user_state'].lower() == 'true',
                str(raw_employee['user_mail']),
                int(raw_employee['user_manager'])
    )

def create_multiple_employees_from_raw(db: Session, raw_csv):
    raw_emp_csv = StringIO(raw_csv)
    csvReader = csv.DictReader(raw_emp_csv)
    new_employees = []
    for raw_employee in csvReader:
        new_employees.append(parse_employee_from_raw(raw_employee))
    db.add_all(new_employees)
    try:
        db.commit()
    except IntegrityError as e:
        logger.error(f"IntegrityError creating multiple employees from raw: {repr(e)}")
        db.rollback()
        return  {'success': False, 'error': repr(e).split('DETAIL')[1]}
    logger.debug(f"Successfully added {len(new_employees)} employees")
    return {'success': True}

#to facilitate testing
# def create_employee(db:Session, employee: schemas.EmployeeCreate):
def create_DBInfo(db:Session, db_info: schemas.DBInfoCreate):
    db.add(db_info)
    try:
        db.commit()
    except IntegrityError as e:
        logger.error(f"IntegrityError creating DBInfo: {repr(e)}")
        db.rollback()
        return False
    logger.debug('adding db_info to db')
    return True


# A field is valid iif:
# - Has all 3 required fields
# - Fields are not None
# - owner_id is not empty nor negative int
# - classification is withing valid range (currently: [0;3])
def validate_db_fields(db_info):
    required_fields = {'db_name': str, 'owner_id': int, 'classification': int}
    #Check all the fields are in the info with their respective type and that they are not None
    for key, expected_type in required_fields.items():
        if key not in db_info or db_info[key] is None or not isinstance(db_info[key], expected_type):
            logger.debug(f"entry missing key, key is none or is not the expected instance. Key: {key}")
            return False
    if db_info['owner_id'] <= 0:
        logger.debug('owner_id is less than 0')
        return False
    if db_info['classification'] not in DBClass._value2member_map_:
        logger.debug(f"classification outside boundaries. Original value was {db_info['classification']}")
        return False
    return db_info['owner_id'] != ''

#to simplify testing and creation
def aux_parse_db_info(entry):
    return DBInfo(
                 str(entry['db_name']) if entry['db_name'] is not None else '',
                 int(entry['owner_id']) if entry['owner_id'] is not None else 0,
                 DBClass(entry['classification']) if entry['classification'] is not None else DBClass.UNCLASSIFIED
    )

# Will throw HTTP 409 if an entry uses an un-existent owner_id
#Method will reject entries with missing or incorrect fields but will accept entries with correct fields and empty values
def create_multiple_db_info_from_raw(db: Session, raw_json):
    parsed_json = json.loads(raw_json)
    valid_entries = []
    invalid_entries = []
    for rd in parsed_json:
        if validate_db_fields(rd):
            valid_entries.append(aux_parse_db_info(rd))
        else:
            #invalids will be return as they came
            logger.debug('rejecting db_info because it is invalid')
            invalid_entries.append(rd)
    db.add_all(valid_entries)
    try:
        db.commit()
    except IntegrityError as e:
        logger.error(f"DB IntegrityError creating multiple db_info from raw json: {repr(e)}")
        db.rollback()
        return {'success': False, 'total': 0, 'error': repr(e).split('DETAIL')[1]}
    logger.debug(f"Adding {len(valid_entries)} db_info entries. Rejecting {len(invalid_entries)}")
    return {'success': True, 'total': len(valid_entries), 'valid_entries': valid_entries, 'invalid_entries': invalid_entries}

def get_unclassified_dbs(db: Session, response_model=list[schemas.DBInfo]):
    return db.query(DBInfo).filter_by(classification=DBClass.UNCLASSIFIED.value).all()
