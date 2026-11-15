
    // ---------- Shared Telemetry Data (From Flask Backend) ----------
    const sharedData = {
      moisture: Number('35') || 35,
      ph: Number('6.8') || 6.8,
      temperature: Number('28') || 28,
      npk: { 
        N: Number('45') || 45, 
        P: Number('32') || 32, 
        K: Number('38') || 38 
      },
      timestamp: new Date().toISOString()
    };
    const demoData = sharedData;

    // Crop specific suitability ranges
    const cropRanges = {
      wheat: {
        label: 'Wheat',
        moisture: [30, 60],
        ph: [6.0, 7.5],
        temperature: [15, 30],
        summary: 'Current soil parameters strongly favor early wheat vegetative growth and root aeration.'
      },
      rice: {
        label: 'Rice (Paddy)',
        moisture: [60, 90],
        ph: [5.5, 6.5],
        temperature: [20, 32],
        summary: 'Rice requires substantially higher soil water saturation. Irrigation will be mandatory.'
      },
      tomato: {
        label: 'Tomato',
        moisture: [50, 70],
        ph: [5.5, 7.0],
        temperature: [18, 28],
        summary: 'Soil moisture is on the lower threshold for optimal tomato blossom retention.'
      },
      potato: {
        label: 'Potato',
        moisture: [45, 65],
        ph: [5.0, 6.5],
        temperature: [15, 24],
        summary: 'Ambient temperature is above the optimal tuber initiation window (18°C-22°C).'
      },
      maize: {
        label: 'Maize (Corn)',
        moisture: [40, 70],
        ph: [5.8, 7.2],
        temperature: [18, 30],
        summary: 'Excellent conditions for maize germination, root anchoring, and nitrogen uptake.'
      }
    };

    // ---------- UI Live Update Functions ----------
    function updateLiveCards(data) {
      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      // Moisture
      const mVal = document.getElementById('moisture-value');
      if (mVal) mVal.textContent = data.moisture + '%';
      setStatus('moisture-status', evaluateStatus('moisture', data.moisture));
      const mUpd = document.getElementById('moisture-updated');
      if (mUpd) mUpd.textContent = 'Target: 30% - 60% • Updated ' + now;

      // pH
      const pVal = document.getElementById('ph-value');
      if (pVal) pVal.textContent = data.ph;
      setStatus('ph-status', evaluateStatus('ph', data.ph));
      const pUpd = document.getElementById('ph-updated');
      if (pUpd) pUpd.textContent = 'Target: 6.0 - 7.5 • Updated ' + now;

      // Temperature
      const tVal = document.getElementById('temp-value');
      if (tVal) tVal.textContent = data.temperature + '°C';
      setStatus('temp-status', evaluateStatus('temperature', data.temperature));
      const tUpd = document.getElementById('temp-updated');
      if (tUpd) tUpd.textContent = 'Target: 18°C - 30°C • Updated ' + now;

      // NPK Nutrient Card
      const npk = data.npk;
      const nSpan = document.getElementById('n-val');
      const pSpan = document.getElementById('p-val');
      const kSpan = document.getElementById('k-val');
      if (nSpan) nSpan.textContent = npk.N + ' mg/kg';
      if (pSpan) pSpan.textContent = npk.P + ' mg/kg';
      if (kSpan) kSpan.textContent = npk.K + ' mg/kg';

      // Compatibility container for legacy selectors
      const npkContainer = document.getElementById('npk-indicators');
      if (npkContainer) {
        npkContainer.innerHTML = `
          <div class="npk-item"><span class="label">N</span>: ${npk.N} mg/kg</div>
          <div class="npk-item"><span class="label">P</span>: ${npk.P} mg/kg</div>
          <div class="npk-item"><span class="label">K</span>: ${npk.K} mg/kg</div>
        `;
      }
      setStatus('npk-status', evaluateNPKStatus(npk));
      const npkUpd = document.getElementById('npk-updated');
      if (npkUpd) npkUpd.textContent = 'Updated: ' + now + ' • Demo data';
    }

    function setStatus(elementId, status) {
      const el = document.getElementById(elementId);
      if (!el) return;
      el.textContent = status.label;
      el.className = 'status-badge status-' + status.type;
    }

    function evaluateStatus(metric, value) {
      if (metric === 'moisture') {
        if (value < 30) return {type:'warning', label:'Low'};
        if (value > 70) return {type:'warning', label:'High'};
        return {type:'good', label:'Normal'};
      }
      if (metric === 'ph') {
        if (value < 5.5) return {type:'warning', label:'Acidic'};
        if (value > 7.5) return {type:'warning', label:'Alkaline'};
        return {type:'good', label:'Balanced'};
      }
      if (metric === 'temperature') {
        if (value < 10) return {type:'warning', label:'Cold'};
        if (value > 35) return {type:'warning', label:'Hot'};
        return {type:'good', label:'Optimal'};
      }
      return {type:'good', label:'Normal'};
    }

    function evaluateNPKStatus(npk) {
      if (npk.N < 40 || npk.P < 30 || npk.K < 35) return {type:'warning', label:'Deficient'};
      return {type:'good', label:'Sufficient'};
    }

    // ---------- Soil Health Score Calculation & Canvas Gauge ----------
    function calculateHealthScore(data) {
      const moistureScore = Math.min(100, Math.round((data.moisture / 60) * 100));
      const phScore = Math.min(100, Math.round((Math.abs(7 - data.ph) < 1 ? 95 : 100 - Math.abs(7 - data.ph) * 30)));
      const tempScore = Math.min(100, Math.round((1 - Math.abs(24 - data.temperature) / 25) * 100));
      const npkScore = Math.min(100, Math.round(((data.npk.N + data.npk.P + data.npk.K) / (3 * 50)) * 100));
      const overall = Math.round(moistureScore * 0.3 + phScore * 0.3 + tempScore * 0.25 + npkScore * 0.15);
      return { overall, moistureScore, phScore, tempScore, npkScore };
    }

    function renderHealthScore(scoreObj) {
      const container = document.getElementById('health-score-circle');
      if (container) {
        container.innerHTML = '';
        const canvas = document.createElement('canvas');
        canvas.width = 130;
        canvas.height = 130;
        const ctx = canvas.getContext('2d');
        const startAngle = -0.5 * Math.PI;
        const endAngle = startAngle + (scoreObj.overall / 100) * 2 * Math.PI;

        // Background Track
        ctx.beginPath();
        ctx.arc(65, 65, 54, 0, 2 * Math.PI);
        ctx.strokeStyle = '#E5E9E3';
        ctx.lineWidth = 10;
        ctx.stroke();

        // Active Ring
        ctx.beginPath();
        ctx.arc(65, 65, 54, startAngle, endAngle);
        ctx.strokeStyle = '#087B50';
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();

        container.appendChild(canvas);
      }

      const label = document.getElementById('health-score-label');
      if (label) {
        let status = 'Good';
        if (scoreObj.overall < 60) status = 'Moderate';
        if (scoreObj.overall < 40) status = 'Poor';
        label.innerHTML = `<strong>${scoreObj.overall}%</strong><span>${status}</span>`;
      }

      const setBar = (id, val) => {
        const bar = document.getElementById(id + '-fill');
        const valSpan = document.getElementById(id + '-val');
        if (bar) bar.style.width = val + '%';
        if (valSpan) valSpan.textContent = val + '%';
      };
      setBar('moisture', scoreObj.moistureScore);
      setBar('ph', scoreObj.phScore);
      setBar('temp', scoreObj.tempScore);
      setBar('npk', scoreObj.npkScore);
    }

    // ---------- Improved Crop Suitability Presentation ----------
    function updateCropSuitability(crop) {
      const config = cropRanges[crop] || cropRanges['wheat'];
      const data = demoData;
      
      const mGood = inRange(data.moisture, config.moisture);
      const pGood = inRange(data.ph, config.ph);
      const tGood = inRange(data.temperature, config.temperature);

      let goodCount = 0;
      if (mGood) goodCount++;
      if (pGood) goodCount++;
      if (tGood) goodCount++;

      // Compute weighted percentage score
      let overall = Math.round((goodCount / 3) * 100);
      if (goodCount === 2) overall = 75;
      if (goodCount === 1) overall = 45;
      if (goodCount === 0) overall = 20;

      // Update badge and text
      const scoreText = document.getElementById('crop-score');
      if (scoreText) {
        scoreText.textContent = `Overall suitability for ${config.label}: ${overall}%`;
      }

      const scoreDesc = document.getElementById('crop-summary-desc');
      if (scoreDesc) {
        scoreDesc.textContent = config.summary;
      }

      const scoreBadge = document.getElementById('crop-score-badge');
      if (scoreBadge) {
        scoreBadge.textContent = overall + '%';
        if (overall >= 80) {
          scoreBadge.style.background = 'rgba(8, 123, 80, 0.15)';
          scoreBadge.style.borderColor = 'rgba(8, 123, 80, 0.4)';
          scoreBadge.style.color = '#087B50';
        } else if (overall >= 50) {
          scoreBadge.style.background = 'rgba(230, 126, 34, 0.15)';
          scoreBadge.style.borderColor = 'rgba(230, 126, 34, 0.4)';
          scoreBadge.style.color = '#D35400';
        } else {
          scoreBadge.style.background = 'rgba(231, 76, 60, 0.15)';
          scoreBadge.style.borderColor = 'rgba(231, 76, 60, 0.4)';
          scoreBadge.style.color = '#C0392B';
        }
      }

      // Render structured parameter cards into #crop-factors
      const list = document.getElementById('crop-factors');
      if (list) {
        const factors = [
          {
            name: 'Soil Moisture',
            icon: 'fa-tint',
            current: data.moisture + '%',
            target: config.moisture[0] + '% - ' + config.moisture[1] + '%',
            isGood: mGood,
            percent: Math.min(100, Math.max(10, Math.round((data.moisture / config.moisture[1]) * 100)))
          },
          {
            name: 'Soil pH Level',
            icon: 'fa-flask',
            current: data.ph,
            target: config.ph[0] + ' - ' + config.ph[1],
            isGood: pGood,
            percent: Math.min(100, Math.max(10, Math.round((data.ph / 10) * 100)))
          },
          {
            name: 'Soil Temperature',
            icon: 'fa-thermometer-half',
            current: data.temperature + '°C',
            target: config.temperature[0] + '°C - ' + config.temperature[1] + '°C',
            isGood: tGood,
            percent: Math.min(100, Math.max(10, Math.round((data.temperature / 40) * 100)))
          }
        ];

        list.innerHTML = factors.map(f => {
          const badgeClass = f.isGood ? 'status-good' : 'status-warning';
          const badgeText = f.isGood ? 'Optimal' : 'Sub-optimal';
          const barColor = f.isGood ? '#087B50' : '#E67E22';

          return `
            <div class="crop-factor-item">
              <div class="factor-header">
                <span class="factor-name">
                  <i class="fas ${f.icon}" style="color:${barColor};"></i>
                  ${f.name}
                </span>
                <span class="factor-badge ${badgeClass}">${badgeText}</span>
              </div>
              <div class="factor-sub">
                <span>Reading: <strong>${f.current}</strong></span>
                <span>Target: <strong>${f.target}</strong></span>
              </div>
              <div class="factor-bar">
                <div class="factor-bar-fill" style="width: ${f.percent}%; background: ${barColor};"></div>
              </div>
            </div>
          `;
        }).join('');
      }

      // Limiting factor note
      const limitingContainer = document.getElementById('limiting-factor-container');
      if (limitingContainer) {
        if (!mGood || !pGood || !tGood) {
          const limitingFactors = [];
          if (!mGood) limitingFactors.push(`Moisture (${data.moisture}% vs target ${config.moisture[0]}-${config.moisture[1]}%)`);
          if (!pGood) limitingFactors.push(`pH (${data.ph} vs target ${config.ph[0]}-${config.ph[1]})`);
          if (!tGood) limitingFactors.push(`Temperature (${data.temperature}°C vs target ${config.temperature[0]}-${config.temperature[1]}°C)`);

          limitingContainer.innerHTML = `
            <div class="limiting-factor-note">
              <i class="fas fa-triangle-exclamation"></i>
              <span><strong>Limiting Factor:</strong> ${limitingFactors.join(', ')}. Action recommended before planting.</span>
            </div>
          `;
        } else {
          limitingContainer.innerHTML = '';
        }
      }
    }

    function inRange(value, [min, max]) { return value >= min && value <= max; }

    // ---------- Improved AI Advisor Multi-Section Output ----------
    const aiBtn = document.getElementById('ai-analyze-btn');
    if (aiBtn) {
      aiBtn.addEventListener('click', () => {
        const results = document.getElementById('ai-results');
        if (!results) return;

        aiBtn.disabled = true;
        aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Telemetry...';

        setTimeout(() => {
          results.innerHTML = `
            <div class="ai-output-box">
              <div class="ai-output-top-bar">
                <div class="ai-output-header">
                  <i class="fas fa-sparkles"></i> Autonomous Soil Diagnostic Report
                </div>
                <span class="demo-tag-mini"><i class="fas fa-microchip"></i> SIMULATED ADVISORY • DEMO DATA</span>
              </div>

              <!-- 1. Detected Conditions -->
              <div>
                <div class="ai-section-title"><i class="fas fa-sensors"></i> 1. Detected Field Conditions</div>
                <div class="ai-conditions-grid">
                  <div class="ai-cond-chip">
                    <span class="ai-cond-label">Volumetric Moisture</span>
                    <span class="ai-cond-val" style="color:#087B50;">35% (Normal)</span>
                  </div>
                  <div class="ai-cond-chip">
                    <span class="ai-cond-label">Soil Acidity (pH)</span>
                    <span class="ai-cond-val" style="color:#0284C7;">6.8 (Balanced)</span>
                  </div>
                  <div class="ai-cond-chip">
                    <span class="ai-cond-label">Subsurface Temp</span>
                    <span class="ai-cond-val" style="color:#E67E22;">28°C (Optimal)</span>
                  </div>
                  <div class="ai-cond-chip">
                    <span class="ai-cond-label">NPK Vector Balance</span>
                    <span class="ai-cond-val" style="color:#087B50;">45-32-38 (Sufficient)</span>
                  </div>
                </div>
              </div>

              <!-- 2. Analytical Evaluation -->
              <div>
                <div class="ai-section-title"><i class="fas fa-microscope"></i> 2. Agronomic Analysis</div>
                <div class="ai-analysis-block">
                  <p class="ai-analysis-text">
                    <strong>Rhizosphere Assessment:</strong> Topsoil moisture at 35% demonstrates balanced pore-space aeration without waterlogging risks. Soil pH of 6.8 falls squarely within the sweet spot for nitrogen mineralization and phosphorus bioavailability. The 28°C surface reading fosters active nitrifying microbial populations.
                  </p>
                </div>
              </div>

              <!-- 3. Actionable Recommendations -->
              <div>
                <div class="ai-section-title"><i class="fas fa-list-check"></i> 3. Recommended Actions</div>
                <ul class="ai-recs-list">
                  <li><i class="fas fa-circle-check"></i> <strong>Irrigation Scheduling:</strong> Current water reserve is stable. Defer irrigation until evening to prevent evaporative loss.</li>
                  <li><i class="fas fa-circle-check"></i> <strong>Nutrient Timing:</strong> Nitrogen levels (45 mg/kg) support vegetative canopy. Plan booster potassium application at flowering.</li>
                  <li><i class="fas fa-circle-check"></i> <strong>Soil Conditioning:</strong> Maintain organic mulch layer to preserve microbial buffer during midday peak heat.</li>
                </ul>
              </div>
            </div>
          `;
          aiBtn.disabled = false;
          aiBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Re-Run AI Soil Diagnostic';
        }, 350);
      });
    }

        // ---------- 3. Improved Historical Charts & Telemetry Datasets ----------
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

    // Fetch historical telemetry series directly from the Flask API endpoint
    async function fetchHistoricalData(range) {
      try {
        const res = await fetch(`/api/historical-soil-data?timeframe=${encodeURIComponent(range)}`);
        if (res.ok) {
          const json = await res.json();
          if (json && Array.isArray(json.records) && json.records.length > 0) {
            return {
              timeframeLabel: json.label || (range === '24h' ? '24 Hours' : range === '7d' ? '7 Days' : '30 Days'),
              labels: json.records.map(r => r.timestamp),
              fullTimestamps: json.records.map(r => r.full_time),
              moisture: json.records.map(r => r.moisture),
              ph: json.records.map(r => r.ph),
              temperature: json.records.map(r => r.temperature),
              npk: {
                N: json.records.map(r => r.N),
                P: json.records.map(r => r.P),
                K: json.records.map(r => r.K)
              }
            };
          }
        }
      } catch (err) {
        console.warn('API fetch error, using local fallback:', err);
      }
      return historicalDatasets[range] || historicalDatasets['24h'];
    }

    // Actual time filter update handler connected to HISTORICAL_SOIL_DATA API
    async function applyTimeFilter(range) {
      const dataset = await fetchHistoricalData(range);
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
      window.location.href = `/api/export-soil-csv?timeframe=${encodeURIComponent(range)}`;
      showCsvToast(`Downloading historical soil readings for ${range === '24h' ? '24 Hours' : range === '7d' ? '7 Days' : '30 Days'}...`);
    }

    const exportBtn = document.getElementById('export-csv-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', exportHistoricalCSV);
    }


    // ---------- Actionable Recommendations ----------
    function generateRecommendations() {
      const recDiv = document.getElementById('recommendations');
      if (!recDiv) return;
      const recs = [
        { title: 'Moisture Aeration Window', text: 'Moisture level is at 35%. Consistent with scheduled field aeration; no daytime irrigation required before 18:00.', icon: 'fa-droplet' },
        { title: 'Optimal pH Bioavailability', text: 'Soil pH is well-balanced at 6.8. Excellent availability of essential micronutrients like zinc and magnesium.', icon: 'fa-vial' },
        { title: 'Nitrogen Reservoir Management', text: 'Adequate Nitrogen reserves (45 mg/kg). Supports vigorous leaf development; continue planned rotation schedule.', icon: 'fa-seedling' },
        { title: 'Topsoil Temperature Equilibrium', text: 'Temperature is 28°C. Enhanced microbiological respiration; maintain organic mulch cover during afternoon heat.', icon: 'fa-temperature-sun' }
      ];
      
      recDiv.innerHTML = recs.map(r => `
        <div class="recommendation-card">
          <div class="rec-icon"><i class="fas ${r.icon}"></i></div>
          <div class="rec-content">
            <h4>${r.title}</h4>
            <p>${r.text}</p>
          </div>
        </div>
      `).join('');
    }

    // ---------- Navigation & Sidebar Active State Handler ----------
    function setupNavigation() {
      const sidebarLinks = document.querySelectorAll('.sidebar-menu .menu-item');
      const topNavLinks = document.querySelectorAll('.top-nav .nav-link');
      const mobileBtn = document.getElementById('mobile-menu-btn');
      const closeBtn = document.getElementById('sidebar-close-btn');
      const backdrop = document.getElementById('sidebar-backdrop');
      const sidebar = document.getElementById('sidebar');

      // Mobile Drawer Toggle
      function openMobileSidebar() {
        if (sidebar) sidebar.classList.add('mobile-open');
        if (backdrop) backdrop.classList.add('mobile-open');
      }
      function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (backdrop) backdrop.classList.remove('mobile-open');
      }

      if (mobileBtn) mobileBtn.addEventListener('click', openMobileSidebar);
      if (closeBtn) closeBtn.addEventListener('click', closeMobileSidebar);
      if (backdrop) backdrop.addEventListener('click', closeMobileSidebar);

      // Section Scrollspy
      const sections = [
        { id: 'overview-section', el: document.getElementById('overview-section') },
        { id: 'crop-section', el: document.getElementById('crop-section') },
        { id: 'ai-section', el: document.getElementById('ai-section') },
        { id: 'recommendations-section', el: document.getElementById('recommendations-section') },
        { id: 'historical-section', el: document.getElementById('historical-section') }
      ];

      function setActiveSection(sectionId) {
        sidebarLinks.forEach(item => {
          if (item.dataset.section === sectionId) {
            item.classList.add('active');
          } else if (item.dataset.section) {
            item.classList.remove('active');
          }
        });

        topNavLinks.forEach(link => {
          if (link.dataset.section === sectionId) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }

      sidebarLinks.forEach(item => {
        const link = item.querySelector('a');
        if (link && link.getAttribute('href').startsWith('#')) {
          link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href').substring(1);
            setActiveSection(targetId);
            closeMobileSidebar();
          });
        }
      });

      topNavLinks.forEach(link => {
        if (link.getAttribute('href').startsWith('#')) {
          link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href').substring(1);
            setActiveSection(targetId);
          });
        }
      });

      window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY + 120;
        let currentSectionId = 'overview-section';

        sections.forEach(sec => {
          if (sec.el && sec.el.offsetTop <= scrollPosition) {
            currentSectionId = sec.id;
          }
        });

        setActiveSection(currentSectionId);
      }, { passive: true });
    }

    // ---------- Initialization ----------
    function init() {
      updateLiveCards(demoData);
      const scoreObj = calculateHealthScore(demoData);
      renderHealthScore(scoreObj);
      
      const cropSelect = document.getElementById('crop-select');
      if (cropSelect) {
        cropSelect.addEventListener('change', e => updateCropSuitability(e.target.value));
        updateCropSuitability('wheat');
      }

      initCharts();
      applyTimeFilter('24h');
      generateRecommendations();
      setupNavigation();
    }

    window.addEventListener('DOMContentLoaded', init);
  