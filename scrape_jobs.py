import requests
import pandas as pd
from jobspy import scrape_jobs
import os
from datetime import datetime

# --- Configuration ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_FILE = "notified_jobs.txt"

def send_telegram_msg(message):
    if not message:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True # Keeps the message compact
    }
    requests.post(url, json=payload)

# 1. Load already notified jobs
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        notified_urls = set(line.strip() for line in f)
else:
    notified_urls = set()

# 2. Scrape Jobs
roles = ["DevOps", "SRE", "Site Reliability Engineer"]
places = ["Pune, Maharashtra, India", "Pune/Pimpri-Chinchwad Area"]
all_jobs = pd.DataFrame()

for place in places:
    for role in roles:
        try:
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=role,
                location=place,
                google_search_term=f"{role} jobs near {place} since yesterday",
                results_wanted=15,
                hours_old=168,
                country_indeed='india'
            )
            all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
        except Exception as e:
            print(f"Error scraping {role}: {e}")

# 3. Filter and Build Batch Message
if not all_jobs.empty:
    all_jobs.drop_duplicates(subset=['job_url'], keep='first', inplace=True)
    
    keywords = ['DevOps', 'dev ops', 'devops', 'sre', 'SRE', 'Site Reliability', 'DevSecOps']
    pattern = '|'.join(keywords)
    
    if 'title' in all_jobs.columns:
        all_jobs['title'] = all_jobs['title'].fillna('')
        filtered_jobs = all_jobs[all_jobs['title'].str.contains(pattern, case=False, na=False)]
        
        new_urls = []
        # Header for the single message
        message_body = f"<b>🔍 New Jobs Found ({datetime.now().strftime('%H:%M')})</b>\n"
        message_body += "—" * 15 + "\n\n"
        
        found_new = False
        for _, job in filtered_jobs.iterrows():
            url = job.get('job_url')
            if url not in notified_urls:
                found_new = True
                # Clean up data
                title = job.get('title', 'N/A')[:40] # Truncate long titles
                company = job.get('company', 'N/A')
                
                # Add to the big message string
                message_body += f"<b>💼 {title}</b>\n"
                message_body += f"🏢 {company}\n"
                message_body += f"🔗 <a href='{url}'>View Job</a>\n\n"
                
                new_urls.append(url)

        if found_new:
            # 4. Send the single batched message
            send_telegram_msg(message_body)

            # 5. Save new URLs back to the file
            with open(DB_FILE, "a") as f:
                for url in new_urls:
                    f.write(url + "\n")
        else:
            send_telegram_msg(f"NO NEW JOBS FOUND - ({datetime.now().strftime('%H:%M')})")
            print("No new unique jobs found in this run.")
