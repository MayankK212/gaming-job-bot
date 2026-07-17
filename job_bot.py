
import os
import sys
import requests
import urllib.parse
import xml.etree.ElementTree as ET
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup

# Configuration
EMAIL_USER = "mkraone7@gmail.com" 
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# ⚠️ APNA GOOGLE ALERT RSS LINK YAHAN PASTE KARO
FEED_URL = "https://www.google.co.in/alerts/feeds/06128253058127210839/3052528383467176900" 

def fetch_fresh_jobs():
    """Step 1: Fetch fresh jobs from Google Alerts RSS feed"""
    jobs = []
    print("Fetching fresh jobs from Google Alerts RSS...")
    if "PASTE_YOUR" in FEED_URL or not FEED_URL:
        print("⚠️ Warning: FEED_URL placeholder not replaced. Skipping RSS.")
        return jobs

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(FEED_URL, headers=headers, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('ns:entry', ns)
            
            for entry in entries:
                raw_title = entry.find('ns:title', ns).text
                title = BeautifulSoup(raw_title, "html.parser").get_text()
                
                raw_link = entry.find('ns:link', ns).attrib['href']
                actual_link = raw_link.split('url=')[1].split('&')[0] if 'url=' in raw_link else raw_link
                
                portal = "Job Portal"
                if "linkedin" in actual_link: portal = "LinkedIn"
                elif "naukri" in actual_link: portal = "Naukri"
                elif "indeed" in actual_link: portal = "Indeed"
                elif "foundit" in actual_link: portal = "Monster"
                
                jobs.append({
                    'title': title,
                    'portal': portal,
                    'link': actual_link
                })
            print(f"✅ Found {len(jobs)} fresh jobs from RSS.")
    except Exception as e:
        print(f"Error fetching alerts RSS: {e}")
    return jobs

def fetch_older_jobs_from_google():
    """Step 2: Fallback to Google Search to pull older/indexed active jobs"""
    print("Fetching older/indexed active jobs from Google Search...")
    jobs = []
    
    # Exact query for older jobs in top portals
    query = 'site:linkedin.com/jobs/ OR site:naukri.com OR site:indeed.com OR site:foundit.in ("game data analyst" OR "data analyst" OR "data engineer" OR "data scientist" OR "senior data analyst" OR "senior data engineer" OR "senior data scientist" OR "lead data analyst" OR "lead data engineer" OR "lead data scientist") AND ("gaming" OR "gameskraft" OR "dream11" OR "zynga" OR "mpl" OR "moonfrog" OR "nazara") AND "India"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract links pointing to target portals
            for a in soup.find_all('a', href=True):
                href = a['href']
                title_text = a.get_text().strip()
                
                # Resolve google redirection if present
                if "/url?q=" in href:
                    actual_link = href.split('/url?q=')[1].split('&')[0]
                    actual_link = urllib.parse.unquote(actual_link)
                else:
                    actual_link = href
                
                # Check if it belongs to target portals
                if any(p in actual_link for p in ["linkedin.com/jobs", "naukri.com", "indeed.com", "foundit.in"]):
                    if len(title_text) > 12: # Avoid junk links
                        portal = "Job Portal"
                        if "linkedin" in actual_link: portal = "LinkedIn"
                        elif "naukri" in actual_link: portal = "Naukri"
                        elif "indeed" in actual_link: portal = "Indeed"
                        elif "foundit" in actual_link: portal = "Monster"
                        
                        # Clean title suffix
                        for suffix in [" - LinkedIn", " | Naukri", " - Indeed", " - Foundit"]:
                            if suffix in title_text:
                                title_text = title_text.split(suffix)[0]
                        
                        jobs.append({
                            'title': title_text,
                            'portal': portal,
                            'link': actual_link
                        })
            print(f"✅ Extracted {len(jobs)} active jobs from Google Search index.")
    except Exception as e:
        print(f"Error scraping google search fallback: {e}")
    return jobs

def send_email(jobs_list):
    if not EMAIL_PASS:
        print("❌ ERROR: EMAIL_PASS is missing in Github Secrets!")
        return

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    msg['Subject'] = '🚀 Daily Gaming Job Matches (LinkedIn, Naukri, Indeed)'
    
    # Format jobs list into text
    formatted_jobs = []
    for i, job in enumerate(jobs_list, 1):
        formatted_jobs.append(f"{i}. 🎯 **Role:** {job['title']}\n📌 **Platform:** {job['portal']}\n🔗 **Link:** {job['link']}\n")
        
    email_content = (
        "Bhai, ye rahi teri daily custom gaming jobs report (New + Active older jobs):\n\n"
        + "\n---------------------------\n\n".join(formatted_jobs)
        + "\n\n💡 Pro Tip: Short notice period (30 days) highlight karke turant direct apply and DM parallelly kar dena!"
    )
    msg.set_content(email_content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("✅ SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    # Get fresh RSS jobs
    all_jobs = fetch_fresh_jobs()
    
    # If we don't have enough fresh jobs, fetch older/active indexed jobs
    if len(all_jobs) < 5:
        older_jobs = fetch_older_jobs_from_google()
        # Merge without duplicates based on link
        seen_links = set([j['link'] for j in all_jobs])
        for job in older_jobs:
            if job['link'] not in seen_links:
                all_jobs.append(job)
                seen_links.add(job['link'])
                
    # Final check: limit to top 5 matches
    final_list = all_jobs[:5]
    
    if final_list:
        send_email(final_list)
    else:
        print("No jobs found in RSS or Search backup.")
