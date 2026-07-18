import io
import os
import re
import smtplib
import time
from email.message import EmailMessage
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pypdf
import requests

# Ensure NLTK resources are available
try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)  # Solves the 'punkt_tab' missing resource error
except Exception as e:
    print(f"Warning: NLTK download failed: {e}")

# ==================== CONFIGURATION ====================
EMAIL_USER = "mkraone7@gmail.com"
EMAIL_PASS = os.environ.get("EMAIL_PASS")
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")
RAPID_API_HOST = "jsearch.p.rapidapi.com"

# Google Drive Resume Link
RESUME_DRIVE_LINK = (
    "https://drive.google.com/file/d/11Q-UeRQCE0Dnnz9Ls0ETwODE3i73BD1l/view?usp=sharing"
)

if not RAPID_API_KEY:
    RAPID_API_KEY = "9843fb14a4msh2c482644769cbbap103b70jsn2c29598596ec"

# 1. Locations & Roles
LOCATIONS = [
    "NCR",
    "New Delhi",
    "Delhi",
    "Remote",
    "Noida",
    "Gurgaon",
    "Gurugram",
    "Greater Noida",
    "Ghaziabad",
]

ROLE_GROUPS = [
    "Data Analyst OR Data Engineer OR Data Scientist",
    "Senior Data Analyst OR Senior Data Engineer OR Senior Data Scientist",
    "Lead Data Analyst OR Lead Data Engineer OR Lead Data Scientist",
    "Game Data Analyst OR Game Data Scientist OR Game Data Engineer",
    "Analyst OR Engineer OR Scientist",
]

# NLTK Stopwords + Generic corporate words to clean the dataset
CUSTOM_EXCLUDE = {
    "using",
    "worked",
    "responsible",
    "responsibilities",
    "project",
    "projects",
    "experience",
    "skills",
    "year",
    "years",
    "work",
    "working",
    "role",
    "roles",
    "team",
    "support",
    "development",
    "design",
    "created",
    "implemented",
}
STOPWORDS_SET = set(stopwords.words("english")).union(CUSTOM_EXCLUDE)
# =======================================================


def extract_resume_keywords_dynamically(drive_url):
    """Google Drive link se Resume download karke key nouns aur technical terms extract karega"""
    print("Reading resume from Google Drive...")
    unique_resume_words = set()
    try:
        # Convert Drive sharing link to Direct Download link
        file_id = drive_url.split("/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        response = requests.get(download_url, timeout=15)
        if response.status_code == 200:
            pdf_file = io.BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_file)
            resume_text = "".join(
                [page.extract_text() or "" for page in reader.pages]
            ).lower()

            # Tokenize using NLTK
            words = word_tokenize(
                re.sub(r"[^\w\+\#\s\-]", " ", resume_text)
            )  # Clean punctuation

            for word in words:
                cleaned_word = word.strip("-").strip()
                if (
                    cleaned_word
                    and len(cleaned_word) > 2
                    and not cleaned_word.isdigit()
                ):
                    if cleaned_word not in STOPWORDS_SET:
                        unique_resume_words.add(cleaned_word)

            print(
                f"✅ Dynamically Extracted {len(unique_resume_words)} unique keywords from your Resume!"
            )
            print(f"Sample Keywords: {list(unique_resume_words)[:15]}...")
            return unique_resume_words
        else:
            print(
                f"⚠️ Resume download failed (Status {response.status_code})."
            )
    except Exception as e:
        print(f"⚠️ Error parsing resume: {e}.")

    # Fallback if drive is down
    return {"python", "sql", "data", "analyst", "tableau", "powerbi"}


def fetch_jobs(resume_keywords):
    url = f"https://{RAPID_API_HOST}/search-v2"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": RAPID_API_HOST}

    all_jobs = []

    for location in LOCATIONS:
        for group in ROLE_GROUPS:
            query = f"({group}) in {location}"
            querystring = {"query": query, "page": "1", "num_pages": "1"}

            print(f"Searching: '{query}'...")
            try:
                response = requests.get(
                    url, headers=headers, params=querystring, timeout=15
                )

                if response.status_code == 200:
                    response_json = response.json()
                    data_payload = response_json.get("data", {})

                    jobs_list = (
                        data_payload.get("jobs", [])
                        if isinstance(data_payload, dict)
                        else data_payload
                        if isinstance(data_payload, list)
                        else []
                    )
                    print(f"-> Found {len(jobs_list)} raw jobs.")

                    for job in jobs_list:
                        if isinstance(job, dict):
                            desc = str(job.get("job_description", "")).lower()
                            title = str(job.get("job_title", "")).lower()

                            # 1. Experience Filter (5+ years check)
                            exp_match = ("5" in desc or "five" in desc) and (
                                "year" in desc or "yr" in desc
                            )

                            if exp_match:
                                # 2. NLTK Tokenization for Job Description to match words accurately
                                jd_words = set(
                                    word_tokenize(
                                        re.sub(
                                            r"[^\w\+\#\s\-]",
                                            " ",
                                            desc + " " + title,
                                        )
                                    )
                                )

                                matched_skills = [
                                    word
                                    for word in resume_keywords
                                    if word in jd_words
                                ]
                                match_score = len(matched_skills)

                                # Relevance check: minimum 5 matching keywords
                                if match_score >= 5:
                                    job["matched_skills_list"] = matched_skills
                                    job["match_score"] = match_score
                                    all_jobs.append(job)
                else:
                    print(
                        f"API Error: Status {response.status_code} - {response.text}"
                    )

                time.sleep(1)
            except Exception as e:
                print(f"Request failed for query '{query}': {e}")

    # Remove duplicates
    unique_jobs = {job["job_id"]: job for job in all_jobs if "job_id" in job}

    # Sort: Highest match score first
    final_list = sorted(
        unique_jobs.values(),
        key=lambda x: x.get("match_score", 0),
        reverse=True,
    )
    print(f"\nTotal Matching Jobs Found: {len(final_list)}")
    return final_list


def generate_email_html(jobs_list):
    """Generates a clean HTML layout with Match Score and Matched Resume Keywords."""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px;">
            🎯 Highly Relevant Jobs (Matched to your actual Resume Experience)
        </h2>
        <p>Bhai, tere resume ke content aur experience se match karti hui jobs niche hain:</p>
    """

    for i, job in enumerate(jobs_list[:15], 1):
        title = job.get("job_title", "N/A")
        company = job.get("employer_name", "N/A")
        location = (
            f"{job.get('job_city', '')}, {job.get('job_country', '')}".strip(
                ", "
            )
            or "N/A"
        )
        link = job.get("job_apply_link", "#")
        matched_skills = job.get("matched_skills_list", [])
        match_score = job.get("match_score", 0)

        # Salary processing
        min_sal = job.get("job_min_salary")
        max_sal = job.get("job_max_salary")
        currency = job.get("job_salary_currency") or ""
        period = (job.get("job_salary_period") or "").lower()

        salary_str = (
            f"{currency} {min_sal:,} - {max_sal:,} per {period}"
            if min_sal and max_sal
            else f"From {currency} {min_sal:,} per {period}"
            if min_sal
            else "Not Specified"
        )

        # Highlight top 10 matched keywords
        skills_html = "".join(
            [
                f'<span style="background-color: #e8f0fe; color: #1a73e8; padding: 2px 6px; margin-right: 5px; margin-bottom: 5px; display: inline-block; border-radius: 3px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{skill}</span>'
                for skill in matched_skills[:10]
            ]
        )
        if len(matched_skills) > 10:
            skills_html += f'<span style="color: #5f6368; font-size: 11px;">+{len(matched_skills)-10} more matches</span>'

        desc = job.get("job_description") or "No description available."
        short_desc = desc[:200] + "..." if len(desc) > 200 else desc

        html += f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid #1a73e8; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
            <div style="float: right; background-color: #e6f4ea; color: #137333; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                Relevance Score: {match_score} matches
            </div>
            <h3 style="margin: 0 0 5px 0; color: #202124;">{i}. {title}</h3>
            <p style="margin: 5px 0; font-weight: bold; color: #5f6368;">{company} | 📍 {location}</p>
            <p style="margin: 5px 0;">💰 <b>Salary:</b> {salary_str}</p>
            <div style="margin: 8px 0; line-height: 1.8;">
                <b>Matched with your Resume:</b><br>{skills_html if skills_html else 'General Match'}
            </div>
            <p style="margin: 10px 0; font-size: 14px; color: #555;">📝 <b>Summary:</b> {short_desc}</p>
            <a href="{link}" target="_blank" style="display: inline-block; background-color: #1a73e8; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-top: 5px;">Apply Now</a>
        </div>
        """

    html += """
        <p style="font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; margin-top: 30px;">
            Automated Job Bot powered by JSearch API, NLTK & Resume Skill Matcher.
        </p>
    </body>
    </html>
    """
    return html


def send_email(jobs_list):
    if not EMAIL_PASS:
        print(
            "❌ Error: EMAIL_PASS environment variable is not set. Cannot send email."
        )
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = "mkraone7@gmail.com"

    if not jobs_list:
        msg["Subject"] = "🟢 Job Bot: No New Matches Today"
        msg.set_content(
            "Hi, no fresh job matches matching your resume and 5+ years of experience were found today."
        )
    else:
        msg["Subject"] = (
            f"🚀 {len(jobs_list)} New Highly Relevant Jobs Found!"
        )
        msg.add_alternative(generate_email_html(jobs_list), subtype="html")

    try:
        print("Sending matched jobs email notification...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"✅ Email successfully sent with {len(jobs_list)} jobs!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


if __name__ == "__main__":
    resume_keywords = extract_resume_keywords_dynamically(RESUME_DRIVE_LINK)
    jobs = fetch_jobs(resume_keywords)
    send_email(jobs)
