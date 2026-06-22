import os
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.database.connection import get_engine, DB_PATH
from src.database.schema import create_schema
from src.pipeline.clean import cleaning_pipeline, load_dim_locations, log_action, get_cleaning_log

DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
TRIP_CSV = os.path.join(DATA_DIR, "yellow_tripdata_2019.csv")
ZONE_CSV = os.path.join(DATA_DIR, "taxi_zone_lookup.csv")


def load_dimensions(engine: Engine) -> None:
    vendors = [
        {"vendor_id": 1, "vendor_name": "Creative Mobile Technologies"},
        {"vendor_id": 2, "vendor_name": "VeriFone Inc."},
        {"vendor_id": 4, "vendor_name": "Unknown Vendor"},
    ]
    rate_codes = [
        {"rate_code_id": 1, "rate_code_name": "Standard"},
        {"rate_code_id": 2, "rate_code_name": "JFK"},
        {"rate_code_id": 3, "rate_code_name": "Newark"},
        {"rate_code_id": 4, "rate_code_name": "Nassau/Westchester"},
        {"rate_code_id": 5, "rate_code_name": "Negotiated"},
        {"rate_code_id": 6, "rate_code_name": "Group Ride"},
        {"rate_code_id": 99, "rate_code_name": "Unknown"},
    ]
    payment_types = [
        {"payment_type_id": 1, "payment_type_name": "Credit Card"},
        {"payment_type_id": 2, "payment_type_name": "Cash"},
        {"payment_type_id": 3, "payment_type_name": "No Charge"},
        {"payment_type_id": 4, "payment_type_name": "Dispute"},
        {"payment_type_id": 5, "payment_type_name": "Unknown"},
        {"payment_type_id": 6, "payment_type_name": "Voided Trip"},
    ]

    locations = load_dim_locations(ZONE_CSV)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fact_trip"))
        conn.execute(text("DELETE FROM dim_location"))
        conn.execute(text("DELETE FROM dim_vendor"))
        conn.execute(text("DELETE FROM dim_rate_code"))
        conn.execute(text("DELETE FROM dim_payment_type"))

        for v in vendors:
            conn.execute(text("INSERT INTO dim_vendor (vendor_id, vendor_name) VALUES (:vid, :vn)"), {"vid": v["vendor_id"], "vn": v["vendor_name"]})
        for rc in rate_codes:
            conn.execute(text("INSERT INTO dim_rate_code (rate_code_id, rate_code_name) VALUES (:id, :name)"), {"id": rc["rate_code_id"], "name": rc["rate_code_name"]})
        for pt in payment_types:
            conn.execute(text("INSERT INTO dim_payment_type (payment_type_id, payment_type_name) VALUES (:id, :name)"), {"id": pt["payment_type_id"], "name": pt["payment_type_name"]})
        for loc in locations:
            conn.execute(text("INSERT INTO dim_location (location_id, borough, zone, service_zone) VALUES (:id, :b, :z, :sz)"),
                         {"id": loc["location_id"], "b": loc["borough"], "z": loc["zone"], "sz": loc["service_zone"]})

    log_action("load", f"Loaded {len(vendors)} vendors, {len(rate_codes)} rate codes, {len(payment_types)} payment types, {len(locations)} locations", engine=engine)


def load_trips(engine: Engine, max_chunks: int = None) -> int:
    from sqlalchemy import Table, MetaData, Column, Integer, String, Float

    total_inserted = 0
    chunk_count = 0

    metadata = MetaData()
    fact_trip = Table(
        "fact_trip", metadata,
        Column("trip_id", Integer, primary_key=True),
        autoload_with=engine,
    )

    for chunk in cleaning_pipeline(TRIP_CSV):
        if max_chunks and chunk_count >= max_chunks:
            break

        with engine.begin() as conn:
            conn.execute(fact_trip.insert(), chunk)
        total_inserted += len(chunk)
        chunk_count += 1
        log_action("load", f"Inserted chunk {chunk_count}: {len(chunk)} trips (total: {total_inserted})", engine=engine)

    log_action("load", f"Finished loading {total_inserted} trip records", engine=engine)
    return total_inserted


def run_pipeline(engine=None, max_chunks: int = None) -> Engine:
    if engine is None:
        engine = get_engine()
    print(f"Database: {DB_PATH}")
    print("Creating schema...")
    create_schema(engine)
    print("Loading dimension tables...")
    load_dimensions(engine)
    print("Loading trip data...")
    count = load_trips(engine, max_chunks=max_chunks)
    print(f"Done. Loaded {count} trips.")
    return engine


if __name__ == "__main__":
    run_pipeline()
