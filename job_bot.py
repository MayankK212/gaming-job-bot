import requests

RAPID_API_KEY = '9843fb14a4msh2c482644769cbbap103b70jsn2c29598596ec'
RAPID_API_HOST = 'jsearch.p.rapidapi.com'

def search_jobs(query):
    """Step 1: Search for jobs and return a list of job IDs and Titles"""
    # IMPORTANT: Replace '/search' with the EXACT URL you see in RapidAPI dashboard
    url = "https://jsearch.p.rapidapi.com/search" 
    
    querystring = {"query": query, "page": "1", "num_pages": "1"}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Search Error: {response.status_code} - {response.text}")
        return []

def get_job_details(job_id):
    """Step 2: Get deep details for a specific job_id"""
    url = "https://jsearch.p.rapidapi.com/job-details"
    querystring = {"job_id": job_id, "country": "us"}
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json().get('data', [{}])[0] # Returns the first item in data list
    else:
        print(f"Details Error: {response.status_code}")
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    user_query = "Data Analyst in India"
    
    print(f"Searching for: {user_query}...\n")
    jobs_list = search_jobs(user_query)

    if jobs_list:
        print(f"Found {len(jobs_list)} jobs. Let's look at the first one in detail:\n")
        
        # Get the ID of the very first job found
        first_job_id = jobs_list[0]['job_id']
        print(f"Fetching details for Job ID: {first_job_id}\n")

        # Call the details endpoint
        details = get_job_details(first_job_id)

        if details:
            print("--- JOB DETAILS ---")
            print(f"TITLE:    {details.get('job_title')}")
            print(f"COMPANY:  {details.get('employer_name')}")
            print(f"LOCATION: {details.get('job_location')}")
            print(f"SALARY:   {details.get('job_min_salary')} - {details.get('job_max_salary')} {details.get('job_salary_period')}")
            print(f"DESCRIPTION (Preview): {details.get('job_description')[:200]}...")
        else:
            print("Could not fetch details.")
    else:
        print("No jobs found or Search API URL is incorrect.")

# import os
# import requests
# import smtplib
# from email.message import EmailMessage

# # Configuration
# EMAIL_USER = "mkraone7@gmail.com"
# EMAIL_PASS = os.environ.get('EMAIL_PASS')
# RAPID_API_KEY = os.environ.get('RAPID_API_KEY')

# # Constants
# # ROLES = '("Analyst" OR "Engineer" OR "Scientist" OR "Data Analyst" OR "Data Engineer" OR "Data Scientist" OR "Senior Data Analyst" OR "Senior Data Engineer" OR "Senior Data Scientist" OR "Lead Data Analyst" OR "Lead Data Engineer" OR "Lead Data Scientist" OR "Game Data Analyst" OR "Game Data Scientist" OR "Game Data Engineer")'
# # LOCATIONS = ["India"]
# # LOCATIONS = ["Gurgaon", "Delhi", "Noida", "Dubai", "Remote", "India"]

# def fetch_jobs():
#     url = "https://jsearch.p.rapidapi.com/search"
#     headers = {
#         "X-RapidAPI-Key": RAPID_API_KEY,
#         "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
#     }
    
#     # Roles ko 3-3 ke chote groups mein baanta (API Friendly)
#     role_groups = [
#         "Data Analyst"
#         # "Data Analyst OR Data Engineer OR Data Scientist",
#         # "Senior Data Analyst OR Senior Data Engineer OR Senior Data Scientist",
#         # "Lead Data Analyst OR Lead Data Engineer OR Lead Data Scientist",
#         # "Game Data Analyst OR Game Data Scientist OR Game Data Engineer"
#     ]
    
#     all_jobs = []
    
#     for group in role_groups:
#         querystring = {
#             "query": f"{group}",
#             "employment_types": "FULLTIME",
#             "remote_jobs_only": "false",
#             "num_pages": "1"
#         }
        
#         try:
#             response = requests.get(url, headers=headers, params=querystring, timeout=15)
#             if response.status_code == 200:
#                 data = response.json().get('data', [])
#                 for job in data:
#                     # Manual filter: Sirf wahi jobs jisme 5+ years ka mention ho
#                     desc = str(job.get('job_description', '')).lower()
#                     if "5" in desc and "year" in desc:
#                         all_jobs.append(job)
#             else:
#                 print(f"API Error for group {group}: {response.status_code}")
#         except Exception as e:
#             print(f"Request failed: {e}")
            
#     # Duplicates hatao
#     unique_jobs = {job['job_id']: job for job in all_jobs}.values()
#     return list(unique_jobs)

# def send_email(jobs_list):
#     msg = EmailMessage()
#     msg['From'] = EMAIL_USER
#     msg['To'] = 'mkraone7@gmail.com'
    
#     if not jobs_list:
#         msg['Subject'] = '🟢 Job Bot: No New Matches'
#         msg.set_content("Bhai, aaj koi fresh job match (5+ exp, Remote, Fulltime) nahi mili.")
#     else:
#         msg['Subject'] = f'🚀 {len(jobs_list)} New High-Level Jobs Found!'
#         content = "Bhai, ye rahi aaj ki fresh jobs (Experience 5+ years):\n\n"
#         for i, job in enumerate(jobs_list[:10], 1): # Top 10 jobs
#             content += f"{i}. {job.get('job_title')}\nCompany: {job.get('employer_name')}\nLocation: {job.get('job_city')}, {job.get('job_country')}\nLink: {job.get('job_apply_link')}\n\n"
#         msg.set_content(content)
    
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#         smtp.login(EMAIL_USER, EMAIL_PASS)
#         smtp.send_message(msg)
#     print(f"✅ Email sent with {len(jobs_list)} jobs!")

# if __name__ == "__main__":
#     jobs = fetch_jobs()
#     send_email(jobs)
