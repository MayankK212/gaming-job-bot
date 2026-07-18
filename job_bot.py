import os
import requests
import smtplib
import time
from email.message import EmailMessage

# ==================== CONFIGURATION ====================
EMAIL_USER = "mkraone7@gmail.com"
EMAIL_PASS = os.environ.get('EMAIL_PASS')
RAPID_API_KEY = os.environ.get('RAPID_API_KEY')
RAPID_API_HOST = "jsearch.p.rapidapi.com"

# Fallback for local testing
if not RAPID_API_KEY:
    RAPID_API_KEY = "9843fb14a4msh2c482644769cbbap103b70jsn2c29598596ec"

# 1. Easily add/remove locations here
LOCATIONS = ["India"]  # Example: ["India", "Dubai", "Remote"]

# 2. All 15 roles grouped into search-friendly query blocks
ROLE_GROUPS = [
    "Data Analyst OR Data Engineer OR Data Scientist",
    "Senior Data Analyst OR Senior Data Engineer OR Senior Data Scientist",
    "Lead Data Analyst OR Lead Data Engineer OR Lead Data Scientist",
    "Game Data Analyst OR Game Data Scientist OR Game Data Engineer",
    "Analyst OR Engineer OR Scientist"  # Broad fallback
]
# =======================================================

def fetch_jobs():
    url = f"https://{RAPID_API_HOST}/search-v2"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }
    
    all_jobs = []
    
    for location in LOCATIONS:
        for group in ROLE_GROUPS:
            # Combine role query with current location
            query = f"({group}) in {location}"
            
            querystring = {
                "query": query,
                "page": "1",
                "num_pages": "1"
            }
            
            print(f"Searching: '{query}'...")
            try:
                response = requests.get(url, headers=headers, params=querystring, timeout=15)
                
                if response.status_code == 200:
                    response_json = response.json()
                    data_payload = response_json.get('data', {})
                    
                    # Handle dict vs list dynamic payload
                    if isinstance(data_payload, dict):
                        jobs_list = data_payload.get('jobs', [])
                    elif isinstance(data_payload, list):
                        jobs_list = data_payload
                    else:
                        jobs_list = []
                    
                    print(f"-> Found {len(jobs_list)} raw jobs.")
                    
                    for job in jobs_list:
                        if isinstance(job, dict):
                            # Experience Filter: Must mention "5" and "year/yr" in description
                            desc = str(job.get('job_description', '')).lower()
                            if ("5" in desc or "five" in desc) and ("year" in desc or "yr" in desc):
                                all_jobs.append(job)
                else:
                    print(f"API Error: Status {response.status_code} - {response.text}")
                
                # Tiny pause to avoid hitting API rate limits too quickly
                time.sleep(1)
                
            except Exception as e:
                print(f"Request failed for query '{query}': {e}")
                
    # Remove duplicates safely using job_id
    unique_jobs = {}
    for job in all_jobs:
        if isinstance(job, dict) and 'job_id' in job:
            unique_jobs[job['job_id']] = job
            
    final_list = list(unique_jobs.values())
    print(f"\nTotal Matching Jobs Found (5+ Years Exp): {len(final_list)}")
    return final_list

def generate_email_html(jobs_list):
    """Generates a clean HTML layout for the email."""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px;">
            🚀 High-Level Job Matches (5+ Years Experience)
        </h2>
        <p>Bhai, here are your latest filtered job opportunities based on your keywords:</p>
    """
    
    for i, job in enumerate(jobs_list[:15], 1):  # Limits to top 15 jobs in the email
        title = job.get('job_title', 'N/A')
        company = job.get('employer_name', 'N/A')
        location = f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(", ") or "N/A"
        link = job.get('job_apply_link', '#')
        
        # 1. Salary processing
        min_sal = job.get('job_min_salary')
        max_sal = job.get('job_max_salary')
        currency = job.get('job_salary_currency', '')
        period = job.get('job_salary_period', '').lower()
        if min_sal and max_sal:
            salary_str = f"{currency} {min_sal:,} - {max_sal:,} per {period}"
        elif min_sal:
            salary_str = f"From {currency} {min_sal:,} per {period}"
        else:
            salary_str = "Not Specified"

        # 2. Extract Skills / Qualifications
        highlights = job.get('job_highlights', {})
        qualifications = highlights.get('Qualifications', []) if isinstance(highlights, dict) else []
        skills_str = ", ".join(qualifications[:4]) if qualifications else "Check description"

        # 3. Truncate Description
        desc = job.get('job_description', 'No description available.')
        short_desc = desc[:200] + "..." if len(desc) > 200 else desc

        # Append structured HTML block for this job
        html += f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid #34a853; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
            <h3 style="margin: 0 0 5px 0; color: #202124;">{i}. {title}</h3>
            <p style="margin: 5px 0; font-weight: bold; color: #5f6368;">{company} | 📍 {location}</p>
            <p style="margin: 5px 0;">💰 <b>Salary:</b> {salary_str}</p>
            <p style="margin: 5px 0;">🛠️ <b>Key Skills:</b> <span style="background-color: #e8f0fe; color: #1a73e8; padding: 2px 6px; border-radius: 3px; font-size: 13px;">{skills_str}</span></p>
            <p style="margin: 10px 0; font-size: 14px; color: #555;">📝 <b>Summary:</b> {short_desc}</p>
            <a href="{link}" target="_blank" style="display: inline-block; background-color: #1a73e8; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-top: 5px;">Apply Now</a>
        </div>
        """
        
    html += """
        <p style="font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; margin-top: 30px;">
            Automated Job Bot powered by JSearch API.
        </p>
    </body>
    </html>
    """
    return html

def send_email(jobs_list):
    if not EMAIL_PASS:
        print("❌ Error: EMAIL_PASS environment variable is not set. Cannot send email.")
        return

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = 'mkraone7@gmail.com'
    
    if not jobs_list:
        msg['Subject'] = '🟢 Job Bot: No New Matches'
        msg.set_content("Hi, no fresh job matches requiring 5+ years of experience were found today.")
    else:
        msg['Subject'] = f'🚀 {len(jobs_list)} New High-Level Jobs Found!'
        # Attach the beautiful HTML version
        msg.add_alternative(generate_email_html(jobs_list), subtype='html')
    
    try:
        print("Sending rich email notification...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"✅ Email successfully sent with {len(jobs_list)} jobs!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
