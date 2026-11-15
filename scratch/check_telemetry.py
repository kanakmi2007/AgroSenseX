import os, sys
sys.path.insert(0, os.path.abspath('.'))
from app import app, SOIL_TELEMETRY

with open('templates/dashboard.html', encoding='utf-8') as f:
    dash_html = f.read()

print("=== Check Overview Dashboard Links ===")
print("Contains url_for('soil_dashboard'):", "url_for('soil_dashboard')" in dash_html or 'url_for("soil_dashboard")' in dash_html)
print("Contains /soil-dashboard link:", "/soil-dashboard" in dash_html)

# Check telemetry rendering in dashboard.html
client = app.test_client()
res = client.get('/dashboard')
html = res.data.decode('utf-8')

print("\n=== Check Shared SOIL_TELEMETRY in Dashboard ===")
print("SOIL_TELEMETRY in app.py:", SOIL_TELEMETRY)
print(f"Moisture ({SOIL_TELEMETRY['moisture']}%) in /dashboard:", f"{SOIL_TELEMETRY['moisture']}%" in html or f"{SOIL_TELEMETRY['moisture']}" in html)
print(f"pH ({SOIL_TELEMETRY['ph']}) in /dashboard:", f"{SOIL_TELEMETRY['ph']}" in html)
print(f"Temp ({SOIL_TELEMETRY['temperature']}°C) in /dashboard:", f"{SOIL_TELEMETRY['temperature']}°C" in html or f"{SOIL_TELEMETRY['temperature']}" in html)

# Check telemetry in soil_dashboard.html
res_soil = client.get('/soil-dashboard')
html_soil = res_soil.data.decode('utf-8')
print("\n=== Check Shared SOIL_TELEMETRY in Soil Dashboard ===")
print(f"Moisture ({SOIL_TELEMETRY['moisture']}%) in /soil-dashboard:", f"{SOIL_TELEMETRY['moisture']}%" in html_soil)
print(f"pH ({SOIL_TELEMETRY['ph']}) in /soil-dashboard:", f"{SOIL_TELEMETRY['ph']}" in html_soil)
print(f"Temp ({SOIL_TELEMETRY['temperature']}°C) in /soil-dashboard:", f"{SOIL_TELEMETRY['temperature']}°C" in html_soil)
print(f"NPK N({SOIL_TELEMETRY['npk']['N']}) in /soil-dashboard:", f"{SOIL_TELEMETRY['npk']['N']} mg/kg" in html_soil)

