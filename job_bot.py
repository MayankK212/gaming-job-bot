import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# Configuration
EMAIL_USER = 'your_email@gmail.com' # Tera Email
EMAIL_PASS = 'your_app_password'    # Google App Password (Important!)
TARGET_URLS = [
    'https://gameskraft.com/careers/',
    'https://about.dreamsports.com/careers/jobs/'
]

def fetch_jobs():
    jobs = []
    for url in TARGET_URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Logic: Har site ka structure alag hota hai, 
        # yahan hum keywords dhund rahe hain
        for link in soup.find_all('a', href=True):
            if 'data' in link.text.lower() or 'data' in link['href']:
                jobs.append(f"{link.text.strip()} : {link['href']}")
    return list(set(jobs))[:5] # Top 5 jobs

def send_email(jobs):
    msg = EmailMessage()
    msg['Subject'] = 'Daily Gaming Data Jobs Alert'
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    msg.set_content("Aaj ki Top 5 Jobs:\n\n" + "\n".join(jobs))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    jobs = fetch_jobs()
    if jobs:
        send_email(jobs)