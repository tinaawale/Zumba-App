import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import os

# Page configurations optimized for vertical mobile phone screens
st.set_page_config(page_title="Roots Zumba App", page_icon="💃", layout="centered")

# NATIVE IPHONE SHORTCUT INJECTION
st.markdown("""
    <head>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Roots Zumba">
        <link rel="apple-touch-icon" href="https://icons8.com">
    </head>
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
        div[data-testid="stMetric"] { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "zumba_students_database.csv"

# Sync data base
if 'students' not in st.session_state:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['phone'] = df['phone'].astype(str)
        st.session_state.students = df.to_dict('records')
    else:
        st.session_state.students = [
            {"name": "Priya Awale", "batch": "Morning", "paid_on": "2026-08-04", "plan": "3 Month Plan", "valid_till": "2026-11-04", "phone": "919284564621", "status": "Paid"}
        ]

def save_data():
    df = pd.DataFrame(st.session_state.students)
    df.to_csv(DB_FILE, index=False)

st.title("💃 Roots Zumba App")
st.markdown("---")

# Compact Metrics for Mobile View
total_students = len(st.session_state.students)
paid_count = sum(1 for s in st.session_state.students if s["status"] == "Paid")
pending_count = sum(1 for s in st.session_state.students if s.get("status", "Pending") in ["Unpaid", "Pending"])

m1, m2, m3 = st.columns(3)
m1.metric("Total", total_students)
m2.metric("Paid ✅", paid_count)
m3.metric("Dues 🚨", pending_count)

st.markdown("---")

# Mobile Data Input Form
st.subheader("➕ Add New Student")
with st.form("add_student_form", clear_on_submit=True):
    new_name = st.text_input("Student Full Name")
    new_batch = st.selectbox("Select Batch", ["Morning", "Evening"])
    new_date = st.date_input("Fees Paid on Date", value=datetime.now())
    new_plan = st.selectbox("Package Duration", ["Monthly Plan", "3 Month Plan", "6 Month Plan", "Year Plan"])
    new_phone = st.text_input("WhatsApp Number (10 digits)")
    new_status = st.selectbox("Payment Status", ["Paid", "Unpaid", "Pending"])
    
    submit_btn = st.form_submit_button("Save Student to App")
    
    if submit_btn and new_name and new_phone:
        clean_phone = "".join(filter(str.isdigit, new_phone))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
            
        # Automatic Expiration Date Math
        months_to_add = {"Monthly Plan": 1, "3 Month Plan": 3, "6 Month Plan": 6, "Year Plan": 12}[new_plan]
        valid_date = pd.to_datetime(new_date) + pd.DateOffset(months=months_to_add)
        
        st.session_state.students.append({
            "name": new_name, "batch": new_batch, "paid_on": str(new_date),
            "plan": new_plan, "valid_till": valid_date.strftime("%Y-%m-%d"),
            "phone": clean_phone, "status": new_status
        })
        save_data()
        st.success(f"Added {new_name} successfully!")
        st.rerun()

st.markdown("---")

# Roster and Dynamic Reminder Triggers
st.subheader("📋 Class Roster")
for idx, student in enumerate(st.session_state.students):
    with st.expander(f"👤 {student['name']} ({student['batch']}) - {student['status']}"):
        st.write(f"**📞 Phone:** +{student['phone']}")
        st.write(f"**📦 Plan Type:** {student['plan']}")
        st.write(f"**📅 Paid Date:** {student['paid_on']}")
        st.write(f"**🚨 Valid Till:** {student['valid_till']}")
        
        new_status = st.selectbox("Quick Change Status", ["Paid", "Unpaid", "Pending"], index=["Paid", "Unpaid", "Pending"].index(student["status"]), key=f"edit_status_{idx}")
        if new_status != student["status"]:
            st.session_state.students[idx]["status"] = new_status
            save_data()
            st.rerun()
            
        if student["status"] != "Paid":
            msg = f"Dear {student['name']},\n\nThis is a friendly reminder from Roots Zumba Studio. 😊 Your {student['plan']} tracking status is currently marked as {student['status'].lower()}.\n\nYour validity ends on {student['valid_till']}. Kindly clear your dues at your earliest convenience. Thank you! 🙏💃"
            encoded_msg = urllib.parse.quote(msg)
            wa_link = f"https://whatsapp.com{student['phone']}&text={encoded_msg}"
            st.markdown(f'<a href="{wa_link}" target="_blank" style="display:inline-block; background:#25D366; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold; margin-top:10px; width:100%; text-align:center;">💬 Send WhatsApp Reminder</a>', unsafe_allow_html=True)
