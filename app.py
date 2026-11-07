
import os
import sqlite3
from pathlib import Path
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "students.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "change-this-local-secret"
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

csrf = CSRFProtect(app)


def get_db():
    DATABASE.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        conn = get_db()
        user = conn.execute(
            "SELECT id, name, role FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()
        conn.close()

        if user is None:
            session.clear()
            flash("Please log in again.")
            return redirect(url_for("login"))

        session["name"] = user["name"]
        session["role"] = user["role"]

        return route(*args, **kwargs)

    return wrapper


def admin_required(route):
    @wraps(route)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return route(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter all details and use a password of at least 8 characters.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO users (name, email, password, role)
                   VALUES (?, ?, ?, 'student')""",
                (name, email, hashed_password)
            )
            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.")
            return redirect(url_for("register"))

        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        role=session["role"],
        total_students=total_students
    )


@app.route("/add_student", methods=["GET", "POST"])
@admin_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        course = request.form.get("course", "").strip()
        phone = request.form.get("phone", "").strip()

        if not all([name, email, course, phone]):
            flash("Please fill in every field.")
            return redirect(url_for("add_student"))

        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO students (name, email, course, phone)
                   VALUES (?, ?, ?, ?)""",
                (name, email, course, phone)
            )
            conn.commit()
            flash("Student added successfully!")
            return redirect(url_for("students"))

        except sqlite3.IntegrityError:
            flash("A student with this email already exists.")
            return redirect(url_for("add_student"))

        finally:
            conn.close()

    return render_template("add_student.html")


@app.route("/students")
@login_required
def students():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        pattern = f"%{search}%"
        student_list = conn.execute(
            """SELECT * FROM students
               WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
               ORDER BY id DESC""",
            (pattern, pattern, pattern)
        ).fetchall()
    else:
        student_list = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=student_list,
        search=search,
        role=session["role"]
    )


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
@admin_required
def edit_student(student_id):
    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if student is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        course = request.form.get("course", "").strip()
        phone = request.form.get("phone", "").strip()

        if not all([name, email, course, phone]):
            conn.close()
            flash("Please fill in every field.")
            return redirect(url_for("edit_student", student_id=student_id))

        try:
            conn.execute(
                """UPDATE students
                   SET name = ?, email = ?, course = ?, phone = ?
                   WHERE id = ?""",
                (name, email, course, phone, student_id)
            )
            conn.commit()
            flash("Student updated successfully!")
            return redirect(url_for("students"))

        except sqlite3.IntegrityError:
            flash("Another student already uses that email.")
            return redirect(url_for("edit_student", student_id=student_id))

        finally:
            conn.close()

    conn.close()
    return render_template("edit_student.html", student=student)


@app.route("/delete_student/<int:student_id>", methods=["POST"])
@admin_required
def delete_student(student_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    conn.commit()
    conn.close()

    flash("Student deleted successfully.")
    return redirect(url_for("students"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
