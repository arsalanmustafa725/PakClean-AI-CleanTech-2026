# ♻️ PakClean AI - Smart Waste & Water Management Portal

**PakClean AI** is an advanced, full-stack Generative AI web application built as an entry for the **CleanTech Hackathon 2026**, offered and presented by **The LUMS Centre for Entrepreneurship (LCE)** and **OGDCL**. 

Designed specifically to tackle severe solid waste dumping, unmanaged sewage, and municipal reporting delays in urban megacities like Karachi, this platform empowers citizens and authorities with intelligent diagnostics and instant emergency dispatch mechanisms.

---

## ✨ Core Features & Architecture

1. **🏠 Home & Problem Overview:** Highlights the critical municipal challenges of waste management and introduces the AI-driven intervention model.
2. **🤖 AI Waste & Water Scanner:** 
   - Supports flexible hybrid inputs (Image-only, Text-only, or both simultaneously).
   - Utilizes advanced Groq AI vision models (`qwen/qwen3.8-27b`) to evaluate waste category, recyclability, health/environmental risk levels (Low to Critical), and step-by-step actionable disposal solutions.
3. **📢 Citizen Reporting & Municipal Dispatch:** 
   - Automatically logs environmental complaints into a local **SQLite3 database (`reports.db`)** with a default "Pending" status.
   - Instantly generates pre-formatted emergency dispatch links for local authorities (**SSWMB**) via **WhatsApp (`wa.me`)** and **Official Web Gmail**.
4. **📊 Municipal & Admin Dashboard:** Provides real-time metrics (Total Reports, Pending Actions, Resolved Cases) alongside a live interactive data registry table (`pandas`).

---

## 🛠️ Tech Stack & Requirements

* **Frontend & UI Framework:** Streamlit (Python)
* **AI Processing Engine:** Groq API (Default Model: `qwen/qwen3.8-27b`)
* **Database Management:** SQLite3 (Embedded local database)
* **Data & Image Handling:** Pandas, Pillow (PIL), Base64 encoding[cite: 6]

---

## 🚀 How to Run This Project Locally

Follow these step-by-step instructions to set up and run the application on your local machine:

### Step 1: Prepare Your Project Files
Ensure your project folder contains the following core files:
* `app.py` (Main application script containing the full source code)[cite: 6]
* `requirements.txt` (Project dependencies list)[cite: 7]

### Step 2: Install Required Dependencies
Open your terminal inside the project folder and run the following command to install all required Python libraries:
```bash
pip install -r requirements.txt
