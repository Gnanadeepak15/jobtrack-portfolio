from functools import wraps
from pathlib import Path
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "jobtrack.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-this-with-a-random-secret-before-deployment"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Applied',
                applied_date TEXT NOT NULL,
                job_url TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "info")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password with at least 8 characters.", "error")
            return render_template("register.html")

        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password))
                )
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered. Please sign in instead.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Email or password is incorrect.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have signed out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    allowed_statuses = ["Applied", "Interview", "Selected", "Rejected"]

    sql = "SELECT * FROM jobs WHERE user_id = ?"
    params = [user_id]
    if search:
        sql += " AND (company LIKE ? OR role LIKE ? OR location LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if status in allowed_statuses:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY applied_date DESC, id DESC"

    with get_db() as db:
        jobs = db.execute(sql, params).fetchall()
        counts = db.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) AS applied,
                SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END) AS interview,
                SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END) AS selected
            FROM jobs WHERE user_id = ?
        """, (user_id,)).fetchone()

    stats = {
        "total": counts["total"] or 0,
        "applied": counts["applied"] or 0,
        "interview": counts["interview"] or 0,
        "selected": counts["selected"] or 0,
    }
    return render_template("dashboard.html", jobs=jobs, stats=stats, search=search, selected_status=status)


@app.route("/jobs/new", methods=["GET", "POST"])
@login_required
def new_job():
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        applied_date = request.form.get("applied_date", "").strip()
        status = request.form.get("status", "Applied").strip()
        location = request.form.get("location", "").strip()
        job_url = request.form.get("job_url", "").strip()
        notes = request.form.get("notes", "").strip()

        if not company or not role or not applied_date:
            flash("Company, role, and application date are required.", "error")
            return render_template("job_form.html", job=None, today="")

        if status not in ["Applied", "Interview", "Selected", "Rejected"]:
            status = "Applied"

        with get_db() as db:
            db.execute("""
                INSERT INTO jobs (user_id, company, role, location, status, applied_date, job_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session["user_id"], company, role, location, status, applied_date, job_url, notes))
        flash("Job application added.", "success")
        return redirect(url_for("dashboard"))

    from datetime import date
    return render_template("job_form.html", job=None, today=date.today().isoformat())


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    with get_db() as db:
        job = db.execute(
            "SELECT * FROM jobs WHERE id = ? AND user_id = ?",
            (job_id, session["user_id"])
        ).fetchone()

    if job is None:
        flash("Application not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        applied_date = request.form.get("applied_date", "").strip()
        status = request.form.get("status", "Applied").strip()
        location = request.form.get("location", "").strip()
        job_url = request.form.get("job_url", "").strip()
        notes = request.form.get("notes", "").strip()

        if not company or not role or not applied_date:
            flash("Company, role, and application date are required.", "error")
            return render_template("job_form.html", job=job, today=job["applied_date"])

        if status not in ["Applied", "Interview", "Selected", "Rejected"]:
            status = "Applied"

        with get_db() as db:
            db.execute("""
                UPDATE jobs
                SET company = ?, role = ?, location = ?, status = ?, applied_date = ?, job_url = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """, (company, role, location, status, applied_date, job_url, notes, job_id, session["user_id"]))
        flash("Application updated.", "success")
        return redirect(url_for("dashboard"))

    return render_template("job_form.html", job=job, today=job["applied_date"])


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    with get_db() as db:
        db.execute("DELETE FROM jobs WHERE id = ? AND user_id = ?", (job_id, session["user_id"]))
    flash("Application deleted.", "info")
    return redirect(url_for("dashboard"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
