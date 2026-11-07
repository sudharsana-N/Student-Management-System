
import getpass
from app import get_db, create_tables
from werkzeug.security import generate_password_hash

create_tables()

name = input("Enter admin name: ").strip()
email = input("Enter admin email: ").strip().lower()
password = getpass.getpass("Enter admin password (minimum 8 characters): ")

if not name or not email or len(password) < 8:
    print("Please enter valid details. Password must be at least 8 characters.")
else:
    conn = get_db()

    try:
        conn.execute(
            """INSERT INTO users (name, email, password, role)
               VALUES (?, ?, ?, 'admin')""",
            (name, email, generate_password_hash(password))
        )
        conn.commit()
        print("Admin account created successfully!")

    except Exception as error:
        print("Could not create admin:", error)

    finally:
        conn.close()
