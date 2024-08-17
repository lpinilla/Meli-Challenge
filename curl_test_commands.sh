#csv
curl -X POST localhost:8000/csv -F "file=@./employee_data.csv"

#json
curl -X POST localhost:8000/json -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@./dbs_data.json"
