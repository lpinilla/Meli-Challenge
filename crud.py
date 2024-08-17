import json
import csv
from io import StringIO
from database import Session
from sqlalchemy.exc import IntegrityError
from models.db_info import DBInfo, DBClass
from models.employee import Employee
import schemas

#for testing only
def create_employee(db:Session, employee: schemas.EmployeeCreate):
    new_employee = Employee(employee.user_id, employee.user_state, employee.user_mail, employee.user_manager)
    db.add(new_employee)
    try:
        db.commit()
    except IntegrityError as e:
        return None
    return new_employee

#for testing only
#no schema as it is raw
#assumes *this* data is correct and not corrupted
def create_employee_from_raw(db: Session, raw_csv):
    raw_emp_csv = StringIO(raw_csv)
    csvReader = csv.DictReader(raw_emp_csv)
    raw_employee = next(csvReader)
    new_employee =  Employee(
            int(raw_employee['user_id']),
            bool(raw_employee['user_state']),
            str(raw_employee['user_mail']),
            int(raw_employee['user_manager']))
    db.add(new_employee)
    try:
        db.commit()
    except IntegrityError as e:
        return None
    return new_employee

def create_multiple_employees_from_raw(db: Session, raw_csv):
    raw_emp_csv = StringIO(raw_csv)
    csvReader = csv.DictReader(raw_emp_csv)
    new_employees = []
    for raw_employee in csvReader:
        new_employees.append(Employee(
                int(raw_employee['user_id']),
                raw_employee['user_state'].lower() == 'true',
                str(raw_employee['user_mail']),
                int(raw_employee['user_manager']))
        )
    db.add_all(new_employees)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return  {'success': False, 'error': repr(e).split('DETAIL')[1]}
    return {'success': True}

# A field is valid iif:
# - Has all 3 required fields
# - db_name and owner_id are not empty or None at the same time
def validate_db_fields(db_info):
    required_fields = ['db_name', 'owner_id', 'classification']
    return all(k in db_info.keys() for k in required_fields) and any([db_info['db_name'], db_info['owner_id']])

#to simplify testing and creation
def aux_parse_db_info(entry):
    return DBInfo(
                 str(entry['db_name']) if entry['db_name'] is not None else '',
                 int(entry['owner_id']) if entry['owner_id'] is not None else 0,
                 DBClass(entry['classification']) if entry['classification'] is not None else DBClass.UNCLASSIFIED
    )

#to facilitate testing
def create_db_info_from_raw(db: Session, raw_json):
    parsed_json = json.loads(raw_json)
    if not validate_db_fields(parsed_json): return None
    valid_db_info = aux_parse_db_info(parsed_json)
    db.add(valid_db_info)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return {'success': False, 'error': repr(e).substring('DETAIL')[1]}
    return {'success': True}

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
            invalid_entries.append(rd)
    db.add_all(valid_entries)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return {'success': False, 'total': 0, 'error': repr(e).split('DETAIL')[1]}
    return {'success': True, 'total': len(valid_entries), 'valid_entries': valid_entries, 'invalid_entries': invalid_entries}

