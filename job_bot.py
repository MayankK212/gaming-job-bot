import requests
import os

RAPID_API_KEY = os.environ.get('RAPID_API_KEY') # Ya yahan seedha apni key likh do

def test_api():
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {"query": "Data Analyst in India"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text[:500]}") # Pehle 500 characters print karega

test_api()

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
