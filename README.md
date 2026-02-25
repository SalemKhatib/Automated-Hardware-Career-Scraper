# Automated-Hardware-Career-Scraper
Author: Salem Khatib

Tech Stack: Python, Workday API, SMTP, JSON

📌 Overview:
In the highly competitive Israeli semiconductor market, timing is everything. I built this automated scraper to monitor the career portals of Nvidia and Intel in real-time. The script ensures I am among the first applicants for new student and intern roles by sending instant email notifications the moment a position is posted.

⚙️ Key Features:
Multi-Source Monitoring: Simultaneously tracks Nvidia (Workday WD5) and Intel (Workday WD1) API endpoints.

Intelligent Filtering: Specifically targets "Student" and "Intern" roles within the Israel region.

Freshness Check: Uses logic to only alert on roles posted "Today," avoiding old listing fatigue.

Email Integration: Uses Python's smtplib to send real-time alerts to a dedicated job-hunting inbox.

Persistence: Maintains a seen_jobs.json database to ensure no duplicate notifications.

🛠️ Why I Built This:
Applying for VLSI and Hardware roles at Tier-1 companies requires speed. By the time a role is "featured" on LinkedIn, it often has hundreds of applicants. This tool gives me a strategic "First-In" advantage.
