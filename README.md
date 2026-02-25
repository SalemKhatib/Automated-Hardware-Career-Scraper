# 🚀 Silicon Career Monitor: Nvidia & Intel (Israel)

### 📌 Project Overview
In the competitive Israeli semiconductor industry, being one of the first applicants is a major strategic advantage. I built this tool to automate the manual process of job hunting. The script monitors the **Workday APIs** of Nvidia and Intel, specifically filtering for student and intern roles at their Israeli development centers (Haifa, Yokneam, Petah Tikva, Jerusalem, and Tel Aviv).

### 🛠️ Technical Features
* **API-Driven Monitoring:** Directly interfaces with Nvidia (WD5) and Intel (WD1) career portal endpoints to fetch real-time data.
* **Intelligent Filtering:** High-precision keyword matching for "Student" and "Intern" roles.
* **Daily Freshness Logic:** Implements a "Posted Today" filter to ensure notifications only trigger for brand-new opportunities.
* **Automated Email Alerts:** Configured with `smtplib` and Google App Passwords for secure, automated notifications to a dedicated job-hunting inbox.
* **Data Persistence:** Uses a local JSON-based tracking system to ensure no duplicate notifications are sent for the same Role ID.
* **Security-First Design:** Built using `os.getenv` for environment variable management, ensuring that personal email credentials remain private and are never hardcoded.

### 💡 Why I Built This
As an **Electrical Engineering student at Tel Aviv University** focusing on **VLSI design and Computer Architecture**, I wanted to ensure I never miss a "Junior DFT" or "Hardware Verification" role. This project bridges my interest in Python automation with my career goals in the hardware-software interface.

### 🚀 Getting Started
1. **Set Environment Variables:**
   - `SCRAPER_EMAIL`: Your dedicated alert email.
   - `SCRAPER_PASS`: Your 16-character Google App Password.
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
