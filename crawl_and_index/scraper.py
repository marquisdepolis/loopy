# scraper.py
import requests
from bs4 import BeautifulSoup


def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.text for p in soup.find_all('p')])
    return text
