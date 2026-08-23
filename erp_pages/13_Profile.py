import streamlit as st
import bcrypt
import hashlib
import hmac
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_supabase

def run():
    supabase = get_supabase()
    
    # Get current user from session securely
    user = st.session_state.get("user")
    
    if not user:
        st.error("Please login first")
        st.stop()

    st.title("👤 My Profile")

    st.write(f"Username : {user.get('username', '')}")
    st.write(f"Full Name : {user.get('full_name', '')}")
    st.write(f"Role : {user.get('role', '')}")

    st.divider()

    st.subheader("🔐 Change Password")

    old_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("💾 Change Password", use_container_width=True):
        if not old_password or not new_password:
            st.error("Please fill all fields")
        elif new_password != confirm_password:
            st.error("Password confirmation does not match")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            try:
                # Fetch user directly from Supabase to verify password
                result = supabase.table("users").select("*").eq("id", user["id"]).limit(1).execute()
                
                if not result.data:
                    st.error("User not found")
                else:
                    user_data = result.data[0]
                    stored_hash = str(user_data.get("password_hash", "")).strip()
                    
                    password_verified = False
                    
                    if stored_hash.startswith("$2"):
                        try:
                            password_verified = bcrypt.checkpw(
                                old_password.encode("utf-8"),
                                stored_hash.encode("utf-8")
                            )
                        except:
                            password_verified = False
                    else:
                        sha256_hash = hashlib.sha256(old_password.encode("utf-8")).hexdigest()
                        password_verified = hmac.compare_digest(stored_hash, sha256_hash) or hmac.compare_digest(stored_hash, old_password)
                    
                    if not password_verified:
                        st.error("Current password is incorrect")
                    else:
                        # Hash new password with bcrypt
                        new_hash = bcrypt.hashpw(
                            new_password.encode("utf-8"),
                            bcrypt.gensalt()
                        ).decode()
                        
                        # Update database
                        supabase.table("users").update({"password_hash": new_hash}).eq("id", user["id"]).execute()
                        
                        st.success("Password changed successfully")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    run()
