from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import settings

def email_sender(message: str, subject: str):

    msg = MIMEMultipart()  # create message object instance

    password = settings.PASSWORD_EMAIL_BOT  # setup the parameters of the message
    msg['From'] = settings.EMAIL_BOT
    msg['To'] = settings.EMAIL_ADMIN
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))  # add in the message body
    server = smtplib.SMTP('smtp.gmail.com: 587')  #create server
    server.starttls()
    server.login(msg['From'], password)  # Login Credentials for sending the mail
    server.sendmail(msg['From'], msg['To'], msg.as_string())  # send the message via the server.
    server.quit()

if __name__ == '__main__':
    email_sender('message "test"!','Subject test')