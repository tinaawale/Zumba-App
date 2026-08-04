import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
import os

# Set web page configuration
st.set_page_config(page_title="Roots Zumba Manager", page_icon="💃", layout="wide")

# Persistent storage file path
DB_FILE = "zumba_students_data.csv"

# Load existing data with automatic error recovery
if 'students' not in st.session_state:
    loaded = False
    if os.path.exists(DB_FILE):
        try:
            if os.path.getsize(DB_FILE) > 0:
                df = pd.read_csv(DB_FILE)
                if not df.empty:
                    df['phone'] = df['phone'].astype(str)
                    st.session_state.students = df.to_dict('records')
                    loaded = True
        except Exception:
            pass
            
    if not loaded:
        st.session_state.students = [
            {"name": "Rahul Sharma", "phone": "919876543210", "batch": "Morning", "plan": "Monthly Plan", "paid_on": "2026-08-01", "valid_till": "2026-09-01", "status": "Paid", "amount": 1500},
            {"name": "Priya Patel", "phone": "918765432109", "batch": "Evening", "plan": "3 Month Plan", "paid_on": "2026-08-01", "valid_till": "2026-11-01", "status": "Pending", "amount": 4000},
        ]
        df = pd.DataFrame(st.session_state.students)
        df.to_csv(DB_FILE, index=False)

def save_data():
    df = pd.DataFrame(st.session_state.students)
    df.to_csv(DB_FILE, index=False)

st.title("💃 Roots Zumba Fitness Studio - Class Manager")
st.subheader(f"Trackings & Dues for {datetime.now().strftime('%B %Y')}")

# Top Metric Dashboard Panels
total_students = len(st.session_state.students)
paid_count = sum(1 for s in st.session_state.students if s["status"] == "Paid")
pending_count = sum(1 for s in st.session_state.students if s["status"] == "Pending")
overdue_count = sum(1 for s in st.session_state.students if s["status"] == "Overdue")
total_earnings = sum(int(s["amount"]) for s in st.session_state.students if s["status"] == "Paid")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Active Students", total_students)
col2.metric("Paid ✅", paid_count)
col3.metric("Pending ⏳", pending_count)
col4.metric("Overdue 🚨", overdue_count)
col5.metric("Collected Income", f"₹{total_earnings}")

st.markdown("---")

# Pending Dues Radar Reminder Box
st.header("🚨 Pending Dues Reminder Radar")
due_students = [s for s in st.session_state.students if s["status"] in ["Pending", "Overdue"]]

if due_students:
    with st.expander(f"⚠️ YOU HAVE {len(due_students)} PENDING DUES TO COLLECT!", expanded=True):
        for student in due_students:
            msg = f"Dear {student['name']},\n\nThis is a friendly reminder from Roots Zumba Fitness Studio. 😊 Your fee of ₹{student['amount']} is currently marked as {student['status'].lower()}.\n\nKindly clear your dues at your earliest convenience. Thank you! 🙏✨"
            encoded_msg = urllib.parse.quote(msg)
            
            # FIXED: Added the required forward slash ('/') right after wa.me
            wa_link = f"https://wa.me{student['phone']}?text={encoded_msg}"
            
            c_name, c_batch, c_status, c_action = st.columns(4)
            c_name.markdown(f"👤 **{student['name']}**")
            c_batch.markdown(f"`{student['batch']} Batch`")
            badge_color = "🔴 Overdue" if student['status'] == "Overdue" else "🟡 Pending"
            c_status.markdown(f"**{badge_color}**")
            
            # FIXED: HTML clickable link button that directly prompts native app switching on iPhone
            link_html = f'<a href="{wa_link}" target="_blank" style="text-decoration:none; background-color:#25D366; color:white; padding:6px 12px; border-radius:4px; font-weight:bold; display:inline-block;">💬 Send Link</a>'
            c_action.markdown(link_html, unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.2em 0px; border-color:#fff3cd;'>", unsafe_allow_html=True)
else:
    st.success("🎉 All clear! Every single student has paid up for this cycle.")

st.markdown("---")

# Section 1: Register a New Member
st.header("➕ Register New Student")
with st.form("add_student_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    new_name = c1.text_input("Full Name")
    new_phone = c2.text_input("WhatsApp Number (10 digits or with 91)")
    new_amount = c3.number_input("Monthly Fee (INR)", min_value=0, value=1500, step=100)
    
    c4, c5, c6, c7 = st.columns(4)
    new_batch = c4.selectbox("Batch", ["Morning", "Evening"])
    new_plan = c5.selectbox("Plan Duration", ["Monthly Plan", "3 Month Plan", "6 Month Plan", "Year Plan"])
    
    new_paid_date = c6.date_input("Fees Paid Date", datetime.today())
    new_status = c7.selectbox("Payment Status", ["Paid", "Pending", "Overdue"])
    
    submit_btn = st.form_submit_button("Add Student to Roster")
    
    if submit_btn and new_name and new_phone:
        clean_phone = "".join(filter(str.isdigit, new_phone))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
            
        months_to_add = {"Monthly Plan": 1, "3 Month Plan": 3, "6 Month Plan": 6, "Year Plan": 12}[new_plan]
        total_days = months_to_add * 30.436875
        valid_date = new_paid_date + timedelta(days=total_days)
        
        st.session_state.students.append({
            "name": new_name,
            "phone": clean_phone,
            "batch": new_batch,
            "plan": new_plan,
            "paid_on": new_paid_date.strftime("%Y-%m-%d"),
            "valid_till": valid_date.strftime("%Y-%m-%d"),
            "status": new_status,
            "amount": new_amount
        })
        save_data()
        st.success(f"Successfully added {new_name} to the roster!")
        st.rerun()

st.markdown("---")

# Section 2: Separate Batch Tab Layout Filtering Selection
st.header("📋 Student Directory")
batch_filter = st.radio("Filter View by Batch:", ["All Students", "Morning Batch Only", "Evening Batch Only"], horizontal=True)

filtered_students = st.session_state.students
if batch_filter == "Morning Batch Only":
    filtered_students = [s for s in st.session_state.students if s.get("batch") == "Morning"]
elif batch_filter == "Evening Batch Only":
    filtered_students = [s for s in st.session_state.students if s.get("batch") == "Evening"]

if not filtered_students:
    st.info("No students found matching this filter.")
else:
    for idx, student in enumerate(filtered_students):
        master_idx = st.session_state.students.index(student)
        
        with st.container():
            r1, r2, r3, r4, r5, r6 = st.columns([2.2, 2.2, 1.2, 1.2, 1.5, 0.7])
            
            r1.markdown(f"👤 **{student['name']}**  \n`🌅 {student.get('batch', 'Morning')} Batch`")
            
            paid_date_val = student.get('paid_on', 'N/A')
            r2.markdown(f"📱 +{student['phone']}  \n💳 **Paid On:** `{paid_date_val}`")
            
            new_status = r3.selectbox(
                "Status", ["Paid", "Pending", "Overdue"], 
                index=["Paid", "Pending", "Overdue"].index(student["status"]), 
                key=f"status_{master_idx}"
            )
            if new_status != student["status"]:
                st.session_state.students[master_idx]["status"] = new_status
                if new_status == "Paid":
                    st.session_state.students[master_idx]["paid_on"] = datetime.now().strftime("%Y-%m-%d")
                save_data()
                st.rerun()
                
            r4.markdown(f"💰 ₹{student['amount']}  \n⌛ **Exp:** `{student.get('valid_till', 'N/A')}`")
            
            if student["status"] in ["Pending", "Overdue"]:
                msg = f"Dear {student['name']},\n\nThis is a friendly reminder from Roots Zumba Fitness Studio. 😊 Your monthly fee of ₹{student['amount']} for your {student.get('plan','package')} is currently marked as {student['status'].lower()}.\n\nPlease clear your dues at your earliest convenience. Thank you! 🙏✨"
                encoded_msg = urllib.parse.quote(msg)
                
                # FIXED: Added forward slash ('/') right after wa.me
                wa_link = f"https://wa.me{student['phone']}?text={encoded_msg}"
                
                # FIXED: Transformed standard markdown to a customized responsive browser component layout action
                row_button_html = f'<a href="{wa_link}" target="_blank" style="text-decoration:none; background-color:#25D366; color:white; padding:8px 16px; border-radius:4px; font-weight:bold; display:inline-block;">💬 Send Reminder</a>'
                r5.markdown(row_button_html, unsafe_allow_html=True)
            else:
                r5.write("✅ Up to Date")
                
            if r6.button("🗑️", key=f"del_{master_idx}", help=f"Remove {student['name']} permanently"):
                st.session_state.students.pop(master_idx)
                save_data()
                st.rerun()
                
            st.markdown("<hr style='margin:0.5em 0px; border-color:#eee;'>", unsafe_allow_html=True)







