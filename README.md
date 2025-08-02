# Smart Bin Route Optimization System (Flask Based)

This project is an AI-powered waste management dashboard that helps optimize garbage bin collection using predictive analytics and geospatial route optimization.

Features

- Predict next-day bin fill levels using historical trends
- Color-coded smart bin map using Folium & Leaflet
- Optimized collection route using geodesic distance + NetworkX TSP
- Alert notifications for high-fill bins (email-enabled)
- Download collection reports in CSV, Excel, and PDF formats
- Real-time sensor API to simulate live bin fill updates
- Interactive web UI built with Flask + HTML/CSS

## Setup Instructions

1.Create virtual environment and activate
Terminal/Command Prompt
python -m venv venv
venv\Scripts\activate  # for Windows


2.Install dependencies
Terminal
pip install -r requirements.txt


3.Ensure dataset exists
Place the bin history CSV file here:
"dataset/bin_history.csv"


4.Run the application
Terminal
python app.py


5.Visit in browser:
http://127.0.0.1:5000/


## Usage Guide

1. On the homepage, enter a "threshold" (e.g. 70%) and click "Optimize Route".
2. You'll get:
   - High-fill bin alerts
   - Optimized pickup route
   - Predicted fill % for next day
   - Suggested pickup time
   - Interactive map showing bins with color-coded markers
3. Use buttons to download reports (CSV/Excel)

## Sample Input:

Threshold: `75`

## Sample Output
- Alerts:
  - Bin001 is 85% full
  - Bin003 is 92% full
- Route: Bin001 -> Bin003
- Predictions:
  - Bin001: 88.5%
  - Bin003: 94.2%
- Pickup Time:
  - Bin001 - 8:00 AM
  - Bin003 - 8:00 AM
- Map: Interactive with red, orange, green bin icons

## Technologies Used
- Python, Flask, Pandas, Scikit-learn
- Folium, Leaflet.js, Bootstrap
- SQLite + SQLAlchemy ORM
- FPDF, yagmail
- NetworkX (route optimization)

Optional 
## API for Sensor Updates
http
POST /api/sensor
Content-Type: application/json
{
  "id": "Bin001",
  "lat": 18.52,
  "lon": 73.85,
  "fill_level": 87
}
