#!/usr/bin/env python3
"""
Static page generator for the Motivation Page.
Selects random quotes and poem based on the current date (deterministic daily selection).
Outputs index.html for GitHub Pages.
"""

import json
import os
import random
import requests
from datetime import date
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "entries.json"
OUTPUT_FILE = BASE_DIR / "docs" / "index.html"

def load_data():
    """Load entries from JSON database."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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

def select_daily_content(data):
    """
    Select 1 quote and 1 poem based on the current date.
    Uses the date as a seed for reproducible daily selection.
    """
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))
    
    rng = random.Random(seed)
    
    quotes = data.get("quotes", [])
    poems = data.get("poems", [])
    
    # Select 1 random quote
    selected_quotes = [rng.choice(quotes)] if quotes else []
    
    # Select 1 random poem
    selected_poem = rng.choice(poems) if poems else None
    
    return selected_quotes, selected_poem

def generate_html(quotes, poem, apod=None):
    """Generate the static HTML page."""
    today = date.today().strftime("%B %d, %Y")
    
    # Generate APOD section (image above quotes)
    apod_image_html = ""
    apod_description_html = ""
    if apod and apod.get("url"):
        if apod.get("media_type") == "video":
            # Handle video (usually YouTube embed)
            apod_image_html = f'''
            <section class="apod-section">
                <h2>Astronomy Picture of the Day</h2>
                <div class="apod-media">
                    <iframe src="{apod["url"]}" frameborder="0" allowfullscreen></iframe>
                </div>
            </section>
            '''
        else:
            # Handle image
            image_url = apod.get("hdurl") or apod.get("url")
            apod_image_html = f'''
            <section class="apod-section">
                <h2>Astronomy Picture of the Day</h2>
                <div class="apod-media">
                    <a href="{image_url}" target="_blank">
                        <img src="{apod["url"]}" alt="{apod.get("title", "NASA APOD")}">
                    </a>
                </div>
            </section>
            '''
        
        # Description at the bottom
        copyright_text = f'<p class="apod-copyright">Image Credit: {apod["copyright"]}</p>' if apod.get("copyright") else ""
        apod_description_html = f'''
        <section class="apod-description">
            <b><p class="apod-title">{apod.get("title", "")}</p></b>
            <p class="apod-explanation">{apod.get("explanation", "")}</p>
            {copyright_text}
            <p class="apod-credit">Image courtesy of <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank">NASA APOD</a></p>
        </section>
        '''
    
    quotes_html = ""
    for q in quotes:
        images_html = ""
        if q.get("images"):
            images_html = '<div class="images">' + "".join(
                f'<img src="{img}" alt="Quote image">' for img in q["images"]
            ) + '</div>'
        
        history_html = ""
        if q.get("history"):
            history_html = f'''
            <button class="history-toggle" onclick="toggleHistory(this)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
                History
            </button>
            <div class="history-content">{q["history"]}</div>
            '''
        
        quotes_html += f'''
        <div class="entry">
            <p class="entry-text">"{q["text"]}"</p>
            <p class="entry-author">— {q["author"]}</p>
            {images_html}
            {history_html}
        </div>
        '''
    
    poem_html = ""
    if poem:
        poem_text = poem["text"].replace("\n", "<br>")
        images_html = ""
        if poem.get("images"):
            images_html = '<div class="images">' + "".join(
                f'<img src="{img}" alt="Poem image">' for img in poem["images"]
            ) + '</div>'
        
        history_html = ""
        if poem.get("history"):
            history_html = f'''
            <button class="history-toggle" onclick="toggleHistory(this)">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
                History
            </button>
            <div class="history-content">{poem["history"]}</div>
            '''
        
        poem_html = f'''
        <div class="entry">
            <p class="entry-text">{poem_text}</p>
            <p class="entry-author">— {poem["author"]}</p>
            {images_html}
            {history_html}
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Inspiration</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* Calm & Focus Design System - Biophilic & Low Arousal */
            --bg-color: #FDFBF7;           /* Off-White/Cream - reduces eye strain */
            --text-color: #333333;          /* Dark Charcoal - softer than pure black */
            --secondary-color: #5a6a5e;     /* Muted sage for secondary text */
            --border-color: #e8e4dc;        /* Warm light border */
            --accent-color: #8FBC8F;        /* Sage Green - restorative effect */
            --info-color: #AEC6CF;          /* Serene Blue - lowers anxiety */
            --warm-accent: #F88379;         /* Soft Coral - warmth without alertness */
            --card-bg: #F7F5F0;             /* Slightly darker cream for cards */
        }}
        
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1a1d1a;            /* Dark with slight green undertone */
                --text-color: #e8e4dc;          /* Warm off-white text */
                --secondary-color: #9aab9e;     /* Muted sage for dark mode */
                --border-color: #2d332d;        /* Subtle green-tinted border */
                --accent-color: #8FBC8F;        /* Sage Green stays consistent */
                --info-color: #AEC6CF;          /* Serene Blue */
                --warm-accent: #F88379;         /* Soft Coral */
                --card-bg: #232823;             /* Dark card background */
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 680px;
            margin: 0 auto;
            padding: 3.6rem 2.4rem;  /* 20% more padding for breathing room */
        }}
        
        header {{
            text-align: center;
            margin-bottom: 4.8rem;  /* 20% more margin */
        }}
        
        h1 {{
            font-size: 1.5rem;
            font-weight: 300;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.9rem;  /* 20% more margin */
            color: var(--secondary-color);
        }}
        
        .date {{
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--text-color);
        }}
        
        h2 {{
            font-size: 0.75rem;
            font-weight: 500;
            margin: 3.6rem 0 1.8rem 0;  /* 20% more margin */
            color: var(--secondary-color);
            text-transform: uppercase;
            letter-spacing: 0.15em;
        }}
        
        .entry {{
            padding: 1.8rem;              /* 20% more padding */
            margin-bottom: 1.8rem;        /* 20% more margin */
            background: var(--card-bg);
            border-radius: 12px;          /* Curved corners - contour bias */
        }}
        
        .entry-text {{
            font-size: 1.25rem;
            font-style: italic;
            margin-bottom: 1.2rem;        /* 20% more margin */
            line-height: 1.6;
            max-width: 65ch;              /* 60-70 char limit for cognitive ease */
        }}
        
        .entry-author {{
            color: var(--secondary-color);
            font-size: 0.9rem;
        }}
        
        .images {{
            margin-top: 1.8rem;           /* 20% more margin */
            display: flex;
            gap: 0.9rem;                  /* 20% more gap */
            flex-wrap: wrap;
        }}
        
        .images img {{
            max-width: 200px;
            border-radius: 12px;          /* Curved corners */
        }}
        
        .history-toggle {{
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;                  /* 20% more gap */
            background: none;
            border: 1px solid var(--border-color);
            padding: 0.6rem 1.2rem;       /* 20% more padding */
            border-radius: 12px;          /* Curved corners */
            color: var(--secondary-color);
            font-size: 0.8rem;
            cursor: pointer;
            margin-top: 1.2rem;           /* 20% more margin */
            transition: all 0.2s ease;
        }}
        
        .history-toggle:hover {{
            border-color: var(--accent-color);
            color: var(--accent-color);
        }}
        
        .history-toggle svg {{
            width: 14px;
            height: 14px;
            transition: transform 0.2s ease;
        }}
        
        .history-toggle.open svg {{
            transform: rotate(180deg);
        }}
        
        .history-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            background: var(--border-color);
            border-radius: 12px;          /* Curved corners */
            margin-top: 0.9rem;           /* 20% more margin */
            font-size: 0.9rem;
            color: var(--secondary-color);
            line-height: 1.6;
            max-width: 65ch;              /* 60-70 char limit */
        }}
        
        .history-content.open {{
            max-height: 500px;
            padding: 1.2rem;              /* 20% more padding */
        }}
        
        .apod-section {{
            margin-bottom: 3.6rem;        /* 20% more margin */
            text-align: center;
        }}
        
        .apod-media {{
            margin: 1.8rem 0;             /* 20% more margin */
        }}
        
        .apod-media img {{
            max-width: 100%;
            border-radius: 12px;          /* Curved corners */
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);  /* Softer shadow */
        }}
        
        .apod-media iframe {{
            width: 100%;
            aspect-ratio: 16/9;
            border-radius: 12px;          /* Curved corners */
        }}
        
        .apod-title {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-color);
            margin-top: 1.2rem;           /* 20% more margin */
        }}
        
        .apod-description {{
            margin-top: 3.6rem;           /* 20% more margin */
            padding: 2.4rem;              /* 20% more padding */
            background: var(--card-bg);
            border-radius: 12px;          /* Curved corners */
        }}
        
        .apod-explanation {{
            font-size: 0.95rem;
            line-height: 1.6;
            color: var(--text-color);
            margin-bottom: 1.2rem;        /* 20% more margin */
            max-width: 65ch;              /* 60-70 char limit */
        }}
        
        .apod-copyright {{
            font-size: 0.8rem;
            color: var(--secondary-color);
            font-style: italic;
            margin-bottom: 0.6rem;        /* 20% more margin */
        }}
        
        .apod-credit {{
            font-size: 0.8rem;
            color: var(--secondary-color);
        }}
        
        .apod-credit a {{
            color: var(--accent-color);
            text-decoration: none;
        }}
        
        .apod-credit a:hover {{
            text-decoration: underline;
        }}
        
        footer {{
            margin-top: 4.8rem;
            text-align: center;
            color: var(--secondary-color);
            font-size: 0.8rem;
        }}
        
        /* Mobile-First Responsive Styles */
        @media (max-width: 768px) {{
            .container {{
                padding: 2rem 1.25rem;    /* Tighter but comfortable mobile padding */
            }}
            
            header {{
                margin-bottom: 2.5rem;
            }}
            
            h1 {{
                font-size: 1.2rem;
                letter-spacing: 0.08em;
            }}
            
            .date {{
                font-size: 1.75rem;       /* Scaled down for mobile */
            }}
            
            h2 {{
                font-size: 0.7rem;
                margin: 2rem 0 1.2rem 0;
            }}
            
            .entry {{
                padding: 1.25rem;
                margin-bottom: 1.25rem;
                border-radius: 10px;      /* Slightly smaller radius on mobile */
            }}
            
            .entry-text {{
                font-size: 1.1rem;        /* Slightly smaller for mobile readability */
                line-height: 1.7;         /* Increased line-height for mobile */
            }}
            
            .entry-author {{
                font-size: 0.85rem;
            }}
            
            .images {{
                margin-top: 1.25rem;
                gap: 0.6rem;
            }}
            
            .images img {{
                max-width: 150px;         /* Smaller images on mobile */
                border-radius: 10px;
            }}
            
            .history-toggle {{
                padding: 0.75rem 1rem;    /* Larger touch target (min 44px) */
                font-size: 0.85rem;
                border-radius: 10px;
                min-height: 44px;         /* iOS accessibility guideline */
            }}
            
            .history-content {{
                border-radius: 10px;
                font-size: 0.85rem;
            }}
            
            .history-content.open {{
                padding: 1rem;
            }}
            
            .apod-section {{
                margin-bottom: 2.5rem;
            }}
            
            .apod-media {{
                margin: 1.25rem 0;
            }}
            
            .apod-media img {{
                border-radius: 10px;
            }}
            
            .apod-media iframe {{
                border-radius: 10px;
            }}
            
            .apod-title {{
                font-size: 1rem;
                margin-top: 1rem;
            }}
            
            .apod-description {{
                margin-top: 2.5rem;
                padding: 1.5rem;
                border-radius: 10px;
            }}
            
            .apod-explanation {{
                font-size: 0.9rem;
                line-height: 1.7;
            }}
            
            footer {{
                margin-top: 3rem;
                font-size: 0.75rem;
            }}
        }}
        
        /* Small phones */
        @media (max-width: 375px) {{
            .container {{
                padding: 1.5rem 1rem;
            }}
            
            .date {{
                font-size: 1.5rem;
            }}
            
            .entry {{
                padding: 1rem;
            }}
            
            .entry-text {{
                font-size: 1rem;
            }}
            
            .apod-description {{
                padding: 1.25rem;
            }}
        }}
        
        /* Touch device optimizations */
        @media (hover: none) and (pointer: coarse) {{
            .history-toggle {{
                padding: 0.875rem 1.25rem;
                min-height: 48px;         /* Larger touch target */
            }}
            
            .history-toggle:hover {{
                border-color: var(--border-color);
                color: var(--secondary-color);
            }}
            
            .history-toggle:active {{
                border-color: var(--accent-color);
                color: var(--accent-color);
                background: var(--card-bg);
            }}
            
            .apod-credit a:hover {{
                text-decoration: none;
            }}
            
            .apod-credit a:active {{
                text-decoration: underline;
            }}
        }}
        
        /* Landscape mobile */
        @media (max-width: 768px) and (orientation: landscape) {{
            .container {{
                padding: 1.5rem 2rem;
            }}
            
            header {{
                margin-bottom: 2rem;
            }}
            
            .apod-media img {{
                max-width: 70%;           /* Constrain in landscape */
            }}
        }}
        
        /* Reduce motion for accessibility */
        @media (prefers-reduced-motion: reduce) {{
            .history-toggle svg,
            .history-content,
            .history-toggle {{
                transition: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <p class="date">{today}</p>
        </header>
        
        <main>
            {apod_image_html}
            
            <h2>Today's Quotes</h2>
            {quotes_html}
            
            <h2>Today's Poem</h2>
            {poem_html}
            
            {apod_description_html}
        </main>
        
        <footer>
            <p>New inspiration every day</p>
        </footer>
    </div>
    <script>
        function toggleHistory(button) {{
            button.classList.toggle('open');
            const content = button.nextElementSibling;
            content.classList.toggle('open');
        }}
    </script>
</body>
</html>
'''
    return html

def main():
    """Main entry point."""
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load data and select content
    data = load_data()
    quotes, poem = select_daily_content(data)
    
    # Fetch NASA APOD
    apod = fetch_apod()
    if apod:
        print(f"Fetched APOD: {apod.get('title', 'Unknown')}")
    else:
        print("Warning: APOD not available, generating without it")
    
    # Generate and write HTML
    html = generate_html(quotes, poem, apod)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated {OUTPUT_FILE}")
    print(f"Selected {len(quotes)} quotes and {'1 poem' if poem else 'no poem'}")

if __name__ == "__main__":
    main()
