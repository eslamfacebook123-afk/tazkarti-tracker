import requests, smtplib, os, json
from email.mime.text import MIMEText

API_URL = "https://www.tazkarti.com/data/matches-list-json.json"

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
        t1ar = m.get("teamNameAr1", "") or ""
        t2ar = m.get("teamNameAr2", "") or ""
        stadium = m.get("stadiumName", "").lower()
        tournament = m.get("tournament", {}).get("nameEn", "").lower()

        is_ahly = "al ahly" in t1 or "al ahly" in t2 or "الأهلي" in t1ar or "الأهلي" in t2ar or "الاهلي" in t1ar or "الاهلي" in t2ar
        is_zamalek = "zamalek" in t1 or "zamalek" in t2 or "الزمالك" in t1ar or "الزمالك" in t2ar
        is_basket = "basket" in tournament
        is_hassan = "hassan moustafa" in stadium or "حسن مصطفى" in stadium or "hassan" in stadium

        if is_ahly and is_zamalek and (is_basket or is_hassan):
            date = m.get("kickOffTime", "")
            send_email(
                "🎟️ تذاكر الأهلي vs الزمالك سلة نزلت — اشتري دلوقتي!",
                f"الماتش: {m['teamName1']} vs {m['teamName2']}\n"
                f"التاريخ: {date}\n"
                f"الاستاد: {m.get('stadiumName', '')}\n\n"
                f"اشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
            )
            print("FOUND - email sent!")
            return
    print("Not yet...")

check()
