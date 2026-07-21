"""
Supercharged URL Shortener — Flask app with persistence, analytics, custom codes, QR, and API.

Features:
- Generate 6-character short codes (or use a custom alias)
- Redirect short URLs to original destinations
- Persistent JSON storage (survives restarts)
- Click analytics (visit count + last access time)
- QR code generation for any short URL
- REST API for programmatic access
- Delete unwanted URLs
"""

import json
import os
import string
import random
from datetime import datetime, timezone
from io import BytesIO

import qrcode
from flask import (
    Flask, request, render_template, redirect,
    url_for, abort, send_file, jsonify
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'urls.json')

# Characters used for auto-generated short codes
CODE_CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
CODE_LENGTH = 6

# ---------------------------------------------------------------------------
# Data helpers — each entry: {url, created, clicks, last_access}
# ---------------------------------------------------------------------------

def load_data() -> dict:
    """Load URL store from JSON file. Returns empty dict if missing / corrupt."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure legacy flat entries are upgraded
            for code, entry in list(data.items()):
                if isinstance(entry, str):
                    data[code] = {
                        'url': entry,
                        'created': datetime.now(timezone.utc).isoformat(),
                        'clicks': 0,
                        'last_access': None,
                    }
            return data
    except (json.JSONDecodeError, IOError):
        return {}


def save_data(data: dict) -> None:
    """Write URL store to JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def generate_short_code(length: int = CODE_LENGTH) -> str:
    """Generate a random alphanumeric short code."""
    return ''.join(random.choices(CODE_CHARS, k=length))


def is_valid_url(url: str) -> bool:
    """Basic URL validation — must start with http:// or https://."""
    return url.startswith(('http://', 'https://'))


def utc_now() -> str:
    """ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def load_or_create_store() -> dict:
    """Return the global store, loaded from disk on first call."""
    if not hasattr(load_or_create_store, '_store'):
        load_or_create_store._store = load_data()
    return load_or_create_store._store


def persist() -> None:
    """Save the in-memory store to disk."""
    save_data(load_or_create_store())

# ---------------------------------------------------------------------------
# Web routes
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page — display the URL shortening form."""
    store = load_or_create_store()
    short_url = None
    error = None
    last_code = None

    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()
        custom_code = request.form.get('custom_code', '').strip().lower()

        # --- Validation ---
        if not original_url:
            error = 'Please enter a URL.'
        elif not is_valid_url(original_url):
            error = 'URL must start with http:// or https://'
        elif custom_code and not custom_code.isalnum():
            error = 'Custom code must contain only letters and numbers.'
        else:
            # Check for duplicate URL
            for code, entry in store.items():
                if entry['url'] == original_url:
                    short_url = url_for('redirect_url', code=code, _external=True)
                    last_code = code
                    break

            if not short_url:
                # Determine code
                if custom_code:
                    if custom_code in store:
                        error = f'Custom code "{custom_code}" is already taken.'
                    else:
                        code = custom_code
                else:
                    code = generate_short_code()
                    while code in store:
                        code = generate_short_code()

                if not error:
                    store[code] = {
                        'url': original_url,
                        'created': utc_now(),
                        'clicks': 0,
                        'last_access': None,
                    }
                    persist()
                    short_url = url_for('redirect_url', code=code, _external=True)
                    last_code = code

    return render_template(
        'index.html',
        short_url=short_url,
        error=error,
        urls=sorted(store.items(), key=lambda x: x[1].get('created', ''), reverse=True),
        last_code=last_code,
    )


@app.route('/short/<code>')
def redirect_url(code: str):
    """Redirect a short code to its original URL (with click tracking)."""
    store = load_or_create_store()
    entry = store.get(code)
    if entry is None:
        abort(404)

    # Update analytics
    entry['clicks'] = entry.get('clicks', 0) + 1
    entry['last_access'] = utc_now()
    persist()

    return redirect(entry['url'], code=302)


@app.route('/qr/<code>')
def qr_code(code: str):
    """Generate and return a QR code PNG for the short URL."""
    store = load_or_create_store()
    if code not in store:
        abort(404)

    target_url = url_for('redirect_url', code=code, _external=True)

    img = qrcode.make(target_url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png', as_attachment=False,
                     download_name=f'{code}_qr.png')


@app.route('/delete/<code>', methods=['POST'])
def delete_url(code: str):
    """Delete a shortened URL."""
    store = load_or_create_store()
    if code in store:
        del store[code]
        persist()
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    """API: Shorten a URL. Accepts JSON with 'url' and optional 'custom_code'."""
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing "url" in request body'}), 400

    original_url = data['url'].strip()
    custom_code = data.get('custom_code', '').strip().lower()

    if not is_valid_url(original_url):
        return jsonify({'error': 'URL must start with http:// or https://'}), 400
    if custom_code and not custom_code.isalnum():
        return jsonify({'error': 'Custom code must be alphanumeric'}), 400

    store = load_or_create_store()

    # Check duplicates
    for code, entry in store.items():
        if entry['url'] == original_url:
            short_url = url_for('redirect_url', code=code, _external=True)
            return jsonify({
                'original_url': original_url,
                'short_code': code,
                'short_url': short_url,
            })

    # Generate / use custom code
    if custom_code:
        if custom_code in store:
            return jsonify({'error': f'Custom code "{custom_code}" already taken.'}), 409
        code = custom_code
    else:
        code = generate_short_code()
        while code in store:
            code = generate_short_code()

    store[code] = {
        'url': original_url,
        'created': utc_now(),
        'clicks': 0,
        'last_access': None,
    }
    persist()

    short_url = url_for('redirect_url', code=code, _external=True)
    return jsonify({
        'original_url': original_url,
        'short_code': code,
        'short_url': short_url,
    }), 201


@app.route('/api/stats/<code>')
def api_stats(code: str):
    """API: Get analytics for a short code."""
    store = load_or_create_store()
    entry = store.get(code)
    if entry is None:
        return jsonify({'error': 'Short code not found.'}), 404

    return jsonify({
        'short_code': code,
        'original_url': entry['url'],
        'created': entry.get('created'),
        'clicks': entry.get('clicks', 0),
        'last_access': entry.get('last_access'),
        'short_url': url_for('redirect_url', code=code, _external=True),
        'qr_url': url_for('qr_code', code=code, _external=True),
    })


@app.route('/api/urls')
def api_list():
    """API: List all shortened URLs with stats."""
    store = load_or_create_store()
    result = []
    for code, entry in sorted(
        store.items(),
        key=lambda x: x[1].get('created', ''),
        reverse=True
    ):
        result.append({
            'short_code': code,
            'original_url': entry['url'],
            'created': entry.get('created'),
            'clicks': entry.get('clicks', 0),
            'last_access': entry.get('last_access'),
            'short_url': url_for('redirect_url', code=code, _external=True),
            'qr_url': url_for('qr_code', code=code, _external=True),
        })
    return jsonify(result)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    """Custom 404 page."""
    return render_template('index.html',
                          error='Short URL not found. It may have expired or never existed.',
                          short_url=None,
                          urls=None,
                          last_code=None), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("🚀 Supercharged URL Shortener running at http://127.0.0.1:5000")
    print("   Features: Persistence | Analytics | Custom codes | QR codes | REST API")
    app.run(debug=True, host='127.0.0.1', port=5000)


