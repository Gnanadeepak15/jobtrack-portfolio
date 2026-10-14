# JobTrack — Job Application Tracker

A responsive full-stack web application for organizing a job search. Users can create an account, track applications, update hiring statuses, and search/filter their opportunities.

## Features

- User registration and sign-in with password hashing
- Per-user job application records
- Create, edit, and delete applications
- Status tracking: Applied, Interview, Selected, Rejected
- Dashboard summary cards
- Search by company, role, or location
- Filter applications by status
- SQLite persistence
- Responsive layout for desktop and mobile

## Tech stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, Jinja templates
- **Database:** SQLite
- **Version control:** Git and GitHub

## Run locally

### 1. Install Python and Git

Install a current Python 3 version and Git. Confirm they are available:

```bash
python --version
git --version
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser. Register an account, then add a few sample applications to explore the dashboard.

The SQLite database is created automatically the first time the app runs.

## Project structure

```text
jobtrack_portfolio/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── job_form.html
└── static/
    └── css/
        └── style.css
```

## Push to GitHub

Create an **empty** repository on GitHub, for example `jobtrack-job-application-tracker`. Do not add a README there if you already have this README locally.

From the project folder:

```bash
git init
git add .
git commit -m "Build JobTrack job application tracker"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/jobtrack-job-application-tracker.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks you to authenticate, follow the browser sign-in flow.

## Before deploying publicly

- Replace the development `SECRET_KEY` in `app.py` with a strong environment-based secret.
- Turn off Flask debug mode in production.
- Add CSRF protection and secure cookie settings.
- Use a production WSGI server and a managed database if needed.
- Do not commit passwords, tokens, `.env` files, or real user data.

## Resume bullet (edit to match your real work)

**JobTrack — Job Application Tracker | Python, Flask, SQLite, HTML, CSS**
- Built a responsive job tracking web app with authentication and CRUD operations.
- Designed a SQLite data model and per-user application management.
- Implemented dashboard metrics, search, and status-based filtering.

Only list features you have tested and can confidently explain in an interview.

## Ideas for version 2

- Add automated tests with pytest
- Add pagination and CSV export
- Add charts for application outcomes
- Add email reminders for follow-ups
- Deploy the app and add a live demo link
