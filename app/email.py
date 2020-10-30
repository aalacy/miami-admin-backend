from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Attachment, FileContent, FileName, FileType, Disposition, ContentId
from datetime import datetime
import pdb
from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

SENDGRID_API_KEY='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'
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

def send_email_with_attachment_general(to_email='ideveloper003@gmail.com', from_email='info@scrapers.com', data="", html=''):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='Finished scraper for sysco. check the attachment',
        html_content=html
    )
    for item in data:
        attachment = Attachment()
        attachment.file_content = FileContent(item['content'])
        attachment.file_type = FileType('application/csv')
        attachment.file_name = FileName(item['file_name'])
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId('Content ID')
        message.add_attachment(attachment)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e)