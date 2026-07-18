import os
import requests
import smtplib
from email.message import EmailMessage

# Configuration
EMAIL_USER = "mkraone7@gmail.com"
EMAIL_PASS = os.environ.get('EMAIL_PASS')
RAPID_API_KEY = os.environ.get('RAPID_API_KEY')

# Constants
ROLES = '("Analyst" OR "Engineer" OR "Scientist" OR "Data Analyst" OR "Data Engineer" OR "Data Scientist" OR "Senior Data Analyst" OR "Senior Data Engineer" OR "Senior Data Scientist" OR "Lead Data Analyst" OR "Lead Data Engineer" OR "Lead Data Scientist" OR "Game Data Analyst" OR "Game Data Scientist" OR "Game Data Engineer")'
LOCATIONS = ["Gurgaon", "Delhi", "Noida", "Dubai", "Remote", "India"]

def fetch_jobs():
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    all_jobs = []
    
    for loc in LOCATIONS:
        # Har location ke liye separate API call
        querystring = {
            "query": f"{ROLES} in {loc}",
            "employment_types": "FULLTIME",
            "job_requirements": "more_than_5_years_experience",
            "remote_jobs_only": "false",
            "num_pages": "1"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            if response.status_code == 200:
                data = response.json().get('data', [])
                all_jobs.extend(data)
        except Exception as e:
            print(f"Failed for {loc}: {e}")
            
    # Duplicate jobs remove karna (job_id ke basis par)
    unique_jobs = {job['job_id']: job for job in all_jobs}.values()
    
    # Sorting by date (Descending)
    return sorted(unique_jobs, key=lambda x: x.get('job_posted_at_timestamp', 0), reverse=True)

def send_email(jobs_list):
    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    
    if not jobs_list:
        msg['Subject'] = '🟢 Job Bot: No New Matches'
        msg.set_content("Bhai, aaj koi fresh job match (5+ exp, Remote, Fulltime) nahi mili.")
    else:
        msg['Subject'] = f'🚀 {len(jobs_list)} New High-Level Jobs Found!'
        content = "Bhai, ye rahi aaj ki fresh jobs (Experience 5+ years):\n\n"
        for i, job in enumerate(jobs_list[:10], 1): # Top 10 jobs
            content += f"{i}. {job.get('job_title')}\nCompany: {job.get('employer_name')}\nLocation: {job.get('job_city')}, {job.get('job_country')}\nLink: {job.get('job_apply_link')}\n\n"
        msg.set_content(content)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print(f"✅ Email sent with {len(jobs_list)} jobs!")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
