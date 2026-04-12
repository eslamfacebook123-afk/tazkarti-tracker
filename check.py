import requests, smtplib, os, json
from email.mime.text import MIMEText

API_URL = "https://www.tazkarti.com/data/matches-list-json.json"
TEAM1 = "al ahly"
TEAM2 = "zamalek"

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
        game = m.get("tournament", {}).get("nameEn", "").lower()
        is_ahly_zamalek = (TEAM1 in t1 or TEAM1 in t2) and (TEAM2 in t1 or TEAM2 in t2)
        is_basket = "basket" in game
        if is_ahly_zamalek and is_basket:
            date = m.get("kickOffTime", "")
            stadium = m.get("stadiumName", "")
            send_email(
                "🎟️ تذاكر الأهلي vs الزمالك سلة نزلت!",
                f"الماتش: {m['teamName1']} vs {m['teamName2']}\nالتاريخ: {date}\nالاستاد: {stadium}\n\nاشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
            )
            print("FOUND - email sent!")
            return
    print("Not yet - no Ahly vs Zamalek basketball match found")

check()
