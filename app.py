"""
URL Shortener — A lightweight Flask app to shorten long URLs.

Features:
- Generate 6-character short codes for URLs
- Redirect short URLs to original destinations
- In-memory storage (fast, no database required)
- Input validation and duplicate detection
"""

import string
import random
from flask import Flask, request, render_template, redirect, url_for, abort

app = Flask(__name__)

# In-memory store: short_code -> original_url
url_store: dict[str, str] = {}

# Characters used for generating short codes
CODE_CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
CODE_LENGTH = 6


def generate_short_code(length: int = CODE_LENGTH) -> str:
    """Generate a random alphanumeric short code."""
    return ''.join(random.choices(CODE_CHARS, k=length))


def is_valid_url(url: str) -> bool:
    """Basic URL validation — must start with http:// or https://."""
    return url.startswith(('http://', 'https://'))


@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page — display the URL shortening form."""
    short_url = None
    error = None

    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()

        if not original_url:
            error = 'Please enter a URL.'
        elif not is_valid_url(original_url):
            error = 'URL must start with http:// or https://'
        else:
            # Check if URL already shortened
            existing = next(
                (code for code, url in url_store.items() if url == original_url),
                None
            )
            if existing:
                short_url = url_for('redirect_url', code=existing, _external=True)
            else:
                # Generate unique short code
                code = generate_short_code()
                while code in url_store:
                    code = generate_short_code()
                url_store[code] = original_url
                short_url = url_for('redirect_url', code=code, _external=True)

    return render_template('index.html', short_url=short_url, error=error)


@app.route('/short/<code>')
def redirect_url(code: str):
    """Redirect a short code to its original URL."""
    original = url_store.get(code)
    if original is None:
        abort(404)
    return redirect(original, code=302)


@app.route('/list')
def list_urls():
    """(Utility) List all shortened URLs."""
    return render_template('index.html', 
                          urls=url_store.items(),
                          short_url=None,
                          error=None)


@app.errorhandler(404)
def not_found(e):
    """Custom 404 page."""
    return render_template('index.html',
                          error='Short URL not found. It may have expired or never existed.',
                          short_url=None), 404


if __name__ == '__main__':
    print("🚀 URL Shortener running at http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)

