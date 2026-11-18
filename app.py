import os
import streamlit as st
import pandas as pd
import sqlite3
import base64
from PIL import Image
from groq import Groq
import urllib.parse

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PakClean AI - CleanTech 2026",
    page_icon="♻️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# SQLite Database Initialization
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_area TEXT,
            issue_type TEXT,
            risk_level TEXT,
            details TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def add_complaint_to_db(city_area, issue_type, risk_level, details):
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (city_area, issue_type, risk_level, details, status)
        VALUES (?, ?, ?, ?, ?)
    """, (city_area, issue_type, risk_level, details, "Pending"))
    conn.commit()
    conn.close()

def get_all_complaints():
    conn = sqlite3.connect("reports.db")
    df = pd.read_sql_query("SELECT id, city_area AS 'City/Area', issue_type AS 'Issue', risk_level AS 'Risk', status AS 'Status', details AS 'Details' FROM complaints", conn)
    conn.close()
    return df

# -----------------------------------------------------------------------------
# Sidebar Configuration & Navigation
# -----------------------------------------------------------------------------
st.sidebar.title("♻️ PakClean AI")
st.sidebar.caption("CleanTech Hackathon 2026 Entry")

api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
# یہاں سے آپ اپنی مرضی کا ماڈل نام خود کنٹرول کر سکتے ہیں
selected_model = st.sidebar.text_input("Groq Model Name:", value="qwen/qwen3.8-27b")

menu = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "🤖 AI Waste & Water Scanner", "📢 Citizen Reporting", "📊 Admin Dashboard"]
)

# -----------------------------------------------------------------------------
# Helper Function: Flexible Hybrid AI Analysis (Image, Text, or Both)
# -----------------------------------------------------------------------------
def analyze_issue_with_groq(image_file, description, user_api_key, model_name):
    try:
        client = Groq(api_key=user_api_key)
        
        system_prompt = """
        You are an expert Environmental & CleanTech AI Specialist for Pakistan. Your task is to analyze the provided environmental issue, waste condition, or water contamination based on the uploaded image and/or text description.

        Provide a highly structured, professional, and clear Markdown response with the following 4 exact sections:
        
        1. 🔍 **Category Identified:** Clearly specify the type of waste or water issue (e.g., Plastic Pollution, Solid Waste Dump, Organic Waste, Industrial Waste, Sewage Overflow, or Water Pipeline Leakage).
        2. ♻️ **Recyclability & Treatment Status:** State whether the identified material is recyclable, biodegradable, or if the water requires specific biological/chemical treatment.
        3. ⚠️ **Health & Environmental Risk Level:** Assess the hazard level (Low, Medium, High, or Critical) and briefly explain the potential risks to public health and the local ecosystem in urban areas like Karachi.
        4. 💡 **Actionable Solution & Disposal Steps:** Provide 3 practical, step-by-step recommendations for local municipal authorities, citizens, or cleanup teams to safely manage or resolve this specific issue.
        """
        
        # Check if an image is provided by the user
        if image_file is not None:
            bytes_data = image_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            
            img_format = image_file.type.split("/")[-1]
            if img_format == 'jpeg':
                img_format = 'jpg'
                
            image_url = f"data:image/{img_format};base64,{base64_image}"
            user_text = description if description else "Please perform a comprehensive environmental hazard analysis of this image."
            
            messages_content = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{system_prompt}\n\nAdditional User Notes/Description: {user_text}"},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ]
        else:
            # Text-only fallback when no image is uploaded
            user_text = description if description else "General environmental waste issue."
            full_prompt = f"{system_prompt}\n\nDescription: {user_text}"
            messages_content = [
                {"role": "user", "content": full_prompt}
            ]

        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_content,
            temperature=0.2,
            max_tokens=900,  # 1500 ko 900 kar dein
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error during AI Analysis: {str(e)}"

# -----------------------------------------------------------------------------
# 1. Home Tab
# -----------------------------------------------------------------------------
if menu == "🏠 Home":
    st.title("🌱 PakClean AI - Smart Waste & Water Management")
    st.markdown("### *Empowering Pakistan's CleanTech Future with AI*")
    st.image("https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 Problem Statement")
        st.write("Urban centers like Karachi face massive challenges with solid waste dumping, unmanaged recycling, and sewage overflow. Manual sorting and delayed reporting lead to extreme environmental hazards.")
    
    with col2:
        st.subheader("🚀 Our AI Solution")
        st.write("PakClean AI utilizes Generative AI to instantly analyze waste hazards, guide recycling efforts, and provide real-time location reporting for municipal action.")

# -----------------------------------------------------------------------------
# 2. AI Scanner Tab (Supports Image-only, Text-only, or Both!)
# -----------------------------------------------------------------------------
elif menu == "🤖 AI Waste & Water Scanner":
    st.title("🤖 AI Waste & Water Hazard Analyzer")
    st.info("Upload an image, type a description, or use both together for maximum AI precision!")

    uploaded_file = st.file_uploader("Upload Image (Optional)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Issue Image", width=350)

    issue_desc = st.text_area("Describe the waste or water issue observed (Optional if image is provided):")

    if st.button("🔍 Analyze with AI"):
        if not api_key:
            st.error("Please enter your Groq API Key in the sidebar first!")
        elif uploaded_file is None and not issue_desc:
            st.warning("Please either upload an image or enter a description to analyze!")
        else:
            spinner_text = "AI is analyzing visual and environmental parameters..." if uploaded_file else "AI is analyzing your text description..."
            with st.spinner(spinner_text):
                result = analyze_issue_with_groq(uploaded_file, issue_desc, api_key, selected_model)
                st.markdown(result)

# -----------------------------------------------------------------------------
# 3. Citizen Reporting Tab (Updated with Direct Web Gmail Integration)
# -----------------------------------------------------------------------------
elif menu == "📢 Citizen Reporting":
    st.title("📢 Report Local Environmental Issue")
    st.write("Submit a location report for open garbage dumps or water overflow in your area. This saves to our database and generates official municipal alerts.")

    with st.form("report_form"):
        area = st.text_input("Location / City Area (e.g., Karachi - North Nazimabad)")
        issue_type = st.selectbox("Issue Type", ["Solid Waste Dump", "Water Pipeline Burst", "Sewage Overflow", "Industrial Waste", "Coastal Plastic Accumulation"])
        risk = st.select_slider("Urgency Level", options=["Low", "Medium", "High", "Critical"])
        details = st.text_area("Additional Details / Observations")
        
        submitted = st.form_submit_button("Submit Report & Register")
        if submitted:
            if area:
                # Save to SQLite Database
                add_complaint_to_db(area, issue_type, risk, details)
                st.success(f"✅ Report successfully registered in Database for {area}!")
                
                # Generate Real-World Action Links
                msg = f"🚨 *PakClean AI Emergency Alert* 🚨\n\n*Area:* {area}\n*Issue:* {issue_type}\n*Risk Level:* {risk}\n*Details:* {details}\n\nKindly dispatch municipal cleanup team."
                encoded_msg = urllib.parse.quote(msg)
                
                # WhatsApp Link
                whatsapp_url = f"https://wa.me/?text={encoded_msg}"
                
                # Web-based Direct Gmail Link (Always works in Browser!)
                email_subject = urllib.parse.quote(f"Urgent CleanTech Complaint: {issue_type} at {area}")
                email_body = urllib.parse.quote(
                    f"Respected Authority,\n\n"
                    f"An urgent environmental issue has been logged via PakClean AI Portal.\n\n"
                    f"Location Area: {area}\n"
                    f"Issue Type: {issue_type}\n"
                    f"Urgency Risk Level: {risk}\n"
                    f"Additional Details: {details}\n\n"
                    f"Please issue immediate resolution directives.\n\n"
                    f"Regards,\nPakClean AI Citizen Portal"
                )
                
                gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to=complaints@sswmb.gos.pk&su={email_subject}&body={email_body}"
                
                st.markdown("---")
                st.subheader("🌐 Send Real-World Alert to Municipal Authorities:")
                col_w, col_e = st.columns(2)
                with col_w:
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">💬 Send via WhatsApp</button></a>', unsafe_allow_html=True)
                with col_e:
                    st.markdown(f'<a href="{gmail_url}" target="_blank"><button style="background-color:#0078D4; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">✉️ Send via Official Gmail</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Please provide a location area.")

# -----------------------------------------------------------------------------
# 4. Admin Dashboard Tab
# -----------------------------------------------------------------------------
elif menu == "📊 Admin Dashboard":
    st.title("📊 Municipal & Admin Dashboard")
    st.write("Real-time monitoring of reported clean-tech issues across zones from the database.")

    df = get_all_complaints()

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reports", len(df))
        col2.metric("Pending Action", len(df[df["Status"] == "Pending"]))
        col3.metric("Resolved Cases", len(df[df["Status"] == "Resolved"]))

        st.subheader("📋 Active Complaints Registry")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No complaints registered yet. Go to 'Citizen Reporting' to add a new report.")
