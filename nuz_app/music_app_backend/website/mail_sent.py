from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from os import login_tty
import smtplib
from jinja2 import Template

# SMTP_SERVER_HOST= "smtp.gmail.com"
SMTP_local_HOST="localhost"
# SMTP_SERVER_PORT= 587
SMTP_local_PORT= 1025

# Sender Address to sender mail Id.
SENDER_ADDRESS = "music.developer@gmail.com"


def send_email(to_address, subject, message):
    msg=MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    msg.attach(MIMEText(message,"html"))
    
    
    # s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    k = smtplib.SMTP(host=SMTP_local_HOST, port=SMTP_local_PORT)
    # s.starttls()
    
    # s.login(SENDER_ADDRESS,SENDER_PASSWORD)
    k.login(SENDER_ADDRESS,"")

    # s.send_message(msg)
    k.send_message(msg)

    # s.quit()
    k.quit()


    return True 

    
def main():
   
    #Send the mail to check the function ios calling or not without error.
    send_email("sample@gmail.com", subject="Test mail", message = "hi")


if __name__=="__main__":
    main()
