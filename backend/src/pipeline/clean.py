import csv
import os
from datetime import datetime
from typing import Iterator, Optional

DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

CLEANING_LOG: list[dict] = []

def log_action(stage: str, description: str, count: int = 0, sample: str = "", engine=None) -> None:
    entry = {
        "stage": stage,
        "description": description,
        "count": count,
        "sample": sample,
        "timestamp": datetime.now().isoformat(),
    }
    CLEANING_LOG.append(entry)
    if engine is not None:
        try:
            from sqlalchemy import text
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO pipeline_log (stage, description, count, sample, timestamp) VALUES (:s, :d, :c, :sm, :ts)"),
                    {"s": stage, "d": description, "c": count, "sm": sample, "ts": entry["timestamp"]}
                )
        except Exception:
            pass

def parse_datetime(val: str) -> Optional[datetime]:
    if not val or val.strip() == "":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except ValueError:
            continue
    return None

def is_valid_record(row: dict) -> tuple[bool, str]:
    pickup = parse_datetime(row.get("tpep_pickup_datetime", ""))
    dropoff = parse_datetime(row.get("tpep_dropoff_datetime", ""))

    if pickup is None or dropoff is None:
        return False, "invalid_datetime"

    if dropoff <= pickup:
        return False, "dropoff_before_pickup"

    try:
        passenger_count = int(float(row.get("passenger_count", 0)))
    except (ValueError, TypeError):
        passenger_count = 0

    try:
        trip_distance = float(row.get("trip_distance", 0))
    except (ValueError, TypeError):
        trip_distance = 0.0

    try:
        fare_amount = float(row.get("fare_amount", 0))
    except (ValueError, TypeError):
        fare_amount = 0.0

    try:
        total_amount = float(row.get("total_amount", 0))
    except (ValueError, TypeError):
        total_amount = 0.0

    try:
        pulocation = int(float(row.get("PULocationID", 0)))
        dolocation = int(float(row.get("DOLocationID", 0)))
    except (ValueError, TypeError):
        return False, "invalid_location"

    if passenger_count < 0:
        return False, "negative_passenger"
    if trip_distance < 0:
        return False, "negative_distance"
    if fare_amount < 0:
        return False, "negative_fare"

    if trip_distance > 100:
        return False, "excessive_distance"
    if fare_amount > 500:
        return False, "excessive_fare"
    if total_amount > 1000:
        return False, "excessive_total"

    if pulocation < 1 or dolocation < 1 or pulocation > 265 or dolocation > 265:
        return False, "invalid_location_id"

    return True, "valid"


def clean_row(row: dict) -> dict:
    pickup = parse_datetime(row.get("tpep_pickup_datetime", ""))
    dropoff = parse_datetime(row.get("tpep_dropoff_datetime", ""))

    duration_min = (dropoff - pickup).total_seconds() / 60.0 if pickup and dropoff else 0.0

    trip_distance = float(row.get("trip_distance", 0) or 0)
    speed = (trip_distance / (duration_min / 60.0)) if duration_min > 0 else 0.0

    fare_amount = float(row.get("fare_amount", 0) or 0)
    tip_amount = float(row.get("tip_amount", 0) or 0)
    tip_pct = (tip_amount / fare_amount * 100) if fare_amount > 0 else 0.0

    total_amount = float(row.get("total_amount", 0) or 0)
    revenue_per_mile = (total_amount / trip_distance) if trip_distance > 0 else 0.0

    passenger_count = int(float(row.get("passenger_count", 0) or 0))
    rate_code_id = int(float(row.get("RatecodeID", 0) or 0))
    valid_rate_codes = {1, 2, 3, 4, 5, 6, 99}
    if rate_code_id not in valid_rate_codes:
        rate_code_id = 99
    pulocation_id = int(float(row.get("PULocationID", 0) or 0))
    dolocation_id = int(float(row.get("DOLocationID", 0) or 0))
    payment_type = int(float(row.get("payment_type", 0) or 0))
    valid_payment_types = {1, 2, 3, 4, 5, 6}
    if payment_type not in valid_payment_types:
        payment_type = 5
    vendor_id = int(float(row.get("VendorID", 0) or 0))
    valid_vendors = {1, 2, 4}
    if vendor_id not in valid_vendors:
        vendor_id = 4

    congestion_surcharge = float(row.get("congestion_surcharge", 0) or 0)
    extra_val = float(row.get("extra", 0) or 0)
    mta_tax = float(row.get("mta_tax", 0) or 0)
    tolls_amount = float(row.get("tolls_amount", 0) or 0)
    improvement_surcharge = float(row.get("improvement_surcharge", 0) or 0)

    store_and_fwd = row.get("store_and_fwd_flag", "N").strip()

    hour = pickup.hour if pickup else 0
    day_of_week = pickup.weekday() if pickup else 0
    is_weekend = 1 if day_of_week >= 5 else 0
    month = pickup.month if pickup else 1

    return {
        "vendor_id": vendor_id,
        "tpep_pickup_datetime": pickup.isoformat() if pickup else "",
        "tpep_dropoff_datetime": dropoff.isoformat() if dropoff else "",
        "passenger_count": passenger_count,
        "trip_distance": round(trip_distance, 2),
        "rate_code_id": rate_code_id,
        "store_and_fwd_flag": store_and_fwd,
        "pulocation_id": pulocation_id,
        "dolocation_id": dolocation_id,
        "payment_type_id": payment_type,
        "fare_amount": round(fare_amount, 2),
        "extra": round(extra_val, 2),
        "mta_tax": round(mta_tax, 2),
        "tip_amount": round(tip_amount, 2),
        "tolls_amount": round(tolls_amount, 2),
        "improvement_surcharge": round(improvement_surcharge, 2),
        "total_amount": round(total_amount, 2),
        "congestion_surcharge": round(congestion_surcharge, 2),
        "trip_duration_minutes": round(duration_min, 2),
        "speed_mph": round(speed, 2),
        "tip_percentage": round(tip_pct, 2),
        "hour_of_day": hour,
        "is_weekend": is_weekend,
        "day_of_week": day_of_week,
        "month": month,
        "revenue_per_mile": round(revenue_per_mile, 2),
    }


def cleaning_pipeline(csv_path: str, chunk_size: int = 50000) -> Iterator[list[dict]]:
    total = 0
    valid = 0
    invalid_counts: dict[str, int] = {}

    log_action("start", f"Starting cleaning pipeline for {csv_path}")

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        chunk: list[dict] = []

        for row in reader:
            total += 1
            is_valid, reason = is_valid_record(row)

            if is_valid:
                cleaned = clean_row(row)
                chunk.append(cleaned)
                valid += 1
            else:
                invalid_counts[reason] = invalid_counts.get(reason, 0) + 1

            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk

    for reason, count in invalid_counts.items():
        log_action("filter", f"Removed {count} records: {reason}", count=count, sample=reason)

    log_action("end", f"Pipeline complete. Total: {total}, Valid: {valid}, Removed: {total - valid}", count=total - valid)


def load_dim_locations(csv_path: str) -> list[dict]:
    locations = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                "location_id": int(row["LocationID"]),
                "borough": row["Borough"].strip(),
                "zone": row["Zone"].strip(),
                "service_zone": row["service_zone"].strip(),
            })
    return locations


def get_cleaning_log() -> list[dict]:
    return CLEANING_LOG
