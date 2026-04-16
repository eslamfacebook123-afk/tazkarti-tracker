import requests, smtplib, os, json, csv
from email.mime.text import MIMEText
from io import StringIO
from pathlib import Path

API_URL = "https://www.tazkarti.com/data/matches-list-json.json"
SHEET_ID = "13bLNp-tCgntsuFh2y335KC677esRL47X0CGGl34uZNI"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SENT_FILE = "sent_matches.txt"  # ← بيحفظ الماتشات اللي اتبعت عنها

def get_sent_matches():
    """اقرأ الماتشات اللي اتبعت عنها قبل كده"""
    if not Path(SENT_FILE).exists():
        return set()
    with open(SENT_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def mark_as_sent(match_id):
    """احفظ إن الماتش ده اتبعت عنه"""
    with open(SENT_FILE, "a") as f:
        f.write(str(match_id) + "\n")

def get_emails():
    r = requests.get(SHEET_URL, timeout=15)
    reader = csv.reader(StringIO(r.text))
    next(reader)
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
    sent_matches = get_sent_matches()

    for m in matches:
        match_id = str(m.get("matchId", ""))
        
        # ✅ تشيك: التذاكر موجودة؟
        has_tickets = m.get("matchHasBookedTickets", False)
        if not has_tickets:
            print(f"Match {match_id}: no tickets yet, skipping")
            continue

        # ✅ تشيك: اتبعت عن الماتش ده قبل كده؟
        if match_id in sent_matches:
            print(f"Match {match_id}: already notified, skipping")
            continue

        t1 = m.get("teamName1", "").lower()
        t2 = m.get("teamName2", "").lower()
        t1ar = m.get("teamNameAr1", "") or ""
        t2ar = m.get("teamNameAr2", "") or ""
        stadium = m.get("stadiumName", "").lower()
        tournament = m.get("tournament", {}).get("nameEn", "").lower()

        is_ittihad = (
            "alithad" in t1 or "alithad" in t2 or
            "ittihad" in t1 or "ittihad" in t2 or
            "الاتحاد" in t1ar or "الاتحاد" in t2ar
        )
        is_telecom = (
            "telecom" in t1 or "telecom" in t2 or
            "تليكوم" in t1ar or "تليكوم" in t2ar or
            "المصرية للاتصالات" in t1ar or "المصرية للاتصالات" in t2ar
        )
        is_basket = "basket" in tournament or "hassan" in stadium

        if (is_ittihad or is_telecom) and is_basket:
            team1_name = m.get("teamNameAr1") or m.get("teamName1", "")
            team2_name = m.get("teamNameAr2") or m.get("teamName2", "")
            match_date = m.get("kickOffTime", "")

            emails = get_emails()
            print(f"✅ Found match {match_id}! Sending to {len(emails)} emails...")

            success_count = 0
            for email in emails:
                try:
                    send_email(
                        email,
                        "🎟️ تذاكر ماتش سلة نزلت!",
                        f"الماتش: {team1_name} vs {team2_name}\n"
                        f"التاريخ: {match_date}\n"
                        f"الاستاد: {m.get('stadiumName', '')}\n\n"
                        f"اشتري دلوقتي:\nhttps://tazkarti.com/#/matches"
                    )
                    print(f"✅ Sent to {email}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ Failed {email}: {e}")

            # ✅ احفظ إن الماتش ده اتبعت عنه (حتى لو في فشل جزئي)
            if success_count > 0:
                mark_as_sent(match_id)
                print(f"Marked match {match_id} as sent")
            return

    print("No matching tickets found yet...")

check()
