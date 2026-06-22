-- MySQL Schema for NYC Taxi Analytics
-- Database: nytp

CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_rate_code (
    rate_code_id INTEGER PRIMARY KEY,
    rate_code_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_payment_type (
    payment_type_id INTEGER PRIMARY KEY,
    payment_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_id INTEGER PRIMARY KEY,
    borough VARCHAR(100) NOT NULL,
    zone VARCHAR(200) NOT NULL,
    service_zone VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_trip (
    trip_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INTEGER,
    tpep_pickup_datetime DATETIME NOT NULL,
    tpep_dropoff_datetime DATETIME NOT NULL,
    passenger_count INTEGER,
    trip_distance DECIMAL(10,2),
    rate_code_id INTEGER,
    store_and_fwd_flag CHAR(1),
    pulocation_id INTEGER,
    dolocation_id INTEGER,
    payment_type_id INTEGER,
    fare_amount DECIMAL(10,2),
    extra DECIMAL(10,2),
    mta_tax DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    tolls_amount DECIMAL(10,2),
    improvement_surcharge DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    congestion_surcharge DECIMAL(10,2),

    -- Derived features
    trip_duration_minutes DECIMAL(10,2),
    speed_mph DECIMAL(10,2),
    tip_percentage DECIMAL(10,2),
    hour_of_day INTEGER,
    is_weekend INTEGER,
    day_of_week INTEGER,
    month INTEGER,
    revenue_per_mile DECIMAL(10,2),

    FOREIGN KEY (vendor_id) REFERENCES dim_vendor(vendor_id),
    FOREIGN KEY (rate_code_id) REFERENCES dim_rate_code(rate_code_id),
    FOREIGN KEY (payment_type_id) REFERENCES dim_payment_type(payment_type_id),
    FOREIGN KEY (pulocation_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (dolocation_id) REFERENCES dim_location(location_id),

    INDEX idx_pickup (tpep_pickup_datetime),
    INDEX idx_pulocation (pulocation_id),
    INDEX idx_dolocation (dolocation_id),
    INDEX idx_vendor (vendor_id),
    INDEX idx_rate_code (rate_code_id),
    INDEX idx_payment (payment_type_id)
);

INSERT INTO dim_vendor (vendor_id, vendor_name) VALUES
    (1, 'Creative Mobile Technologies'),
    (2, 'VeriFone Inc.'),
    (4, 'Unknown Vendor');

INSERT INTO dim_rate_code (rate_code_id, rate_code_name) VALUES
    (1, 'Standard'),
    (2, 'JFK'),
    (3, 'Newark'),
    (4, 'Nassau/Westchester'),
    (5, 'Negotiated'),
    (6, 'Group Ride'),
    (99, 'Unknown');

INSERT INTO dim_payment_type (payment_type_id, payment_type_name) VALUES
    (1, 'Credit Card'),
    (2, 'Cash'),
    (3, 'No Charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided Trip');

-- Load locations from CSV:
-- LOAD DATA INFILE 'taxi_zone_lookup.csv'
-- INTO TABLE dim_location
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;
