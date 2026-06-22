from sqlalchemy import text
from sqlalchemy.engine import Engine


def create_schema(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()

    tables = [
        """
        CREATE TABLE IF NOT EXISTS dim_vendor (
            vendor_id INTEGER PRIMARY KEY,
            vendor_name TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dim_rate_code (
            rate_code_id INTEGER PRIMARY KEY,
            rate_code_name TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dim_payment_type (
            payment_type_id INTEGER PRIMARY KEY,
            payment_type_name TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dim_location (
            location_id INTEGER PRIMARY KEY,
            borough TEXT NOT NULL,
            zone TEXT NOT NULL,
            service_zone TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS fact_trip (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            tpep_pickup_datetime TEXT NOT NULL,
            tpep_dropoff_datetime TEXT NOT NULL,
            passenger_count INTEGER,
            trip_distance REAL,
            rate_code_id INTEGER,
            store_and_fwd_flag TEXT,
            pulocation_id INTEGER,
            dolocation_id INTEGER,
            payment_type_id INTEGER,
            fare_amount REAL,
            extra REAL,
            mta_tax REAL,
            tip_amount REAL,
            tolls_amount REAL,
            improvement_surcharge REAL,
            total_amount REAL,
            congestion_surcharge REAL,

            trip_duration_minutes REAL,
            speed_mph REAL,
            tip_percentage REAL,
            hour_of_day INTEGER,
            is_weekend INTEGER,
            day_of_week INTEGER,
            month INTEGER,
            revenue_per_mile REAL,

            FOREIGN KEY (vendor_id) REFERENCES dim_vendor(vendor_id),
            FOREIGN KEY (rate_code_id) REFERENCES dim_rate_code(rate_code_id),
            FOREIGN KEY (payment_type_id) REFERENCES dim_payment_type(payment_type_id),
            FOREIGN KEY (pulocation_id) REFERENCES dim_location(location_id),
            FOREIGN KEY (dolocation_id) REFERENCES dim_location(location_id)
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_pickup ON fact_trip(tpep_pickup_datetime)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_pulocation ON fact_trip(pulocation_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_dolocation ON fact_trip(dolocation_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_vendor ON fact_trip(vendor_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_rate_code ON fact_trip(rate_code_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_trip_payment ON fact_trip(payment_type_id)
        """,
    ]

    log_table = """
        CREATE TABLE IF NOT EXISTS pipeline_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage TEXT NOT NULL,
            description TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            sample TEXT DEFAULT '',
            timestamp TEXT NOT NULL
        )
        """
    tables.append(log_table)

    with engine.begin() as conn:
        for table_sql in tables:
            conn.execute(text(table_sql))
