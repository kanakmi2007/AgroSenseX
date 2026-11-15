import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import re
from app import app

print("=== 1. Flask Registered Endpoints ===")
for rule in app.url_map.iter_rules():
    methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
    print(f"{rule.rule:35s} -> {rule.endpoint} (methods: {methods})")

print("\n=== 2. Check url_for in templates ===")
templates = ['home.html', 'dashboard.html', 'soil_dashboard.html', 'index.html']
for t_name in templates:
    t_path = os.path.join('templates', t_name)
    if os.path.exists(t_path):
        with open(t_path, encoding='utf-8') as f:
            content = f.read()
        urls = re.findall(r"url_for\(['\"]([^'\"]+)['\"]", content)
        print(f"\n{t_name} url_for calls: {set(urls)}")
        for target in set(urls):
            if target != 'static' and target not in app.view_functions:
                print(f"  --> ERROR: Broken endpoint '{target}' in {t_name}")
            else:
                print(f"  --> OK: '{target}'")

print("\n=== 3. Test HTTP Requests via Flask Test Client ===")
client = app.test_client()
routes_to_test = [
    '/',
    '/dashboard',
    '/dashboard/soil',
    '/soil-dashboard',
    '/api/soil-data',
    '/api/historical-soil-data',
    '/api/export-soil-csv'
]

for r in routes_to_test:
    res = client.get(r)
    print(f"GET {r:28s} -> Status: {res.status_code} (Length: {len(res.data)} bytes)")
