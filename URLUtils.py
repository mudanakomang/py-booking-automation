
import requests

apiUrl="https://cleanuri.com/api/v1/shorten"

def shorten_url(url):
    response = requests.post(apiUrl, data={"url": url})
    return response.json()['result_url']
