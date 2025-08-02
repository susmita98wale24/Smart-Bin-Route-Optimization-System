from flask import Flask, request, render_template, send_file, jsonify, url_for
import folium
from folium import PolyLine
import pandas as pd
from fpdf import FPDF
from sklearn.linear_model import LinearRegression
from geopy.distance import geodesic
import networkx as nx
import yagmail
from sqlalchemy import create_engine, Column, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

#  SQLite Database Setup 
engine = create_engine("sqlite:///bins.db")  # Create SQLite engine
Base = declarative_base()  # Base class for models

# Define table schema for bin status
class BinStatus(Base):
    __tablename__ = 'bins'
    id = Column(String, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    fill_level = Column(Float)

# Create table if not exists
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)  # Session to interact with DB

# Fallback Bin Data if DB is Empty 
bin_data = [
    {"id": "Bin001", "lat": 18.5204, "lon": 73.8567, "current_fill": 85},
    {"id": "Bin002", "lat": 18.5300, "lon": 73.8700, "current_fill": 40},
    {"id": "Bin003", "lat": 18.5450, "lon": 73.8600, "current_fill": 92},
    {"id": "Bin004", "lat": 18.5555, "lon": 73.8650, "current_fill": 30}
]

last_bins_collected = []  # Stores last collected bins (used in report downloads)

# Route Optimization Function 
def get_optimized_route(bins):
    G = nx.complete_graph(len(bins))  # Create complete graph
    for i in range(len(bins)):
        for j in range(len(bins)):
            if i != j:
                loc1 = (bins[i]['lat'], bins[i]['lon'])
                loc2 = (bins[j]['lat'], bins[j]['lon'])
                G[i][j]['weight'] = geodesic(loc1, loc2).km  # Distance as weight
    path = nx.approximation.traveling_salesman_problem(G)
    return [bins[i]['id'] for i in path]

# Predict Next Day Fill Using Linear Regression 
def predict_next_day_fill():
    try:
        df = pd.read_csv("F:/Using Flask AI powered waste optimization system/dataset/bin_history.csv", encoding="utf-8-sig")
        predictions = {}
        pickup_schedule = {}

        for bin_id in df['id'].unique():
            bin_df = df[df['id'] == bin_id].copy()
            bin_df['day'] = range(len(bin_df))
            model = LinearRegression()
            model.fit(bin_df[['day']], bin_df['fill_level'])
            next_day = [[len(bin_df)]]
            predicted_fill = model.predict(next_day)[0]
            predictions[bin_id] = round(predicted_fill, 2)

            # Determine pickup schedule based on predicted fill
            if predicted_fill >= 90:
                pickup_time = "08:00 AM"
            elif predicted_fill >= 70:
                pickup_time = "11:00 AM"
            else:
                pickup_time = "03:00 PM"
            pickup_schedule[bin_id] = pickup_time

        return predictions, pickup_schedule
    except Exception as e:
        print("Prediction Error:", e)
        return {}, {}

# Email Alerts 
def send_email_alert(bin_id, fill_level):
    try:
        yag = yagmail.SMTP("your_email@gmail.com", "your_app_password")
        yag.send(
            to="authority@example.com",
            subject="🚨 Bin Alert!",
            contents=f"Bin {bin_id} has reached {fill_level}% fill level!"
        )
    except Exception as e:
        print("Email Alert Error:", e)

# API to Accept Real-Time Sensor Data 
@app.route('/api/sensor', methods=['POST'])
def sensor_api():
    data = request.json
    session = Session()
    session.merge(BinStatus(
        id=data['id'],
        lat=data['lat'],
        lon=data['lon'],
        fill_level=data['fill_level']
    ))
    session.commit()
    return jsonify({"status": "success", "msg": "Data stored"}), 200

# Main Dashboard Route 
@app.route('/', methods=['GET', 'POST'])
def index():
    global last_bins_collected
    if request.method == 'POST':
        threshold = int(request.form['threshold'])  # Get threshold from form

        # Fetch bins from DB or fallback data
        session = Session()
        bins = session.query(BinStatus).all()
        if bins:
            bin_list = [{"id": b.id, "lat": b.lat, "lon": b.lon, "current_fill": b.fill_level} for b in bins]
        else:
            bin_list = bin_data

        # Filter bins above threshold
        bins_to_collect = [b for b in bin_list if b['current_fill'] >= threshold]
        last_bins_collected = bins_to_collect

        # Predict fill levels and get pickup schedules
        predictions, schedule = predict_next_day_fill()

        # Prepare alert messages
        alerts = [f"Bin {b['id']} is {b['current_fill']}% full!" for b in bins_to_collect]

        # Optimize collection route
        optimized_route = get_optimized_route(bins_to_collect)

        # Send alert emails
        for b in bins_to_collect:
            send_email_alert(b['id'], b['current_fill'])

        # Map Generation 
        m = folium.Map(location=[18.52, 73.85], zoom_start=13)

        # Add color-coded markers
        for b in bin_list:
            color = "red" if b['current_fill'] >= 80 else "orange" if b['current_fill'] >= 50 else "green"
            folium.Marker(
                [b['lat'], b['lon']],
                popup=f"{b['id']} - {b['current_fill']}%",
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Draw optimized route and step markers
        if len(bins_to_collect) > 1:
            route_coords = []
            for i, bin_id in enumerate(optimized_route):
                b = next(bin for bin in bins_to_collect if bin['id'] == bin_id)
                route_coords.append((b['lat'], b['lon']))
                folium.CircleMarker(
                    location=(b['lat'], b['lon']),
                    radius=12,
                    fill=True,
                    fill_opacity=0.7,
                    color='blue',
                    fill_color='white',
                    popup=f"Step {i+1}: {b['id']}",
                    tooltip=f"Step {i+1}"
                ).add_to(m)
            PolyLine(route_coords, color="blue", weight=3).add_to(m)

        # Add legend to map
        legend_html = '''
         <div style="
         position: fixed; 
         bottom: 50px; left: 50px; width: 160px; height: 110px; 
         background-color: white; z-index:9999; font-size:14px;
         border:2px solid grey; padding: 10px;
         ">
         <b>🗑 Bin Fill Legend</b><br>
         🟥 > 80% (High)<br>
         🟧 50–79% (Medium)<br>
         🟩 < 50% (Low)
         </div>
         '''
        m.get_root().html.add_child(folium.Element(legend_html))

        m.save("static/map.html")  # Save final map to file

        # Render result page with data
        return render_template(
            "result.html",
            bins=bins_to_collect,
            route=optimized_route,
            predictions=predictions,
            schedule=schedule,
            alerts=alerts,
            now=datetime.now()
        )

    # On GET request, show form
    return render_template("index.html")


# Report Downloads 
@app.route('/download/csv')
def download_csv():
    df = pd.DataFrame(last_bins_collected)
    path = "F:/Using Flask AI powered waste optimization system/static/bins_to_collect.csv"
    df.to_csv(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/download/excel')
def download_excel():
    df = pd.DataFrame(last_bins_collected)
    path = "F:/Using Flask AI powered waste optimization system/static/bins_to_collect.xlsx"
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/download/pdf')
def download_pdf():
    path = "static/bins_to_collect.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Bins to Collect", ln=True, align='C')
    for b in last_bins_collected:
        pdf.cell(200, 10, f"{b['id']} – {b['current_fill']}%", ln=True)
    pdf.output(path)
    return send_file(path, as_attachment=True)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
