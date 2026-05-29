"""
PCN Auth Backend — FastAPI
Login, Register, JWT Auth, Admin Panel APIs
Run: uvicorn auth.main:app --reload --port 8001
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import sqlite3, hashlib, secrets, datetime, jwt, os

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET", "pcn-super-secret-key-change-in-production")
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 24
DB_PATH    = "pcn_users.db"

app = FastAPI(title="PCN Auth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Database Setup ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            is_admin    INTEGER DEFAULT 0,
            is_banned   INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now')),
            last_login  TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            risk_label  TEXT,
            probability TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    # Create default admin if not exists
    existing = c.execute("SELECT id FROM users WHERE email=?", ("admin@pcn.com",)).fetchone()
    if not existing:
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute(
            "INSERT INTO users (name, email, password, is_admin) VALUES (?,?,?,?)",
            ("Super Admin", "admin@pcn.com", pw_hash, 1)
        )
        print("[DB] Default admin created → admin@pcn.com / admin123")
    conn.commit()
    conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def create_token(user_id: int, email: str, is_admin: bool) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(user_id), "email": email, "is_admin": is_admin, "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_token(token)
    user = db.execute("SELECT * FROM users WHERE id=?", (payload["sub"],)).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    if user["is_banned"]:
        raise HTTPException(status_code=403, detail="Your account has been suspended. Contact admin.")
    return user

def get_admin_user(current_user=Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user

# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name:     str
    email:    str
    password: str

class LoginRequest(BaseModel):
    email:    str
    password: str

class AssessmentLog(BaseModel):
    risk_label:  str
    probability: str

class BanRequest(BaseModel):
    reason: Optional[str] = "No reason provided"

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.post("/auth/register")
def register(req: RegisterRequest, db=Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    if len(req.name.strip()) < 2:
        raise HTTPException(400, "Name must be at least 2 characters.")
    existing = db.execute("SELECT id FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    if existing:
        raise HTTPException(400, "Email already registered.")
    pw_hash = hash_password(req.password)
    db.execute(
        "INSERT INTO users (name, email, password) VALUES (?,?,?)",
        (req.name.strip(), req.email.lower(), pw_hash)
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    token = create_token(user["id"], user["email"], bool(user["is_admin"]))
    return {
        "message": "Account created successfully.",
        "token": token,
        "user": {
            "id":       user["id"],
            "name":     user["name"],
            "email":    user["email"],
            "is_admin": bool(user["is_admin"]),
        }
    }

@app.post("/auth/login")
def login(req: LoginRequest, db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    if not user or user["password"] != hash_password(req.password):
        raise HTTPException(401, "Invalid email or password.")
    if user["is_banned"]:
        raise HTTPException(403, "Your account has been suspended. Please contact the administrator.")
    db.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
    db.commit()
    token = create_token(user["id"], user["email"], bool(user["is_admin"]))
    return {
        "message": "Login successful.",
        "token": token,
        "user": {
            "id":       user["id"],
            "name":     user["name"],
            "email":    user["email"],
            "is_admin": bool(user["is_admin"]),
        }
    }

@app.get("/auth/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id":         current_user["id"],
        "name":       current_user["name"],
        "email":      current_user["email"],
        "is_admin":   bool(current_user["is_admin"]),
        "created_at": current_user["created_at"],
        "last_login": current_user["last_login"],
    }

# ── Assessment Logging ────────────────────────────────────────────────────────
@app.post("/assessment/log")
def log_assessment(req: AssessmentLog, current_user=Depends(get_current_user), db=Depends(get_db)):
    db.execute(
        "INSERT INTO assessments (user_id, risk_label, probability) VALUES (?,?,?)",
        (current_user["id"], req.risk_label, req.probability)
    )
    db.commit()
    return {"message": "Assessment logged."}

@app.get("/assessment/history")
def my_history(current_user=Depends(get_current_user), db=Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
        (current_user["id"],)
    ).fetchall()
    return [dict(r) for r in rows]

@app.delete("/assessment/{assessment_id}")
def delete_assessment(assessment_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    assessment = db.execute("SELECT * FROM assessments WHERE id=? AND user_id=?", (assessment_id, current_user["id"])).fetchone()
    if not assessment:
        raise HTTPException(404, "Assessment not found or not owned by user.")
    db.execute("DELETE FROM assessments WHERE id=?", (assessment_id,))
    db.commit()
    return {"message": "Assessment deleted."}

# ── Admin Routes ──────────────────────────────────────────────────────────────
@app.get("/admin/users")
def list_users(admin=Depends(get_admin_user), db=Depends(get_db)):
    users = db.execute("""
        SELECT u.id, u.name, u.email, u.is_admin, u.is_banned, u.created_at, u.last_login,
               COUNT(a.id) as assessment_count
        FROM users u
        LEFT JOIN assessments a ON a.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    return [dict(u) for u in users]

@app.get("/admin/stats")
def admin_stats(admin=Depends(get_admin_user), db=Depends(get_db)):
    total      = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    banned     = db.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
    admins     = db.execute("SELECT COUNT(*) FROM users WHERE is_admin=1").fetchone()[0]
    assessments= db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
    high_risk  = db.execute("SELECT COUNT(*) FROM assessments WHERE risk_label='High Risk'").fetchone()[0]
    return {
        "total_users":    total,
        "banned_users":   banned,
        "admin_users":    admins,
        "active_users":   total - banned,
        "total_assessments": assessments,
        "high_risk_count":   high_risk,
    }

@app.put("/admin/users/{user_id}/ban")
def ban_user(user_id: int, admin=Depends(get_admin_user), db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(404, "User not found.")
    if user["is_admin"]:
        raise HTTPException(400, "Cannot ban an admin user.")
    if user["id"] == admin["id"]:
        raise HTTPException(400, "You cannot ban yourself.")
    db.execute("UPDATE users SET is_banned=1 WHERE id=?", (user_id,))
    db.commit()
    return {"message": f"User '{user['name']}' has been banned."}

@app.put("/admin/users/{user_id}/unban")
def unban_user(user_id: int, admin=Depends(get_admin_user), db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(404, "User not found.")
    db.execute("UPDATE users SET is_banned=0 WHERE id=?", (user_id,))
    db.commit()
    return {"message": f"User '{user['name']}' has been unbanned."}

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, admin=Depends(get_admin_user), db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(404, "User not found.")
    if user["is_admin"]:
        raise HTTPException(400, "Cannot delete an admin user.")
    if user["id"] == admin["id"]:
        raise HTTPException(400, "You cannot delete yourself.")
    db.execute("DELETE FROM assessments WHERE user_id=?", (user_id,))
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    return {"message": f"User '{user['name']}' has been deleted."}

@app.put("/admin/users/{user_id}/make-admin")
def make_admin(user_id: int, admin=Depends(get_admin_user), db=Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(404, "User not found.")
    db.execute("UPDATE users SET is_admin=1, is_banned=0 WHERE id=?", (user_id,))
    db.commit()
    return {"message": f"User '{user['name']}' is now an admin."}

@app.get("/")
def root():
    return {"status": "PCN Auth API running", "docs": "/docs"}



