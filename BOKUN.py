import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
from TextUtils import parse_bokun_booking, format_bokun_message
from DateUtils import extract_date
from WAUtils import send_wa
from GoogleServices import create_calendar, insert_spreadsheet
from TableUtils import bokun_table_to_row


IMAP_SERVER = 'imap.hostinger.com'
EMAIL_USER = 'info@balisnaptrip.com'
EMAIL_PASS = 'BStrip@123'
IMAP_PORT = 993
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)
mail.select("INBOX")


def new_booking():
    print("Proccess New Booking")
    global subject
    search_query = '(UNSEEN SUBJECT "New booking:" FROM "no-reply@bokun.io")'
    status, messages = mail.search(None, search_query)

    if status != 'OK' or not messages[0]:
        mail.logout()
        return
    
    email_ids = messages[0].split()
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status != 'OK':
            continue
    
    for response_part in msg_data:
            if not isinstance(response_part, tuple):
                continue

            msg = email.message_from_bytes(response_part[1])
            subject = decode_header(msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            subject = re.sub(r'\s+', ' ', subject.strip())

            # Get email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        body_bytes = part.get_payload(decode=True)
                        body = body_bytes.decode('utf-8', errors='ignore')
                        break
            else:
                body_bytes = msg.get_payload(decode=True)
                body = body_bytes.decode('utf-8', errors='ignore')

            # Find the booking table
            soup = BeautifulSoup(body, 'html.parser')
            booking_table = soup.find('table')
            
            if booking_table:
                booking_data = parse_bokun_booking(str(booking_table))
                    
                # Format WhatsApp message
                message = format_bokun_message(booking_data, subject)                
                send_wa(message)
                date = extract_date(message)
                create_calendar(subject, date, message)
                table_row = bokun_table_to_row(booking_data)
                insert_spreadsheet(table_row)
                # Mark as read
                mail.store(email_id, '+FLAGS', '\\Seen')
            else:
                print("No booking table found in email")
