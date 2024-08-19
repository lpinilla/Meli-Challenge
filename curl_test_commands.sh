#csv
curl -X POST localhost:8080/employees/upload -F "file=@./employee_data.csv"

#json
curl -X POST localhost:8080/db_info/upload -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@./dbs_data.json"

#get unclassified
curl localhost:8080/db_info/unclassified
