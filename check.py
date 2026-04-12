import requests, smtplib, os
from email.mime.text import MIMEText

URL = "https://tazkarti.com/ar/events?category=basketball"
KEYWORDS = ["أهلي", "زمالك", "ahly", "zamalek"]

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"]   = os.environ["EMAIL_TO"]
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["EMAIL_FROM"], os.environ["EMAIL_PASS"])
        s.send_message(msg)

def check():
    r = requests.get(URL, timeout=15,
        headers={"User-Agent": "Mozilla/5.0"})
    found = any(k in r.text for k in KEYWORDS)
    if found:
        send_email(
            "🎟️ تذاكر الأهلي vs الزمالك نزلت!",
            "اشتري دلوقتي:\nhttps://tazkarti.com/ar/events?category=basketball"
        )
        print("FOUND - email sent!")
    else:
        print("Not yet...")

check()
