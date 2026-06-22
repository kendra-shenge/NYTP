from sqlalchemy import text
from sqlalchemy.engine import Engine


def get_kpi_summary(engine: Engine) -> dict:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT
                COUNT(*) as total_trips,
                ROUND(SUM(total_amount), 2) as total_revenue,
                ROUND(AVG(trip_distance), 2) as avg_distance,
                ROUND(AVG(trip_duration_minutes), 2) as avg_duration,
                ROUND(AVG(fare_amount), 2) as avg_fare,
                ROUND(AVG(tip_amount), 2) as avg_tip,
                ROUND(AVG(passenger_count), 2) as avg_passengers,
                ROUND(AVG(speed_mph), 2) as avg_speed
            FROM fact_trip
        """)).mappings().first()
        return dict(row) if row else {}


def get_trips_by_hour(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT hour_of_day, COUNT(*) as trip_count, ROUND(AVG(fare_amount), 2) as avg_fare
            FROM fact_trip
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_trips_by_day(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                CASE day_of_week
                    WHEN 0 THEN 'Monday'
                    WHEN 1 THEN 'Tuesday'
                    WHEN 2 THEN 'Wednesday'
                    WHEN 3 THEN 'Thursday'
                    WHEN 4 THEN 'Friday'
                    WHEN 5 THEN 'Saturday'
                    WHEN 6 THEN 'Sunday'
                END as day_name,
                day_of_week,
                COUNT(*) as trip_count,
                ROUND(AVG(trip_distance), 2) as avg_distance
            FROM fact_trip
            GROUP BY day_of_week
            ORDER BY day_of_week
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_trips_by_month(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT month, COUNT(*) as trip_count, ROUND(SUM(total_amount), 2) as revenue
            FROM fact_trip
            GROUP BY month
            ORDER BY month
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_top_pickup_locations(engine: Engine, limit: int = 15) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT l.zone, l.borough, COUNT(*) as trip_count
            FROM fact_trip t
            JOIN dim_location l ON t.pulocation_id = l.location_id
            GROUP BY l.location_id
            ORDER BY trip_count DESC
            LIMIT {limit}
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_top_dropoff_locations(engine: Engine, limit: int = 15) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT l.zone, l.borough, COUNT(*) as trip_count
            FROM fact_trip t
            JOIN dim_location l ON t.dolocation_id = l.location_id
            GROUP BY l.location_id
            ORDER BY trip_count DESC
            LIMIT {limit}
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_revenue_by_borough(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT l.borough,
                   COUNT(*) as trip_count,
                   ROUND(SUM(t.total_amount), 2) as revenue,
                   ROUND(AVG(t.fare_amount), 2) as avg_fare
            FROM fact_trip t
            JOIN dim_location l ON t.pulocation_id = l.location_id
            GROUP BY l.borough
            ORDER BY revenue DESC
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_payment_type_distribution(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT pt.payment_type_name, COUNT(*) as count, ROUND(SUM(t.total_amount), 2) as revenue
            FROM fact_trip t
            JOIN dim_payment_type pt ON t.payment_type_id = pt.payment_type_id
            GROUP BY t.payment_type_id
            ORDER BY count DESC
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_tip_analysis(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                CASE
                    WHEN tip_percentage = 0 THEN 'No Tip'
                    WHEN tip_percentage < 10 THEN '0-10%'
                    WHEN tip_percentage < 15 THEN '10-15%'
                    WHEN tip_percentage < 20 THEN '15-20%'
                    WHEN tip_percentage < 25 THEN '20-25%'
                    ELSE '25%+'
                END as tip_bucket,
                COUNT(*) as count,
                ROUND(AVG(fare_amount), 2) as avg_fare,
                ROUND(AVG(tip_amount), 2) as avg_tip
            FROM fact_trip
            GROUP BY tip_bucket
            ORDER BY MIN(tip_percentage)
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_speed_distance_bins(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
                CASE
                    WHEN trip_distance < 1 THEN '< 1 mile'
                    WHEN trip_distance < 3 THEN '1-3 miles'
                    WHEN trip_distance < 5 THEN '3-5 miles'
                    WHEN trip_distance < 10 THEN '5-10 miles'
                    ELSE '10+ miles'
                END as distance_bucket,
                COUNT(*) as count,
                ROUND(AVG(speed_mph), 2) as avg_speed,
                ROUND(AVG(fare_amount), 2) as avg_fare
            FROM fact_trip
            GROUP BY distance_bucket
            ORDER BY MIN(trip_distance)
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_vendor_comparison(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT v.vendor_name,
                   COUNT(*) as trip_count,
                   ROUND(AVG(t.fare_amount), 2) as avg_fare,
                   ROUND(AVG(t.trip_duration_minutes), 2) as avg_duration,
                   ROUND(AVG(t.trip_distance), 2) as avg_distance
            FROM fact_trip t
            JOIN dim_vendor v ON t.vendor_id = v.vendor_id
            GROUP BY v.vendor_id
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_rate_code_usage(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT rc.rate_code_name, COUNT(*) as count, ROUND(SUM(t.total_amount), 2) as revenue
            FROM fact_trip t
            JOIN dim_rate_code rc ON t.rate_code_id = rc.rate_code_id
            GROUP BY t.rate_code_id
            ORDER BY count DESC
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_hourly_revenue(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT hour_of_day,
                   ROUND(SUM(total_amount), 2) as revenue,
                   ROUND(AVG(fare_amount), 2) as avg_fare
            FROM fact_trip
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_top_routes(engine: Engine, limit: int = 20) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT
                pu.zone as pickup_zone,
                pu.borough as pickup_borough,
                do.zone as dropoff_zone,
                do.borough as dropoff_borough,
                COUNT(*) as trip_count,
                ROUND(AVG(t.fare_amount), 2) as avg_fare,
                ROUND(AVG(t.trip_distance), 2) as avg_distance
            FROM fact_trip t
            JOIN dim_location pu ON t.pulocation_id = pu.location_id
            JOIN dim_location do ON t.dolocation_id = do.location_id
            GROUP BY t.pulocation_id, t.dolocation_id
            ORDER BY trip_count DESC
            LIMIT {limit}
        """)).mappings().all()
        return [dict(r) for r in rows]


def get_filtered_trips(engine: Engine, filters: dict = None, limit: int = 1000) -> list[dict]:
    conditions = []
    params = {}

    if filters:
        if "min_date" in filters and filters["min_date"]:
            conditions.append("tpep_pickup_datetime >= :min_date")
            params["min_date"] = filters["min_date"]
        if "max_date" in filters and filters["max_date"]:
            conditions.append("tpep_pickup_datetime <= :max_date")
            params["max_date"] = filters["max_date"]
        if "min_distance" in filters and filters["min_distance"] is not None:
            conditions.append("trip_distance >= :min_dist")
            params["min_dist"] = filters["min_distance"]
        if "max_distance" in filters and filters["max_distance"] is not None:
            conditions.append("trip_distance <= :max_dist")
            params["max_dist"] = filters["max_distance"]
        if "min_fare" in filters and filters["min_fare"] is not None:
            conditions.append("fare_amount >= :min_fare")
            params["min_fare"] = filters["min_fare"]
        if "max_fare" in filters and filters["max_fare"] is not None:
            conditions.append("fare_amount <= :max_fare")
            params["max_fare"] = filters["max_fare"]
        if "vendor_id" in filters and filters["vendor_id"]:
            conditions.append("vendor_id = :vid")
            params["vid"] = filters["vendor_id"]
        if "payment_type" in filters and filters["payment_type"]:
            conditions.append("payment_type_id = :ptid")
            params["ptid"] = filters["payment_type"]
        if "pulocation" in filters and filters["pulocation"]:
            conditions.append("pulocation_id = :puloc")
            params["puloc"] = filters["pulocation"]
        if "dolocation" in filters and filters["dolocation"]:
            conditions.append("dolocation_id = :doloc")
            params["doloc"] = filters["dolocation"]
        if "min_passengers" in filters and filters["min_passengers"] is not None:
            conditions.append("passenger_count >= :min_pax")
            params["min_pax"] = filters["min_passengers"]
        if "hour" in filters and filters["hour"] is not None:
            conditions.append("hour_of_day = :hour")
            params["hour"] = filters["hour"]

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql = f"""
        SELECT
            t.trip_id, t.tpep_pickup_datetime, t.tpep_dropoff_datetime,
            t.passenger_count, t.trip_distance, t.fare_amount, t.tip_amount,
            t.total_amount, t.trip_duration_minutes, t.speed_mph,
            t.hour_of_day, t.is_weekend,
            v.vendor_name,
            pu.zone as pickup_zone, pu.borough as pickup_borough,
            do.zone as dropoff_zone, do.borough as dropoff_borough,
            pt.payment_type_name
        FROM fact_trip t
        JOIN dim_vendor v ON t.vendor_id = v.vendor_id
        JOIN dim_location pu ON t.pulocation_id = pu.location_id
        JOIN dim_location do ON t.dolocation_id = do.location_id
        JOIN dim_payment_type pt ON t.payment_type_id = pt.payment_type_id
        WHERE {where_clause}
        ORDER BY t.tpep_pickup_datetime DESC
        LIMIT {limit}
    """

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
