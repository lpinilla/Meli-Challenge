import csv
from io import StringIO
from sqlalchemy.orm import Session
from models.db_info import DBInfo, DBClass
from models.employee import Employee
import schemas

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
    db.commit()
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
    db.commit()
    return new_employees

