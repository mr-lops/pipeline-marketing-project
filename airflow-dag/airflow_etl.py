# Importa pacotes que serão utilizados
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import load_dotenv
import os
from airflow import DAG
import airflow.utils.dates as airflow_date
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

# Pastas temporarias onde irão ficar os dados que foram extraidos e os dados que foram tratados.
staging = "tmp/staging/"
refined = "tmp/refined/"


# Carrega as variaveis de ambiente definidas no arquivo ".env"
load_dotenv()

# Função de extração dos dados do bucket S3
def _extract():
    import boto3
    import pathlib
    import glob
    import pandas as pd
    
    # Pegar as credenciais da conta AWS por meio de variaveis de ambiente
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    # Configura as credenciais de acesso à conta da AWS
    s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
    
    # Pegar o nome do bucket por meio de variaveis de ambiente
    bucket = s3.Bucket(os.environ.get('BUCKET_NAME'))
    
    # Cria diretorio para armazenar os arquivos baixados do bucket
    pathlib.Path(staging).mkdir(parents=True, exist_ok=True)
    
    # Baixa todos os arquivos .CSV que foram adicionados em um itervalo de 6 dias e meio atras e salva no diretorio criado anteriormente
    for obj in bucket.objects.all():
        if obj.key.lower().endswith('.csv') == True:
            hr_add = int((datetime.now(timezone('America/Sao_Paulo')) - obj.last_modified.astimezone(timezone('America/Sao_Paulo'))).seconds//3600)
            if hr_add < 156:
                print("Downloading: " + obj.key)
                bucket.download_file(obj.key, f'{staging}{obj.key}')
    
    # Cria um lista com todos os arquivos do tipo CSV que existem no diretorio definido na variavel staging
    joined_list = glob.glob(os.path.join(staging, "*.csv"))

    # Junta os arquivos CSV em um só arquivo
    df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
    df.to_csv(f"{staging}marketing.csv", index=False)
            
    

# Função de transformação dos dados, os deixando no padrão para serem enviados
def _transform():
    import pandas as pd
    import numpy as np
    import pathlib
    
    pathlib.Path(refined).mkdir(parents=True, exist_ok=True)
    
    # Lê o arquivo CSV criado na função anterior
    marketing = pd.read_csv(f"{staging}marketing.csv")

    # Separa os dados em 3 tabelas
    client = marketing.loc[:, ["client_id", "age", "job", "marital", "education", 
                "credit_default", "housing", "loan"]]
    campaign = marketing.loc[:, ["client_id", "campaign", "month", "day", 
                "duration", "pdays", "previous", "poutcome", "y"]]
    economics = marketing.loc[:, ["client_id", "emp_var_rate", "cons_price_idx", 
                    "euribor3m", "nr_employed"]]

    # Renomeia client_id na tabela client
    client.rename(columns={"client_id": "id"}, inplace=True)

    # Renomeia as colunas duration, y, campaign, previous e poutcome
    campaign.rename(columns={"duration": "contact_duration", 
                            "y": "campaign_outcome", 
                            "campaign": "number_contacts",
                            "previous": "previous_campaign_contacts",
                            "poutcome": "previous_outcome"}, 
                            inplace=True)

    # Renomeia as colunas euribor3m and nr_employed
    economics.rename(columns={"euribor3m": "euribor_three_months", 
                            "nr_employed": "number_employed"}, 
                            inplace=True)

    # Aplica transformações na coluna education
    client["education"] = client["education"].str.replace(".", "_")
    client["education"] = client["education"].replace("unknown", np.NaN)

    # Aplica transformações na coluna column
    client["job"] = client["job"].str.replace(".", "")

    # Troca os valores da coluna campaign_outcome para valores binarios
    campaign["campaign_outcome"] = campaign["campaign_outcome"].map({"yes": 1, 
                                                                    "no": 0})

    # Troca os valores da coluna previous_outcome para valores binarios e trata os valores nulos
    campaign["previous_outcome"] = campaign["previous_outcome"].replace("nonexistent", 
                                                                        np.NaN)
    campaign["previous_outcome"] = campaign["previous_outcome"].map({"success": 1, 
                                                                    "failure": 0})

    # Adiciona a coluna campaign_id
    campaign["campaign_id"] = 1

    # Padroniza a coluna month com a função capitalize
    campaign["month"] = campaign["month"].str.capitalize()

    # Adiciona a coluna year
    campaign["year"] = "2022"

    # Converte a coluna day para string
    campaign["day"] = campaign["day"].astype(str)

    # Cria a coluna last_contact_date e a converte para o tipo datetime
    campaign["last_contact_date"] = campaign["year"] + "-" + campaign["month"] + "-" + campaign["day"]
    campaign["last_contact_date"] = pd.to_datetime(campaign["last_contact_date"], 
                                                format="%Y-%b-%d")

    # Exclui colunas que não irão ser utilizadas
    campaign.drop(columns=["month", "day", "year"], inplace=True)

    # Salva as 3 tabelas em arquivos CSV no diretorio definido na variavel refined
    client.to_csv(f"{refined}client.csv", index=False)
    campaign.to_csv(f"{refined}campaign.csv", index=False)
    economics.to_csv(f"{refined}economics.csv", index=False)


# Função de carregamento dos dados ja transformados para o banco Postgres
def _load():
    import psycopg2
    import shutil
    # Conecta com o banco de dados Postgres
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port = os.environ.get('DB_PORT'))
    
    # Cria um cursor para executar as instruções SQL
    cur = conn.cursor()
    
    # Adiciona os dados dos arquivos csv para o banco de dados
    cur.execute(f"""
       \copy client from '{refined}client.csv' DELIMITER ',' CSV HEADER 
    """)
    cur.execute(f"""
       \copy campaign from '{refined}campaign.csv' DELIMITER ',' CSV HEADER 
    """)
    cur.execute(f"""
       \copy economics from '{refined}economics.csv' DELIMITER ',' CSV HEADER
    """)
    
    # Aplica as alterações no banco de dados
    conn.commit()
    
    # Fecha conexão com o banco de dados
    cur.close()
    conn.close()
    
    # remove pasta temporaria
    shutil.rmtree("tmp", ignore_errors=False, onerror=None)

# Cria uma Dag no Airflow
with DAG (
    dag_id="Pipeline ETL Marketing",
    description = 'Realiza a extração, tranformação e carga de dados de um bucket S3 para um banco de dados Postgres',
    start_date = airflow_date.days_ago(1),
    schedule_interval= "0 22 * * 6",
    tags=['Marketing','ETL'],
    
    
) as dag:
    
    # Cria a tarefa que realiza a extração dos dados do bucket S3
    extract = PythonOperator(
        task_id = 'extract_task',
        python_callable= _extract,
        email_on_failure= True,
        email = os.environ.get('EMAIL'),
        retries = 3,
        retry_delay = timedelta(minutes=5)
        
    )
    
    # Cria a tarefa que realiza a transformação dos dados
    transform = PythonOperator(
        task_id = 'transform_task',
        python_callable= _transform,
        email_on_failure= True,
        email = os.environ.get('EMAIL')
    )
    
    # Cria a tarefa que realiza o carregamento dos dados tratados para o banco de dados Postgres
    load = PythonOperator(
        task_id = 'load_task',
        python_callable= _load,
        email_on_failure= True,
        email = os.environ.get('EMAIL'),
        retries = 3,
        retry_delay = timedelta(minutes=5)
    )
    
    # Cria a tarefa que notifica por email que o pipeline foir realiza sem falhas
    notify = EmailOperator(
        task_id = 'notify_task',
        email_on_failure= True,
        email = os.environ.get('EMAIL'), 
        to= os.environ.get('EMAIL'),
        subject='Pipeline Realizado Com Sucesso',
        html_content=f"<p> O Pipeline foi executado com sucesso as {str(datetime.now(timezone('America/Sao_Paulo')))}. <p>"
    )
    
    # Define a ordem que as tarefas serão executadas
    extract >> transform >> load >> notify
