
import re
from datetime import datetime
from typing import Any


def parse_date(date:str) ->  datetime | Any:
    try:
        date = date.strip()

        # Format all-day: "April 3, 2025"
        if re.match(r"^[A-Za-z]+\s\d{1,2},\s\d{4}$", date):
            return datetime.strptime(date, "%B %d, %Y").date()
        
        # Format all-day: "2025-04-03"
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return datetime.strptime(date, "%Y-%m-%d").date()
        
        # Format all-day: "31/03/2025"
        elif re.match(r"^\d{2}/\d{2}/\d{4}$", date):
            return datetime.strptime(date, "%d/%m/%Y").date()

         # Format dengan waktu: "April 3, 2025 8:00 AM"
        elif re.match(r"^[A-Za-z]+\s\d{1,2},\s\d{4}\s\d{1,2}:\d{2}\s[AP]M$", date):
            return datetime.strptime(date, "%B %d, %Y %I:%M %p").date()

        # Format pendek: "Mon 31.Mar '25"
        elif re.match(r"^[A-Za-z]{3}\s\d{2}\.[A-Za-z]{3}\s'\d{2}$", date):
            return datetime.strptime(date, "%a %d.%b '%y").date()
        
        # Format ISO dengan waktu: "2025-04-03 08:00"
        elif re.match(r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$", date):
            return datetime.strptime(date, "%Y-%m-%d %H:%M").date()
        
        else:
            raise ValueError("Format tanggal tidak dikenali")

    except Exception as e:
        print(f"Error parsing: {str(e)}")
        return None
    
def extract_date(text):
    """
    Mengekstrak string tanggal dari text dengan 2 format spesifik:
    1. 'April 3, 2025 8:00 AM'
    2. 'Mon 31.Mar '25'
    
    Returns:
        String tanggal yang pertama ditemukan atau None jika tidak ada
    """
    # Pattern untuk format pertama: April 3, 2025 8:00 AM
    pattern1 = r"(?:Date:\s*)?([A-Za-z]+\s\d{1,2},\s\d{4}\s\d{1,2}:\d{2}\s[AP]M)"
    match1 = re.search(pattern1, text, re.IGNORECASE)
    
    if match1:
        return match1.group(1)
    
    # Pattern untuk format kedua: Mon 31.Mar '25
    pattern2 = r"(?:Date:\s*)?([A-Za-z]{3}\s\d{2}\.[A-Za-z]{3}\s'\d{2})"
    match2 = re.search(pattern2, text)
    
    if match2:
        return match2.group(1)
    
    return None