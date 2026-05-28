# routes/auth.py — Login / Register / Logout / Switch Account
from flask import Blueprint, request, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import (get_db_connection, hash_password, verify_password,
                       create_session, get_user_by_token, delete_session)

auth_bp = Blueprint('auth', __name__)

AVATAR_COLORS = ['#f5a623','#3d8ef8','#00e5a0','#ff4d6d','#a855f7','#f97316','#06b6d4','#ec4899']

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username","").strip()
    email    = data.get("email","").strip().lower()
    password = data.get("password","")
    
    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username or email already exists"}), 409
    
    import random
    color = random.choice(AVATAR_COLORS)
    pwd_hash = hash_password(password)
    
    conn.execute(
        "INSERT INTO users (username, email, password_hash, avatar_color) VALUES (?,?,?,?)",
        (username, email, pwd_hash, color)
    )
    conn.commit()
    user_id = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
    conn.close()
    
    token = create_session(user_id)
    return jsonify({"token": token, "username": username, "email": email, "avatar_color": color})

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    identifier = data.get("identifier","").strip()  # username or email
    password   = data.get("password","")
    
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (identifier, identifier.lower())
    ).fetchone()
    conn.close()
    
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username/email or password"}), 401
    
    # Update last login
    conn = get_db_connection()
    conn.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
    conn.commit()
    conn.close()
    
    token = create_session(user["id"])
    return jsonify({
        "token": token,
        "username": user["username"],
        "email": user["email"],
        "avatar_color": user["avatar_color"]
    })

@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    delete_session(token)
    return jsonify({"status": "logged out"})

@auth_bp.route("/auth/me", methods=["GET"])
def me():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    user = get_user_by_token(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "avatar_color": user["avatar_color"],
        "created_at": user["created_at"]
    })

@auth_bp.route("/auth/accounts", methods=["GET"])
def list_saved_accounts():
    """Returns usernames stored client-side (frontend manages local list)"""
    return jsonify({"info": "Accounts managed client-side in localStorage"})
