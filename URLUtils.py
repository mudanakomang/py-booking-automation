
import pyshorteners

def shorten_url(url):
    s = pyshorteners.Shortener()
    short = s.tinyurl.short(url)
    return short
