# Employee Management System — Cloud Computing Project

A simple responsive web application built with Python Flask, HTML, CSS, and SQLite. It demonstrates employee record management through a browser-based dashboard.

## Features
- Login-protected employee dashboard
- Add employee records
- View and search employee records
- Edit employee details
- Delete employee records
- Dashboard summary: employee count and departments
- SQLite database for local development
- Responsive layout for desktop and mobile

## Requirements
- Python 3.10+
- pip

## Run locally
1. Download or clone the repository.
2. Open a terminal in the project folder.
3. Create a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Visit `http://127.0.0.1:5000`.

## Demo login
- Username: `admin`
- Password: `Admin123!`

Change the demo password and Flask secret key before deploying publicly. This is an educational starter project, not a production HR system. Do not store real employee personal data until you have implemented production authentication, authorization, HTTPS, secure secrets, backups, and appropriate privacy controls.

## Cloud computing extension
This version runs locally with SQLite. To make it a cloud project, deploy it to a hosting platform and migrate to a managed database such as PostgreSQL. Configure secrets using environment variables, use a production WSGI server, and enable HTTPS and backups.

## GitHub
Upload `app.py`, `templates/`, `static/`, `requirements.txt`, `.gitignore`, and `README.md`. Do not upload the virtual environment, database file, or secrets.
