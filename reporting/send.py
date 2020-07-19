import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")  
password = os.getenv("PASSWORD_EMAIL")
smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")

message = MIMEMultipart("alternative")
message["Subject"] = "Ellie Card Report Sunday 19th July"
message["From"] = sender_email
message["To"] = receiver_email

html = """\
<html>
  <body>
  <h1> Ellie did great today! </h1>
  </body>
</html>
"""

message.attach(MIMEText(html, "html"))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )
