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


CREATE TABLE economics
(
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    emp_var_rate FLOAT,
    cons_price_idx FLOAT,
    euribor_three_months FLOAT,
    number_employed FLOAT
);

ALTER TABLE campaign
ADD CONSTRAINT fk_campaign_client FOREIGN KEY (client_id) REFERENCES client(id);

ALTER TABLE economics
ADD CONSTRAINT fk_economics_client FOREIGN KEY (client_id) REFERENCES client(id);