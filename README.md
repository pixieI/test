# URL Shortener

A lightweight, fast URL shortening service built with Flask.

## Features

- Shorten long URLs into compact 6-character codes
- Redirect from short URLs to original destinations
- Input validation and error handling
- Clean, responsive web interface

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   Navigate to `http://127.0.0.1:5000`

## Usage

1. Enter a valid URL (e.g., `https://example.com/very/long/path`) in the form
2. Click **Shorten**
3. Copy the generated short URL (e.g., `http://127.0.0.1:5000/short/abc123`)
4. Share the short URL — anyone visiting it gets redirected to the original

## Project Structure

```
url-shortener/
├── app.py              # Flask application logic
├── requirements.txt    # Dependencies
├── templates/
│   ├── index.html      # Home page with form
│   └── result.html     # Shortened URL result page
└── README.md           # This file
```

