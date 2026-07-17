import os
import requests
import xml.etree.ElementTree as ET
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup

# Secrets fetching
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
FEED_URL = "PASTE_YOUR_GOOGLE_ALERT_RSS_LINK_HERE" # ⚠️ ISKO APNE LINK SE REPLACE KARNA HAI

def fetch_jobs_from_portals():
    jobs = []
    print("--- STEP 1: FETCHING JOBS ---")
    
    # Quick Check
    if "PASTE_YOUR" in FEED_URL:
        print("❌ ERROR: Apne FEED_URL ko replace nahi kiya hai!")
        return jobs

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        print(f"Google Feed Status Code: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('ns:entry', ns)
            print(f"Total entries found: {len(entries)}")
            
            for entry in entries:
                try:
                    raw_title = entry.find('ns:title', ns).text
                    title = BeautifulSoup(raw_title, "html.parser").get_text()
                    
                    raw_link = entry.find('ns:link', ns).attrib['href']
                    actual_link = raw_link.split('url=')[1].split('&')[0] if 'url=' in raw_link else raw_link
                    
                    portal = "Job Portal"
                    if "linkedin" in actual_link: portal = "LinkedIn"
                    elif "naukri" in actual_link: portal = "Naukri"
                    elif "indeed" in actual_link: portal = "Indeed"
                    elif "foundit" in actual_link: portal = "Monster"
                    
                    jobs.append(f"🎯 **Role:** {title}\n📌 **Platform:** {portal}\n🔗 **Link:** {actual_link}\n")
                except Exception as parse_err:
                    print(f"Skipping entry due to parsing error: {parse_err}")
        else:
            print("❌ ERROR: Google Feed returned non-200 status.")
    except Exception as e:
        print(f"❌ ERROR inside fetch_jobs_from_portals: {e}")
        
    return jobs[:5]

def send_email(jobs_list):
    print("--- STEP 2: SENDING EMAIL ---")
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ ERROR: EMAIL_USER ya EMAIL_PASS Secret settings mein missing hai!")
        return

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    
    if not jobs_list:
        print("No jobs found today. Sending Status Email...")
        msg['Subject'] = '🟢 Gaming Job Bot: Active'
        email_content = "Bhai, bot sahi chal raha hai par aaj koi nayi job nahi mili. System is active!"
    else:
        print(f"Sending {len(jobs_list)} jobs...")
        msg['Subject'] = '🚀 Your Daily Gaming Job Match (LinkedIn, Naukri, Indeed)'
        email_content = "Bhai, ye rahi teri report:\n\n" + "\n\n---\n\n".join(jobs_list)
        
    msg.set_content(email_content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("✅ SUCCESS: Email sent successfully!")
    except Exception as smtp_err:
        print(f"❌ SMTP GMAIL ERROR: {smtp_err}")
        print("Apna 16-digit app password aur email settings verify karein.")

if __name__ == "__main__":
    jobs = fetch_jobs_from_portals()
    send_email(jobs)
