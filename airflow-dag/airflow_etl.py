# Importa pacotes que serão utilizados
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import load_dotenv
import os
from airflow import DAG
import airflow.utils.dates as airflow_date
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

# Carrega as variaveis de ambiente definidas no arquivo ".env"
load_dotenv()

# Função de extração dos dados do bucket S3
def _extract():
    pass

# Função de transformação dos dados, os deixando no padrão para serem enviados
def _transform():
    pass

# Função de carregamento dos dados ja transformados para o banco Postgres
def _load():
    
    # Conecta com o banco de dados Postgres
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port = os.environ.get('DB_PORT'))
    
    # Cria um cursos para executar as instruções SQL
    cur = conn.cursor()

with DAG (
    dag_id="Pipeline ETL Marketing",
    description = 'Realiza a extração, tranformação e carga de dados de um bucket S3 para um banco de dados Postgres',
    start_date = airflow_date.days_ago(1),
    schedule_interval= "0 22 * * 6",
    tags=['Marketing','ETL'],
    
    
) as dag:
    
    extract = PythonOperator(
        task_id = 'extract_task',
        python_callable= _extract,
        email_on_failure= True,
        email = os.environ.get('EMAIL'),
        retries = 3,
        retry_delay = timedelta(minutes=5)
        
    )
    
    transform = PythonOperator(
        task_id = 'tansform_task',
        python_callable= _transform,
        email_on_failure= True,
        email = os.environ.get('EMAIL')
    )
    
    load = PythonOperator(
        task_id = 'load_task',
        python_callable= _load,
        email_on_failure= True,
        email = os.environ.get('EMAIL'),
        retries = 3,
        retry_delay = timedelta(minutes=5)
    )
    
    notify = EmailOperator(
        task_id = 'notify_task',
        email_on_failure= True,
        email = os.environ.get('EMAIL'), 
        to= os.environ.get('EMAIL'),
        subject='Pipeline Realizado Com Sucesso',
        html_content=f"<p> O Pipeline foi executado com sucesso as {str(datetime.now(timezone('America/Sao_Paulo')))}. <p>"
    )
    
    extract >> transform >> load >> notify
    
