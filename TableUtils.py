import re

def gyg_text_to_row(text):

    lines = text.strip().split("\n")  # Pisahkan teks per baris
    tour = lines[1].strip() if len(lines) > 1 else None

    booking_ref_match = re.search(r"Reference number:\n(\w+)", text)
    booking_ref = booking_ref_match.group(1) if booking_ref_match else ""

    date_match = re.search(r"Date:\n(.+)", text)
    date = date_match.group(1).strip() if date_match else ""

    pax_match = re.search(r"Number of participants:\n(\d+)", text)
    pax = int(pax_match.group(1)) if pax_match else 0

    phone_match = re.search(r"Phone:\s*([\+\d\s\(\)]+)", text)
    phone_number = phone_match.group(1).strip() if phone_match else None

    main_customer_match = re.search(r"Main customer:\s*([A-Za-z\s]+)\n([A-Za-z\s]+)?(?=\n|$)", text)
    if main_customer_match:
        if main_customer_match.group(2):
            main_customer = f"{main_customer_match.group(1)} {main_customer_match.group(2)}".strip()
        else:
            main_customer = main_customer_match.group(1).strip()
    else:
        main_customer = ""

    return [tour, booking_ref, date, pax, main_customer, phone_number]

def bokun_table_to_row(booking_data):
    field_order = [
        'Product',
        'Booking Ref',
        'Date',
        'Pax',
        'Customer',
        'Customer Phone',
    ]
    
    row = []
    for field in field_order:
        value = booking_data.get(field, '')
        row.append(value.strip() if isinstance(value, str) else value)
    
    return row
