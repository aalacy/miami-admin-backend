from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from datetime import datetime
import pdb

SENDGRID_API_KEY = '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'
sg = SendGridAPIClient(SENDGRID_API_KEY)

def send_simple_email(text, title='Report about the scraper', to_email='ideveloper003@protonmail.com'):
    msg_body = '<strong>{} at {}</strong>'.format(text,  datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = Mail(
        from_email='no-reply@scraper.tech',
        to_emails=[to_email, 'ideveloper003@gmail.com'],
        subject=title,
        html_content=msg_body)
    try:
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(str(e.body))