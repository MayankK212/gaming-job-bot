import os
import requests
import smtplib
from email.message import EmailMessage

# Configuration
EMAIL_USER = "mkraone7@gmail.com"
EMAIL_PASS = os.environ.get('EMAIL_PASS')
RAPID_API_KEY = os.environ.get('RAPID_API_KEY')

def fetch_jobs():
    url = "https://jsearch.p.rapidapi.com/search"
    # Yahan apne keywords change kar le
    querystring = {"query": "Data Analyst Gaming India", "num_pages": "1"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def send_email(jobs_list):
    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    
    if not jobs_list:
        msg['Subject'] = '🟢 Gaming Job Bot: No New Matches'
        msg.set_content("Bhai, aaj koi fresh job match nahi mili. Kal phir try karenge!")
    else:
        msg['Subject'] = f'🚀 {len(jobs_list)} New Gaming Jobs Found!'
        content = "Bhai, ye rahi aaj ki fresh jobs:\n\n"
        for i, job in enumerate(jobs_list[:5], 1): # Top 5 jobs
            content += f"{i}. {job.get('job_title')}\nCompany: {job.get('employer_name')}\nLink: {job.get('job_apply_link')}\n\n"
        msg.set_content(content)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("✅ Email sent!")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
