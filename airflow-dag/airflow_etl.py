import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
from airflow import DAG
import airflow.utils.dates as airflow_date
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

load_dotenv()

#os.environ.get('DB_NAME')

default_agrs = {
    'description' : 'Realiza a extração, tranformação e carga de dados de um bucket S3 para um banco de dados Postgres',
    'start_date' : airflow_date.days_ago(7),
}

with DAG (
    dag_id="Pipeline ETL Marketing",
    default_args= default_agrs,
    schedule_interval= "0 22 * * 6",
    tags=['Marketing','ETL'],
    
    
) as dag:
    
    extract = PythonOperator(
        task_id = 'extract_task'
    )
    
    transform = PythonOperator(
        task_id = 'tansform_task'
    )
    
    load = PythonOperator(
        task_id = 'load_task'
    )
    
    notify = EmailOperator(
        task_id = 'notify_task'
    )
    
    extract >> transform >> load >> notify
    
