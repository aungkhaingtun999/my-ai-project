import streamlit as st
import hashlib
import bcrypt
import hmac
import time
from datetime import datetime, timezone, timedelta
from database import get_supabase

supabase = get_supabase()

# ==================================================
# SECURITY & CONSTANTS
# ==================================================
SESSION_IDLE_TIMEOUT = 1800  # 30 minutes
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15

ROLE_MAP = {
    1: "Admin",
    2: "Manager",
    3: "Cashier"
}

# ==================================================
# AUDIT LOGGING
# ==================================================
def log_auth_event(user_id, event_type, status="success"):
    try:
        supabase.table("auth_logs").insert({
            "user_id": user_id,
            "event": event_type,
            "status": status,
            "ip_address": "system-detected"
        }).execute()
    except Exception:
        pass

# ==================================================
# PASSWORD VERIFICATION (v15 Final)
# ==================================================
def verify_password(user, password):
    stored = user.get("password_hash")
    if not stored: return False
    stored = str(stored).strip()
    
    # 1. bcrypt check
    if stored.startswith("$2"):
        if bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8")):
            return True
        return False
        
    # 2. SHA256 / Plain text check (Migration)
    sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if hmac.compare_digest(stored, sha256_hash) or hmac.compare_digest(stored, password):
        upgrade_password(user["id"], password)
        return True
        
    return False

def upgrade_password(user_id, password):
    try:
        new_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()
        supabase.table("users").update({"password_hash": new_hash}).eq("id", user_id).execute()
    except Exception:
        pass # Password upgrade shouldn't stop login

# ==================================================
# CORE AUTH FUNCTIONS
# ==================================================
def get_user(username):
    try:
        response = supabase.table("users").select("*").eq("username", username.strip()).eq("is_active", True).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error("Authentication Database Error")
        return None

def login_user(username, password):
    user = get_user(username)
    if not user: return False, "User not found."

    locked_until = user.get("locked_until")
    if locked_until:
        lock_time = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
        if datetime.now(timezone.utc) < lock_time:
            return False, "Account locked. Try again later."

    if verify_password(user, password):
        supabase.table("users").update({"failed_attempts": 0, "locked_until": None}).eq("id", user["id"]).execute()
        build_session(user)
        log_auth_event(user["id"], "login")
        return True, "Success"
    else:
        new_attempts = user.get("failed_attempts", 0) + 1
        update_data = {"failed_attempts": new_attempts}
        if new_attempts >= MAX_FAILED_ATTEMPTS:
            update_data["locked_until"] = (datetime.now(timezone.utc) + timedelta(minutes=LOCK_DURATION_MINUTES)).isoformat()
        
        supabase.table("users").update(update_data).eq("id", user["id"]).execute()
        log_auth_event(user["id"], "login", "failed")
        return False, "Invalid password."

def build_session(user):
    st.session_state.user = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name", user["username"]),
        "role_id": int(user.get("role_id", 3)),
        "role": ROLE_MAP.get(int(user.get("role_id", 3)), "Cashier"),
        "is_active": bool(user.get("is_active", True)),
        "last_activity": time.time()
    }

# ==================================================
# GUARDS & HELPERS
# ==================================================
def is_authenticated():
    user = st.session_state.get("user")
    if not user or not user.get("is_active"): return False
    
    if (time.time() - user["last_activity"]) > SESSION_IDLE_TIMEOUT:
        logout()
        return False
    user["last_activity"] = time.time()
    return True

def require_login():
    if not is_authenticated():
        login_page()
        st.stop()
    return st.session_state.user

def require_role(role_id):
    user = require_login()
    if user["role_id"] != role_id:
        st.error(f"⛔ Access Denied: Requires {ROLE_MAP.get(role_id)}")
        st.stop()
    return user

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def login_page():
    st.title("🔐 ERP Enterprise Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        success, msg = login_user(username, password)
        if success: st.rerun()
        else: st.error(msg)

def auth_sidebar():
    if is_authenticated():
        user = st.session_state.user
        with st.sidebar:
            st.success(f"👤 {user['full_name']}")
            st.caption(f"Role: {user['role']}")
            if st.button("🚪 Logout"): logout()

