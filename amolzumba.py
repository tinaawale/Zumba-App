import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
import os

# Set web page configuration optimized for mobile screens
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

# Convert dataset list to a structured data frame
df_master = pd.DataFrame(st.session_state.students)

# Calculate summary counts based only on the absolute latest active entry for each person
if not df_master.empty:
    df_latest = df_master.sort_values('paid_on').groupby('name').last().reset_index()
    total_students = len(df_latest)
    paid_count = sum(1 for s in df_latest['status'] if s == "Paid")
    pending_count = sum(1 for s in df_latest['status'] if s == "Pending")
    overdue_count = sum(1 for s in df_latest['status'] if s == "Overdue")
    total_earnings = sum(int(s) for s in df_master[df_master['status'] == "Paid"]['amount'])
else:
    total_students = paid_count = pending_count = overdue_count = total_earnings = 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Active Students", total_students)
col2.metric("Paid ✅", paid_count)
col3.metric("Pending ⏳", pending_count)
col4.metric("Overdue 🚨", overdue_count)
col5.metric("Collected Income", f"₹{total_earnings}")

st.markdown("---")

# Pending Dues Radar Warning Box up top
st.header("🚨 Pending Dues Reminder Radar")
if not df_master.empty and pending_count + overdue_count > 0:
    df_due = df_latest[df_latest['status'].isin(["Pending", "Overdue"])]
    with st.expander(f"⚠️ YOU HAVE {len(df_due)} PENDING DUES TO COLLECT!", expanded=True):
        for _, student in df_due.iterrows():
            msg = f"Dear {student['name']},\n\nThis is a friendly reminder from Roots Zumba Fitness Studio. 😊 Your fee of ₹{student['amount']} is currently marked as {student['status'].lower()}.\n\nKindly clear your dues at your earliest convenience. Thank you! 🙏✨"
            encoded_msg = urllib.parse.quote(msg)
            wa_link = f"whatsapp://send?phone={student['phone']}&text={encoded_msg}"
            
            c_name, c_batch, c_status, c_action = st.columns(4)
            c_name.markdown(f"👤 **{student['name']}**")
            c_batch.markdown(f"`{student['batch']} Batch`")
            badge_color = "🔴 Overdue" if student['status'] == "Overdue" else "🟡 Pending"
            c_status.markdown(f"**{badge_color}**")
            
            link_html = f'<a href="{wa_link}" target="_top" style="text-decoration:none; background-color:#25D366; color:white; padding:6px 12px; border-radius:4px; font-weight:bold; display:inline-block;">💬 Send Link</a>'
            c_action.markdown(link_html, unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.2em 0px; border-color:#fff3cd;'>", unsafe_allow_html=True)
else:
    st.success("🎉 All clear! Every single student has paid up for this cycle.")

st.markdown("---")

# Section 1: Form to log a record or new payment month
st.header("➕ Register Student or Log Renewal Payment")
with st.form("add_student_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    new_name = c1.text_input("Full Name (Type exactly to update existing member history)")
    new_phone = c2.text_input("WhatsApp Number (10 digits)")
    new_amount = c3.number_input("Monthly Fee (INR)", min_value=0, value=1500, step=100)
    
    c4, c5, c6, c7 = st.columns(4)
    new_batch = c4.selectbox("Batch", ["Morning", "Evening"])
    new_plan = c5.selectbox("Plan Duration", ["Monthly Plan", "3 Month Plan", "6 Month Plan", "Year Plan"])
    new_paid_date = c6.date_input("Fees Paid Date", datetime.today())
    new_status = c7.selectbox("Payment Status", ["Paid", "Pending", "Overdue"])
    
    submit_btn = st.form_submit_button("Save Entry / Record Payment")
    
    if submit_btn and new_name and new_phone:
        clean_phone = "".join(filter(str.isdigit, new_phone))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
            
        months_to_add = {"Monthly Plan": 1, "3 Month Plan": 3, "6 Month Plan": 6, "Year Plan": 12}[new_plan]
        total_days = months_to_add * 30.436875
        valid_date = new_paid_date + timedelta(days=total_days)
        
        st.session_state.students.append({
            "name": new_name.strip(),
            "phone": clean_phone,
            "batch": new_batch,
            "plan": new_plan,
            "paid_on": new_paid_date.strftime("%Y-%m-%d"),
            "valid_till": valid_date.strftime("%Y-%m-%d"),
            "status": new_status,
            "amount": new_amount
        })
        save_data()
        st.success(f"Successfully recorded data for {new_name}!")
        st.rerun()

st.markdown("---")

# Section 2: Main clean directory panel display
st.header("📋 Student Directory")
search_query = st.text_input("🔍 Search Student Profile by Name:", "").lower().strip()
batch_filter = st.radio("Filter View by Batch:", ["All Students", "Morning Batch Only", "Evening Batch Only"], horizontal=True)

if not df_master.empty:
    unique_names = df_master['name'].unique()
    
    for u_name in unique_names:
        history = df_master[df_master['name'] == u_name].sort_values('paid_on', ascending=False)
        latest_record = history.iloc[0]
        first_record = history.iloc[-1]  # Earliest logged record acts as true "Date of Joining"
        
        # Apply search and batch filtering logic strings
        if search_query and search_query not in u_name.lower():
            continue
        if batch_filter == "Morning Batch Only" and latest_record['batch'] != "Morning":
            continue
        if batch_filter == "Evening Batch Only" and latest_record['batch'] != "Evening":
            continue
            
        master_idx = st.session_state.students.index(latest_record.to_dict())
        
        with st.container():
            # ROW 1: Clean display layout panel showing Primary Details First
            r1, r2, r3, r4, r5, r6 = st.columns([2.2, 2.2, 1.2, 1.2, 1.5, 0.7])
            
            # Primary Details Block Layout
            r1.markdown(f"👤 **{latest_record['name']}**  \n`🌅 {latest_record['batch']} Batch`  \n📅 **Joined On:** `{first_record['paid_on']}`")
            r2.markdown(f"📱 +{latest_record['phone']}  \n📦 **Current Plan:** {latest_record['plan']}")
            
            new_status = r3.selectbox(
                "Status", ["Paid", "Pending", "Overdue"], 
                index=["Paid", "Pending", "Overdue"].index(latest_record["status"]), 
                key=f"status_{master_idx}"
            )
            if new_status != latest_record["status"]:
                for i, s in enumerate(st.session_state.students):
                    if s['name'] == latest_record['name'] and s['paid_on'] == latest_record['paid_on']:
                        st.session_state.students[i]["status"] = new_status
                        if new_status == "Paid":
                            st.session_state.students[i]["paid_on"] = datetime.now().strftime("%Y-%m-%d")
                        break
                save_data()
                st.rerun()
                
            r4.markdown(f"💰 **Last Fee:** ₹{latest_record['amount']}  \n⌛ **Expires On:** `{latest_record['valid_till']}`")
            
            # WhatsApp direct reminder link block execution
            if latest_record["status"] in ["Pending", "Overdue"]:
                msg = f"Dear {latest_record['name']},\n\nThis is a friendly reminder from Roots Zumba Fitness Studio. 😊 Your monthly fee of ₹{latest_record['amount']} is currently marked as {latest_record['status'].lower()}.\n\nPlease clear your dues at your earliest convenience. Thank you! 🙏✨"
                encoded_msg = urllib.parse.quote(msg)
                wa_link = f"whatsapp://send?phone={latest_record['phone']}&text={encoded_msg}"
                r5.markdown(f'<a href="{wa_link}" target="_top" style="text-decoration:none; background-color:#25D366; color:white; padding:8px 16px; border-radius:4px; font-weight:bold; display:inline-block;">💬 Send Reminder</a>', unsafe_allow_html=True)
            else:
                r5.write("✅ Up to Date")
                
            if r6.button("🗑️", key=f"del_{master_idx}"):
                st.session_state.students = [s for s in st.session_state.students if s['name'] != latest_record['name']]
                save_data()
                st.rerun()
                
            # FIXED INDENTATION ALIGNMENT: Perfectly structured expansion history drawer tray
            with st.expander(f"📜 View History Ledger Timeline ({len(history)} past entries)"):
