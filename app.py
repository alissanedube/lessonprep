"""LessonPrep — lesson preparation for independent language tutors.

Milestone version:
  - public landing page
  - public tutor profile with a trial-lesson request form (no account needed)
  - registration, login, logout (hashed passwords, sessions)
  - protected dashboard: the tutor's own students, profile and trial requests
"""
import os
import re
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import storage

load_dotenv()  # reads SECRET_KEY and FLASK_DEBUG from the .env file

app = Flask(__name__)

# The secret key signs the session cookie. It comes from the environment,
# never from the source code. Without it, the app refuses to start.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and set it.")

# Session cookie hardening: JavaScript cannot read it, and it is not sent
# on requests coming from other websites.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


# ---------- Helpers ----------

def login_required(view):
    """Decorator: send visitors who are not logged in to the login page."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "tutor_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def field(name):
    """Read a form field safely: missing fields become "" instead of crashing."""
    return (request.form.get(name) or "").strip()


def valid_email(email):
    return bool(EMAIL_RE.match(email)) and len(email) <= 120


# ---------- Public pages ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tutor/<tutor_id>", methods=["GET", "POST"])
def public_profile(tutor_id):
    """The tutor's public front door. Anyone can view it and send a
    trial-lesson request; nothing private is shown here."""
    tutor = storage.find_tutor_by_id(tutor_id)
    if tutor is None:
        abort(404)

    if request.method == "POST":
        name = field("name")
        email = field("email").lower()
        message = field("message")

        errors = []
        if not 1 <= len(name) <= 60:
            errors.append("Please enter your name (max 60 characters).")
        if not valid_email(email):
            errors.append("Please enter a valid email address.")
        if not 1 <= len(message) <= 1000:
            errors.append("Please write a short message (max 1000 characters).")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("profile_public.html", tutor=tutor,
                                   form={"name": name, "email": email, "message": message}), 400

        storage.add_trial_request(tutor["id"], name, email, message)
        flash(f"Thanks! {tutor['name']} will contact you soon.", "success")
        return redirect(url_for("public_profile", tutor_id=tutor["id"]))

    return render_template("profile_public.html", tutor=tutor, form={})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", form={})

    name = field("name")
    email = field("email").lower()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""

    # Server-side validation: the browser checks can be bypassed,
    # so every rule is checked again here.
    errors = []
    if not 1 <= len(name) <= 60:
        errors.append("Name is required (max 60 characters).")
    if not valid_email(email):
        errors.append("Enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")

    if not errors:
        tutor = storage.create_tutor(name, email, generate_password_hash(password))
        if tutor is None:
            errors.append("An account with this email already exists.")
        else:
            session.clear()
            session["tutor_id"] = tutor["id"]
            flash(f"Welcome to LessonPrep, {tutor['name']}!", "success")
            return redirect(url_for("dashboard"))

    for e in errors:
        flash(e, "error")
    # Send back what was typed (except passwords) so the user does not retype it.
    return render_template("register.html", form={"name": name, "email": email}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", form={})

    email = field("email").lower()
    password = request.form.get("password") or ""
    tutor = storage.find_tutor_by_email(email)

    # Same message whether the email or the password is wrong,
    # so an attacker cannot discover which emails have accounts.
    if tutor is None or not check_password_hash(tutor["password_hash"], password):
        flash("Incorrect email or password.", "error")
        return render_template("login.html", form={"email": email}), 401

    session.clear()  # start a fresh session at login
    session["tutor_id"] = tutor["id"]
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You are logged out.", "success")
    return redirect(url_for("index"))


# ---------- Protected pages ----------

@app.route("/dashboard")
@login_required
def dashboard():
    tutor = storage.find_tutor_by_id(session["tutor_id"])
    if tutor is None:  # account no longer exists
        session.clear()
        return redirect(url_for("login"))
    students = storage.list_students(tutor["id"])
    languages = sorted({s["language"] for s in students}, key=str.lower)
    return render_template(
        "dashboard.html",
        tutor=tutor,
        students=students,
        languages=languages,
        requests=storage.list_trial_requests(tutor["id"]),
        levels=LEVELS,
    )


@app.route("/students", methods=["POST"])
@login_required
def add_student():
    name = field("name")
    language = field("language")
    level = field("level")
    goal = field("goal")

    errors = []
    if not 1 <= len(name) <= 60:
        errors.append("Student name is required (max 60 characters).")
    if not 1 <= len(language) <= 40:
        errors.append("Language is required (max 40 characters).")
    if level not in LEVELS:
        errors.append("Choose a level between A1 and C2.")
    if len(goal) > 200:
        errors.append("Learning goal must be 200 characters or less.")

    if errors:
        for e in errors:
            flash(e, "error")
    else:
        # The owner comes from the session, not from the form:
        # a tutor cannot create a student in someone else's workspace.
        storage.create_student(session["tutor_id"], name, language, level, goal)
        flash(f"{name} was added.", "success")
    return redirect(url_for("dashboard"))


@app.route("/profile", methods=["POST"])
@login_required
def edit_profile():
    languages = field("languages")
    philosophy = field("philosophy")
    # getlist returns every checked box; keep only real levels, in order.
    picked = request.form.getlist("levels")
    levels = [lvl for lvl in LEVELS if lvl in picked]

    errors = []
    if len(languages) > 100:
        errors.append("Languages taught: max 100 characters.")
    if len(philosophy) > 500:
        errors.append("Teaching philosophy: max 500 characters.")

    if errors:
        for e in errors:
            flash(e, "error")
    else:
        storage.update_profile(session["tutor_id"], languages, levels, philosophy)
        flash("Public profile saved.", "success")
    return redirect(url_for("dashboard"))


# ---------- Errors ----------

@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(405)
def bad_method(_e):
    return render_template("error.html", message="This action is not allowed."), 405


if __name__ == "__main__":
    # Debug mode only if FLASK_DEBUG=1 in .env — never on in "production".
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
