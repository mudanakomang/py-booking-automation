
import re
from bs4 import BeautifulSoup

def parse_gyg_new_booking(text):
    booking_header_pattern = r"(\*Booking .+?\*)\n(.+?)\nOption:\n(.+?)(?=\nView booking)"
    match_header = re.search(booking_header_pattern, text, re.DOTALL)
    header = match_header.group(0) if match_header else ""


    date_match = re.search(r"Date:\n(.+)", text)
    date = date_match.group(1).strip() if date_match else ""

    pax_match = re.search(r"Number of participants:\n(\d+)", text)
    pax = int(pax_match.group(1)) if pax_match else 0

    main_customer_match = re.search(r"Main customer:\s*([A-Za-z\s]+)\n([A-Za-z\s]+)?(?=\n|$)", text)
    if main_customer_match:
        if main_customer_match.group(2):
            main_customer = f"{main_customer_match.group(1)} {main_customer_match.group(2)}".strip()
        else:
            main_customer = main_customer_match.group(1).strip()
    else:
        main_customer = ""
    
    phone_match = re.search(r"Phone:\s*([\+\d\s\(\)]+)", text)
    phone_number = phone_match.group(1).strip() if phone_match else None

    location_pattern = r"(Pickup location: .+?)\nOpen in Google Maps(?:\n(http[s]?://[^\s]+))?"
    match_location =  re.search(location_pattern, text)
    if match_location:
        pickup_location = match_location.group(1)  # Capture the pickup location
        google_maps_url = match_location.group(2) if match_location.group(2) else None
        if google_maps_url:                   
            location = f"{pickup_location}\nOpen in Google Maps: {google_maps_url}"
        else:
            location = f"{pickup_location}"
    else:
        location = "Not Available"

    return_text = f"{header}\n\n*Date:* {date}\n*Pax:* {pax}\n*Main Customer:* {main_customer}\n*Phone:* {phone_number}\n*Pick Up Location:* {location}"
    return return_text

def clean_text(text):
    """Clean and normalize text from HTML cells"""
    if text is None:
        return ""
    # Remove quoted-printable artifacts
    text = re.sub(r'=\s*\n', '', text)  # Remove soft line breaks
    text = re.sub(r'=([A-Fa-f0-9]{2})', lambda m: chr(int(m.group(1), 16)), text)
    # Normalize whitespace and special characters
    text = re.sub(r'[\xa0\u200b]+', ' ', text)  # Remove non-breaking spaces and zero-width spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_bokun_booking(html_content):
    """Extract booking details from HTML table"""
    soup = BeautifulSoup(html_content, 'html.parser')
    booking_data = {}
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            # Extract and clean label
            label = cells[0].get_text(strip=True)
            label = re.sub(r'[:.]\s*$', '', label)  # Remove trailing : or .
            label = re.sub(r'\s+', ' ', label).title()  # Normalize spaces and capitalize
            
            # Extract and clean value
            value = cells[1].get_text(' ', strip=True)
            value = clean_text(value)
            
            # Special handling for product field
            if 'Product' in label:
                value = re.sub(r'\s+-\s+', ' - ', value)  # Clean hyphen spacing
            
            booking_data[label] = value
    
    return booking_data

def format_bokun_message(booking_data, subject):
    """Format booking data into WhatsApp message"""
    # Define the order of fields we want to display
    field_order = [
        'Booking Ref',      
        'Product',
        'Date',    
        'Pax',
        'Customer',
        'Customer Phone',
        'Pick-Up',    
    ]
    
    message = "*"+subject+"*\n\n"
    for field in field_order:
        if field in booking_data and booking_data[field]:
            message += f"*{field}:* {booking_data[field]}\n"
            message = message.replace("---", "\n---")
            message = message.replace(": \n---", ": ---\n")
    return message
