import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email_report(to_email, report_text, filename="report.txt"):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["Subject"] = "Your AI Resume Analyzer Report"
    msg["From"] = sender_email
    msg["To"] = to_email

    body = MIMEText("Hello,\n\nPlease find your resume analysis report attached.\n\nBest regards,\nTalentIQ Analyzer", "plain")
    msg.attach(body)

    attachment = MIMEApplication(report_text.encode('utf-8'), Name=filename)
    attachment['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(attachment)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print(f"Email sent to {to_email} with attachment {filename}")