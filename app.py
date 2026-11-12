import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'terravyx-smart-agri-secret-key-2026'

# Ensure uploads folder exists
os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)

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
    """Main SaaS Farm Dashboard"""
    user = session.get('user', 'Farmer Ramesh')
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)