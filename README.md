# NYC Taxi Trip Analyzer

A full-stack analytics dashboard for exploring New York City taxi trips from 2019. This project combines a lightweight Python backend, a browser-based frontend, and a normalized SQLite dataset with a MySQL-ready schema.

## Links
- Scrumboard: _TODO_
- Participation sheet: https://docs.google.com/spreadsheets/d/1IqUfeTE-UAdMirhrYXWT4rBRgdkrR49XH9G579nJivI/edit?usp=sharing
- Website: _TODO_
- Walkthrough video: _TODO_

## What this project includes
- **Backend**: Raw Python using the standard library (`http.server`), no web framework required
- **Frontend**: HTML, CSS, JavaScript, and Chart.js for interactive visualizations
- **Database**: SQLite with a normalized schema, ready for MySQL migration if needed
- **ETL pipeline**: Data cleaning, validation, and bulk loading into a star-schema-style model

## System Architecture

```
+------------------------------------------------------------------+
|                        USER BROWSER                               |
|  (index.html + style.css + app.js + charts.js + Chart.js CDN)    |
+------------------------------------------------------------------+
          |  HTTP requests (fetch API)        | Static files
          v                                   v
+-------------------+          +---------------------------+
|  Backend REST API |          |  Static File Server       |
|  /api/* endpoints |          |  serves frontend assets   |
+-------------------+          +---------------------------+
          |
          | SQL / Database access
          v
+------------------------------------------------------------------+
|                    Database (nytp.db / MySQL-ready)               |
|  +---------------+  +---------------+  +------------------------+ |
|  | dim_vendor    |  | dim_location  |  | fact_trip              | |
|  | dim_rate_code |  | dim_payment   |  | (7.6M rows, indexed)   | |
|  +---------------+  +---------------+  +------------------------+ |
+------------------------------------------------------------------+
          ^
          |
+------------------------------------------------------------------+
|                     ETL Pipeline (src/pipeline/)                  |
|  clean.py (validation, outliers, derived features)               |
|  load.py (bulk insert into normalized schema)                    |
+------------------------------------------------------------------+
          ^
          |
+------------------------------------------------------------------+
|  Raw source files:                                               |
|  yellow_tripdata_2019.csv     taxi_zone_lookup.csv               |
|  taxi_zones/ (GeoJSON boundaries)                                |
+------------------------------------------------------------------+
```

## Setup

### Prerequisites

- Python 3.10 or newer
- pip

### Installation

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Start the backend server
cd backend && python server.py

# Open the app in your browser
# http://localhost:8000
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/kpi` | KPI summary with total trips, revenue, and averages for fare, distance, duration, and speed |
| `GET /api/trips-by-hour` | Hourly trip volume and average fare |
| `GET /api/trips-by-day` | Trip volume by day of week |
| `GET /api/trips-by-month` | Monthly trip counts and revenue totals |
| `GET /api/top-pickup-locations?limit=N` | Top N pickup zones |
| `GET /api/top-dropoff-locations?limit=N` | Top N dropoff zones |
| `GET /api/revenue-by-borough` | Revenue, trip count, and average fare by borough |
| `GET /api/payment-types` | Payment method distribution and revenue breakdown |
| `GET /api/tip-analysis` | Tip percentage buckets with counts and averages |
| `GET /api/top-routes?limit=N` | Most popular pickup-to-dropoff routes |
| `GET /api/trip-count` | Total number of trip records |
| `GET /api/trips?min_date=&max_date=&min_fare=&max_fare=&pulocation=&dolocation=&limit=N` | Filtered trip data query |
| `GET /api/pipeline-log` | Data cleaning and ETL pipeline log |

## Notes

- The backend serves both the API and the frontend assets.
- Data files are expected to be loaded through the ETL pipeline before the dashboard is fully functional.
- The schema is designed for analytics and can be lifted into MySQL if the dataset grows.

