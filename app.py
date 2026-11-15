import os
import io
import csv
import json
import random
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response

load_dotenv()
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

# Realistically modeled historical telemetry readings for 24h, 7d, and 30d windows
HISTORICAL_SOIL_DATA = {
    '24h': {
        'timeframe': '24 Hours',
        'records': [
            {'timestamp': '00:00', 'full_time': 'Today 00:00', 'moisture': 38.2, 'ph': 6.75, 'temperature': 22.4, 'N': 46.5, 'P': 33.0, 'K': 39.2},
            {'timestamp': '03:00', 'full_time': 'Today 03:00', 'moisture': 37.5, 'ph': 6.78, 'temperature': 21.8, 'N': 46.2, 'P': 32.8, 'K': 39.0},
            {'timestamp': '06:00', 'full_time': 'Today 06:00', 'moisture': 36.8, 'ph': 6.80, 'temperature': 22.5, 'N': 45.8, 'P': 32.5, 'K': 38.6},
            {'timestamp': '09:00', 'full_time': 'Today 09:00', 'moisture': 35.4, 'ph': 6.84, 'temperature': 25.6, 'N': 45.4, 'P': 32.2, 'K': 38.4},
            {'timestamp': '12:00', 'full_time': 'Today 12:00', 'moisture': 33.8, 'ph': 6.82, 'temperature': 29.8, 'N': 45.1, 'P': 32.0, 'K': 38.1},
            {'timestamp': '15:00', 'full_time': 'Today 15:00', 'moisture': 33.1, 'ph': 6.80, 'temperature': 30.2, 'N': 44.8, 'P': 31.8, 'K': 37.9},
            {'timestamp': '18:00', 'full_time': 'Today 18:00', 'moisture': 34.2, 'ph': 6.79, 'temperature': 28.9, 'N': 45.0, 'P': 32.0, 'K': 38.0},
            {'timestamp': '21:00', 'full_time': 'Today 21:00', 'moisture': 35.0, 'ph': 6.80, 'temperature': 28.0, 'N': 45.0, 'P': 32.0, 'K': 38.0}
        ]
    },
    '7d': {
        'timeframe': '7 Days',
        'records': [
            {'timestamp': 'Nov 8', 'full_time': 'Nov 8, 2026', 'moisture': 29.4, 'ph': 6.65, 'temperature': 26.2, 'N': 49.0, 'P': 34.5, 'K': 41.0},
            {'timestamp': 'Nov 9', 'full_time': 'Nov 9, 2026', 'moisture': 28.0, 'ph': 6.70, 'temperature': 27.5, 'N': 48.2, 'P': 34.0, 'K': 40.2},
            {'timestamp': 'Nov 10', 'full_time': 'Nov 10, 2026', 'moisture': 43.5, 'ph': 6.90, 'temperature': 25.8, 'N': 47.0, 'P': 33.2, 'K': 39.5},
            {'timestamp': 'Nov 11', 'full_time': 'Nov 11, 2026', 'moisture': 41.2, 'ph': 6.85, 'temperature': 26.9, 'N': 46.5, 'P': 32.8, 'K': 39.0},
            {'timestamp': 'Nov 12', 'full_time': 'Nov 12, 2026', 'moisture': 38.6, 'ph': 6.82, 'temperature': 27.8, 'N': 45.8, 'P': 32.4, 'K': 38.5},
            {'timestamp': 'Nov 13', 'full_time': 'Nov 13, 2026', 'moisture': 36.4, 'ph': 6.80, 'temperature': 28.4, 'N': 45.2, 'P': 32.1, 'K': 38.2},
            {'timestamp': 'Nov 14', 'full_time': 'Nov 14, 2026', 'moisture': 35.0, 'ph': 6.80, 'temperature': 28.0, 'N': 45.0, 'P': 32.0, 'K': 38.0}
        ]
    },
    '30d': {
        'timeframe': '30 Days',
        'records': [
            {'timestamp': 'Oct 16', 'full_time': 'Oct 16, 2026', 'moisture': 32.0, 'ph': 6.50, 'temperature': 24.5, 'N': 54.0, 'P': 36.5, 'K': 44.0},
            {'timestamp': 'Oct 19', 'full_time': 'Oct 19, 2026', 'moisture': 27.5, 'ph': 6.55, 'temperature': 25.2, 'N': 52.5, 'P': 35.8, 'K': 43.0},
            {'timestamp': 'Oct 22', 'full_time': 'Oct 22, 2026', 'moisture': 45.0, 'ph': 6.72, 'temperature': 26.0, 'N': 51.0, 'P': 35.0, 'K': 42.1},
            {'timestamp': 'Oct 25', 'full_time': 'Oct 25, 2026', 'moisture': 41.5, 'ph': 6.85, 'temperature': 27.1, 'N': 49.5, 'P': 34.2, 'K': 41.0},
            {'timestamp': 'Oct 28', 'full_time': 'Oct 28, 2026', 'moisture': 36.8, 'ph': 6.80, 'temperature': 28.5, 'N': 48.0, 'P': 33.5, 'K': 40.2},
            {'timestamp': 'Oct 31', 'full_time': 'Oct 31, 2026', 'moisture': 30.2, 'ph': 6.68, 'temperature': 29.0, 'N': 47.0, 'P': 33.0, 'K': 39.5},
            {'timestamp': 'Nov 3', 'full_time': 'Nov 3, 2026', 'moisture': 44.0, 'ph': 6.75, 'temperature': 27.4, 'N': 46.2, 'P': 32.6, 'K': 38.8},
            {'timestamp': 'Nov 6', 'full_time': 'Nov 6, 2026', 'moisture': 39.5, 'ph': 6.82, 'temperature': 26.8, 'N': 45.5, 'P': 32.2, 'K': 38.4},
            {'timestamp': 'Nov 9', 'full_time': 'Nov 9, 2026', 'moisture': 36.2, 'ph': 6.80, 'temperature': 27.5, 'N': 45.2, 'P': 32.1, 'K': 38.2},
            {'timestamp': 'Nov 14', 'full_time': 'Nov 14, 2026', 'moisture': 35.0, 'ph': 6.80, 'temperature': 28.0, 'N': 45.0, 'P': 32.0, 'K': 38.0}
        ]
    }
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
    return render_template('soil_dashboard.html', user=user, soil=SOIL_TELEMETRY, history=HISTORICAL_SOIL_DATA)

@app.route('/api/soil-data')
def api_soil_data():
    """REST API endpoint for real-time telemetry updates"""
    return jsonify(SOIL_TELEMETRY)

@app.route('/api/historical-soil-data')
def api_historical_soil_data():
    """REST API endpoint for historical time series queries"""
    timeframe = request.args.get('timeframe', '24h')
    data = HISTORICAL_SOIL_DATA.get(timeframe, HISTORICAL_SOIL_DATA['24h'])
    return jsonify({
        'timeframe': timeframe,
        'label': data['timeframe'],
        'data_type': 'Simulated Historical Soil Telemetry',
        'records': data['records']
    })

@app.route('/api/export-soil-csv')
def api_export_soil_csv():
    """Export historical soil readings as CSV"""
    timeframe = request.args.get('timeframe', '24h')
    data = HISTORICAL_SOIL_DATA.get(timeframe, HISTORICAL_SOIL_DATA['24h'])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Timestamp', 'Formatted Date/Time', 'Time Window', 
        'Soil Moisture (%)', 'Soil pH', 'Soil Temperature (C)', 
        'Nitrogen (mg/kg)', 'Phosphorus (mg/kg)', 'Potassium (mg/kg)', 'Data Category'
    ])
    for r in data['records']:
        writer.writerow([
            r['timestamp'], r['full_time'], data['timeframe'],
            r['moisture'], r['ph'], r['temperature'],
            r['N'], r['P'], r['K'], 'Simulated Historical Reading'
        ])
    
    csv_bytes = output.getvalue()
    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=terravyx_historical_soil_{timeframe}.csv'}
    )

@app.route('/api/chat', methods=['POST'])
@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """AI Krishi Agronomist chat endpoint backed by Gemini when configured."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'success': False, 'error': 'Request body must be valid JSON.'}), 400

    message = payload.get('message')
    if not isinstance(message, str):
        return jsonify({'success': False, 'error': 'Message must be a string.'}), 400
    message = message.strip()
    history = payload.get('history', [])

    if not message:
        return jsonify({'success': False, 'error': 'Please provide a message.'}), 400
    if len(message) > 4000:
        return jsonify({'success': False, 'error': 'Please keep messages under 4,000 characters.'}), 400
    if not isinstance(history, list):
        return jsonify({'success': False, 'error': 'Conversation history must be a list.'}), 400

    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        return jsonify({
            'success': False,
            'error': 'Gemini API key is not configured. Add GEMINI_API_KEY to your environment to enable live AI responses.'
        }), 503

    model_name = os.getenv('GEMINI_MODEL', 'gemini-3.8-flash').strip()
    if not model_name:
        return jsonify({'success': False, 'error': 'Gemini model is not configured.'}), 503

    fallback_model = 'gemini-3.6-flash'
    max_inline_retry_after = 8
    max_output_tokens = 512

    def parse_duration(value):
        if isinstance(value, (int, float)):
            return max(0.0, float(value))
        if not isinstance(value, str):
            return None

        value = value.strip()
        try:
            return max(0.0, float(value))
        except ValueError:
            pass

        match = re.fullmatch(
            r'(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?',
            value,
            re.IGNORECASE
        )
        if not match or not any(match.groups()):
            return None
        hours, minutes, seconds = (float(part or 0) for part in match.groups())
        return hours * 3600 + minutes * 60 + seconds

    def as_mapping(value):
        if isinstance(value, dict):
            return value
        if hasattr(value, 'model_dump'):
            return value.model_dump(exclude_none=True)
        return {}

    def inspect_gemini_error(exc, failed_model):
        status = getattr(exc, 'code', None)
        error_status = getattr(exc, 'status', None)
        error_name = type(exc).__name__.lower()
        message = getattr(exc, 'message', None) or str(exc)
        details = getattr(exc, 'details', None) or []
        if isinstance(details, dict):
            details = [details]

        quota_fields = []
        retry_after = None
        retry_source = None
        for raw_detail in details:
            detail = as_mapping(raw_detail)
            detail_type = str(detail.get('@type', ''))
            if detail_type.endswith('RetryInfo') and retry_after is None:
                retry_after = parse_duration(detail.get('retryDelay'))
                if retry_after is not None:
                    retry_source = 'google.rpc.RetryInfo'
            if detail_type.endswith('QuotaFailure'):
                for raw_violation in detail.get('violations', []):
                    violation = as_mapping(raw_violation)
                    quota_fields.append({
                        'description': str(violation.get('description', '')),
                        'metric': str(violation.get('quotaMetric', '')),
                        'id': str(violation.get('quotaId', '')),
                        'value': str(violation.get('quotaValue', ''))
                    })

        response = getattr(exc, 'response', None)
        headers = getattr(response, 'headers', {}) if response is not None else {}
        retry_header = headers.get('retry-after') if headers else None
        if retry_header:
            try:
                retry_after = max(0.0, float(retry_header))
            except ValueError:
                try:
                    retry_date = parsedate_to_datetime(retry_header)
                    if retry_date.tzinfo is None:
                        retry_date = retry_date.replace(tzinfo=timezone.utc)
                    retry_after = max(0.0, (retry_date - datetime.now(timezone.utc)).total_seconds())
                except (TypeError, ValueError, OverflowError):
                    retry_after = None
            if retry_after is not None:
                retry_source = 'Retry-After'

        if retry_after is None:
            match = re.search(
                r'\bretry in\s+((?:\d+(?:\.\d+)?h)?(?:\d+(?:\.\d+)?m)?(?:\d+(?:\.\d+)?s)?)',
                message,
                re.IGNORECASE
            )
            if match:
                retry_after = parse_duration(match.group(1))
                if retry_after is not None:
                    retry_source = 'error message'

        quota_text = ' '.join(
            f"{item['description']} {item['metric']} {item['id']}"
            for item in quota_fields
        ).lower()
        compact_quota_text = re.sub(r'[^a-z0-9]+', '', quota_text)
        lowered_message = message.lower()
        quota_type = None
        if 'perday' in compact_quota_text or 'per day' in quota_text or 'daily' in quota_text:
            quota_type = 'daily'
        elif (
            ('billing' in lowered_message or 'credit' in lowered_message or 'payment' in lowered_message)
            and status in (402, 403)
        ):
            quota_type = 'billing'
        elif status == 429 and 'token' in quota_text and ('minute' in quota_text or 'perminute' in compact_quota_text):
            quota_type = 'tpm'
        elif status == 429 and 'request' in quota_text and ('minute' in quota_text or 'perminute' in compact_quota_text):
            quota_type = 'rpm'
        elif status == 429:
            quota_type = 'unknown'

        safe_message = message
        if gemini_api_key:
            safe_message = safe_message.replace(gemini_api_key, '[REDACTED]')
        safe_message = re.sub(r'AIza[0-9A-Za-z_-]{20,}', '[REDACTED]', safe_message)
        safe_message = re.sub(
            r'(?i)(api[_ -]?key|access[_ -]?token|authorization)(\s*[:=]\s*)[^\s,;]+',
            r'\1\2[REDACTED]',
            safe_message
        )[:1200]

        return {
            'model': failed_model,
            'http_status': status,
            'error_status': error_status,
            'error_code': status,
            'exception': type(exc).__name__,
            'message': safe_message,
            'quota_type': quota_type,
            'quota': quota_fields[0] if quota_fields else None,
            'retry_after_seconds': retry_after,
            'retry_source': retry_source,
            'network_failure': any(
                term in error_name
                for term in ('timeout', 'connect', 'network', 'transport', 'protocol', 'readerror', 'writeerror', 'pooltimeout')
            )
        }

    def log_gemini_error(info):
        app.logger.warning(
            'gemini_api_error %s',
            json.dumps(info, ensure_ascii=False, separators=(',', ':'))
        )

    def retry_delay(info, retry_number=1):
        provider_delay = info['retry_after_seconds']
        if provider_delay is not None:
            if provider_delay > max_inline_retry_after:
                return None
            return provider_delay
        base_delay = min(4.0, 0.5 * (2 ** (retry_number - 1)))
        return base_delay + random.uniform(0.0, 0.5)

    def format_retry_after(seconds):
        if seconds is None:
            return None
        total_seconds = max(0, int(round(seconds)))
        if total_seconds >= 3600:
            hours, remainder = divmod(total_seconds, 3600)
            minutes = remainder // 60
            return f'{hours}h {minutes}m' if minutes else f'{hours}h'
        if total_seconds >= 60:
            return f'{total_seconds // 60}m'
        return f'{total_seconds}s'

    def gemini_error_response(info, both_models_failed=False):
        status = info['http_status']
        quota_type = info['quota_type']
        retry_after = info['retry_after_seconds']
        prefix = 'Both Gemini models failed. ' if both_models_failed else ''
        error_code = 'GEMINI_REQUEST_FAILED'
        http_status = 502

        if quota_type == 'daily':
            wait_text = format_retry_after(retry_after)
            wait_advice = f' Retry in about {wait_text}.' if wait_text else ''
            message = (
                f"The Gemini daily free-tier quota is exhausted for {info['model']}."
                f"{wait_advice} No retry or model fallback was attempted for this quota."
            )
            error_code = 'DAILY_QUOTA_EXHAUSTED'
            http_status = 429
        elif quota_type == 'billing':
            message = 'Gemini billing or credits are unavailable. Check the Google AI project billing and credits.'
            error_code = 'BILLING_OR_CREDITS_UNAVAILABLE'
            http_status = 403
        elif status == 401:
            message = 'Gemini rejected the API key. Check GEMINI_API_KEY in the server environment.'
            error_code = 'GEMINI_AUTHENTICATION_FAILED'
            http_status = 502
        elif status == 403:
            message = 'Gemini denied access to this model or project. Check API permissions and billing.'
            error_code = 'GEMINI_ACCESS_FORBIDDEN'
            http_status = 502
        elif status == 404:
            message = f"Gemini model {info['model']} is invalid or unavailable."
            error_code = 'GEMINI_MODEL_UNAVAILABLE'
            http_status = 502
        elif status == 429:
            quota_name = {'rpm': 'RPM', 'tpm': 'TPM'}.get(quota_type)
            if quota_name:
                wait_text = format_retry_after(retry_after)
                advice = f' Retry after about {wait_text}.' if wait_text else ' Please try again later.'
                message = f'Gemini {quota_name} quota was exceeded.{advice} Model fallback is disabled for quota errors.'
                error_code = f'GEMINI_{quota_name}_LIMIT'
            else:
                message = 'Gemini quota is exhausted or rate-limited. Check your AI Studio quota and try again later.'
                error_code = 'GEMINI_QUOTA_LIMIT'
            http_status = 429
        elif status == 503:
            message = 'Gemini is temporarily overloaded. Please try again shortly.'
            error_code = 'GEMINI_MODEL_OVERLOADED'
            http_status = 503
        elif status in (408, 504) or info['network_failure']:
            message = 'Gemini timed out or could not be reached. Please try again shortly.'
            error_code = 'GEMINI_NETWORK_TIMEOUT'
            http_status = 504
        elif status in (500, 502) or (isinstance(status, int) and status >= 500):
            message = 'Gemini is temporarily unavailable. Please try again shortly.'
            error_code = 'GEMINI_UPSTREAM_ERROR'
            http_status = 503
        else:
            message = 'Gemini could not complete this request. Please try again shortly.'

        if retry_after is not None and quota_type != 'daily':
            wait_text = format_retry_after(retry_after)
            if wait_text and status != 429:
                message += f' Provider retry delay: about {wait_text}; no further automatic retry was made.'

        body = {'success': False, 'error': prefix + message, 'error_code': error_code}
        if retry_after is not None:
            body['retry_after_seconds'] = int(round(retry_after))
        return jsonify(body), http_status

    client = None
    try:
        client = genai.Client(
            api_key=gemini_api_key,
            http_options={
                'timeout': 45000,
                'retry_options': {
                    'attempts': 1,
                    'http_status_codes': []
                }
            }
        )
        chat_context = []
        for item in history[-6:]:
            if isinstance(item, dict):
                role = item.get('role', 'user')
                content = item.get('content', '')
                if role in ('user', 'model') and isinstance(content, str) and content.strip():
                    chat_context.append({'role': role, 'parts': [{'text': content[-2000:]}]})

        soil_snapshot = (
            'Configured farm telemetry from the shared SOIL_TELEMETRY dictionary '
            '(these project values are not verified as live sensor readings): '
            f"soil moisture {SOIL_TELEMETRY['moisture']}%, "
            f"pH {SOIL_TELEMETRY['ph']}, "
            f"temperature {SOIL_TELEMETRY['temperature']}°C, "
            f"NPK {SOIL_TELEMETRY['npk']}, "
            f"organic matter {SOIL_TELEMETRY['organic_matter']}%, "
            f"health score {SOIL_TELEMETRY['health_score']}/100."
        )

        prompt = (
            'You are AI Krishi Agronomist for TERRAVYX, an agronomy assistant for Indian farmers. '
            'Answer in clear practical agronomy guidance. Use the latest soil telemetry provided as context. '
            'Keep responses concise but actionable. Prefer local crop and irrigation advice with Indian agriculture context. '
            'Do not invent crop type, soil type, growth stage, weather, or sensor readings. '
            'If crop type, soil type, or growth stage is not supplied, say that recommendations depend on it. '
            'Distinguish the configured dashboard telemetry below from verified live sensor data. '
            f'{soil_snapshot}\n\nUser asks: {message}'
        )

        contents = [*chat_context, {'role': 'user', 'parts': [{'text': prompt}]}]
        generation_config = types.GenerateContentConfig(
            max_output_tokens=512,
            thinking_config=types.ThinkingConfig(thinking_level='minimal')
        )
        def generate_response(model):
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=generation_config
            )

        response_model = model_name
        try:
            response = generate_response(model_name)
        except Exception as primary_error:
            primary_info = inspect_gemini_error(primary_error, model_name)
            log_gemini_error(primary_info)
            status = primary_info['http_status']

            if primary_info['quota_type'] == 'daily' or primary_info['quota_type'] == 'billing':
                return gemini_error_response(primary_info)

            if status == 429:
                if primary_info['quota_type'] not in ('rpm', 'tpm'):
                    return gemini_error_response(primary_info)
                delay = retry_delay(primary_info)
                if delay is None:
                    return gemini_error_response(primary_info)

                app.logger.info(
                    'Gemini quota retry model=%s quota_type=%s delay_seconds=%.2f',
                    model_name,
                    primary_info['quota_type'],
                    delay
                )
                if delay:
                    time.sleep(delay)
                try:
                    response = generate_response(model_name)
                except Exception as retry_error:
                    retry_info = inspect_gemini_error(retry_error, model_name)
                    log_gemini_error(retry_info)
                    return gemini_error_response(retry_info)
            else:
                transient_service_failure = status in (500, 502, 503, 504) or primary_info['network_failure']
                if not transient_service_failure:
                    return gemini_error_response(primary_info)

                delay = retry_delay(primary_info)
                if delay is None:
                    app.logger.info(
                        'Gemini retry deferred model=%s retry_after_seconds=%s',
                        model_name,
                        primary_info['retry_after_seconds']
                    )
                    return gemini_error_response(primary_info)
                if delay:
                    time.sleep(delay)

                if model_name == fallback_model:
                    retry_model = model_name
                else:
                    try:
                        available_models = {
                            item.name.rsplit('/', 1)[-1]
                            for item in client.models.list()
                            if getattr(item, 'name', None)
                        }
                    except Exception as availability_error:
                        availability_info = inspect_gemini_error(availability_error, fallback_model)
                        log_gemini_error(availability_info)
                        return gemini_error_response(primary_info)

                    if fallback_model not in available_models:
                        app.logger.warning(
                            'gemini_fallback_unavailable primary_model=%s fallback_model=%s',
                            model_name,
                            fallback_model
                        )
                        return gemini_error_response(primary_info)
                    retry_model = fallback_model

                app.logger.warning(
                    'gemini_transient_retry primary_model=%s retry_model=%s http_status=%s delay_seconds=%.2f',
                    model_name,
                    retry_model,
                    status,
                    delay
                )
                try:
                    response = generate_response(retry_model)
                    response_model = retry_model
                except Exception as retry_error:
                    retry_info = inspect_gemini_error(retry_error, retry_model)
                    log_gemini_error(retry_info)
                    return gemini_error_response(retry_info, both_models_failed=retry_model != model_name)

        reply_text = getattr(response, 'text', None)
        if not reply_text:
            app.logger.warning('Gemini returned an empty response (model=%s)', response_model)
            return jsonify({'success': False, 'error': 'Gemini returned an empty response. Please try again.'}), 502
        app.logger.info('Gemini response generated (model=%s)', response_model)
        return jsonify({'success': True, 'reply': reply_text.strip()})
    except Exception as exc:
        return gemini_error_response(exc)
    finally:
        if client is not None:
            client.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Bind to 0.0.0.0 so all interfaces (127.0.0.1, localhost, and local network) are accessible
    app.run(host='0.0.0.0', port=5000, debug=True)
