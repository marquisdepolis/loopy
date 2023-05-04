# scraper.py
# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.text for p in soup.find_all('p')])
    return text


def scrape_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    return links


def get_links_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [urljoin(url, link["href"])
             for link in soup.find_all("a", href=True)]
    return links
