"""Raw Python HTTP server - no frameworks (no Flask, Django, Streamlit)."""

import sys
import os
import json
import mimetypes
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_engine
from src.queries import analytics
from src.pipeline.clean import get_cleaning_log

ENGINE = get_engine()
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
PORT = 8000


class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict | list, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_file(self, filepath: str):
        mime, _ = mimetypes.guess_type(filepath)
        if mime is None:
            mime = "application/octet-stream"
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_error(404, "File not found")

    def _send_error(self, status: int, message: str):
        self._send_json({"error": message}, status)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = urllib.parse.parse_qs(parsed.query)

        routes = {
            "/api/kpi": self._handle_kpi,
            "/api/trips-by-hour": self._handle_trips_by_hour,
            "/api/trips-by-day": self._handle_trips_by_day,
            "/api/trips-by-month": self._handle_trips_by_month,
            "/api/top-pickup-locations": self._handle_top_pickup,
            "/api/top-dropoff-locations": self._handle_top_dropoff,
            "/api/revenue-by-borough": self._handle_revenue_borough,
            "/api/payment-types": self._handle_payment_types,
            "/api/tip-analysis": self._handle_tip_analysis,
            "/api/top-routes": self._handle_top_routes,
            "/api/trip-count": self._handle_trip_count,
            "/api/trips": self._handle_filtered_trips,
            "/api/pipeline-log": self._handle_pipeline_log,
        }

        if path in routes:
            routes[path](params)
        elif path.startswith("/api/"):
            self._send_error(404, f"Unknown endpoint: {path}")
        else:
            self._serve_static(path)

    def _serve_static(self, path: str):
        if path == "" or path == "/":
            path = "/index.html"
        filepath = os.path.join(FRONTEND_DIR, path.lstrip("/"))
        if not os.path.realpath(filepath).startswith(os.path.realpath(FRONTEND_DIR)):
            self._send_error(403, "Forbidden")
            return
        self._send_file(filepath)

    def _get_int_param(self, params: dict, key: str, default=None):
        if key in params and params[key][0].strip():
            try:
                return int(params[key][0])
            except ValueError:
                return default
        return default

    def _get_float_param(self, params: dict, key: str, default=None):
        if key in params and params[key][0].strip():
            try:
                return float(params[key][0])
            except ValueError:
                return default
        return default

    def _handle_kpi(self, params):
        data = analytics.get_kpi_summary(ENGINE)
        self._send_json(data)

    def _handle_trips_by_hour(self, params):
        data = analytics.get_trips_by_hour(ENGINE)
        self._send_json(data)

    def _handle_trips_by_day(self, params):
        data = analytics.get_trips_by_day(ENGINE)
        self._send_json(data)

    def _handle_trips_by_month(self, params):
        data = analytics.get_trips_by_month(ENGINE)
        self._send_json(data)

    def _handle_top_pickup(self, params):
        limit = self._get_int_param(params, "limit", 15)
        data = analytics.get_top_pickup_locations(ENGINE, limit)
        self._send_json(data)

    def _handle_top_dropoff(self, params):
        limit = self._get_int_param(params, "limit", 15)
        data = analytics.get_top_dropoff_locations(ENGINE, limit)
        self._send_json(data)

    def _handle_revenue_borough(self, params):
        data = analytics.get_revenue_by_borough(ENGINE)
        self._send_json(data)

    def _handle_payment_types(self, params):
        data = analytics.get_payment_type_distribution(ENGINE)
        self._send_json(data)

    def _handle_tip_analysis(self, params):
        data = analytics.get_tip_analysis(ENGINE)
        self._send_json(data)

    def _handle_top_routes(self, params):
        limit = self._get_int_param(params, "limit", 20)
        data = analytics.get_top_routes(ENGINE, limit)
        self._send_json(data)

    def _handle_trip_count(self, params):
        with ENGINE.connect() as conn:
            from sqlalchemy import text
            count = conn.execute(text("SELECT COUNT(*) FROM fact_trip")).scalar()
        self._send_json({"count": count})

    def _handle_filtered_trips(self, params):
        filters = {}
        if "min_date" in params:
            filters["min_date"] = params["min_date"][0]
        if "max_date" in params:
            filters["max_date"] = params["max_date"][0]
        min_fare = self._get_float_param(params, "min_fare")
        max_fare = self._get_float_param(params, "max_fare")
        min_dist = self._get_float_param(params, "min_distance")
        max_dist = self._get_float_param(params, "max_distance")
        if min_fare is not None:
            filters["min_fare"] = min_fare
        if max_fare is not None:
            filters["max_fare"] = max_fare
        if min_dist is not None:
            filters["min_distance"] = min_dist
        if max_dist is not None:
            filters["max_distance"] = max_dist
        puloc = self._get_int_param(params, "pulocation")
        doloc = self._get_int_param(params, "dolocation")
        if puloc:
            filters["pulocation"] = puloc
        if doloc:
            filters["dolocation"] = doloc
        limit = self._get_int_param(params, "limit", 200)
        data = analytics.get_filtered_trips(ENGINE, filters, limit)
        self._send_json(data)

    def _handle_pipeline_log(self, params):
        from datetime import datetime
        logs = get_cleaning_log()
        try:
            from sqlalchemy import text
            with ENGINE.connect() as conn:
                db_logs = conn.execute(
                    text("SELECT stage, description, count, sample, timestamp FROM pipeline_log ORDER BY id")
                ).mappings().all()
                if db_logs:
                    logs = [dict(r) for r in db_logs]
        except Exception:
            pass

        if not logs:
            with ENGINE.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM fact_trip")).scalar()
            logs = [
                {"stage": "info", "description": f"Database contains {count} cleaned trip records loaded from yellow_tripdata_2019.csv", "count": count, "sample": "", "timestamp": datetime.now().isoformat()},
                {"stage": "info", "description": "Dimensions: 3 vendors, 7 rate codes, 6 payment types, 265 locations", "count": 281, "sample": "", "timestamp": datetime.now().isoformat()},
                {"stage": "info", "description": "Derived features computed: trip_duration_minutes, speed_mph, tip_percentage, hour_of_day, is_weekend, day_of_week, month, revenue_per_mile", "count": 8, "sample": "", "timestamp": datetime.now().isoformat()},
            ]
        self._send_json(logs)

    def log_message(self, format, *args):
        if "/api/" in str(args[0]):
            print(f"[API] {args[0]}")


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), APIHandler)
    print(f"Backend server running on http://localhost:{PORT}")
    print(f"Frontend: http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
