import os
import sys
import requests
import xml.etree.ElementTree as ET
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup

# HARDCODED SENDER EMAIL (No secret needed for username!)
EMAIL_USER = "mkraone7@gmail.com" 
# Secret required only for password
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# ⚠️ APNA GOOGLE ALERT RSS LINK YAHAN PASTE KARO
FEED_URL = "https://www.google.co.in/alerts/feeds/06128253058127210839/3052528383467176900" 

print("--- DEBUGGING INFO ---")
print(f"EMAIL_USER config: {EMAIL_USER}")
print(f"EMAIL_PASS present: {'Yes' if EMAIL_PASS else 'No (Secret is missing!)'}")

def fetch_jobs_from_portals():
    jobs = []
    print("Fetching jobs from Google Alerts RSS...")
    
    if "PASTE_YOUR" in FEED_URL:
        print("⚠️ Warning: FEED_URL placeholder not replaced.")
        return jobs

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('ns:entry', ns)
            print(f"Found {len(entries)} entries.")
            
            for entry in entries[:10]:
                raw_title = entry.find('ns:title', ns).text
                title = BeautifulSoup(raw_title, "html.parser").get_text()
                
                raw_link = entry.find('ns:link', ns).attrib['href']
                actual_link = raw_link.split('url=')[1].split('&')[0] if 'url=' in raw_link else raw_link
                
                portal = "Job Portal"
                if "linkedin" in actual_link: portal = "LinkedIn"
                elif "naukri" in actual_link: portal = "Naukri"
                elif "indeed" in actual_link: portal = "Indeed"
                elif "foundit" in actual_link: portal = "Monster/Foundit"
                
                jobs.append(f"🎯 **Role:** {title}\n📌 **Platform:** {portal}\n🔗 **Direct Apply Link:** {actual_link}\n")
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        
    return jobs[:5]

def send_email(jobs_list):
    if not EMAIL_PASS:
        print("❌ ERROR: EMAIL_PASS is missing in Github Secrets!")
        return

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com' # Destination Email
    
    if not jobs_list:
        print("No jobs found today. Sending Status Email...")
        msg['Subject'] = '🟢 Gaming Job Bot: Online & Working'
        email_content = (
            "Bhai, tera automation system aur Gmail connection 100% chal raha hai!\n\n"
            "Lekin aaj Google Alerts par tere keywords ke hisaab se koi naye roles index nahi huye.\n"
            "Kal subah system fir se scan karega aur naye roles aate hi tujhe mail aa jayega.\n\n"
            "Chill kar, system is active!"
        )
    else:
        print(f"Sending {len(jobs_list)} jobs...")
        msg['Subject'] = '🚀 Your Daily Gaming Job Match (LinkedIn, Naukri, Indeed)'
        email_content = (
            "Bhai, ye rahi teri customized jobs report:\n\n"
            + "\n\n---------------------------\n\n".join(jobs_list)
        )
        
    msg.set_content(email_content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("✅ Success: Email sent successfully!")
    except Exception as smtp_err:
        print(f"❌ SMTP Error: {smtp_err}")

if __name__ == "__main__":
    jobs = fetch_jobs_from_portals()
    send_email(jobs)
