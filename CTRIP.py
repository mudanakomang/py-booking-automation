import imaplib
import email
import quopri
from bs4 import BeautifulSoup
from GoogleServices import delete_event, insert_spreadsheet, create_calendar, remove_spreadsheet_row, update_event_description
import re
from WAUtils import send_wa

IMAP_SERVER = 'imap.hostinger.com'
EMAIL_USER = 'info@balisnaptrip.com'
EMAIL_PASS = 'BStrip@123'
IMAP_PORT = 993

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)
mail.select("INBOX")

def new_booking():
    print("Proccess New Booking Trip.com")
    status, messages = mail.search(None, '(UNSEEN FROM "TNT_noreply@trip.com" SUBJECT "New booking reminder")')

    if status != "OK":
        print("❌ Gagal mencari email.")
        return
   
    email_ids = messages[0].split()

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            print(f"❌ Gagal mengambil email ID {email_id}")
            continue

        for response_part in msg_data:
            subject = ''
            body = ''
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject= msg['Subject']
                body_bytes = msg.get_payload(decode=True)
                content_transfer_encoding = msg.get("Content-Transfer-Encoding")
                if content_transfer_encoding == "quoted-printable":
                    body = quopri.decodestring(body_bytes).decode("utf-8", errors="ignore")
                else:
                    body = body_bytes.decode("utf-8", errors="ignore")

            soup = BeautifulSoup(body, "html.parser")
            container = soup.find('div', class_='container03')
            if container:
                table = container.find('table')
                if table:
                    rows = table.find_all('tr')[1:]
                    
                    data = []
                    for row in rows:
                        cols = [td.get_text(strip=True) for td in row.find_all('td')]
                        if cols:
                            data.append(cols)
                    product = data[0][1]
                    resource = '\n※ '.join(field.strip() for field in data[0][0].split('|'))
                    matchRef =  re.search(r'no\.(\d+)', subject)
                    if matchRef:
                        bookingRef = matchRef.group(1)
                    else:
                        bookingRef = ''
                    bookingDate = data[0][2].strip()
                    activityDate = data[0][3].strip()
                    customer = data[0][4].strip()
                    pax = data[0][5].strip()

                    newSubject = f"Trip.com Booking Reminder - {bookingRef}"
                    text = "*" + newSubject + "*" + "\n"
                    text += "Product: " + product + "\n"
                    text += "Booking Ref: " + bookingRef + "\n"
                    text += "Resource: " + resource + "\n"
                    text += "Booking Date: " + bookingDate + "\n"
                    text += "Activity Date: " + activityDate + "\n"
                    text += "Customer: " + customer + "\n"
                    text += "Pax: " + pax + "\n"

                    calendarBody = "Product: " + product + "\n"
                    calendarBody += "Booking Ref: " + bookingRef + "\n"
                    calendarBody += "Resource: " + resource + "\n"
                    calendarBody += "Booking Date: " + bookingDate + "\n"
                    calendarBody += "Activity Date: " + activityDate + "\n"
                    calendarBody += "Customer: " + customer + "\n"
                    calendarBody += "Pax: " + pax + "\n"

                    spreadSheetData = [product, bookingRef, activityDate, pax, customer, "-"]
                    insert_spreadsheet(spreadSheetData)
                    create_calendar(subject, activityDate, calendarBody)
                    if subject.strip() != "":
                        send_wa(text)