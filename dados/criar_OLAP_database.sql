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
    campaign_id SERIAL PRIMARY KEY,
    client_id SERIAL references client (id),
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
    client_id SERIAL references client (id),
    emp_var_rate FLOAT,
    cons_price_idx FLOAT,
    euribor_three_months FLOAT,
    number_employed FLOAT
);

client_id SERIAL references client (id),
client_id SERIAL references client (id),