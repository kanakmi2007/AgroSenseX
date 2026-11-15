import sys
sys.path.insert(0, '.')
from app import app

client = app.test_client()
resp = client.get('/soil-dashboard')
print('Status code:', resp.status_code)
html = resp.data.decode('utf-8')
print('HTML Length:', len(html))

expected_ids = [
    'sidebar-backdrop', 'sidebar', 'sidebar-close-btn', 'mobile-menu-btn',
    'overview-section', 'card-moisture', 'moisture-status', 'moisture-value',
    'moisture-updated', 'card-ph', 'ph-status', 'ph-value', 'ph-updated',
    'card-temp', 'temp-status', 'temp-value', 'temp-updated', 'card-npk',
    'npk-status', 'n-val', 'p-val', 'k-val', 'npk-value', 'npk-indicators',
    'npk-updated', 'health-score-circle', 'health-score-label', 'moisture-fill',
    'moisture-val', 'ph-fill', 'ph-val', 'temp-fill', 'temp-val', 'npk-fill',
    'npk-val', 'crop-section', 'crop-select', 'crop-score-badge', 'crop-score',
    'crop-summary-desc', 'crop-factors', 'limiting-factor-container', 'ai-section',
    'ai-analyze-btn', 'ai-results', 'recommendations-section', 'recs-count',
    'recommendations', 'historical-section', 'time-filter', 'moisture-chart',
    'ph-chart', 'temp-chart', 'npk-chart',
    # New IDs for Historical Soil Analytics requirements:
    'export-csv-btn', 'moisture-avg', 'moisture-min', 'moisture-max',
    'ph-avg', 'ph-min', 'ph-max', 'temp-avg', 'temp-min', 'temp-max',
    'n-stats', 'p-stats', 'k-stats', 'csv-export-toast'
]

missing = [i for i in expected_ids if f'id="{i}"' not in html]
print('Missing IDs count:', len(missing))
if missing:
    print('Missing IDs:', missing)
else:
    print('SUCCESS: All', len(expected_ids), 'expected IDs are present and intact!')

# Also check for Historical Soil Analytics title
print('Has Historical Soil Analytics heading:', 'Historical Soil Analytics' in html)
print('Has 24 Hours, 7 Days, 30 Days options:', '24 Hours' in html and '7 Days' in html and '30 Days' in html)
print('Has Export CSV button:', 'Export CSV' in html)

