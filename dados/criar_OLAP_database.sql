-- cria banco dados
CREATE DATABASE loan;

-- Conecte ao banco de dados criado e execute as instruções SQL abaixo

-- Cria tabela client
CREATE TABLE client
(
    id SERIAL PRIMARY KEY,
    age INTEGER,
    job TEXT,
    marital TEXT,
    education TEXT,
    credit_default BOOLEAN,
    housing BOOLEAN,
    loan BOOLEAN
);

-- Cria tabela campaign
CREATE TABLE campaign
(
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    number_contacts INTEGER,
    contact_duration INTEGER,
    pdays INTEGER,
    previous_campaign_contacts INTEGER,
    previous_outcome BOOLEAN,
    campaign_outcome BOOLEAN,
    last_contact_date DATE    
);

-- Cria tabela economics
CREATE TABLE economics
(
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    emp_var_rate FLOAT,
    cons_price_idx FLOAT,
    euribor_three_months FLOAT,
    number_employed FLOAT
);

-- Cria o relacionamento entre as tabelas
ALTER TABLE campaign
ADD CONSTRAINT fk_campaign_client FOREIGN KEY (client_id) REFERENCES client(id);

ALTER TABLE economics
ADD CONSTRAINT fk_economics_client FOREIGN KEY (client_id) REFERENCES client(id);

-- Cria usuario airflow
CREATE USER airflow WITH
PASSWORD 'MyP@ssword';

-- Da Permissão ao usuario airflow de somente inserir registros
GRANT INSERT ON economics,campaign,client TO airflow;

-- Cria grupo data_analyst
CREATE ROLE data_analyst;

-- Da Permissão ao grupo data_analyst de somente consultar registros
GRANT SELECT ON economics,campaign,client TO data_analyst;

-- Criar usuario joao
CREATE USER joao WITH
PASSWORD 'MinhaSenha';

-- Adiciona o usuario joao ao grupo data_analyst
GRANT data_analyst TO joao;
