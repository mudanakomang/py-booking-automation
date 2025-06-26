import imaplib
import email
import quopri
from bs4 import BeautifulSoup
import re
from GoogleServices import delete_event, insert_spreadsheet, create_calendar, remove_spreadsheet_row, update_event_description
from WAUtils import send_wa
# from URLUtils import shorten_url
from DateUtils import extract_date
from TableUtils import gyg_text_to_row
from TextUtils import parse_gyg_new_booking

IMAP_SERVER = 'imap.hostinger.com'
EMAIL_USER = 'admin@balisnaptrip.com'
EMAIL_PASS = '!BaliSnap24#'
IMAP_PORT = 993

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)
mail.select("INBOX")


def cancel_booking():
    print("Proccess Booking cancelation")
    status, messages = mail.search(None, '(UNSEEN SUBJECT "A booking has been canceled - S497054")')
    
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
                subject = msg['Subject']
                body_bytes = msg.get_payload(decode=True)
                content_transfer_encoding = msg.get("Content-Transfer-Encoding")

                if content_transfer_encoding == "quoted-printable":
                    body = quopri.decodestring(body_bytes).decode("utf-8", errors="ignore")
                else:
                    body = body_bytes.decode("utf-8", errors="ignore")

            start_text = "booking has been canceled."
            end_text = "Please remove this customer"

            start_pos = body.find(start_text) + len(start_text)
            end_pos = body.find(end_text)

            extracted_text = body[start_pos:end_pos].strip()
            soup = BeautifulSoup(extracted_text, 'html.parser')

            text = soup.get_text(separator="\n", strip=True)
            if subject.strip() != "":
                final_text = f"*{subject}*\n{text}"
                send_wa(final_text)

            booking_ref_match = re.search(r"Reference Number:\n(\w+)", text)
            booking_ref = booking_ref_match.group(1) if booking_ref_match else ""

            if booking_ref:
                delete_event(booking_ref)
                remove_spreadsheet_row(booking_ref)
            else:
                print("⚠️ Booking reference tidak ditemukan.")


def new_booking():
    print("Proccess New Booking")
    status, messages = mail.search(None, '(UNSEEN SUBJECT "Booking - S497054")')
    
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
                # Decode Subject
                subject= msg['Subject']
                body_bytes = msg.get_payload(decode=True)
                content_transfer_encoding = msg.get("Content-Transfer-Encoding")
                if content_transfer_encoding == "quoted-printable":
                    # Dekode dengan quopri jika menggunakan Quoted-Printable
                    body = quopri.decodestring(body_bytes).decode("utf-8", errors="ignore")
                else:
                    body = body_bytes.decode("utf-8", errors="ignore")

                soup = BeautifulSoup(body, 'html.parser')

                start_text = "Hi Supply Partner, great news! The following offer has been booked:"
                end_text = "Best regards,"

                # Find the start and end positions
                start_pos = body.find(start_text) + len(start_text)
                end_pos = body.find(end_text)

                # Extract the text between those positions
                extracted_text = body[start_pos:end_pos].strip()

                sp = BeautifulSoup(extracted_text, "html.parser")
                google_maps_link = sp.find('a', string='Open in Google Maps')

                cleaned = sp.get_text(separator="\n", strip=True)
                if google_maps_link and google_maps_link.has_attr('href'):
                    maps_url = google_maps_link['href']
                    cleaned += f"\n{maps_url}"

                text = "*" + subject + "*" + "\n"
                text += cleaned
                date = extract_date(text)

                table = gyg_text_to_row(text)
                parsed = parse_gyg_new_booking(text)
                insert_spreadsheet(table)
                create_calendar(subject, date, parsed)
                if subject.strip() != "":
                    send_wa(parsed)

def update_booking():
    print("Proccess Update Booking")
    status, messages = mail.search(None, '(UNSEEN SUBJECT "Booking detail change: - S497054")')
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
                # Decode Subject
                subject= msg['Subject']
                body_bytes = msg.get_payload(decode=True)
                content_transfer_encoding = msg.get("Content-Transfer-Encoding")
                if content_transfer_encoding == "quoted-printable":
                    # Dekode dengan quopri jika menggunakan Quoted-Printable
                    body = quopri.decodestring(body_bytes).decode("utf-8", errors="ignore")
                else:
                    body = body_bytes.decode("utf-8", errors="ignore")

                soup = BeautifulSoup(body, 'html.parser')

                start_text = "Hi PT. BALI SNAP TRIP"
                end_text = "Customer hasn't"

                # Find the start and end positions
                start_pos = body.find(start_text) + len(start_text)
                end_pos = body.find(end_text)

                # Extract the text between those positions
                extracted_text = body[start_pos:end_pos].strip()
                sp = BeautifulSoup(extracted_text, "html.parser")
                possible_links = sp.find_all('a', href=True)
                google_maps_link= ''
                for link in possible_links:
                    if link.get_text(strip=True) == "Open in Google Maps":
                        google_maps_link = link
                        break
                cleaned = sp.get_text(separator="\n", strip=True)
                if google_maps_link and google_maps_link.has_attr('href'):
                    maps_url = google_maps_link['href']
                    cleaned += f"\n{maps_url}"

                    text = "*" + subject + "*" + "\n"
                    text += cleaned
                booking_ref_match = re.search(r"We would like to inform you that the following booking has changed:\n(\w+)", text)
                booking_ref = booking_ref_match.group(1) if booking_ref_match else ""

                location_pattern = r"Pickup location:\n.*?\n.*?\n.*?(?:\n|$)"
                match_location =  re.search(location_pattern, text)
                if match_location:
                    location = match_location.group(0).strip() if match_location else ""
                if booking_ref and location:
                    update_event_description(booking_ref, location)
                if subject.strip() != "":
                    send_wa(text)                    