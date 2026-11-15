import urllib.request
import json

base = 'http://127.0.0.1:5000'

# 1. Fetch soil-dashboard page and verify new HTML structure
req = urllib.request.Request(base + '/soil-dashboard', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req, timeout=8) as r:
    html = r.read().decode()

checks = {
    'npk-stats-grid div present': 'npk-stats-grid' in html,
    'npk-stat-col div present': 'npk-stat-col' in html,
    'npk-col-badge present': 'npk-col-badge' in html,
    'npk-col-name present': 'npk-col-name' in html,
    'id n-avg present': 'id="n-avg"' in html,
    'id n-min present': 'id="n-min"' in html,
    'id n-max present': 'id="n-max"' in html,
    'id p-avg present': 'id="p-avg"' in html,
    'id p-min present': 'id="p-min"' in html,
    'id p-max present': 'id="p-max"' in html,
    'id k-avg present': 'id="k-avg"' in html,
    'id k-min present': 'id="k-min"' in html,
    'id k-max present': 'id="k-max"' in html,
    'OLD n-stats removed': 'id="n-stats"' not in html,
    'OLD p-stats removed': 'id="p-stats"' not in html,
    'OLD k-stats removed': 'id="k-stats"' not in html,
    'Nitrogen label': 'Nitrogen' in html,
    'Phosphorus label': 'Phosphorus' in html,
    'Potassium label': 'Potassium' in html,
    'npk-col-rows present': 'npk-col-rows' in html,
    'npk-col-row present': 'npk-col-row' in html,
    'npk-row-label present': 'npk-row-label' in html,
    'npk-row-val present': 'npk-row-val' in html,
}
print('--- HTML Structure Checks ---')
all_pass = True
for label, ok in checks.items():
    status = 'PASS' if ok else 'FAIL'
    if not ok:
        all_pass = False
    print(f'  {status}: {label}')

# 2. Check CSS has new rules
req2 = urllib.request.Request(base + '/static/css/soil_dashboard.css', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req2, timeout=8) as r:
    css = r.read().decode()
css_checks = {
    '.npk-stats-grid defined': '.npk-stats-grid' in css,
    '.npk-stat-col defined': '.npk-stat-col' in css,
    '.npk-col-badge defined': '.npk-col-badge' in css,
    '.npk-row-label defined': '.npk-row-label' in css,
    '.npk-row-val defined': '.npk-row-val' in css,
    'responsive @media 600px': '@media (max-width: 600px)' in css,
    'grid-template-columns: 1fr for mobile': 'grid-template-columns: 1fr' in css,
}
print()
print('--- CSS Checks ---')
for label, ok in css_checks.items():
    status = 'PASS' if ok else 'FAIL'
    if not ok:
        all_pass = False
    print(f'  {status}: {label}')

# 3. API still works - calculate expected stats
req3 = urllib.request.Request(base + '/api/historical-soil-data?timeframe=24h', headers={'User-Agent': 'test/1.0'})
with urllib.request.urlopen(req3, timeout=8) as r:
    data = json.loads(r.read())
records = data['records']
n_vals = [rec['N'] for rec in records]
p_vals = [rec['P'] for rec in records]
k_vals = [rec['K'] for rec in records]
print()
print('--- API: Expected Stats for 24h window ---')
print(f'  N: avg={sum(n_vals)/len(n_vals):.1f} min={min(n_vals):.1f} max={max(n_vals):.1f} mg/kg')
print(f'  P: avg={sum(p_vals)/len(p_vals):.1f} min={min(p_vals):.1f} max={max(p_vals):.1f} mg/kg')
print(f'  K: avg={sum(k_vals)/len(k_vals):.1f} min={min(k_vals):.1f} max={max(k_vals):.1f} mg/kg')

# 4. Verify JS updated to use new IDs
js_checks = {
    'setStatText n-avg': "setStatText('n-avg'" in html,
    'setStatText n-min': "setStatText('n-min'" in html,
    'setStatText n-max': "setStatText('n-max'" in html,
    'setStatText p-avg': "setStatText('p-avg'" in html,
    'setStatText p-min': "setStatText('p-min'" in html,
    'setStatText p-max': "setStatText('p-max'" in html,
    'setStatText k-avg': "setStatText('k-avg'" in html,
    'setStatText k-min': "setStatText('k-min'" in html,
    'setStatText k-max': "setStatText('k-max'" in html,
    'OLD n-stats JS removed': "setStatText('n-stats'" not in html,
}
print()
print('--- JavaScript Checks ---')
for label, ok in js_checks.items():
    status = 'PASS' if ok else 'FAIL'
    if not ok:
        all_pass = False
    print(f'  {status}: {label}')

print()
if all_pass:
    print('ALL CHECKS PASSED')
else:
    print('SOME CHECKS FAILED - review above')
