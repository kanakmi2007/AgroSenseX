import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'terravyx-smart-agri-secret-key-2026'

# Ensure uploads folder exists
os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)

# ----------------- SHARED BACKEND DATA SOURCE ----------------- #
# Unified live telemetry used across Overview Dashboard and Soil Intelligence module
SOIL_TELEMETRY = {
    'moisture': 35,                      # % volumetric soil moisture
    'ph': 6.8,                          # soil acidity/alkalinity
    'temperature': 28,                  # °C root-zone temperature
    'npk': {
        'N': 45,                        # mg/kg Nitrogen
        'P': 32,                        # mg/kg Phosphorus
        'K': 38                         # mg/kg Potassium
    },
    'organic_matter': 3.4,              # %
    'microbiome_status': 'Optimal',
    'health_score': 85,                 # /100
    'health_status': 'Good',
    'last_updated': 'Just now'
}

# ----------------- ROUTES ----------------- #

@app.route('/')
def home():
    """Landing Page matching the Behance UI design"""
    return render_template('home.html')

@app.route('/check', methods=['GET', 'POST'])
def check():
    """Authentication entry point (Login / Signup)"""
    if request.method == 'POST':
        # Simple instant auth for seamless testing
        email = request.form.get('email', 'farmer@terravyx.com')
        session['user'] = email.split('@')[0].capitalize()
        flash('Welcome to TERRAVYX Smart Farm Dashboard!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('home.html', open_auth_modal=True)

@app.route('/dashboard')
def dashboard():
    """Main SaaS Farm Dashboard (Overview)"""
    user = session.get('user', 'Farmer Ramesh')
    return render_template('dashboard.html', user=user, soil=SOIL_TELEMETRY)

@app.route('/dashboard/soil')
@app.route('/soil-dashboard')
def soil_dashboard():
    """Soil Health Intelligence Dashboard"""
    user = session.get('user', 'Farmer Ramesh')
    return render_template('soil_dashboard.html', user=user, soil=SOIL_TELEMETRY)

@app.route('/api/soil-data')
def api_soil_data():
    """REST API endpoint for real-time telemetry updates"""
    return jsonify(SOIL_TELEMETRY)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
