import requests

GROUP_ID="120363418411119627@g.us"
URL = "https://7103.api.greenapi.com/waInstance7103153214/sendMessage/8e6bb3a6bb66445194b48989ddc67873149f227f436e4cd480"
HEADERS = {
    'Content-Type': 'application/json'
}

def send_wa(text): 
    payload = {
        "chatId": GROUP_ID,
        "message": text,
        "linkPreview": True
    }
    response = requests.post(URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")