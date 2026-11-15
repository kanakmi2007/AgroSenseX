import urllib.request, json

base = 'http://127.0.0.1:5000'

# --- Fetch page ---
req = urllib.request.Request(base + '/soil-dashboard', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req, timeout=8) as r:
    html = r.read().decode()

# --- Fetch CSS ---
req2 = urllib.request.Request(base + '/static/css/soil_dashboard.css', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req2, timeout=8) as r:
    css = r.read().decode()

# --- HTML structure ---
html_checks = {
    'npk-table-wrap present':        'npk-table-wrap' in html,
    'npk-stat-table present':        'npk-stat-table' in html,
    'table element used':            '<table' in html,
    'thead element used':            '<thead' in html,
    'tbody element used':            '<tbody' in html,
    'Header: Nutrient column':       '>Nutrient<' in html,
    'Header: AVG column':            '>AVG<' in html,
    'Header: MIN column':            '>MIN<' in html,
    'Header: MAX column':            '>MAX<' in html,
    'Row: Nitrogen (N) label':       'Nitrogen (N)' in html,
    'Row: Phosphorus (P) label':     'Phosphorus (P)' in html,
    'Row: Potassium (K) label':      'Potassium (K)' in html,
    'id n-avg present':              'id="n-avg"' in html,
    'id n-min present':              'id="n-min"' in html,
    'id n-max present':              'id="n-max"' in html,
    'id p-avg present':              'id="p-avg"' in html,
    'id p-min present':              'id="p-min"' in html,
    'id p-max present':              'id="p-max"' in html,
    'id k-avg present':              'id="k-avg"' in html,
    'id k-min present':              'id="k-min"' in html,
    'id k-max present':              'id="k-max"' in html,
    'npk-dot badges present':        'npk-dot' in html,
    'npk-name class present':        'npk-name' in html,
    'mg/kg in heading (not in rows)':'NPK Nutrients (mg/kg)' in html,
    'mg/kg not in JS setStatText':   "toFixed(1) + ' mg/kg'" not in html,
    'OLD npk-stats-grid gone':       'npk-stats-grid' not in html,
    'OLD npk-stat-col gone':         'npk-stat-col' not in html,
    'chart-wrapper + canvas intact': 'id="npk-chart"' in html,
}

# --- CSS rules ---
css_checks = {
    '.npk-table-wrap defined':       '.npk-table-wrap' in css,
    '.npk-stat-table defined':       '.npk-stat-table' in css,
    '.npk-th defined':               '.npk-th' in css,
    '.npk-th-nutrient defined':      '.npk-th-nutrient' in css,
    '.npk-th-num defined':           '.npk-th-num' in css,
    '.npk-td-nutrient defined':      '.npk-td-nutrient' in css,
    '.npk-td-num defined':           '.npk-td-num' in css,
    '.npk-dot defined':              '.npk-dot' in css,
    '.npk-name defined':             '.npk-name' in css,
    'responsive @media 480px':       '@media (max-width: 480px)' in css,
    'OLD npk-stats-grid gone':       '.npk-stats-grid' not in css,
    'OLD npk-stat-col gone':         '.npk-stat-col' not in css,
    'white-space: nowrap on name':   'white-space: nowrap' in css,
}

# --- Print ---
all_pass = True
print('--- HTML Checks ---')
for label, ok in html_checks.items():
    if not ok: all_pass = False
    print(f'  {"PASS" if ok else "FAIL"}: {label}')

print()
print('--- CSS Checks ---')
for label, ok in css_checks.items():
    if not ok: all_pass = False
    print(f'  {"PASS" if ok else "FAIL"}: {label}')

# --- API stats ---
req3 = urllib.request.Request(base + '/api/historical-soil-data?timeframe=24h', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req3, timeout=8) as r:
    data = json.loads(r.read())
records = data['records']
n = [r['N'] for r in records]
p = [r['P'] for r in records]
k = [r['K'] for r in records]
print()
print('--- Live API Stats (24h) ---')
print(f'  N (Nitrogen):   avg={sum(n)/len(n):.1f}  min={min(n):.1f}  max={max(n):.1f}')
print(f'  P (Phosphorus): avg={sum(p)/len(p):.1f}  min={min(p):.1f}  max={max(p):.1f}')
print(f'  K (Potassium):  avg={sum(k)/len(k):.1f}  min={min(k):.1f}  max={max(k):.1f}')

print()
print('ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED — review above')
