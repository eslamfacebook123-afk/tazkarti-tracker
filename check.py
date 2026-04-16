import requests, smtplib, os, json, csv
from email.mime.text import MIMEText
from io import StringIO

API_URL = "https://www.tazkarti.com/data/matches-list-json.json"
SHEET_ID = "13bLNp-tCgntsuFh2y335KC677esRL47X0CGGl34uZNI"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_emails():
    r = requests.get(SHEET_URL, timeout=15)
    reader = csv.reader(StringIO(r.text))
    next(reader)  # skip header
    emails = [row[1] for row in reader if len(row) > 1 and "@" in row[1]]
    return list(set(emails))

def send_email(to, subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_FROM"]
    msg["To"] = to
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
        is_basket = "basket" in tournament or "hassan" in stadium

        if is_ahly and is_zamalek and is_basket:
            emails = get_emails()
            print(f"Found! Sending to {len(emails)} emails...")
            for email in emails:
                try:
                    send_email(
                        email,
                        "🎟️ تذاكر الأهلي vs الزمالك سلة نزلت!",
                        f"الماتش: {m['teamName1']} vs {m['teamName2']}\n"
                        f"التاريخ: {m.get('kickOffTime', '')}\n"
                        f"الاستاد: {m.get('stadiumName', '')}\n\n"
                        f"اشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
                    )
                    print(f"Sent to {email}")
                except Exception as e:
                    print(f"Failed {email}: {e}")
            return
    print("Not yet...")

check()
