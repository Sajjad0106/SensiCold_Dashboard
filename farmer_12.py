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
# FAIL-SAFE BACKGROUND FUNCTION
# ------------------------------
def add_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         /* Target the main view container */
         [data-testid="stAppViewContainer"] {{
             background-image: url("{url}");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}
         
         /* Target the root app (Backup) */
         .stApp {{
             background-image: url("{url}");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}

         /* IMPORTANT: Make the text box transparent! 
            If this is 1.0 (solid), it will cover your background. */
         .main {{
             background-color: rgba(255,255,255,0.5) !important; 
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Your specific GitHub Raw Link
add_bg_from_url("https://raw.githubusercontent.com/Sajjad0106/SensiCold_Dashboard/main/background.jpg")

# --- SIMPLIFIED CSS ---
st.markdown("""
<style>
    .main { background-color: rgba(255,255,255,0.85); border-radius: 15px; padding: 20px; }
    .stMetric {
        background-color: None;
        backdrop-filter: blur(3px);
        border: 1px dashed #1e3a8a;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 { color: #1e293b; }
            
    .stExpander{
        background-color: None;
        backdrop-filter: blur(3px);
        border: 1.5px dashed #1e3a8a;
        padding: 5px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 { color: #1e293b; }
            
    /* Center the main title */
    .block-container h1 {
        text-align: center;
    }
    
    /* Headers Color Override */
    h2, h3, h4, h5, h6 { 
    color: #1e3a8a !important; /* Deep Blue for all headers */
    }
            
    st.text_input > div > div > input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
    }
            
    /* Tab Styling */
    button[data-baseweb="tab"] {
        color: #1e3a8a;
        font-weight: light;
    }
            
    div[data-testid="stMetricValue"] {
        color: #1e3a8a !important; /* Dark Blue for Value */
        font-weight: 400;
    }    

    /* Selector-Box */    
    div[data-testid="stSelectbox"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }

    /* Number-Input */    
    div[data-testid="stNumberInput"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }       

    /* Multi-Selection */    
    div[data-testid="stMultiSelect"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }
            
    /* Date-Input */    
    div[data-testid="stDateInput"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }           
    /* Text-Input */    
    div[data-testid="stTextInput"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }    

    /* Slider */    
    div[data-testid="stSlider"] label p {
        color: #64748b !important; /* Slate Grey */
        font-weight: 600;
        font-size: 14px;
    }  
                     
    /* Map Border */
    .element-container iframe {
        border: 1px solid #ccc;
        border-radius: 10px;  
    }
</style>
""", unsafe_allow_html=True)

# --- DATA & CONSTANTS ---
CSV_FILE = 'sensor_data_history.csv'

CROP_DATA = {
    'Apple': {'temp': '0-4', 'humidity': '90-95', 'ethylene': 'Low', 'co2': '2-5'},
    'Mango': {'temp': '10-13', 'humidity': '85-90', 'ethylene': 'High', 'co2': '3-5'},
    'Banana': {'temp': '13-15', 'humidity': '90-95', 'ethylene': 'High', 'co2': '2-5'},
    'Grapes': {'temp': '0-2', 'humidity': '90-95', 'ethylene': 'Very Low', 'co2': '2-5'},
    'Potato': {'temp': '3-5', 'humidity': '90-95', 'ethylene': 'Very Low', 'co2': '2-5'},
    'Onion': {'temp': '0-2', 'humidity': '65-70', 'ethylene': 'Very Low', 'co2': '0-5'},
    'Tomato': {'temp': '10-13', 'humidity': '90-95', 'ethylene': 'Moderate', 'co2': '3-5'},
}

# --- SESSION STATE INITIALIZATION ---
if 'listings' not in st.session_state:
    # UPDATED: Added lat/lon coordinates so the Map feature works
    st.session_state.listings = [
        {'crop': 'Apple', 'quality': 'Grade A', 'harvest_date': '2025-11-01', 'price': 80, 'location': 'Sangli', 'transport': True, 'lat': 16.8524, 'lon': 74.5815},
        {'crop': 'Mango', 'quality': 'Premium', 'harvest_date': '2025-10-25', 'price': 120, 'location': 'Pune', 'transport': False, 'lat': 18.5204, 'lon': 73.8567},
        {'crop': 'Grapes', 'quality': 'Export', 'harvest_date': '2025-11-05', 'price': 90, 'location': 'Nashik', 'transport': True, 'lat': 19.9975, 'lon': 73.7898},
        {'crop': 'Onion', 'quality': 'Standard', 'harvest_date': '2025-11-12', 'price': 30, 'location': 'Lasalgaon', 'transport': False, 'lat': 20.1477, 'lon': 74.2250},
    ]

# Initialize Bookings State for Pay-Per-Use Logic
if 'bookings' not in st.session_state:
    st.session_state.bookings = [
        {'id': 101, 'farmer': 'Rajesh Kumar', 'crop': 'Apple', 'weight': 500, 'entry_date': '2025-11-01', 'rate': 2.5, 'status': 'Active'},
        {'id': 102, 'farmer': 'Suresh Patil', 'crop': 'Mango', 'weight': 200, 'entry_date': '2025-11-10', 'rate': 2.5, 'status': 'Active'},
    ]

# --- HELPER FUNCTIONS ---
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=['timestamp', 'crop', 'temperature', 'humidity', 'ethylene', 'co2', 'air_temp', 'status', 'alerts'])

def save_to_csv(data, file_path):
    df = pd.DataFrame([data])
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

def check_conditions(sensor_data, crop):
    alerts = []
    params = CROP_DATA[crop]
    
    t_min, t_max = map(float, params['temp'].split('-'))
    h_min, h_max = map(float, params['humidity'].split('-'))
    
    if sensor_data['temperature'] < t_min: alerts.append(f"⚠️ Low Temp ({sensor_data['temperature']}°C)")
    elif sensor_data['temperature'] > t_max: alerts.append(f"⚠️ High Temp ({sensor_data['temperature']}°C)")
    
    if sensor_data['humidity'] < h_min: alerts.append(f"⚠️ Low Humidity ({sensor_data['humidity']}%)")
    elif sensor_data['humidity'] > h_max: alerts.append(f"⚠️ High Humidity ({sensor_data['humidity']}%)")
        
    status = "✅ Optimal" if not alerts else "⚠️ Attention Needed"
    return status, alerts

# --- GAUGE FUNCTION ---
def create_gauge(value, min_val, max_val, title, unit, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#334155'}},
        number={'suffix': unit, 'font': {'size': 24, 'color': '#334155'}}, # Dark Grey Number
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "#64748b"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [min_val, min_val + (max_val - min_val) * 0.33], 'color': '#fee2e2'},
                {'range': [min_val + (max_val - min_val) * 0.33, min_val + (max_val - min_val) * 0.66], 'color': '#fef3c7'},
                {'range': [min_val + (max_val - min_val) * 0.66, max_val], 'color': '#d1fae5'}
            ],
            'threshold': {'line': {'color': "#1e293b", 'width': 4}, 'thickness': 0.75, 'value': value}
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def create_multiline_chart(df, metrics):
    if df.empty: return None
    fig = go.Figure()
    colors = {'temperature': "#3b82f6", 'humidity': '#10b981', 'ethylene': '#f59e0b', 'co2': '#8b5cf6', 'air_temp': '#ec4899'}
    for m in metrics:
        if m in df.columns:
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df[m], mode='lines+markers', name=m.title(), line=dict(color=colors.get(m, 'black'))))
    fig.update_layout(title="Historical Trends", height=400, hovermode='x unified', template='plotly_white')
    return fig

# --- CERTIFICATE JPG GENERATOR ---
def generate_certificate_jpg(farmer_name, crop, weight, date):
    width, height = 1100, 750
    img = Image.new('RGB', (width, height), color='white')
    d = ImageDraw.Draw(img)
    
    border_color = "#1e3a8a" 
    text_color = "black"
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 28)
        sub_font = ImageFont.truetype("arial.ttf", 16)
        body_font = ImageFont.truetype("arial.ttf", 16)
        bold_font = ImageFont.truetype("arialbd.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    d.rectangle([20, 20, width-20, height-20], outline=border_color, width=4)
    d.rectangle([28, 28, width-28, height-28], outline=border_color, width=1)

    d.text((width/2, 60), "🛡️ SENSICOLD WAREHOUSING SERVICES", fill=border_color, anchor="mm", font=bold_font)
    d.text((width/2, 110), "ELECTRONIC NEGOTIABLE WAREHOUSE RECEIPT", fill=border_color, anchor="mm", font=title_font)
    d.text((width/2, 150), "(For Pledge Finance / Loan Against Commodity Retrieval)", fill="black", anchor="mm", font=sub_font)

    market_rates = {'Apple': 120, 'Mango': 80, 'Banana': 30, 'Grapes': 90, 'Potato': 25, 'Onion': 30, 'Tomato': 40}
    rate_per_kg = market_rates.get(crop, 50) 
    
    total_market_value = weight * rate_per_kg
    eligible_loan = total_market_value * 0.70  
    mt = weight / 1000

    body_text = (
        f"This certifies that Mr./Ms. {farmer_name} has deposited the following agricultural produce \n"
        f"in the Sensicold Smart Storage Facility. The stock has been graded and verified for quality. \n"
        f"This document serves as proof of storage and may be used for retrieving a Pledge Loan \n"
        f"from partner financial institutions based on the valuation below."
    )
    d.multiline_text((80, 200), body_text, fill="black", font=body_font, spacing=10)

    start_y = 350
    left_x = 80
    d.text((left_x, start_y), "STOCK VALUATION & LOAN ELIGIBILITY", fill=border_color, font=bold_font)
    d.line([(left_x, start_y+25), (left_x+400, start_y+25)], fill="gray", width=1)
    
    details = [
        ("Crop Variety:", f"{crop} (Grade A)"),
        ("Market Rate (Approx):", f"Rs. {rate_per_kg}/kg"),
        ("Total Market Value:", f"Rs. {total_market_value:,.2f}"),
        ("Eligible Pledge Loan (70%):", f"Rs. {eligible_loan:,.2f}"),
        ("Est. Monthly Storage Cost:", f"Rs. {(weight * 2.5 * 30):,.2f}")
    ]
    
    curr_y = start_y + 40
    for label, val in details:
        d.text((left_x, curr_y), label, fill="black", font=body_font)
        if "Eligible Pledge" in label:
             d.rectangle([left_x+250-5, curr_y-2, left_x+450, curr_y+20], fill="#e6fffa")
        d.text((left_x + 250, curr_y), val, fill="black", font=bold_font)
        curr_y += 35

    right_x = 600
    d.text((right_x, start_y), "DEPOSIT DETAILS", fill=border_color, font=bold_font)
    d.line([(right_x, start_y+25), (right_x+400, start_y+25)], fill="gray", width=1)
    
    specs = [
        ("Receipt No:", f"WR/{random.randint(10000,99999)}"),
        ("Deposit Date:", date),
        ("Net Weight:", f"{weight} KG ({mt} MT)"),
        ("No. of Crates/Bags:", f"{int(weight/20)} Units"),
        ("Warehouse Location:", "Sangli, MH"),
        ("Valid Until:", "3 Months from Date")
    ]
    
    curr_y = start_y + 40
    for label, val in specs:
        d.text((right_x, curr_y), label, fill="black", font=body_font)
        d.text((right_x + 200, curr_y), val, fill="black", font=bold_font)
        curr_y += 35

    sig_y = height - 150
    d.text((80, sig_y), "License No.: WDRA-REG-2025-88", fill="black", font=small_font)
    d.text((80, sig_y+20), f"Insurance Policy: INS/{random.randint(100,999)}", fill="black", font=small_font)
    
    d.rectangle([width-300, sig_y-20, width-80, sig_y+30], outline=border_color, width=2)
    d.text((width-190, sig_y+5), "STOCK VERIFIED", fill=border_color, anchor="mm", font=bold_font)
    
    d.line([(width-300, sig_y+80), (width-80, sig_y+80)], fill="black", width=1)
    d.text((width-190, sig_y+100), "WAREHOUSE MANAGER", fill="black", anchor="mm", font=bold_font)
    d.text((width-190, sig_y+120), "Sensicold Services", fill="gray", anchor="mm", font=small_font)

    footer = "DISCLAIMER: Market rates are estimates. Final loan amount is subject to bank inspection and market fluctuation."
    d.text((width/2, height-30), footer, fill="gray", anchor="mm", font=small_font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# --- MAIN TITLE ---
st.markdown("<h1 style='text-align:center; color: #F2F2F2; font-weight: bold;font-size: 100px;'>SensiCold Master Dashboard</h1>", unsafe_allow_html=True)

# --- MAIN NAVIGATION TABS ---
main_tabs = st.tabs(["👤 Owner Dashboard", "🛒 E-Mandi Marketplace"])

# =========================================================
# TAB 1: OWNER DASHBOARD
# =========================================================
with main_tabs[0]:
    st.subheader("🔆 Solar Panel Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Solar Output", "4.5 kW", "0.2 kW")
    col2.metric("Grid Voltage", "230 V", "Stable")
    col3.metric("Battery Level", "85%", "-2%")
    col4.metric("Energy Savings", "28.5 kWh", "Today")
    st.markdown("---")
    
    with st.expander("🎛️  1. Control Room (Live Monitoring)", expanded=True):
        st.subheader("Live Control Room", divider='red')
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Crop & Simulation Settings </h4>", unsafe_allow_html=True)
            target_crop = st.selectbox("Select Active Crop", list(CROP_DATA.keys()))
            params = CROP_DATA[target_crop]
            st.info(f"Target: {params['temp']}°C | {params['humidity']}% Humidity")
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Simulate Sensors </h4>", unsafe_allow_html=True)
            temp_in = st.number_input("Chamber Temp (°C)", -10.0, 40.0, 2.5, step=0.1)
            hum_in = st.number_input("Humidity (%)", 0.0, 100.0, 92.0, step=0.5)
            eth_in = st.number_input("Ethylene (ppm)", 0.0, 20.0, 1.5, step=0.1)
            co2_in = st.number_input("CO2 Level (%)", 0.0, 15.0, 3.5, step=0.1)
            air_temp_in = st.number_input("Air Temp (°C)", -10.0, 40.0, 2.8, step=0.1)
        with c2:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Current Sensor Readings</h4>", unsafe_allow_html=True)
            g1, g2, g3 = st.columns(3)
            with g1: st.plotly_chart(create_gauge(temp_in, -5, 20, "Temperature", "°C", "#3b82f6"), use_container_width=True)
            with g2: st.plotly_chart(create_gauge(hum_in, 0, 100, "Humidity", "%", "#10b981"), use_container_width=True)
            with g3: st.plotly_chart(create_gauge(eth_in, 0, 10, "Ethylene", "ppm", "#f59e0b"), use_container_width=True)
            g4, g5 = st.columns(2)
            with g4: st.plotly_chart(create_gauge(co2_in, 0, 10, "CO2", "%", "#8b5cf6"), use_container_width=True)
            with g5: st.plotly_chart(create_gauge(air_temp_in, -5, 20, "Air Temp", "°C", "#ec4899"), use_container_width=True)
            if st.button("🧠 AI Diagnose & Log Data", type="primary", use_container_width=True):
                sensor_packet = {'temperature': temp_in, 'humidity': hum_in, 'co2': co2_in, 'ethylene': eth_in, 'air_temp': air_temp_in}
                status, alerts = check_conditions(sensor_packet, target_crop)
                save_to_csv({'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'crop': target_crop, **sensor_packet, 'status': status, 'alerts': "; ".join(alerts)}, CSV_FILE)
                if status == "✅ Optimal": st.success(f"System Status: {status}")
                else: 
                    st.error(f"System Status: {status}")
                    for a in alerts: st.warning(a)

    with st.expander("📊 2. Analytics & History", expanded=False):
        st.subheader("Historical Performance", divider='red')
        df_hist = load_data(CSV_FILE)
        if not df_hist.empty:
            f1, f2 = st.columns([1, 3])
            with f1:
                sel_crop = st.selectbox("Filter by Crop", ['All'] + list(df_hist['crop'].unique()))
                sel_met = st.multiselect("Metrics", ['temperature', 'humidity', 'co2', 'ethylene', 'air_temp'], default=['temperature', 'humidity'])
            with f2:
                if sel_crop != 'All': df_hist = df_hist[df_hist['crop'] == sel_crop]
                fig = create_multiline_chart(df_hist, sel_met)
                if fig: st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_hist.tail(10).sort_values('timestamp', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No data logged yet.")

    with st.expander("💰 3. Rentals & Business Management (Pay-Per-Use)", expanded=False):
        st.subheader("Invoicing & Financial Records", divider='red')
        b1, b2, b3, b4 = st.columns(4)
        total_stored = sum(b['weight'] for b in st.session_state.bookings if b['status']=='Active')
        capacity = 2000 
        b1.metric("Current Occupancy", f"{total_stored} / {capacity} kg", f"{total_stored/capacity*100:.1f}% Full")
        b2.metric("Active Users", f"{len(st.session_state.bookings)}", "Farmers")
        b3.metric("Est. Daily Revenue", f"₹ {total_stored * 2.5:.0f}", "Based on Load")
        b4.metric("Collected (This Month)", "₹ 12,450", "+8%")
        st.markdown("---")
        rt1, rt2, rt3 = st.tabs(["📥 New Check-In", "📤 Active Inventory & Certificate", "⚙️ Rate Configuration"])
        with rt1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("<h4 style='text-align:center; color: #607D8B;'> Farmer Details </h4>", unsafe_allow_html=True)
                b_name = st.text_input("Farmer Name", key="b_name")
                b_crop = st.selectbox("Crop Deposited", list(CROP_DATA.keys()), key="b_crop")
            with c2:
                st.markdown("<h4 style='text-align:center; color: #607D8B;'> Stock Details </h4>", unsafe_allow_html=True)
                b_weight = st.number_input("Weight Deposited (kg)", min_value=1, value=500, key="b_weight")
                mock_rates = {'Apple': 120, 'Mango': 80, 'Banana': 30, 'Grapes': 90, 'Potato': 25, 'Onion': 30, 'Tomato': 40}
                est_val = b_weight * mock_rates.get(b_crop, 50)
                st.success(f"💰 **Est. Stock Market Value:** ₹{est_val:,.0f}")
                st.caption(f"*Calculated at approx market rate of ₹{mock_rates.get(b_crop, 50)}/kg*")
            if st.button("✅ Generate Receipt & Store", use_container_width=True, type="primary"):
                if b_name:
                    new_booking = {'id': len(st.session_state.bookings) + 101, 'farmer': b_name, 'crop': b_crop, 'weight': b_weight, 'entry_date': datetime.now().strftime("%Y-%m-%d"), 'rate': 2.5, 'status': 'Active'}
                    st.session_state.bookings.append(new_booking)
                    st.success(f"Stock Receipt Created for {b_name}!")
                    st.rerun()
                else:
                    st.error("Please enter Farmer Details")
        with rt2:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Active Storage Inventory </h4>", unsafe_allow_html=True)
            active_df = pd.DataFrame([b for b in st.session_state.bookings if b['status'] == 'Active'])
            if not active_df.empty:
                st.dataframe(active_df[['farmer', 'crop', 'weight', 'entry_date', 'rate']], use_container_width=True, hide_index=True)
                st.markdown("---")
                st.markdown("<h4 style='text-align:center; color: #607D8B;'> 📜 E-Warehouse Receipt  </h4>", unsafe_allow_html=True)
                col_cert1, col_cert2 = st.columns([3, 1])
                with col_cert1:
                    selected_farmer_cert = st.selectbox("Select Farmer", active_df['farmer'].unique())
                    farmer_data = active_df[active_df['farmer'] == selected_farmer_cert].iloc[0]
                with col_cert2:
                    st.write("") 
                    generate_btn = st.button("🖨️ Generate & Preview", use_container_width=True, type='primary')
                if generate_btn or 'cert_img' in st.session_state:
                    jpg_data = generate_certificate_jpg(farmer_data['farmer'], farmer_data['crop'], farmer_data['weight'], farmer_data['entry_date'])
                    st.image(jpg_data, caption="Certificate Preview", use_container_width=True)
                    st.download_button(label="📥 Download Certificate as JPG", data=jpg_data, file_name=f"Warehouse_Receipt_{selected_farmer_cert}.jpg", mime="image/jpeg", use_container_width=True, type='primary')
            else:
                st.info("Storage is currently empty.")
        with rt3:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Set Pricing </h4>", unsafe_allow_html=True)
            st.number_input("Base Rate (₹ per kg/day)", value=2.5, step=0.1)
            st.number_input("Cooling Surcharge (₹ flat fee)", value=50.0)
            st.button("Update System Rates", use_container_width=True, type='primary')

# =========================================================
# TAB 2: E-MANDI MARKETPLACE (UPDATED & VISIBLE)
# =========================================================
with main_tabs[1]:
    st.subheader("🛒 E-Mandi Marketplace")
    st.markdown("---")
    
    # 5 TABS NOW INCLUDING LOGISTICS
    mkt_tabs = st.tabs(["🔍 Browse Listings", "🗺️ Map View", "📈 Market Insights", "➕ Sell Produce", "🚚 Logistic Support"])
    
    # --- TAB 1: BROWSE LISTINGS ---
    with mkt_tabs[0]:
        f1, f2 = st.columns(2)
        with f1:
            search_txt = st.text_input("🔍 Search Crop Name...", placeholder="e.g. Apple")
        with f2:
            price_filter = st.slider("💰 Max Price (₹/kg)", 0, 200, 150)
            
        listings_df = pd.DataFrame(st.session_state.listings)
        if search_txt:
            listings_df = listings_df[listings_df['crop'].str.contains(search_txt, case=False)]
        listings_df = listings_df[listings_df['price'] <= price_filter]
        
        if not listings_df.empty:
            cols = st.columns(3)
            for idx, row in listings_df.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: None; padding: 5px; border-radius: 12px; border: 1px dashed #1e3a8a; margin-bottom: 15px; backdrop-filter: blur(3px);">
                        <div style="display:flex; justify-content:space-between;">
                                <h3 style="margin:0; color:white">{row['crop']}</h3>
                                <span style="background:#dcfce7; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold; color:green">{row['quality']}</span>
                        </div>
                        <hr style="margin:8px 0; border-color:#eee;">
                        <p style="margin:0; font-size:13px; color: White;">📍 <b>Location:</b> {row['location']}</p>
                        <p style="margin:0; font-size:13px; color: White;">📅 <b>Harvest:</b> {row['harvest_date']}</p>
                        <div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:18px; font-weight:bold; color: black">₹{row['price']}/kg</span>
                        </div>
                    </div>
                        """, unsafe_allow_html=True)
                    st.button(f"📞 Contact Seller", key=f"buy_{idx}", use_container_width=True)
        else:
            st.info("No listings found matching your criteria.")

    # --- TAB 2: MAP VIEW ---
    with mkt_tabs[1]:
        st.markdown("<h4 style='text-align:center; color: #607D8B;'> Live Listings & Tracking Map </h4>", unsafe_allow_html=True)
        map_df = pd.DataFrame(st.session_state.listings)
        if 'lat' in map_df.columns and 'lon' in map_df.columns:
            st.map(map_df, latitude='lat', longitude='lon', size=20, zoom=6)
        else:
            st.warning("Location data missing for map visualization.")

    # --- TAB 3: MARKET INSIGHTS ---
    with mkt_tabs[2]:
        st.markdown("<h4 style='text-align:center; color: #607D8B;'> Price Trends by Crop </h4>", unsafe_allow_html=True)
        chart_df = pd.DataFrame(st.session_state.listings)
        if not chart_df.empty:
            avg_price = chart_df.groupby('crop')['price'].mean().reset_index()
            fig_bar = px.bar(avg_price, x='crop', y='price', color='crop', title="Average Market Price (₹/kg)")
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="black")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Not enough data for insights.")

    # --- TAB 4: SELL PRODUCE ---
    with mkt_tabs[3]:
        with st.form("listing_form_new"):
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Create New Crop Listing </h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            new_crop = c1.selectbox("Crop", list(CROP_DATA.keys()))
            new_price = c2.number_input("Price (₹/kg)", 0, 1000, 50)
            
            c3, c4 = st.columns(2)
            new_qual = c3.text_input("Quality Grade", "A+")
            new_loc = c4.text_input("Location", "Sangli")
            
            new_date = st.date_input("Harvest Date")
            
            if st.form_submit_button("📢 Publish Listing"):
                lat_base, lon_base = 18.5204, 73.8567 
                new_lat = lat_base + random.uniform(-2.0, 2.0)
                new_lon = lon_base + random.uniform(-2.0, 2.0)
                
                st.session_state.listings.append({
                    'crop': new_crop, 'price': new_price, 'quality': new_qual,
                    'location': new_loc, 'harvest_date': str(new_date), 'transport': True,
                    'lat': new_lat, 'lon': new_lon
                })
                st.success("Listing Published Successfully!")
                st.rerun()

    # --- TAB 5: LOGISTIC SUPPORT (NEW ADDITION) ---
    with mkt_tabs[4]:
        st.markdown("<h4 style='text-align:center; color: #607D8B;'> Smart Cold Chain Logistics </h4>", unsafe_allow_html=True)        
        log_c1, log_c2 = st.columns([1, 1])
        
        with log_c1:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Route & Cost Estimator </h4>", unsafe_allow_html=True)        
            l_orig = st.selectbox("Pickup Location", ["Sangli", "Satara", "Pune", "Nashik"])
            l_dest = st.selectbox("Market Destination", ["Mumbai Vashi", "Pune Market Yard", "Bangalore", "Delhi Azadpur"])
            l_weight = st.number_input("Cargo Weight (kg)", 100, 10000, 500)
            
            if st.button("Calculate Shipping"):
                dist_map = {("Sangli", "Mumbai Vashi"): 390, ("Sangli", "Pune Market Yard"): 230, ("Nashik", "Mumbai Vashi"): 170}
                dist = dist_map.get((l_orig, l_dest), random.randint(200, 800))
                rate = 15 # Rs per km for small truck
                cost = dist * rate
                st.success(f"**Est. Distance:** {dist} km")
                st.info(f"💰 **Shipping Cost:** ₹{cost:,.0f} (Inclusive of Reefer charges)")
                st.warning("⚠️ **Spoilage Risk:** Low (if < 12 hrs)")

        with log_c2:
            st.markdown("<h4 style='text-align:center; color: #607D8B;'> Deals of Days (50% Off) </h4>", unsafe_allow_html=True)        
            st.caption("Trucks returning empty on these routes looking for cargo.")
            
            deals = [
                {"Route": "Mumbai -> Sangli", "Capacity": "2 Tons", "Time": "Today 4 PM", "Price": "₹3,500"},
                {"Route": "Pune -> Nashik", "Capacity": "1.5 Tons", "Time": "Tomorrow 8 AM", "Price": "₹2,200"},
            ]
            
            for d in deals:
                with st.container():
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.7); border:1px dashed #1e3a8a; padding:10px; border-radius:8px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; font-weight:bold;">
                            <span style="color:red">{d['Route']}</span>
                            <span style="color:green">{d['Price']}</span>
                        </div>
                        <div style="font-size:12px; color: black;">
                            🚛 {d['Capacity']} | ⏰ {d['Time']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.button(f"Book Deal {d['Route']}", key=d['Route'])




