import requests, smtplib, os, json
from email.mime.text import MIMEText

API_URL = "https://www.tazkarti.com/data/matches-list-json.json"
TEAM1 = "zamalek"
TEAM2 = "cr belouizdad"

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"]   = os.environ["EMAIL_TO"]
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["EMAIL_FROM"], os.environ["EMAIL_PASS"])
        s.send_message(msg)

def check():
    r = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    matches = json.loads(r.text)
    for m in matches:
        t1 = m.get("teamName1", "").lower()
        t2 = m.get("teamName2", "").lower()
        is_match = (TEAM1 in t1 or TEAM1 in t2) and (TEAM2 in t1 or TEAM2 in t2)
        if is_match:
            date = m.get("kickOffTime", "")
            stadium = m.get("stadiumName", "")
            send_email(
                "🎟️ تذاكر الزمالك vs CR Belouizdad نزلت!",
                f"الماتش: {m['teamName1']} vs {m['teamName2']}\nالتاريخ: {date}\nالاستاد: {stadium}\n\nاشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
            )
            print("FOUND - email sent!")
            return
    print("Not yet...")

check()
