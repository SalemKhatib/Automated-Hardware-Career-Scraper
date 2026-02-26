# 🚨 Israel Student Job Scraper

Monitors Nvidia and Intel's Workday job boards for new student / intern roles posted in Israel, and sends an email alert the moment one appears.

---

## Features

- Scrapes Nvidia and Intel Workday APIs every 30 minutes
- Filters for student / intern roles in Israeli locations
- Sends a Gmail alert with the job title, location, and direct apply link
- Remembers seen jobs (with 90-day pruning) so you never get duplicate emails
- Retries automatically on network errors

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/job-scraper.git
cd job-scraper
```

### 2. Install dependencies
```bash
pip install requests python-dotenv
```

### 3. Configure your credentials
```bash
cp .env.example .env
```
Then open `.env` and fill in your Gmail address and [App Password](https://support.google.com/accounts/answer/185833).

```
SENDER_EMAIL=your.email@gmail.com
RECEIVER_EMAIL=your.email@gmail.com
EMAIL_APP_PASSWORD=your16letterapppassword
```

> ⚠️ `.env` is listed in `.gitignore` and will never be committed to GitHub.

### 4. Run
```bash
python job_scraper.py
```

The script will send a test email on startup to confirm the connection, then begin scanning every 30 minutes. Keep the terminal open (or run it in the background with `nohup` or a scheduler).

---

## Running in the background (optional)

```bash
# Linux / Mac — keep running after you close the terminal
nohup python job_scraper.py &

# Check output
tail -f nohup.out
```

---

## Adding more companies

Add a new entry to the `COMPANIES` dict in `job_scraper.py`:

```python
COMPANIES = {
    "Nvidia": "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
    "Intel":  "https://intel.wd1.myworkdayjobs.com/wday/cxs/intel/External/jobs",
    "NewCo":  "https://newco.wd1.myworkdayjobs.com/wday/cxs/newco/Careers/jobs",  # ← add here
}
```

---

## File structure

```
job-scraper/
├── job_scraper.py    # Main script
├── .env.example      # Credentials template (safe to commit)
├── .env              # Your real credentials (gitignored)
├── .gitignore
└── README.md
```

`seen_jobs.json` is created automatically at runtime and is also gitignored.
