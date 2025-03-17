import streamlit as st
import yaml
from yaml.loader import SafeLoader
import hashlib
import os

def load_user_credentials():
    """Load user credentials exclusively from config file"""
    config_path = "config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path) as file:
                config = yaml.load(file, Loader=SafeLoader)
                return config.get("users", {})
        except Exception as e:
            st.error(f"⚠️ Error loading config: {e}")
            return {}
    else:
        st.error("⚠️ Config file (config.yaml) not found.")
        return {}

def hash_password(password):
    """Create a simple hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username, password):
    """Verify username and password against stored credentials"""
    users = load_user_credentials()
    
    if username in users:
        stored_hash = users[username]["password"]
        return stored_hash == hash_password(password)
    
    return False

def show_login_form():
    """Display a simple login form"""
    st.title("ABC-XYZ Analysis Dashboard Login")
    st.markdown("Please enter your credentials to access the dashboard.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if verify_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["display_name"] = load_user_credentials().get(username, {}).get("name", username)
                st.rerun()
            else:
                st.error("❌ Incorrect username or password. Please try again.")

def logout():
    """Handle user logout"""
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["display_name"] = None
        st.rerun()

def initialize_auth_state():
    """Initialize authentication state variables"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "display_name" not in st.session_state:
        st.session_state["display_name"] = None

def check_authentication():
    """Check if user is authenticated and show login if not"""
    if not st.session_state["authenticated"]:
        show_login_form()
        return False
    return True