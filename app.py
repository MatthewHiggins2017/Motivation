#!/usr/bin/env python3
"""
Local Flask app for managing the Motivation Page database.
Run locally to add new quotes and poems via a web form.
"""

import json
import os
import uuid
import requests
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "motivation-page-local-dev"

# Paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "entries.json"

def load_data():
    """Load entries from JSON database."""
    if not DATA_FILE.exists():
        return {"quotes": [], "poems": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """Save entries to JSON database."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_apod():
    """
    Fetch NASA Astronomy Picture of the Day.
    Returns dict with 'url', 'title', 'explanation', and 'media_type' or None if unavailable.
    """
    api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "url": data.get("url"),
            "hdurl": data.get("hdurl"),
            "title": data.get("title"),
            "explanation": data.get("explanation"),
            "media_type": data.get("media_type"),
            "copyright": data.get("copyright"),
        }
    except Exception as e:
        print(f"Warning: Could not fetch APOD: {e}")
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Inspiration</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Calm & Focus Design System - Biophilic & Low Arousal */
            --bg-color: #FDFBF7;           /* Off-White/Cream - reduces eye strain */
            --text-color: #333333;          /* Dark Charcoal - softer than pure black */
            --secondary-color: #5a6a5e;     /* Muted sage for secondary text */
            --border-color: #e8e4dc;        /* Warm light border */
            --accent-color: #8FBC8F;        /* Sage Green - restorative effect */
            --info-color: #AEC6CF;          /* Serene Blue - lowers anxiety */
            --warm-accent: #F88379;         /* Soft Coral - warmth without alertness */
            --card-bg: #F7F5F0;             /* Slightly darker cream for cards */
            --success-color: #8FBC8F;
            --error-color: #d63031;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1a1d1a;            /* Dark with slight green undertone */
                --text-color: #e8e4dc;          /* Warm off-white text */
                --secondary-color: #9aab9e;     /* Muted sage for dark mode */
                --border-color: #2d332d;        /* Subtle green-tinted border */
                --accent-color: #8FBC8F;        /* Sage Green stays consistent */
                --info-color: #AEC6CF;          /* Serene Blue */
                --warm-accent: #F88379;         /* Soft Coral */
                --card-bg: #232823;             /* Dark card background */
                --success-color: #8FBC8F;
                --error-color: #d63031;
            }
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 680px;
            margin: 0 auto;
            padding: 3.6rem 2.4rem;
        }
        
        .admin-icon {
            position: fixed;
            top: 1.5rem;
            right: 1.5rem;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            color: var(--secondary-color);
            text-decoration: none;
            transition: all 0.2s ease;
            z-index: 100;
        }
        
        .admin-icon:hover {
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
            transform: scale(1.05);
        }
        
        .admin-icon svg {
            width: 18px;
            height: 18px;
        }
        
        .back-link {
            position: fixed;
            top: 1.5rem;
            left: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--secondary-color);
            text-decoration: none;
            font-size: 0.875rem;
            transition: color 0.2s ease;
        }
        
        .back-link:hover {
            color: var(--accent-color);
        }
        
        header {
            text-align: center;
            margin-bottom: 4.8rem;
        }
        
        h1 {
            font-size: 1.5rem;
            font-weight: 300;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
            color: var(--secondary-color);
        }
        
        .date {
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--text-color);
        }
        
        h2 {
            font-size: 0.75rem;
            font-weight: 500;
            margin: 3.6rem 0 1.8rem 0;
            color: var(--secondary-color);
            text-transform: uppercase;
            letter-spacing: 0.15em;
        }
        
        .flash {
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        
        .flash.success {
            background: rgba(143, 188, 143, 0.1);
            border: 1px solid var(--success-color);
            color: var(--success-color);
        }
        
        .flash.error {
            background: rgba(214, 48, 49, 0.1);
            border: 1px solid var(--error-color);
            color: var(--error-color);
        }
        
        form {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            color: var(--secondary-color);
        }
        
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background: var(--bg-color);
            color: var(--text-color);
            font-family: inherit;
            font-size: 1rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        
        input[type="text"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(143, 188, 143, 0.1);
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        button {
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 0.875rem 2rem;
            border-radius: 10px;
            font-size: 1rem;
            cursor: pointer;
            font-weight: 500;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(143, 188, 143, 0.3);
        }
        
        .entry {
            padding: 1.8rem;
            margin-bottom: 1.8rem;
            background: var(--card-bg);
            border-radius: 12px;
        }
        
        .entry-text {
            font-size: 1.25rem;
            font-style: italic;
            margin-bottom: 1.2rem;
            line-height: 1.6;
            max-width: 65ch;
        }
        
        .entry-author {
            color: var(--secondary-color);
            font-size: 0.9rem;
        }
        
        .images {
            margin-top: 1.8rem;
            display: flex;
            gap: 0.9rem;
            flex-wrap: wrap;
        }
        
        .images img {
            max-width: 200px;
            border-radius: 12px;
        }
        
        .history-toggle {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            background: none;
            border: 1px solid var(--border-color);
            padding: 0.6rem 1.2rem;
            border-radius: 12px;
            color: var(--secondary-color);
            font-size: 0.8rem;
            cursor: pointer;
            margin-top: 1.2rem;
            transition: all 0.2s ease;
        }
        
        .history-toggle:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
        }
        
        .history-toggle svg {
            width: 14px;
            height: 14px;
            transition: transform 0.2s ease;
        }
        
        .history-toggle.open svg {
            transform: rotate(180deg);
        }
        
        .history-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            background: var(--border-color);
            border-radius: 12px;
            margin-top: 0.9rem;
            font-size: 0.9rem;
            color: var(--secondary-color);
            line-height: 1.6;
            max-width: 65ch;
        }
        
        .history-content.open {
            max-height: 500px;
            padding: 1.2rem;
        }
        
        .apod-section {
            margin-bottom: 3.6rem;
            text-align: center;
        }
        
        .apod-media {
            margin: 1.8rem 0;
        }
        
        .apod-media img {
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .apod-media iframe {
            width: 100%;
            aspect-ratio: 16/9;
            border-radius: 12px;
        }
        
        .apod-title {
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-color);
            margin-top: 1.2rem;
        }
        
        .apod-description {
            margin-top: 3.6rem;
            padding: 2.4rem;
            background: var(--card-bg);
            border-radius: 12px;
        }
        
        .apod-explanation {
            font-size: 0.95rem;
            line-height: 1.6;
            color: var(--text-color);
            margin-bottom: 1.2rem;
            max-width: 65ch;
        }
        
        .apod-copyright {
            font-size: 0.8rem;
            color: var(--secondary-color);
            font-style: italic;
            margin-bottom: 0.6rem;
        }
        
        .apod-credit {
            font-size: 0.8rem;
            color: var(--secondary-color);
        }
        
        .apod-credit a {
            color: var(--accent-color);
            text-decoration: none;
        }
        
        .apod-credit a:hover {
            text-decoration: underline;
        }
        
        .stats {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            justify-content: center;
        }
        
        .stat {
            text-align: center;
            padding: 1.5rem 2rem;
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--accent-color);
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: var(--secondary-color);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        
        footer {
            margin-top: 4.8rem;
            text-align: center;
            color: var(--secondary-color);
            font-size: 0.8rem;
        }
        
        /* Mobile-First Responsive Styles */
        @media (max-width: 768px) {
            .container {
                padding: 2rem 1.25rem;
            }
            
            header {
                margin-bottom: 2.5rem;
            }
            
            h1 {
                font-size: 1.2rem;
                letter-spacing: 0.08em;
            }
            
            .date {
                font-size: 1.75rem;
            }
            
            h2 {
                font-size: 0.7rem;
                margin: 2rem 0 1.2rem 0;
            }
            
            .entry {
                padding: 1.25rem;
                margin-bottom: 1.25rem;
                border-radius: 10px;
            }
            
            .entry-text {
                font-size: 1.1rem;
                line-height: 1.7;
            }
            
            .entry-author {
                font-size: 0.85rem;
            }
            
            .images {
                margin-top: 1.25rem;
                gap: 0.6rem;
            }
            
            .images img {
                max-width: 150px;
                border-radius: 10px;
            }
            
            .history-toggle {
                padding: 0.75rem 1rem;
                font-size: 0.85rem;
                border-radius: 10px;
                min-height: 44px;
            }
            
            .history-content {
                border-radius: 10px;
                font-size: 0.85rem;
            }
            
            .history-content.open {
                padding: 1rem;
            }
            
            .apod-section {
                margin-bottom: 2.5rem;
            }
            
            .apod-media {
                margin: 1.25rem 0;
            }
            
            .apod-media img {
                border-radius: 10px;
            }
            
            .apod-media iframe {
                border-radius: 10px;
            }
            
            .apod-title {
                font-size: 1rem;
                margin-top: 1rem;
            }
            
            .apod-description {
                margin-top: 2.5rem;
                padding: 1.5rem;
                border-radius: 10px;
            }
            
            .apod-explanation {
                font-size: 0.9rem;
                line-height: 1.7;
            }
            
            footer {
                margin-top: 3rem;
                font-size: 0.75rem;
            }
        }
        
        /* Small phones */
        @media (max-width: 375px) {
            .container {
                padding: 1.5rem 1rem;
            }
            
            .date {
                font-size: 1.5rem;
            }
            
            .entry {
                padding: 1rem;
            }
            
            .entry-text {
                font-size: 1rem;
            }
            
            .apod-description {
                padding: 1.25rem;
            }
        }
        
        /* Touch device optimizations */
        @media (hover: none) and (pointer: coarse) {
            .history-toggle {
                padding: 0.875rem 1.25rem;
                min-height: 48px;
            }
            
            .history-toggle:hover {
                border-color: var(--border-color);
                color: var(--secondary-color);
            }
            
            .history-toggle:active {
                border-color: var(--accent-color);
                color: var(--accent-color);
                background: var(--card-bg);
            }
        }
        
        /* Reduce motion for accessibility */
        @media (prefers-reduced-motion: reduce) {
            .history-toggle svg,
            .history-content,
            .history-toggle {
                transition: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
    {% endwith %}
    
    {% block content %}{% endblock %}
    </div>
    <script>
        function toggleHistory(button) {
            button.classList.toggle('open');
            const content = button.nextElementSibling;
            content.classList.toggle('open');
        }
    </script>
</body>
</html>
'''

INDEX_TEMPLATE = '''
{% extends "base" %}
{% block content %}
    <a href="{{ url_for('add_page') }}" class="admin-icon" title="Add new entry">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
    </a>
    
    <header>
        <p class="date">{{ today }}</p>
    </header>
    
    {% if apod and apod.url %}
    <section class="apod-section">
        <h2>Astronomy Picture of the Day</h2>
        <div class="apod-media">
            {% if apod.media_type == 'video' %}
            <iframe src="{{ apod.url }}" frameborder="0" allowfullscreen></iframe>
            {% else %}
            <a href="{{ apod.hdurl or apod.url }}" target="_blank">
                <img src="{{ apod.url }}" alt="{{ apod.title or 'NASA APOD' }}">
            </a>
            {% endif %}
        </div>
    </section>
    {% endif %}
    
    <h2>Today's Quote</h2>
    {% for quote in quotes %}
    <div class="entry">
        <p class="entry-text">"{{ quote.text }}"</p>
        <p class="entry-author">— {{ quote.author }}</p>
        {% if quote.images %}
        <div class="images">
            {% for img in quote.images %}
            <img src="{{ img }}" alt="Quote image">
            {% endfor %}
        </div>
        {% endif %}
        {% if quote.history %}
        <button class="history-toggle" onclick="toggleHistory(this)">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
            History
        </button>
        <div class="history-content">{{ quote.history }}</div>
        {% endif %}
    </div>
    {% endfor %}
    
    <h2>Today's Poem</h2>
    {% if poem %}
    <div class="entry">
        <p class="entry-text">{{ poem.text|replace('\n', '<br>')|safe }}</p>
        <p class="entry-author">— {{ poem.author }}</p>
        {% if poem.images %}
        <div class="images">
            {% for img in poem.images %}
            <img src="{{ img }}" alt="Poem image">
            {% endfor %}
        </div>
        {% endif %}
        {% if poem.history %}
        <button class="history-toggle" onclick="toggleHistory(this)">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
            History
        </button>
        <div class="history-content">{{ poem.history }}</div>
        {% endif %}
    </div>
    {% else %}
    <p style="color: var(--secondary-color); text-align: center;">No poem available</p>
    {% endif %}
    
    {% if apod and apod.url %}
    <section class="apod-description">
        <b><p class="apod-title">{{ apod.title or '' }}</p></b>
        <p class="apod-explanation">{{ apod.explanation or '' }}</p>
        {% if apod.copyright %}
        <p class="apod-copyright">Image Credit: {{ apod.copyright }}</p>
        {% endif %}
        <p class="apod-credit">Image courtesy of <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank">NASA APOD</a></p>
    </section>
    {% endif %}
    
    <footer>
        <p>New inspiration every day</p>
    </footer>
{% endblock %}
'''

ADD_TEMPLATE = '''
{% extends "base" %}
{% block content %}
    <a href="{{ url_for('index') }}" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
    </a>
    
    <header>
        <h1>Add Entry</h1>
        <p class="date" style="font-size: 1rem; font-weight: 400;">Add a new quote or poem</p>
    </header>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{{ quotes|length }}</div>
            <div class="stat-label">Quotes</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ poems|length }}</div>
            <div class="stat-label">Poems</div>
        </div>
    </div>
    
    <form method="POST" action="{{ url_for('add_entry') }}">
        <div class="form-group">
            <label for="type">Type</label>
            <select name="type" id="type" required>
                <option value="quote">Quote</option>
                <option value="poem">Poem</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="text">Text</label>
            <textarea name="text" id="text" required placeholder="Enter the quote or poem text..."></textarea>
        </div>
        
        <div class="form-group">
            <label for="author">Author</label>
            <input type="text" name="author" id="author" required placeholder="Author name">
        </div>
        
        <div class="form-group">
            <label for="history">History / Context (optional)</label>
            <textarea name="history" id="history" placeholder="Background information about this entry..."></textarea>
        </div>
        
        <button type="submit">Add Entry</button>
    </form>
{% endblock %}
'''

PREVIEW_TEMPLATE = '''
{% extends "base" %}
{% block content %}
    <a href="{{ url_for('index') }}" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back
    </a>
    
    <header>
        <h1>Regenerate Page</h1>
        <p class="date" style="font-size: 1rem; font-weight: 400;">
            <a href="{{ url_for('regenerate') }}" style="color: var(--accent-color); text-decoration: none;">Click to regenerate static page</a>
        </p>
    </header>
{% endblock %}
'''

def render_with_base(content_template):
    """Combine base template with content template."""
    content = content_template.replace('{% extends "base" %}', '').replace('{% block content %}', '').replace('{% endblock %}', '')
    return HTML_TEMPLATE.replace('{% block content %}{% endblock %}', content)

@app.route("/")
def index():
    import random
    from datetime import date
    
    data = load_data()
    today_date = date.today()
    seed = int(today_date.strftime("%Y%m%d"))
    rng = random.Random(seed)
    
    quotes = data.get("quotes", [])
    poems = data.get("poems", [])
    
    # Select 1 random quote (matching generate_page.py)
    selected_quotes = [rng.choice(quotes)] if quotes else []
    selected_poem = rng.choice(poems) if poems else None
    
    today = today_date.strftime("%B %d, %Y")
    
    # Fetch NASA APOD
    apod = fetch_apod()
    
    return render_template_string(
        render_with_base(INDEX_TEMPLATE),
        quotes=selected_quotes,
        poem=selected_poem,
        today=today,
        apod=apod
    )

@app.route("/add")
def add_page():
    data = load_data()
    return render_template_string(
        render_with_base(ADD_TEMPLATE),
        quotes=data.get("quotes", []),
        poems=data.get("poems", [])
    )

@app.route("/add-entry", methods=["POST"])
def add_entry():
    entry_type = request.form.get("type")
    text = request.form.get("text", "").strip()
    author = request.form.get("author", "").strip()
    history = request.form.get("history", "").strip()
    
    if not text or not author:
        flash("Text and author are required", "error")
        return redirect(url_for("add_page"))
    
    entry = {
        "id": f"{'q' if entry_type == 'quote' else 'p'}{uuid.uuid4().hex[:8]}",
        "text": text,
        "author": author,
        "history": history,
        "images": []
    }
    
    data = load_data()
    key = "quotes" if entry_type == "quote" else "poems"
    data[key].append(entry)
    save_data(data)
    
    flash(f"Added new {entry_type}!", "success")
    return redirect(url_for("add_page"))

@app.route("/preview")
def preview():
    return render_template_string(
        render_with_base(PREVIEW_TEMPLATE)
    )

@app.route("/regenerate")
def regenerate():
    import subprocess
    try:
        subprocess.run(["python3", "generate_page.py"], cwd=BASE_DIR, check=True)
        flash("Static page regenerated successfully!", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Error regenerating page: {e}", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("Starting Motivation Page Admin...")
    print("Open http://localhost:5001 in your browser")
    app.run(debug=True, port=5001)
