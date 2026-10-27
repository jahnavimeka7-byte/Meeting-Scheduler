from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "replace-this-with-a-long-random-secret-before-deployment"
DB_PATH = Path(__file__).with_name("employees.db")

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db_connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            job_title TEXT NOT NULL,
            phone TEXT,
            hire_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Demo login: admin / Admin123!
        if not db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone():
            db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                       ("admin", generate_password_hash("Admin123!")))

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    with db_connect() as db:
        total = db.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        departments = db.execute("SELECT COUNT(DISTINCT department) FROM employees").fetchone()[0]
        recent = db.execute("SELECT * FROM employees ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("index.html", total=total, departments=departments, recent=recent)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db_connect() as db:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["logged_in"] = True
            session["username"] = user["username"]
            return redirect(url_for("employees"))
        flash("Incorrect username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/employees")
@login_required
def employees():
    query = request.args.get("q", "").strip()
    with db_connect() as db:
        if query:
            pattern = f"%{query}%"
            rows = db.execute("""
                SELECT * FROM employees
                WHERE full_name LIKE ? OR email LIKE ? OR department LIKE ? OR job_title LIKE ?
                ORDER BY id DESC
            """, (pattern, pattern, pattern, pattern)).fetchall()
        else:
            rows = db.execute("SELECT * FROM employees ORDER BY id DESC").fetchall()
    return render_template("employees.html", employees=rows, query=query)

@app.route("/employees/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        data = {
            "full_name": request.form.get("full_name", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "department": request.form.get("department", "").strip(),
            "job_title": request.form.get("job_title", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "hire_date": request.form.get("hire_date", "").strip()
        }
        if not all(data[key] for key in ("full_name", "email", "department", "job_title")):
            flash("Please complete all required fields.", "danger")
            return render_template("employee_form.html", employee=data, mode="Add")
        try:
            with db_connect() as db:
                db.execute("""
                    INSERT INTO employees(full_name,email,department,job_title,phone,hire_date)
                    VALUES(:full_name,:email,:department,:job_title,:phone,:hire_date)
                """, data)
            flash("Employee added successfully.", "success")
            return redirect(url_for("employees"))
        except sqlite3.IntegrityError:
            flash("An employee with this email already exists.", "danger")
            return render_template("employee_form.html", employee=data, mode="Add")
    return render_template("employee_form.html", employee={}, mode="Add")

@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
def edit_employee(employee_id):
    with db_connect() as db:
        employee = db.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if not employee:
            flash("Employee not found.", "danger")
            return redirect(url_for("employees"))
        if request.method == "POST":
            data = {
                "id": employee_id,
                "full_name": request.form.get("full_name", "").strip(),
                "email": request.form.get("email", "").strip().lower(),
                "department": request.form.get("department", "").strip(),
                "job_title": request.form.get("job_title", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "hire_date": request.form.get("hire_date", "").strip()
            }
            if not all(data[key] for key in ("full_name", "email", "department", "job_title")):
                flash("Please complete all required fields.", "danger")
                return render_template("employee_form.html", employee=data, mode="Edit")
            try:
                db.execute("""
                    UPDATE employees SET full_name=:full_name, email=:email,
                    department=:department, job_title=:job_title, phone=:phone,
                    hire_date=:hire_date WHERE id=:id
                """, data)
                flash("Employee details updated.", "success")
                return redirect(url_for("employees"))
            except sqlite3.IntegrityError:
                flash("That email is already used by another employee.", "danger")
                return render_template("employee_form.html", employee=data, mode="Edit")
    return render_template("employee_form.html", employee=employee, mode="Edit")

@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
@login_required
def delete_employee(employee_id):
    with db_connect() as db:
        db.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    flash("Employee record deleted.", "success")
    return redirect(url_for("employees"))

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
