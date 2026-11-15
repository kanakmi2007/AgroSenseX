import os, sys
sys.path.insert(0, os.path.abspath('.'))
from app import app
import re

client = app.test_client()

print("=== 1. Testing Navigation: Overview -> Soil Intelligence ===")
res_overview = client.get('/dashboard')
assert res_overview.status_code == 200, f"Expected 200, got {res_overview.status_code}"
html_overview = res_overview.data.decode('utf-8')

# Find Soil Intelligence links in Overview
soil_links = re.findall(r'<a[^>]+href=[\'"]([^\'"]*soil[^\'"]*)[\'"]', html_overview)
print(f"Found {len(soil_links)} Soil Intelligence link(s) on /dashboard: {set(soil_links)}")
for link in set(soil_links):
    target_res = client.get(link)
    assert target_res.status_code == 200, f"Link {link} failed with status {target_res.status_code}"
    print(f"  Navigating to {link} -> SUCCESS (HTTP {target_res.status_code}, {len(target_res.data):,} bytes)")

print("\n=== 2. Testing Navigation: Soil Intelligence -> Overview ===")
res_soil = client.get('/soil-dashboard')
assert res_soil.status_code == 200, f"Expected 200, got {res_soil.status_code}"
html_soil = res_soil.data.decode('utf-8')

# Find Overview links on Soil Dashboard
overview_links = re.findall(r'<a[^>]+href=[\'"]([^\'"]*dashboard[^\'"]*)[\'"]', html_soil)
# Filter for actual overview links
overview_links = [l for l in overview_links if l in ('/dashboard', '/')]
print(f"Found Overview link(s) on /soil-dashboard: {set(overview_links)}")
for link in set(overview_links):
    target_res = client.get(link)
    assert target_res.status_code == 200, f"Link {link} failed with status {target_res.status_code}"
    print(f"  Navigating back to {link} -> SUCCESS (HTTP {target_res.status_code}, {len(target_res.data):,} bytes)")

print("\n=== 3. Consistency of Metrics Across Pages ===")
from app import SOIL_TELEMETRY
print(f"Backend SOIL_TELEMETRY values:")
print(f"  Moisture:    {SOIL_TELEMETRY['moisture']}%")
print(f"  pH:          {SOIL_TELEMETRY['ph']}")
print(f"  Temperature: {SOIL_TELEMETRY['temperature']}°C")
print(f"  NPK:         N:{SOIL_TELEMETRY['npk']['N']}, P:{SOIL_TELEMETRY['npk']['P']}, K:{SOIL_TELEMETRY['npk']['K']}")

# Check in Overview
assert f"{SOIL_TELEMETRY['moisture']}%" in html_overview, "Moisture missing in /dashboard"
assert f"{SOIL_TELEMETRY['ph']}" in html_overview, "pH missing in /dashboard"
assert f"{SOIL_TELEMETRY['temperature']}°C" in html_overview, "Temp missing in /dashboard"
print("  All metrics match on /dashboard: PASS")

# Check in Soil Dashboard
assert f"{SOIL_TELEMETRY['moisture']}%" in html_soil, "Moisture missing in /soil-dashboard"
assert f"{SOIL_TELEMETRY['ph']}" in html_soil, "pH missing in /soil-dashboard"
assert f"{SOIL_TELEMETRY['temperature']}°C" in html_soil, "Temp missing in /soil-dashboard"
assert f"{SOIL_TELEMETRY['npk']['N']} mg/kg" in html_soil, "NPK N missing in /soil-dashboard"
assert f"{SOIL_TELEMETRY['npk']['P']} mg/kg" in html_soil, "NPK P missing in /soil-dashboard"
assert f"{SOIL_TELEMETRY['npk']['K']} mg/kg" in html_soil, "NPK K missing in /soil-dashboard"
print("  All metrics match on /soil-dashboard: PASS")

print("\nALL BIDIRECTIONAL NAVIGATION & TELEMETRY TESTS PASSED!")

