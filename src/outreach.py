import csv
import smtplib
from email.message import EmailMessage
import time
import os

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "vilouraai1@gmail.com"
# Use an App Password generated from your Google Account security settings
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "YOUR_APP_PASSWORD_HERE") 

LEADS_FILE = "enriched_leads.csv"  # Ensure your CSV has columns: name, email, company
DELAY_SECONDS = 15  # Delay between emails to avoid spam triggers

def send_outreach():
    if not os.path.exists(LEADS_FILE):
        print(f"Error: Could not find {LEADS_FILE}. Make sure your leads file is in the directory.")
        return

    print("Connecting to SMTP server...")
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("Connected and logged in successfully.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    with open(LEADS_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        count = 0

        for row in reader:
            name = row.get("name", "Creator")
            email = row.get("email")
            company = row.get("company", "your team")

            if not email:
                continue

            msg = EmailMessage()
            msg["Subject"] = f"Listing AI agents from {company} on VilouraAI"
            msg["From"] = SENDER_EMAIL
            msg["To"] = email
            
            # Tailored pitch for early AI agent creators
            msg.set_content(f"""Hi {name},

I've been following what you're building at {company} and love your work in the AI space. 

I'm reaching out from VilouraAI—we are launching a dedicated marketplace specifically built for developers and creators to showcase, distribute, and monetize autonomous AI agents. 

We are currently onboarding a select group of founding creators ahead of our public push. I'd love to get your agents listed early with zero platform commission for our beta cohort. 

Are you open to checking out a quick preview of how it works?

Best regards,
Jilsha Jose
Founder, VilouraAI
https://vilouraai.com
""")

            try:
                server.send_message(msg)
                count += 1
                print(f"[{count}] Successfully sent pitch to {email} ({name})")
            except Exception as e:
                print(f"Failed to send to {email}: {e}")

            # Respect rate limits
            time.sleep(DELAY_SECONDS)

    server.quit()
    print(f"Outreach complete! Total emails sent: {count}")

if __name__ == "__main__":
    send_outreach()
