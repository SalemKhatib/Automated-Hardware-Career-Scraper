import requests
import json
import time
import smtplib
import re
import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

# --- EMAIL SETTINGS ---
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")

if not all([SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD]):
    raise EnvironmentError(
        "Missing required environment variables. "
        "Please copy .env.example to .env and fill in your credentials."
    )

# --- SCRAPER SETTINGS ---
SEEN_FILE = Path("seen_jobs.json")
MAX_PAGES = 50

COMPANIES = {
    "Nvidia": "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
    "Intel": "https://intel.wd1.myworkdayjobs.com/wday/cxs/intel/External/jobs"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Session with automatic retry on transient network errors
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def load_seen():
    """Load seen jobs from file, pruning entries older than 90 days."""
    if not SEEN_FILE.exists():
        return {}
    try:
        data = json.loads(SEEN_FILE.read_text())
        # Handle legacy format (plain list) gracefully
        if isinstance(data, list):
            today = datetime.date.today().isoformat()
            return {job_id: today for job_id in data}
        # Prune entries older than 90 days
        cutoff = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
        return {k: v for k, v in data.items() if v >= cutoff}
    except json.JSONDecodeError:
        return {}


def save_seen(seen: dict):
    """Persist the seen jobs dict to disk immediately."""
    SEEN_FILE.write_text(json.dumps(seen))


def send_email_alert(company, title, location, url, is_test=False):
    """Send a job alert email. Pass is_test=True to verify the connection."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    if is_test:
        msg['Subject'] = "✅ Scraper Test: Email Connection Successful!"
        body = (
            "Your Python scraper has successfully connected to this email account "
            "and is now monitoring for Nvidia and Intel jobs in the background."
        )
    else:
        msg['Subject'] = f"🚨 New {company} Student Job: {title}"
        body = (
            f"A new role was posted today!\n\n"
            f"Company: {company}\n"
            f"Role: {title}\n"
            f"Location: {location}\n\n"
            f"Apply here: {url}"
        )

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        if not is_test:
            print(f"  - Email sent for: {title} @ {company}")
    except Exception as e:
        print(f"  - Failed to send email: {e}")


# --- MAIN LOOP ---
TIMER = 1800  # seconds between checks (30 minutes)

print("Testing email connection...")
send_email_alert("", "", "", "", is_test=True)
print(f"✅ Email OK! Checking every {TIMER // 60} mins. Press Ctrl+C to stop.\n")

while True:
    seen = load_seen()
    print(f"[{time.strftime('%X')}] Scanning jobs...")

    for company_name, api_url in COMPANIES.items():
        try:
            search_terms = (
                ["Israel"]
                if company_name == "Nvidia"
                else ["Haifa", "Petah-Tikva", "Petah Tikva", "Jerusalem", "Kiryat Gat", "Kiryat-Gat"]
            )

            for term in search_terms:
                offset = 0
                page = 0

                while page < MAX_PAGES:
                    payload = {
                        "appliedFacets": {},
                        "limit": 20,
                        "offset": offset,
                        "searchText": term
                    }

                    resp = session.post(api_url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                    jobs = data.get("jobPostings", [])
                    if not jobs:
                        break

                    for job in jobs:
                        title = job.get("title", "").lower()
                        job_id = job.get("externalPath", "")
                        location = job.get("locationsText", "").lower()
                        posted_on = job.get("postedOn", "").lower()

                        is_student = bool(re.search(r'\b(student|students|intern|interns)\b', title))
                        is_in_israel = any(loc in location for loc in [
                            "israel", "haifa", "petah tikva", "jerusalem", "yokneam",
                            "tel aviv", "beer sheva", "ra'anana", "kiryat gat", "kiryat-gat"
                        ])
                        is_posted_today = "today" in posted_on

                        if is_student and is_in_israel:
                            if not is_posted_today:
                                if job_id not in seen:
                                    print(f"  [SKIP] '{job.get('title')}' — not posted today ('{job.get('postedOn')}')")
                                    seen[job_id] = datetime.date.today().isoformat()
                                    save_seen(seen)
                            elif job_id in seen:
                                pass  # Already alerted
                            else:
                                seen[job_id] = datetime.date.today().isoformat()
                                save_seen(seen)

                                domain = (
                                    "nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite"
                                    if company_name == "Nvidia"
                                    else "intel.wd1.myworkdayjobs.com/en-US/External"
                                )
                                job_url = f"https://{domain}{job_id}"

                                print(f"\n🚨 NEW {company_name.upper()} JOB: {job.get('title')} — {job.get('locationsText')}")
                                send_email_alert(company_name, job.get('title'), job.get('locationsText'), job_url)

                    offset += 20
                    page += 1

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Could not fetch {company_name} jobs: {e}")

    print(f"[{time.strftime('%X')}] Scan complete. Next check in {TIMER // 60} mins.\n")
    time.sleep(TIMER)
