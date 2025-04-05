
from DateUtils import parse_date
from datetime import timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build


SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks', 'https://www.googleapis.com/auth/spreadsheets']
CALENDAR_ID = '0cdc37ddd3a3e8cf1367b54b4e13af8ebab707bb3d5c17365aecacbee8b3ef1d@group.calendar.google.com'
SPREADSHEET_ID = "1JakrE66Hvt30HqCBw6ElAWQVIfFdaCKksmBratNve3w"


def create_calendar(summary: str, date: str, desc=None):
    start_date = parse_date(date)
    end_date = start_date + timedelta(days=1)

    if not start_date or not end_date:
        return None
    
    event = {
        'summary': summary,
        'start': {
            'date': start_date.isoformat()
        },
        'end': {
            'date': end_date.isoformat()
        }
    }

    if desc:
        event['description'] = desc

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        
        created_event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event
        ).execute()
        return created_event
    
    except Exception as e:
        print(f"❌ Error creating event: {str(e)}")
        return None

def delete_event(keyword):
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)

    events_result  = service.events().list(
        calendarId=CALENDAR_ID,
        q=keyword,
        singleEvents=True,
        maxResults=1,       
    ).execute()

    events = events_result.get('items', [])
    target_summary = f"Booking - S497054 - {keyword}"

    # Cari 1 event pertama yang summary-nya exact match
    for event in events:
        summary = event.get('summary', '').strip()
        if summary == target_summary:
            print(f"🗑️ Menghapus event: {summary}")
            service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
            print("✅ Event berhasil dihapus.")
            return True

    print("❌ Tidak ditemukan event yang cocok.")
    return False
    
def insert_spreadsheet(data, sheet_name='Sheet1', start_row=2):    
    print(f"Data Received: {data}")  # Cek data yang diterima

    try:
        if data and all(item for item in data):  # Memastikan data tidak kosong atau None
            data = [data] if isinstance(data[0], str) else data

            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('sheets', 'v4', credentials=credentials)
            
            range_ = f'{sheet_name}!A{start_row}:G{start_row}'

            print(f"Range: {range_}")
            print(f"Data to append: {data}")  # Cek data yang akan dikirim

            result = service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": data}
            ).execute()

            print(f"{result.get('updates').get('updatedCells')} cells updated.")
        else:
            print("❌ No valid data to insert. Skipping append.")
            return None

    except Exception as e:
        print(f"❌ Error creating event: {str(e)}")
        return None
    
def remove_spreadsheet_row(keyword, sheet_name='Sheet1'):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name).execute()
    values = result.get('values', [])

    if not values:
        print("❌ Sheet kosong.")
        return
    
    row_index_to_delete = None
    for idx, row in enumerate(values):
        if len(row) > 1 and str(row[1]) == keyword:
            row_index_to_delete = idx + 1  # +1 karena Sheets pakai 1-based index
            break
    
    if row_index_to_delete:
        print(f"✅ Menghapus baris ke-{row_index_to_delete} yang mengandung '{keyword}'")

        # Hapus baris dengan batchUpdate
        request_body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": 0,  # Sheet ID, bukan nama. Ubah jika perlu.
                            "dimension": "ROWS",
                            "startIndex": row_index_to_delete - 1,  # 0-based
                            "endIndex": row_index_to_delete,
                        }
                    }
                }
            ]
        }

        sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request_body).execute()
    else:
        print(f"⚠️ Tidak ditemukan baris dengan keyword '{keyword}'")


def update_event_description(booking_ref, text):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)

    # Cari event berdasarkan booking_ref
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        q=booking_ref,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    # Ambil event yang summary-nya cocok exact (misalnya mengandung booking ref)
    matched_event = None
    for event in events:
        if booking_ref in event.get('summary', ''):
            matched_event = event
            break

    if not matched_event:
        print(f"⚠️ Event dengan booking_ref '{booking_ref}' tidak ditemukan.")
        return

    event_id = matched_event['id']
    current_description = matched_event.get('description', '')

    new_description = f"{current_description}\n\nUpdate:\n{text}"

    updated_event = {
        'description': new_description.strip()
    }

    # Update event
    service.events().patch(
        calendarId=CALENDAR_ID,
        eventId=event_id,
        body=updated_event
    ).execute()

    print(f"✅ Event '{booking_ref}' berhasil diupdate dengan pickup location.")
