# -*- coding: utf-8 -*-
import os

with open('templates/soil_dashboard.html', 'r', encoding='utf-8') as f:
    current_html = f.read()

# Let's replace the historical section and script in current_html
new_historical_section = '''    <!-- Historical Soil Analytics Section -->
    <section class="historical-section" id="historical-section">
      <div class="section-header-bar">
        <div>
          <h3><i class="fas fa-chart-line" style="color: #087B50;"></i> Historical Soil Analytics</h3>
          <p class="section-sub">Parameter trajectory across field sensors &bull; <span class="demo-tag-mini"><i class="fas fa-database"></i> SIMULATED HISTORICAL READINGS</span></p>
        </div>
        <div class="historical-actions-group">
          <div class="filter-wrapper">
            <label for="time-filter" class="filter-label"><i class="fas fa-clock"></i> Time Window:</label>
            <select class="dropdown filter-select" id="time-filter" title="Select Historical Time Window">
              <option value="24h" selected>24 Hours</option>
              <option value="7d">7 Days</option>
              <option value="30d">30 Days</option>
            </select>
          </div>
          <button class="btn-export-csv" id="export-csv-btn" title="Download Historical Soil Telemetry CSV">
            <i class="fa-solid fa-file-arrow-down"></i> Export CSV
          </button>
        </div>
      </div>

      <div class="charts-grid">
        <!-- 1. Soil Moisture Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title"><i class="fas fa-tint" style="color:#087B50;"></i> Soil Moisture (%)</span>
            <span class="chart-val-badge" id="moisture-current-badge">{{ soil.moisture }}% Current</span>
          </div>
          <div class="chart-stats-strip">
            <div class="stat-stat-item">
              <span class="stat-stat-label">Avg:</span>
              <span class="stat-stat-val" id="moisture-avg">--%</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Min:</span>
              <span class="stat-stat-val" id="moisture-min">--%</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Max:</span>
              <span class="stat-stat-val" id="moisture-max">--%</span>
            </div>
          </div>
          <div class="chart-wrapper">
            <canvas id="moisture-chart"></canvas>
          </div>
        </div>

        <!-- 2. Soil pH Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title"><i class="fas fa-flask" style="color:#0284C7;"></i> Soil pH</span>
            <span class="chart-val-badge" id="ph-current-badge">{{ soil.ph }} pH</span>
          </div>
          <div class="chart-stats-strip">
            <div class="stat-stat-item">
              <span class="stat-stat-label">Avg:</span>
              <span class="stat-stat-val" id="ph-avg">--</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Min:</span>
              <span class="stat-stat-val" id="ph-min">--</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Max:</span>
              <span class="stat-stat-val" id="ph-max">--</span>
            </div>
          </div>
          <div class="chart-wrapper">
            <canvas id="ph-chart"></canvas>
          </div>
        </div>

        <!-- 3. Soil Temperature Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title"><i class="fas fa-thermometer-half" style="color:#E67E22;"></i> Soil Temperature (°C)</span>
            <span class="chart-val-badge" id="temp-current-badge">{{ soil.temperature }}°C Current</span>
          </div>
          <div class="chart-stats-strip">
            <div class="stat-stat-item">
              <span class="stat-stat-label">Avg:</span>
              <span class="stat-stat-val" id="temp-avg">--°C</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Min:</span>
              <span class="stat-stat-val" id="temp-min">--°C</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label">Max:</span>
              <span class="stat-stat-val" id="temp-max">--°C</span>
            </div>
          </div>
          <div class="chart-wrapper">
            <canvas id="temp-chart"></canvas>
          </div>
        </div>

        <!-- 4. NPK Nutrients Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title"><i class="fas fa-vial" style="color:#2E7D32;"></i> NPK Nutrients (mg/kg)</span>
            <span class="chart-val-badge" id="npk-current-badge">Multi-Vector</span>
          </div>
          <div class="chart-stats-strip npk-stats-strip">
            <div class="stat-stat-item">
              <span class="stat-stat-label" style="color:#087B50;">N (Avg/Min/Max):</span>
              <span class="stat-stat-val" id="n-stats">--</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label" style="color:#FF9800;">P (Avg/Min/Max):</span>
              <span class="stat-stat-val" id="p-stats">--</span>
            </div>
            <div class="stat-stat-item">
              <span class="stat-stat-label" style="color:#0284C7;">K (Avg/Min/Max):</span>
              <span class="stat-stat-val" id="k-stats">--</span>
            </div>
          </div>
          <div class="chart-wrapper">
            <canvas id="npk-chart"></canvas>
          </div>
        </div>
      </div>
    </section>

    <!-- Toast Notification for CSV Export -->
    <div id="csv-export-toast" class="csv-toast">
      <i class="fa-solid fa-circle-check" style="color:#4ADE80;"></i>
      <span id="csv-toast-msg">Historical soil readings exported to CSV!</span>
    </div>'''

# Find old historical section start and end
start_marker = '<!-- Historical Soil Trends (4 Separate Readable Charts) -->'
end_marker = '</main>'

start_pos = current_html.find(start_marker)
end_pos = current_html.find(end_marker, start_pos)

if start_pos != -1 and end_pos != -1:
    before_part = current_html[:start_pos]
    after_part = current_html[end_pos:]
    current_html = before_part + new_historical_section + '\n  ' + after_part
    print('Replaced historical section in HTML!')
else:
    print('Could not find start/end markers in HTML, please check!')

# Now let's update the script part
new_chart_script = '''    // ---------- 3. Improved Historical Charts & Telemetry Datasets ----------
    const historicalDatasets = {
      '24h': {
        timeframeLabel: '24 Hours',
        labels: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
        fullTimestamps: [
          'Today 00:00', 'Today 03:00', 'Today 06:00', 'Today 09:00',
          'Today 12:00', 'Today 15:00', 'Today 18:00', 'Today 21:00'
        ],
        moisture: [38.2, 37.5, 36.8, 35.4, 33.8, 33.1, 34.2, 35.0],
        ph: [6.75, 6.78, 6.80, 6.84, 6.82, 6.80, 6.79, 6.80],
        temperature: [22.4, 21.8, 22.5, 25.6, 29.8, 30.2, 28.9, 28.0],
        npk: {
          N: [46.5, 46.2, 45.8, 45.4, 45.1, 44.8, 45.0, 45.0],
          P: [33.0, 32.8, 32.5, 32.2, 32.0, 31.8, 32.0, 32.0],
          K: [39.2, 39.0, 38.6, 38.4, 38.1, 37.9, 38.0, 38.0]
        }
      },
      '7d': {
        timeframeLabel: '7 Days',
        labels: ['Nov 8', 'Nov 9', 'Nov 10', 'Nov 11', 'Nov 12', 'Nov 13', 'Nov 14'],
        fullTimestamps: [
          'Nov 8, 2026', 'Nov 9, 2026', 'Nov 10, 2026', 'Nov 11, 2026',
          'Nov 12, 2026', 'Nov 13, 2026', 'Nov 14, 2026'
        ],
        moisture: [29.4, 28.0, 43.5, 41.2, 38.6, 36.4, 35.0],
        ph: [6.65, 6.70, 6.90, 6.85, 6.82, 6.80, 6.80],
        temperature: [26.2, 27.5, 25.8, 26.9, 27.8, 28.4, 28.0],
        npk: {
          N: [49.0, 48.2, 47.0, 46.5, 45.8, 45.2, 45.0],
          P: [34.5, 34.0, 33.2, 32.8, 32.4, 32.1, 32.0],
          K: [41.0, 40.2, 39.5, 39.0, 38.5, 38.2, 38.0]
        }
      },
      '30d': {
        timeframeLabel: '30 Days',
        labels: ['Oct 16', 'Oct 19', 'Oct 22', 'Oct 25', 'Oct 28', 'Oct 31', 'Nov 3', 'Nov 6', 'Nov 9', 'Nov 14'],
        fullTimestamps: [
          'Oct 16, 2026', 'Oct 19, 2026', 'Oct 22, 2026', 'Oct 25, 2026',
          'Oct 28, 2026', 'Oct 31, 2026', 'Nov 3, 2026', 'Nov 6, 2026',
          'Nov 9, 2026', 'Nov 14, 2026'
        ],
        moisture: [32.0, 27.5, 45.0, 41.5, 36.8, 30.2, 44.0, 39.5, 36.2, 35.0],
        ph: [6.50, 6.55, 6.72, 6.85, 6.80, 6.68, 6.75, 6.82, 6.80, 6.80],
        temperature: [24.5, 25.2, 26.0, 27.1, 28.5, 29.0, 27.4, 26.8, 27.5, 28.0],
        npk: {
          N: [54.0, 52.5, 51.0, 49.5, 48.0, 47.0, 46.2, 45.5, 45.2, 45.0],
          P: [36.5, 35.8, 35.0, 34.2, 33.5, 33.0, 32.6, 32.2, 32.1, 32.0],
          K: [44.0, 43.0, 42.1, 41.0, 40.2, 39.5, 38.8, 38.4, 38.2, 38.0]
        }
      }
    };

    function calcStats(arr) {
      if (!arr || !arr.length) return { avg: 0, min: 0, max: 0 };
      const min = Math.min(...arr);
      const max = Math.max(...arr);
      const sum = arr.reduce((acc, v) => acc + v, 0);
      const avg = sum / arr.length;
      return { avg, min, max };
    }

    function setStatText(elementId, text) {
      const el = document.getElementById(elementId);
      if (el) el.textContent = text;
    }

    function updateHistoricalStats(dataset) {
      const mStats = calcStats(dataset.moisture);
      setStatText('moisture-avg', mStats.avg.toFixed(1) + '%');
      setStatText('moisture-min', mStats.min.toFixed(1) + '%');
      setStatText('moisture-max', mStats.max.toFixed(1) + '%');

      const pStats = calcStats(dataset.ph);
      setStatText('ph-avg', pStats.avg.toFixed(2));
      setStatText('ph-min', pStats.min.toFixed(2));
      setStatText('ph-max', pStats.max.toFixed(2));

      const tStats = calcStats(dataset.temperature);
      setStatText('temp-avg', tStats.avg.toFixed(1) + '°C');
      setStatText('temp-min', tStats.min.toFixed(1) + '°C');
      setStatText('temp-max', tStats.max.toFixed(1) + '°C');

      const nStats = calcStats(dataset.npk.N);
      const pKStats = calcStats(dataset.npk.P);
      const kStats = calcStats(dataset.npk.K);
      setStatText('n-stats', `${nStats.avg.toFixed(1)} / ${nStats.min.toFixed(1)} / ${nStats.max.toFixed(1)}`);
      setStatText('p-stats', `${pKStats.avg.toFixed(1)} / ${pKStats.min.toFixed(1)} / ${pKStats.max.toFixed(1)}`);
      setStatText('k-stats', `${kStats.avg.toFixed(1)} / ${kStats.min.toFixed(1)} / ${kStats.max.toFixed(1)}`);
    }

    let charts = {};
    function initCharts() {
      const ctxM = document.getElementById('moisture-chart');
      const ctxP = document.getElementById('ph-chart');
      const ctxT = document.getElementById('temp-chart');
      const ctxN = document.getElementById('npk-chart');
      if (!ctxM || !ctxP || !ctxT || !ctxN) return;

      const initialKey = '24h';
      const initialData = historicalDatasets[initialKey];
      const labels = initialData.labels;

      const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 6, bottom: 2, left: 4, right: 6 }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: '#06251C',
            titleColor: '#E8F5E9',
            bodyColor: '#FFFFFF',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            titleFont: { family: 'Plus Jakarta Sans', size: 12, weight: 700 },
            bodyFont: { family: 'Plus Jakarta Sans', size: 12 },
            displayColors: true,
            boxPadding: 4,
            callbacks: {
              title: function(items) {
                if (!items.length) return '';
                const idx = items[0].dataIndex;
                const selectEl = document.getElementById('time-filter');
                const range = selectEl ? selectEl.value : '24h';
                const ds = historicalDatasets[range] || historicalDatasets['24h'];
                return ds.fullTimestamps[idx] || items[0].label;
              },
              label: function(context) {
                let label = context.dataset.label || '';
                const val = context.parsed.y;
                if (val !== null) {
                  if (label.includes('Moisture')) return ` Soil Moisture: ${val.toFixed(1)}%`;
                  if (label.includes('pH')) return ` Soil pH: ${val.toFixed(2)} pH`;
                  if (label.includes('Temp')) return ` Temperature: ${val.toFixed(1)}°C`;
                  if (context.dataset.label === 'N') return ` Nitrogen (N): ${val.toFixed(1)} mg/kg`;
                  if (context.dataset.label === 'P') return ` Phosphorus (P): ${val.toFixed(1)} mg/kg`;
                  if (context.dataset.label === 'K') return ` Potassium (K): ${val.toFixed(1)} mg/kg`;
                  return ` ${label}: ${val}`;
                }
                return label;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: '#778078',
              font: { family: 'Plus Jakarta Sans', size: 11, weight: 500 },
              maxTicksLimit: 8,
              maxRotation: 0,
              autoSkip: true,
              padding: 6
            }
          },
          y: {
            grid: { color: 'rgba(229, 233, 227, 0.7)' },
            ticks: {
              color: '#778078',
              font: { family: 'Plus Jakarta Sans', size: 11, weight: 500 },
              padding: 6
            }
          }
        }
      };

      charts.moisture = new Chart(ctxM.getContext('2d'), {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Moisture (%)',
            data: initialData.moisture,
            borderColor: '#087B50',
            backgroundColor: 'rgba(8, 123, 80, 0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 3.5,
            pointHoverRadius: 6
          }]
        },
        options: commonOptions
      });

      charts.ph = new Chart(ctxP.getContext('2d'), {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'pH Level',
            data: initialData.ph,
            borderColor: '#0284C7',
            backgroundColor: 'rgba(2, 132, 199, 0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 3.5,
            pointHoverRadius: 6
          }]
        },
        options: commonOptions
      });

      charts.temp = new Chart(ctxT.getContext('2d'), {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Temp (°C)',
            data: initialData.temperature,
            borderColor: '#E67E22',
            backgroundColor: 'rgba(230, 126, 34, 0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 3.5,
            pointHoverRadius: 6
          }]
        },
        options: commonOptions
      });

      const npkOptions = JSON.parse(JSON.stringify(commonOptions));
      npkOptions.plugins.legend = {
        display: true,
        position: 'top',
        align: 'end',
        labels: { boxWidth: 10, font: { size: 11, family: 'Plus Jakarta Sans', weight: 600 }, color: '#1D2923', padding: 12 }
      };

      charts.npk = new Chart(ctxN.getContext('2d'), {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'N', data: initialData.npk.N, borderColor: '#087B50', tension: 0.35, pointRadius: 3 },
            { label: 'P', data: initialData.npk.P, borderColor: '#FF9800', tension: 0.35, pointRadius: 3 },
            { label: 'K', data: initialData.npk.K, borderColor: '#0284C7', tension: 0.35, pointRadius: 3 }
          ]
        },
        options: npkOptions
      });

      // Compute initial summary statistics
      updateHistoricalStats(initialData);
    }

    // Actual time filter update handler (Updates displayed data, labels, and stats)
    function applyTimeFilter(range) {
      const dataset = historicalDatasets[range] || historicalDatasets['24h'];
      const labels = dataset.labels;

      if (charts.moisture) {
        charts.moisture.data.labels = labels;
        charts.moisture.data.datasets[0].data = dataset.moisture;
        charts.moisture.update();
      }

      if (charts.ph) {
        charts.ph.data.labels = labels;
        charts.ph.data.datasets[0].data = dataset.ph;
        charts.ph.update();
      }

      if (charts.temp) {
        charts.temp.data.labels = labels;
        charts.temp.data.datasets[0].data = dataset.temperature;
        charts.temp.update();
      }

      if (charts.npk) {
        charts.npk.data.labels = labels;
        charts.npk.data.datasets[0].data = dataset.npk.N;
        charts.npk.data.datasets[1].data = dataset.npk.P;
        charts.npk.data.datasets[2].data = dataset.npk.K;
        charts.npk.update();
      }

      // Recompute and update Avg, Min, Max stats
      updateHistoricalStats(dataset);
    }

    const timeFilter = document.getElementById('time-filter');
    if (timeFilter) {
      timeFilter.addEventListener('change', (e) => {
        applyTimeFilter(e.target.value);
      });
    }

    // ---------- 5. Export CSV Button for Historical Soil Readings ----------
    function showCsvToast(msg) {
      const toast = document.getElementById('csv-export-toast');
      const text = document.getElementById('csv-toast-msg');
      if (!toast) return;
      if (text) text.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => {
        toast.classList.remove('show');
      }, 3500);
    }

    function exportHistoricalCSV() {
      const selectEl = document.getElementById('time-filter');
      const range = selectEl ? selectEl.value : '24h';
      const dataset = historicalDatasets[range] || historicalDatasets['24h'];

      const rows = [
        ['Timestamp', 'Formatted Checkpoint', 'Time Window', 'Soil Moisture (%)', 'Soil pH', 'Soil Temperature (C)', 'Nitrogen (mg/kg)', 'Phosphorus (mg/kg)', 'Potassium (mg/kg)', 'Data Category']
      ];

      for (let i = 0; i < dataset.labels.length; i++) {
        rows.push([
          dataset.labels[i],
          dataset.fullTimestamps[i],
          dataset.timeframeLabel,
          dataset.moisture[i],
          dataset.ph[i],
          dataset.temperature[i],
          dataset.npk.N[i],
          dataset.npk.P[i],
          dataset.npk.K[i],
          'Simulated Historical Reading'
        ]);
      }

      const csvContent = rows.map(r => r.map(val => `"${String(val).replace(/"/g, '""')}"`).join(',')).join('\\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `terravyx_historical_soil_readings_${range}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      showCsvToast(`Exported ${dataset.timeframeLabel} soil readings to CSV!`);
    }

    const exportBtn = document.getElementById('export-csv-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', exportHistoricalCSV);
    }
'''

# Find old chart functions in current_html
script_start_marker = '// ---------- Improved Historical Charts Readability ----------'
script_end_marker = '// ---------- Actionable Recommendations ----------'

s_start = current_html.find(script_start_marker)
s_end = current_html.find(script_end_marker, s_start)

if s_start != -1 and s_end != -1:
    b_part = current_html[:s_start]
    a_part = current_html[s_end:]
    current_html = b_part + new_chart_script + '\n\n    ' + a_part
    print('Replaced chart script in HTML!')
else:
    print('Could not find script markers! s_start:', s_start, 's_end:', s_end)

with open('templates/soil_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(current_html)

print('Updated templates/soil_dashboard.html successfully!')

