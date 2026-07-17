import os
import requests
import xml.etree.ElementTree as ET
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup

# Configuration from GitHub Secrets
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# ⚠️ APNA GOOGLE ALERT RSS LINK YAHAN PASTE KARO (Step 1 wala)
FEED_URL = "https://www.google.co.in/alerts/feeds/06128253058127210839/3052528383467176900" 

def fetch_jobs_from_portals():
    jobs = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('ns:entry', ns)[:10]: # Top 10 latest entries
                raw_title = entry.find('ns:title', ns).text
                # Clean HTML tags from title
                title = BeautifulSoup(raw_title, "html.parser").get_text()
                
                raw_link = entry.find('ns:link', ns).attrib['href']
                # Google Alerts link contains redirect, we extract the actual job portal link
                actual_link = raw_link.split('url=')[1].split('&')[0] if 'url=' in raw_link else raw_link
                
                # Identify Portal Name for better readability
                portal = "Job Portal"
                if "linkedin" in actual_link: portal = "LinkedIn"
                elif "naukri" in actual_link: portal = "Naukri"
                elif "indeed" in actual_link: portal = "Indeed"
                elif "foundit" in actual_link: portal = "Monster/Foundit"
                
                jobs.append(f"🎯 **Role:** {title}\n📌 **Platform:** {portal}\n🔗 **Direct Apply Link:** {actual_link}\n")
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        
    return jobs[:5] # Send exactly top 5 matches

def send_email(jobs_list):
    if not jobs_list:
        print("No new jobs found today.")
        return
        
    msg = EmailMessage()
    msg['Subject'] = '🚀 Your Daily Gaming Job Match (LinkedIn, Naukri, Indeed)'
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com' # Your email
    
    email_content = (
        "Bhai, ye rahi teri customized jobs report (Filtered from LinkedIn, Naukri, Indeed & Monster):\n\n"
        + "\n\n---------------------------\n\n".join(jobs_list)
        + "\n\n💡 Pro Tip: Short notice period (30 days) highlights ko email replies mein use karna!"
    )
    msg.set_content(email_content)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    jobs = fetch_jobs_from_portals()
    send_email(jobs)
