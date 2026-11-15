# -*- coding: utf-8 -*-
"""
Script to update templates/soil_dashboard.html and static/css/soil_dashboard.css
with the improved Historical Soil Analytics section.
"""

# Read existing CSS and append/replace historical section styling
with open('static/css/soil_dashboard.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

# Add styling for .historical-actions-group, .btn-export-csv, .chart-stats-strip, .stat-stat-item, .csv-toast
historical_css_additions = '''
/* ==========================================================================
   HISTORICAL SOIL ANALYTICS ENHANCEMENTS
   ========================================================================== */
.historical-actions-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-export-csv {
  background: #FFFFFF;
  color: var(--accent-primary);
  border: 1.5px solid var(--accent-primary);
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.btn-export-csv:hover {
  background: var(--accent-primary);
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(8, 123, 80, 0.25);
  transform: translateY(-1px);
}

.btn-export-csv:active {
  transform: translateY(0);
}

/* Stat strip showing Avg, Min, Max */
.chart-stats-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #F9F9F7;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 6px 12px;
  margin-bottom: 12px;
  font-size: 0.72rem;
}

.stat-stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-stat-label {
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.65rem;
  letter-spacing: 0.3px;
}

.stat-stat-val {
  font-weight: 700;
  color: var(--text-primary);
}

.npk-stats-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  padding: 6px 10px;
}

.npk-stats-strip .stat-stat-item {
  justify-content: center;
  white-space: nowrap;
}

/* Export Toast Notification */
.csv-toast {
  position: fixed;
  bottom: 24px;
  right: 28px;
  background: #06251C;
  color: #FFFFFF;
  border-left: 4px solid #22C55E;
  padding: 12px 18px;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  pointer-events: none;
  transform: translateY(10px);
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.csv-toast.show {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}
'''

if '.historical-actions-group' not in css_text:
    css_text += historical_css_additions
    with open('static/css/soil_dashboard.css', 'w', encoding='utf-8') as f:
        f.write(css_text)
    print('Updated static/css/soil_dashboard.css with new historical styles!')
else:
    print('CSS already includes historical-actions-group!')

