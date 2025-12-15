# SensiCold Owner Auth + Dashboard Navigation
import pyrebase
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import base64
import random
import json
import os
import glob
import requests
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter
import io
from PIL import Image, ImageDraw, ImageFont
import streamlit.components.v1 as components

# ------------------------------
# Background Image Function (Fixed)
# ------------------------------
def add_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{url}");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url("https://raw.githubusercontent.com/Sajjad0106/SensiCold_Dashboard/main/background.jpg")

# --- SIMPLIFIED CSS ---
st.markdown("""
<style>
    .main { background-color: rgba(255,255,255,0.85); border-radius: 15px; padding: 20px; }
    .stExpander{
        background-color: None;
        backdrop-filter: blur(3px);
        border: 1px dashed #1e3a8a;        
        padding: 5px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        color: #0f172a;

    }
    h1, h2, h3 { color: #1e293b; }
    
    st.text_input > div > div > input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
    }
            
    /* Text-Input */    
    div[data-testid="stTextInput"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    } 
    /* Tab Styling */
    button[data-baseweb="tab"] {
        color: #1e3a8a;
        font-weight: light;
    }     
    
    # /* Center the main title */
    # .block-container h1 {
    #     text-align: center;
    # }
    
    # /* Map Border */
    # .element-container iframe {
    #     border: 1px solid #ccc;
    #     border-radius: 10px;
    # }
</style>
""", unsafe_allow_html=True)

# Firebase Config
firebaseConfig = dict(st.secrets["firebase"])

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# Session State Init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "role" not in st.session_state:
    st.session_state.role = "Owner" # Hardcoded to Owner

# Set Layout
st.set_page_config(page_title="SensiCold Owner Access", layout="centered", page_icon ='sensicold logo.png')
if os.path.exists("sensicold logo.png"):
    st.image("sensicold logo.png", use_container_width=True)
# st.markdown("<h1 style='text-align:center; color: #F2F2F2; font-weight: bold;font-size: 50px;'> SensiCold Owner Portal</h1>", unsafe_allow_html=True) 
# st.markdown("<h1 style='text-align:center; color: #8C8C8C;'>☀️ SensiCold Owner Portal</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align:center; color: #607D8B;'>☀️ SensiCold Owner Portal</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align:center; color: #B89B72;'>☀️ SensiCold Owner Portal</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align:center; color: #424240;'>☀️ SensiCold Owner Portal</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align:center; color: #EAE6DF;'>☀️ SensiCold Owner Portal</h1>", unsafe_allow_html=True)



# -------------------------------------
# 🟢 Authenticated View (Dashboard Only)
# -------------------------------------
if st.session_state.authenticated:

    col1, col2 = st.columns([6, 1])
    with col1:
        st.success(f"👑 Welcome Owner: {st.session_state.email}")
            
    with col2:
        if st.button("Logout 🔒"):
            st.session_state.authenticated = False
            st.session_state.email = ""
            st.rerun()

    # Run the Dashboard Code
    with st.spinner("Launching Owner Dashboard..."):
        try:
            with open("farmer_12.py", encoding="utf-8") as f:
                exec(f.read())
        except FileNotFoundError:
            st.error("Error: 'farmer_12.py' not found. Please ensure the dashboard file is in the same directory.")

# -------------------------------------
# 🔐 Unauthenticated View (Owner Only)
# -------------------------------------
else:
    with st.expander("---", expanded=True):
        # st.markdown("""<h6 style='text-align:left; color: #607D8B; font-weight: bold;font-size: 15px;'>
        #     This portal is exclusively for System Owners to manage and monitor their SensiCold installations.
        #     Owners have elevated privileges to configure system settings, view comprehensive analytics, and manage users.
        #     If you are not a System Owner, please use the standard user login portal.
        # </h6>""", unsafe_allow_html=True)

        st.markdown("""<h1 style='text-align:center; color: #B89B72; font-weight: bold; font-size: 70px;'>🛡️ Owner Access</h1>""", unsafe_allow_html=True)
        # 1. Standard Login/Register Tabs
        tab1, tab2 = st.tabs(["Login", "Register New Owner"])

        # --- LOGIN LOGIC ---
        with tab1:
            email = st.text_input("📧 Email", key="login_email")
            password = st.text_input("🔑 Password", type="password", key="login_pass")
            
            if st.button("Login as Owner", type="primary"):
                try:
                    # 1. Authenticate with Firebase Auth
                    user = auth.sign_in_with_email_and_password(email, password)
                    user_id = user['localId']

                    # 2. Check ONLY the "Owners" folder
                    user_data = db.child("Owners").child(user_id).get().val()
                    
                    if user_data:
                        # User found in Owners group
                        st.session_state.authenticated = True
                        st.session_state.email = email
                        st.session_state.role = "Owner"
                        st.rerun()
                    else:
                        st.error("Access Denied: Account not found in Owner records.")
                        
                except Exception as e:
                    try:
                        error_json = e.args[1]
                        error_data = json.loads(error_json)
                        if "error" in error_data and "message" in error_data["error"]:
                            error_message = error_data["error"]["message"]
                        else:
                            error_message = str(error_data)
                    except:
                        error_message = str(e)
                    
                    st.error(f"Login Failed: {error_message}")

        # --- REGISTER LOGIC (Updated with Location & Phone) ---
        with tab2:
            st.info("Create a new System Owner account.")
            r_email = st.text_input("📧 Email", key="reg_email")
            r_password = st.text_input("🔑 Password (min 6 chars)", type="password", key="reg_pass")
            r_handle = st.text_input("👤 Owner Name", value="Admin", key="reg_handle")
            
            # NEW FIELDS
            r_location = st.text_input("📍 Facility Location", placeholder="e.g. Pune, MH", key="reg_loc")
            r_phone = st.text_input("📱 Phone Number", placeholder="+91 XXXXX XXXXX", key="reg_phone")
            
            if st.button("Create Owner Account", type="primary"):
                if len(r_password) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    try:
                        # 1. Create User in Firebase Auth
                        user = auth.create_user_with_email_and_password(r_email, r_password)
                        
                        # 2. Save User Details into "Owners" folder
                        user_data = {
                            "Handle": r_handle,
                            "ID": user['localId'],
                            "UserType": "Owner",
                            "Location": r_location, # Saved to DB
                            "Phone": r_phone,       # Saved to DB
                            "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Saving to db.child("Owners")
                        db.child("Owners").child(user['localId']).set(user_data)
                        
                        st.success("🎉 Owner account created successfully! Please log in.")
                        
                    except Exception as e:
                        try:
                            error_json = e.args[1]
                            error_data = json.loads(error_json)
                            if "error" in error_data and "message" in error_data["error"]:
                                error_message = error_data["error"]["message"]
                            else:
                                error_message = str(error_data)
                        except:
                            error_message = str(e)

                        if "EMAIL_EXISTS" in str(error_message):
                            st.error("Email already exists. Try logging in.")
                        else:

                            st.error(f"Error: {error_message}")

