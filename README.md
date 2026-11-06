# Student Management System

A web-based Student Management System developed using Python Flask and SQLite. This project provides a simple interface to register users, log in, and manage student records.

## Project Overview

The Student Management System is designed to simplify basic student record management through a web application. It allows authenticated users to add, view, search, update, and delete student information.

## Features

- User registration
- Secure user login and logout
- Password hashing
- Dashboard with student count
- Add student records
- View all student records
- Search student records
- Edit student details
- Delete student records
- SQLite database integration
- CSRF protection for forms

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML | Web page structure |
| CSS | Styling |
| Werkzeug | Password hashing |
| Flask-WTF | CSRF protection |
| Git and GitHub | Version control |

## Project Structure

```text
Student-Management-System/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── database/
│   └── students.db
│
├── screenshots/
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── add_student.html
    ├── students.html
    └── edit_student.html
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sudharsana-N/Student-Management-System.git
```

### 2. Open the project folder

```bash
cd Student-Management-System
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the secret key

Create a `.env` file in the project root and add:

```text
SECRET_KEY=replace-with-a-secure-random-secret
```

Use a securely generated secret key. Do not upload your `.env` file to GitHub.

### 7. Run the application

```bash
python app.py
```

### 8. Open in your browser

```text
http://127.0.0.1:5000/
```

Register an account and log in to start using the application.

## Screenshots

Screenshots demonstrating the application's pages and functionality are available in the `screenshots` folder.

## Database

The application uses SQLite to store user accounts and student records. The database is created locally when the application initializes.

## Security Features

- Passwords are stored using secure password hashing.
- SQL queries use parameterized statements.
- CSRF protection is applied to supported forms.
- Login sessions are used for authentication.

## Future Enhancements

- Role-based administrator access
- Student profile and additional academic details
- MySQL or cloud database integration
- Docker containerization
- Cloud deployment
- Automated testing and CI/CD integration
- Monitoring and logging

## Author

**Sudharsana N.**

B.Sc. Computer Science

## Project Status

Developed as an academic internship capstone project. The current version supports local execution using Flask and SQLite.
