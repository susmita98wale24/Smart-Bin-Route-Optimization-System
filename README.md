# Smart-Bin-Route-Optimization-System
Overview

The Smart Bin Route Optimization System is an AI-powered waste management web application that helps municipal authorities monitor smart waste bins, predict fill levels, and optimize garbage collection routes using data-driven insights. It improves operational efficiency, reduces missed pickups, and contributes to environmental sustainability. Built using Flask, Folium, SQLite, and scikit-learn, the system integrates real-time sensor data with machine learning and geospatial routing to intelligently manage urban waste collection.

Key Features
1. Stores bin location and fill level in an SQLite database.
2. Predictive Fill-Level Forecasting:Uses Linear Regression to forecast next-day bin fill levels based on historical data. Dynamically suggests pickup schedules based on predicted levels (e.g.fill ≥ 90%).
3. Route Optimization: Applies Traveling Salesman Problem (TSP) using networkx and geopy to calculate optimal collection routes for bins exceeding a user-defined threshold.
4. Interactive Visualization Dashboard:
   Displays:
   Bin Alerts for high-fill bins, Predicted fill levels and pickup times, Color-coded map (green, orange, red) using Folium + Leaflet for bin status, Optimized path plotted with polyline route steps, Generates downloadable reports in CSV, Excel, and PDF formats.

Technologies Used

Backend:Python, Flask
Data Storage:	SQLite, CSV
Machine Learning:	scikit-learn (Linear Regression)
Geospatial Routing:	geopy, networkx
Visualization:	Folium, Leaflet.js, Bootstrap
Reporting:	Pandas, FPDF
