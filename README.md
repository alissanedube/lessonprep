# LessonPrep

LessonPrep helps independent language tutors prepare personalized lessons
faster by bringing each student's goals, recurring difficulties, and next
steps into one private view.

SOEN 287 — Course Project, Fall 2026
Alissane Dube 40375727

## Tech stack
- Back end: Python 3 + Flask
- Front end: HTML5, CSS (Flexbox/Grid, responsive), vanilla JavaScript
- Storage: JSON files in `data/` (no SQL database)
- Authentication: Flask sessions, passwords hashed with Werkzeug (`generate_password_hash`)

## Features (milestone)
- Public landing page
- Public tutor profile (`/tutor/<id>`): languages, levels, teaching approach,
  and a trial-lesson request form, no account needed
- Sign up, log in, log out, with hashed passwords
- Protected dashboard (logged-in tutors only)
- Each tutor sees only their own students and trial requests
- Add a student (name, language, CEFR level, learning goal), validated on the server
- Edit the public profile
- Live validation on the sign-up form (JavaScript)
- Live student filter by name and language (JavaScript)

## Planned next
- Edit and delete students
- Dated lesson notes, difficulty tags (highlighted when seen in 2+ lessons)
- Tutor tasks and the "Prepare next lesson" page

## Setup and run
```bash
# 1. Create and activate a virtual environment
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env          # Windows: copy .env.example .env
# then replace SECRET_KEY with the output of:
python -c "import secrets; print(secrets.token_hex(32))"

# 4. Run
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Data layout
```
data/tutors.json              every tutor: account + public profile
data/tutors/<tutor_id>.json   one tutor's private data: students, trial requests
```

## Project structure
```
app.py            routes, validation, authentication
storage.py        reads and writes the JSON files
templates/        HTML pages (Jinja templates)
static/css/       stylesheet
static/js/        client-side JavaScript
data/             JSON data, created at runtime (not committed)
```
