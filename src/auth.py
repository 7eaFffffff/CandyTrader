
import sqlite3
import hashlib
import hmac
import secrets
from pathlib import Path

DB_NAME = str(Path(__file__).resolve().parent / "users.db")


def connect():
    return sqlite3.connect(DB_NAME, timeout=10)


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                role TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS invitations (
                code_hash TEXT PRIMARY KEY,
                parent_id INTEGER NOT NULL,
                used_by INTEGER,
                FOREIGN KEY (parent_id) REFERENCES users(id),
                FOREIGN KEY (used_by) REFERENCES users(id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS parent_child (
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES users(id),
                FOREIGN KEY (child_id) REFERENCES users(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                points INTEGER NOT NULL CHECK(points > 0),
                FOREIGN KEY(parent_id) REFERENCES users(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS point_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES users(id)
            )
        """)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600000
    )


def hash_code(code):
    return hashlib.sha256(
        code.strip().upper().encode("utf-8")
    ).hexdigest()


def generate_invite(parent_username):
    with connect() as db:
        parent = db.execute(
            "SELECT id FROM users WHERE username=? AND role='parent'",
            (parent_username,)
        ).fetchone()

        if parent is None:
            return None

        code = secrets.token_hex(8).upper()

        db.execute(
            "INSERT INTO invitations (code_hash, parent_id) VALUES (?, ?)",
            (hash_code(code), parent[0])
        )

    return code


def signup(username, password, role="child", invitation_code=""):
    username = username.strip()

    if not username or len(password) < 8:
        return False, "Username required; password must be 8+ characters."

    if role not in ("parent", "child"):
        return False, "Invalid account type."

    if role == "child" and not invitation_code.strip():
        return False, "An invitation code is required."

    salt = secrets.token_bytes(16)
    password_hash = hash_password(password, salt)

    try:
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")

            parent_id = None

            if role == "child":
                invitation = db.execute(
                    """SELECT parent_id FROM invitations
                       WHERE code_hash=? AND used_by IS NULL""",
                    (hash_code(invitation_code),)
                ).fetchone()

                if invitation is None:
                    return False, "Invalid or already used invitation code."

                parent_id = invitation[0]

            cursor = db.execute(
                """INSERT INTO users
                   (username, salt, password_hash, role)
                   VALUES (?, ?, ?, ?)""",
                (username, salt, password_hash, role)
            )

            child_id = cursor.lastrowid

            if role == "child":
                db.execute(
                    """INSERT INTO parent_child
                       (parent_id, child_id) VALUES (?, ?)""",
                    (parent_id, child_id)
                )

                updated = db.execute(
                    """UPDATE invitations SET used_by=?
                       WHERE code_hash=? AND used_by IS NULL""",
                    (child_id, hash_code(invitation_code))
                )

                if updated.rowcount != 1:
                    raise ValueError("Invitation already used.")

        return True, "Account created!"

    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except ValueError as error:
        return False, str(error)


def login(username, password):
    with connect() as db:
        user = db.execute(
            """SELECT salt, password_hash, role
               FROM users WHERE username=?""",
            (username.strip(),)
        ).fetchone()

    if user is None:
        return None

    salt, saved_hash, role = user

    if hmac.compare_digest(
        hash_password(password, salt),
        saved_hash
    ):
        return role

    return None


def get_children(parent_username):
    with connect() as db:
        rows = db.execute(
            """SELECT child.username
               FROM parent_child AS link
               JOIN users AS parent ON parent.id = link.parent_id
               JOIN users AS child ON child.id = link.child_id
               WHERE parent.username=? AND parent.role='parent'
               ORDER BY child.username""",
            (parent_username,)
        ).fetchall()

    return [row[0] for row in rows]

def add_reward(parent_username, name, points):
    name = name.strip()

    try:
        points = int(points)
    except (ValueError, TypeError):
        return False, "Please enter a valid number of points."

    if not name or points <= 0:
        return False, "Enter an item name and a positive point cost."

    with connect() as db:
        parent = db.execute(
            "SELECT id FROM users WHERE username=? AND role='parent'",
            (parent_username,)
        ).fetchone()

        if parent is None:
            return False, "Parent account not found."

        db.execute(
            "INSERT INTO rewards (parent_id, name, points) VALUES (?, ?, ?)",
            (parent[0], name, points)
        )

    return True, "Reward added!"


def get_rewards(child_username):
    with connect() as db:
        rows = db.execute(
            """
            SELECT DISTINCT rewards.id, rewards.name, rewards.points
            FROM rewards
            JOIN parent_child
                ON rewards.parent_id = parent_child.parent_id
            JOIN users
                ON parent_child.child_id = users.id
            WHERE users.username=? AND users.role='child'
            ORDER BY rewards.id DESC
            """,
            (child_username,)
        ).fetchall()

    return rows

def get_points(child_username):
    with connect() as db:
        result = db.execute(
            """
            SELECT COALESCE(SUM(pt.amount), 0)
            FROM users u
            LEFT JOIN point_transactions pt
                ON pt.child_id = u.id
            WHERE u.username = ? AND u.role = 'child'
            """,
            (child_username,)
        ).fetchone()

    return int(result[0]) if result else 0


def add_points(child_username, amount, source="manual"):
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return False, "Enter a valid point amount."

    if amount <= 0 or amount > 10000:
        return False, "Points must be between 1 and 10000."

    with connect() as db:
        child = db.execute(
            "SELECT id FROM users WHERE username=? AND role='child'",
            (child_username,)
        ).fetchone()

        if child is None:
            return False, "Child account not found."

        db.execute(
            """
            INSERT INTO point_transactions
                (child_id, amount, source)
            VALUES (?, ?, ?)
            """,
            (child[0], amount, source)
        )

    return True, f"Added {amount} points!"


def get_point_history(child_username):
    with connect() as db:
        return db.execute(
            """
            SELECT pt.amount, pt.source, pt.created_at
            FROM point_transactions pt
            JOIN users u ON u.id = pt.child_id
            WHERE u.username = ? AND u.role = 'child'
            ORDER BY pt.id DESC
            LIMIT 20
            """,
            (child_username,)
        ).fetchall()
if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) == 4 and sys.argv[1] == "add":
        username = sys.argv[2]
        amount = sys.argv[3]

        success, message = add_points(
            username,
            amount,
            source="developer_test"
        )

        print(message)

        if success:
            print("Current balance:", get_points(username))
    else:
        print("Usage: python auth.py add <username> <points>")