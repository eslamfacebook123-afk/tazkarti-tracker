import requests, smtplib, os
from email.mime.text import MIMEText

API_URL = "https://tazkarti.com/#/matches"
KEYWORDS = ["Al Ahly", "Pharco FC", "أهلي", "زمالك"]

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"]   = os.environ["EMAIL_TO"]
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["EMAIL_FROM"], os.environ["EMAIL_PASS"])
        s.send_message(msg)

def check():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(API_URL, headers=headers, timeout=15)
    print("Status:", r.status_code)
    print("Response preview:", r.text[:500])
    found = any(k in r.text for k in KEYWORDS)
    if found:
        send_email(
            "🎟️ تذاكر الأهلي vs الزمالك نزلت!",
            "اشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
        )
        print("FOUND - email sent!")
    else:
        print("Not yet...")

check()
