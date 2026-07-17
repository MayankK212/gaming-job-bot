import os
import sys
import requests
import xml.etree.ElementTree as ET
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup

# Configuration (Email is hardcoded, Password from GitHub Secret)
EMAIL_USER = "mkraone7@gmail.com" 
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# Verified Google Alert RSS Feed Link (Hardcoded by AI)
FEED_URL = "https://www.google.co.in/alerts/feeds/06128253058127210839/3052528383467176900" 

def fetch_jobs_from_feed():
    jobs = []
    print("--- STARTING RSS SCRAPE ---")
    print(f"Target Feed: {FEED_URL}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        print(f"RSS Status Code: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('ns:entry', ns)
            print(f"Found {len(entries)} entries in RSS.")
            
            for entry in entries:
                raw_title = entry.find('ns:title', ns).text
                title = BeautifulSoup(raw_title, "html.parser").get_text()
                
                raw_link = entry.find('ns:link', ns).attrib['href']
                actual_link = raw_link.split('url=')[1].split('&')[0] if 'url=' in raw_link else raw_link
                
                portal = "Job Portal"
                if "linkedin" in actual_link: portal = "LinkedIn"
                elif "naukri" in actual_link: portal = "Naukri"
                elif "indeed" in actual_link: portal = "Indeed"
                elif "foundit" in actual_link: portal = "Monster/Foundit"
                
                jobs.append({
                    'title': title,
                    'portal': portal,
                    'link': actual_link
                })
        else:
            print(f"RSS fetch failed with status {response.status_code}")
    except Exception as e:
        print(f"Error parsing RSS Feed: {e}")
    return jobs[:5]

def send_email(jobs_list):
    print("--- PREPARING EMAIL ---")
    if not EMAIL_PASS:
        print("❌ ERROR: EMAIL_PASS is missing in Github Secrets!")
        return

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    
    if not jobs_list:
        print("0 jobs found. Sending Status Email with direct search fallback links...")
        msg['Subject'] = '🟢 Gaming Job Bot: Active (No Fresh Matches Found Today)'
        
        # Static direct search links for manual quick-check
        email_content = (
            "Bhai, tera automation system aur Gmail connection 100% chal raha hai!\n\n"
            "Lekin aaj Google Alerts RSS feed par koi naye matching roles nahi mile.\n"
            "Chinta mat kar, tu in direct links par click karke aaj ke active openings dekh sakta hai:\n\n"
            "1. 📌 LinkedIn Jobs (Gaming + Data India):\n"
            "   https://www.linkedin.com/jobs/search/?keywords=%22Data%22%20AND%20%22Gaming%22%20AND%20%22India%22\n\n"
            "2. 📌 Naukri Jobs (Data roles in Gameskraft, Dream11, Zynga):\n"
            "   https://www.naukri.com/gaming-data-jobs\n\n"
            "System roz subah scan karta rahega aur jaise hi koi fresh match dikhega, automatic bhej dega!"
        )
    else:
        print(f"Sending {len(jobs_list)} jobs...")
        msg['Subject'] = '🚀 Your Daily Gaming Job Match (LinkedIn, Naukri, Indeed)'
        formatted_jobs = []
        for i, job in enumerate(jobs_list, 1):
            formatted_jobs.append(f"{i}. 🎯 **Role:** {job['title']}\n📌 **Platform:** {job['portal']}\n🔗 **Link:** {job['link']}\n")
            
        email_content = (
            "Bhai, ye rahi teri daily gaming jobs report:\n\n"
            + "\n---------------------------\n\n".join(formatted_jobs)
            + "\n\n💡 Pro Tip: Short notice period (30 days) use karke direct referrals maang lena!"
        )
        
    msg.set_content(email_content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("✅ SUCCESS: Email sent successfully!")
    except Exception as smtp_err:
        print(f"❌ SMTP GMAIL ERROR: {smtp_err}")

if __name__ == "__main__":
    jobs = fetch_jobs_from_feed()
    send_email(jobs)
