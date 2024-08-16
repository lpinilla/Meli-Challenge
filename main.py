import os
import csv
import json
from models.models import Employee, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker

DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

db = create_engine("postgresql://%s:%s@%s:%s/%s" % (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME))
Session = sessionmaker(bind=db)
Base.metadata.create_all(db)


employees = []

#read csv
with open('employee_data.csv', encoding='utf-8') as f:
        csvReader = csv.DictReader(f)
        for r in csvReader:
            employees.append(Employee(int(r['user_id']), bool(r['user_state']), str(r['user_mail']), int(r['user_manager'])))
            session = Session()
            session.add_all(employees)
            session.commit()
            session.close()

