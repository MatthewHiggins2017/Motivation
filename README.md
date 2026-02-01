# Daily Inspiration

A simple web app made to replace social media scrolling in the morning.

-----------

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                         │
├─────────────────────────────────────────────────────────────────┤
│  data/entries.json     ← The database           │
│  generate_page.py      ← Static page generator                  │
│  docs/index.html       ← Generated static page (GitHub Pages)   │
│  app.py                ← Local Flask admin interface            │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
           GitHub Actions            GitHub Pages
           (Daily at 4am UTC)        (Hosts docs/)
           Regenerates page          Serves to visitors
```
-----------


### Public Website (GitHub Pages)

The public-facing site is a **static HTML page** hosted on GitHub Pages from the `docs/` folder. It displays:
- 1 randomly selected quote
- 1 randomly selected poem

The selection is deterministic based on the date—everyone sees the same content on the same day.

-----------


### Daily Regeneration (GitHub Actions)

A GitHub Action automatically regenerates the static page every day:

- **Schedule**: Runs at 4:00 AM UTC daily
- **Process**: 
  1. Checks out the repository
  2. Runs `python generate_page.py`
  3. Commits and pushes the updated `docs/index.html`
- **Manual Trigger**: Can also be run manually via the Actions tab

-----------


### Local Admin Interface (Flask)

Running the Flask app locally to manage and update the database content:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the admin interface
python app.py
```

-----------

### File Structure

```
├── app.py                 # Flask admin interface (run locally)
├── generate_page.py       # Static page generator script
├── requirements.txt       # Python dependencies
├── data/
│   └── entries.json       # Quote & poem database
├── docs/
│   └── index.html         # Generated static page (served by GitHub Pages)
└── .github/
    └── workflows/
        └── daily-update.yml  # Daily regeneration workflow
```