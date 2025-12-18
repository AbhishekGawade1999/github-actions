import requests
import pandas as pd
from jobspy import scrape_jobs
import os

# --- Configuration ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_FILE = "notified_jobs.txt"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

# 1. Load already notified jobs
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        notified_urls = set(line.strip() for line in f)
else:
    notified_urls = set()

# 2. Scrape Jobs
roles = ["DevOps", "devops", "SRE", "Site Reliability Engineer"]
all_jobs = pd.DataFrame()

for role in roles:
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=role,
            location="Pune, Maharashtra, India",
            results_wanted=15,
            hours_old=4,
            country_indeed='india'
        )
        all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
    except Exception as e:
        print(f"Error scraping {role}: {e}")

# 3. Filter and Deduplicate
if not all_jobs.empty:
    all_jobs.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
    
    keywords = ['DevOps', 'dev ops', 'devops', 'sre', 'SRE', 'Site Reliability', 'DevSecOps']
    pattern = '|'.join(keywords)
    
    if 'title' in all_jobs.columns:
        all_jobs['title'] = all_jobs['title'].fillna('')
        filtered_jobs = all_jobs[all_jobs['title'].str.contains(pattern, case=False, na=False)]
        
        new_notifications = []
        
        for _, job in filtered_jobs.iterrows():
            url = job.get('job_url')
            if url not in notified_urls:
                # Format message
                msg = (
                    f"🚀 <b>New Job Alert!</b>\n\n"
                    f"<b>Pos:</b> {job.get('title')}\n"
                    f"<b>Co:</b> {job.get('company')}\n"
                    f"<b>Loc:</b> {job.get('location')}\n"
                    f"🔗 <a href='{url}'>Apply Here</a>"
                )
                send_telegram_msg(msg)
                new_notifications.append(url)

        # 4. Save new URLs back to the file
        with open(DB_FILE, "a") as f:
            for url in new_notifications:
                f.write(url + "\n")
