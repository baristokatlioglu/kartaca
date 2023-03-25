from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
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

#### Task 1 : Print log for Starting Task
def start_log(dag_name):
    logging.info(f"{dag_name} DAG has been started")

#### Task 2 : Join tables and Write to data_merge table

def send_query():
    mycursor.execute("DROP TABLE IF EXISTS data_merge;")
    mydb.commit()
    mycursor.execute("CREATE TABLE IF NOT EXISTS data_merge(CountryID CHAR(2), CountryName VARCHAR(70), Currency VARCHAR(3));")
    mydb.commit()
    mycursor.execute("INSERT INTO data_merge (SELECT * FROM country as ctr JOIN currency as crn USING (CountryID));")
    mydb.commit()

    mydb.close()

#### Task 3 : Finish Log
def finish_log(dag_name):
    logging.info(f"{dag_name} DAG has been finished")


with DAG("data_merge", default_args=default_args, schedule_interval="10 10 * * *", catchup=False) as dag:

    trigger_dag = TriggerDagRunOperator(task_id="trigger_dependent_dag", trigger_dag_id="currency", wait_for_completion=True)

    start = PythonOperator(task_id="start_task", provide_context=True, python_callable=start_log, op_kwargs={'dag_name':'data_merge'})

    merge_task = PythonOperator(task_id="data_merge_task", python_callable=send_query)

    final = PythonOperator(task_id="final_task", provide_context=True, python_callable=finish_log, op_kwargs={'dag_name':'data_merge'})

    trigger_dag >> start >> merge_task >> final

