import os
import requests
import smtplib
from email.message import EmailMessage

# Configuration (Loads from system environment variables)
EMAIL_USER = "mkraone7@gmail.com"
EMAIL_PASS = os.environ.get('EMAIL_PASS')
RAPID_API_KEY = os.environ.get('RAPID_API_KEY')
RAPID_API_HOST = "jsearch.p.rapidapi.com"

# Fallback for local testing if environment variables are not set in your IDE yet
if not RAPID_API_KEY:
    RAPID_API_KEY = "9843fb14a4msh2c482644769cbbap103b70jsn2c29598596ec"

def fetch_jobs():
    # Updated to the correct working /search-v2 endpoint
    url = f"https://{RAPID_API_HOST}/search-v2"
    
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }
    
    # You can uncomment or add more roles to this list as needed
    role_groups = [
        "Data Analyst in India",
        # "Data Engineer in India",
        # "Data Scientist in India"
    ]
    
    all_jobs = []
    
    for group in role_groups:
        querystring = {
            "query": group,
            "page": "1",
            "num_pages": "1"
        }
        
        print(f"Fetching jobs for query: '{group}'...")
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"Found {len(data)} raw jobs for this query.")
                
                for job in data:
                    # Filter logic: Looking for "5" and "year" or "yrs" in description
                    desc = str(job.get('job_description', '')).lower()
                    if ("5" in desc or "five" in desc) and ("year" in desc or "yr" in desc):
                        all_jobs.append(job)
            else:
                print(f"API Error for group '{group}': Status Code {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed for group '{group}': {e}")
            
    # Remove duplicate jobs based on unique job_id
    unique_jobs = {job['job_id']: job for job in all_jobs}.values()
    final_jobs_list = list(unique_jobs)
    print(f"Filtering complete. Total matching jobs found (5+ Years Exp): {len(final_jobs_list)}")
    return final_jobs_list

def send_email(jobs_list):
    # Ensure password exists before trying to send email
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
        content = "Hi, here are today's fresh job matches requiring 5+ years of experience:\n\n"
        
        for i, job in enumerate(jobs_list[:10], 1): # Top 10 jobs
            content += f"{i}. {job.get('job_title')}\n"
            content += f"   Company: {job.get('employer_name')}\n"
            content += f"   Location: {job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}\n"
            content += f"   Apply Link: {job.get('job_apply_link')}\n\n"
            
        msg.set_content(content)
    
    try:
        print("Sending email notification...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"✅ Email successfully sent with {len(jobs_list)} jobs!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
