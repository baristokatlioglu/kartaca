from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import json
from urllib.request import urlopen
import mysql.connector

start_date = datetime.today() - timedelta(days=1)

# Deafult ARGs for DAG
default_args = {
    "owner": "kartaca",
    "start_date": start_date,
    "retries": 1,
    "retry_delay": timedelta(seconds=5)
}

# DB Connection
mydb = mysql.connector.connect(
    host="kartaca-db-1",
    user="kartaca",
    password="kartaca",
    database="kartaca"
)
mycursor = mydb.cursor()

# Task 1 : Print log for Starting Task
def start_log(dag_name):
    logging.info(f"{dag_name} DAG has been started")

# Task 2 : Read JSON file and assign to variable
def read_JSON_to_var():
    # Parse JSON from URL
    url = "http://country.io/names.json"
    response = urlopen(url)

    data_json = json.loads(response.read())

    return data_json

# Assing json to variable
global data
data = read_JSON_to_var()

# Task 3 : Modify Variable for insert process
def data_to_db():
    # Insert each item of JSON line by line
    for k, v in data.items():
        mycursor.execute("INSERT INTO country (CountryID, CountryName) VALUES (%s, %s)", (k,v))
        mydb.commit()

    mydb.close()
# Task 4 : Finish Log
def finish_log(dag_name):
    logging.info(f"{dag_name} DAG has been finished")


with DAG("country", default_args=default_args, schedule_interval="0 10 * * *", catchup=False) as dag:

    start = PythonOperator(task_id="start_task", provide_context=True, python_callable=start_log, op_kwargs={'dag_name':'Country'})

    readJSON = PythonOperator(task_id="Read_JSON", python_callable=read_JSON_to_var)

    insertDB = PythonOperator(task_id="Insert_DB", python_callable=data_to_db)

    final = PythonOperator(task_id="final_task", provide_context=True, python_callable=finish_log, op_kwargs={'dag_name':'Country'})

    start >> readJSON >> insertDB >> final

