import requests
import json
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# --- EMAIL SETTINGS (PROFESSIONAL CONFIGURATION) ---
# os.getenv looks for these variables on your computer's system
SENDER_EMAIL = os.getenv("SCRAPER_EMAIL") 
RECEIVER_EMAIL = os.getenv("SCRAPER_EMAIL") 
EMAIL_PASSWORD = os.getenv("SCRAPER_PASS") 

# --- SCRAPER SETTINGS ---
KEYWORDS = ["student", "intern", "working student"]
SEEN_FILE = Path("seen_jobs.json")

# Career Portals
COMPANIES = {
    "Nvidia": "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
    "Intel": "https://intel.wd1.myworkdayjobs.com/wday/cxs/intel/External/jobs"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

PAYLOAD = {
    "appliedFacets": {},
    "limit": 20, 
    "offset": 0,
    "searchText": "Israel" 
}

def send_email_alert(company, title, location, url, is_test=False):
    if not EMAIL_PASSWORD or not SENDER_EMAIL:
        print("⚠️ Environment variables not set. Skipping email.")
        return 
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    if is_test:
        msg['Subject'] = "✅ Scraper Test: Connection Successful"
        body = "System check passed. Monitoring career portals..."
    else:
        msg['Subject'] = f"🚨 New {company} Role: {title}"
        body = f"Role: {title}\nLocation: {location}\n\nApply: {url}"
        
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email Error: {e}")

def run_scraper():
    print(f"[{time.strftime('%X')}] Checking for new postings...")
    
    if SEEN_FILE.exists():
        try:
            seen = set(json.loads(SEEN_FILE.read_text()))
        except json.JSONDecodeError:
            seen = set()
    else:
        seen = set()

    for company_name, api_url in COMPANIES.items():
        try:
            resp = requests.post(api_url, headers=HEADERS, json=PAYLOAD)
            resp.raise_for_status()
            data = resp.json()

            for job in data.get("jobPostings", []):
                title = job.get("title", "").lower()
                job_id = job.get("externalPath", "")
                location = job.get("locationsText", "").lower()
                posted_on = job.get("postedOn", "").lower()

                # Business Logic: Student + Israel + Posted Today
                is_student = any(k in title for k in KEYWORDS)
                is_in_israel = any(loc in location for loc in ["israel", "haifa", "yokneam", "tel aviv"])
                is_new = "today" in posted_on

                if is_student and is_in_israel and is_new and job_id not in seen:
                    seen.add(job_id)
                    domain = "nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite" if company_name == "Nvidia" else "intel.wd1.myworkdayjobs.com/en-US/External"
                    job_url = f"https://{domain}{job_id}"
                    
                    send_email_alert(company_name, job.get('title'), job.get('locationsText'), job_url)
                    print(f"Match Found: {job.get('title')}")

        except Exception as e:
            print(f"API Error ({company_name}): {e}")

    SEEN_FILE.write_text(json.dumps(list(seen)))

if __name__ == "__main__":
    send_email_alert("", "", "", "", is_test=True)
    while True:
        run_scraper()
        time.sleep(1800)
