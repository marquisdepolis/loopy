# main.py
from urllib.parse import urlparse
import scraper
import embedder
import indexer
import query_handler
import spacy
from dotenv import load_dotenv

load_dotenv()
MAX_CHUNK_SIZE = 2048


def process_url(url, visited, base_domain=None):
    if url in visited:
        return

    visited.add(url)
    print(f"Processing {url}")

    text = scraper.scrape_data(url)
    if not text:
        return

    text_chunks = query_handler.split_text_into_chunks(text, MAX_CHUNK_SIZE)
    for chunk in text_chunks:
        embedding = embedder.embed_data(chunk, OPENAI_API_KEY)
        indexer.update_index(url, embedding, chunk)

    links = scraper.scrape_links(url)
    for link in links:
        # Only process URLs with HTTP or HTTPS schemes
        parsed_url = urlparse(link)
        if parsed_url.scheme in ["http", "https"]:
            # Check if the link has the same domain as the base domain or if the base domain is not set yet
            if base_domain is None:
                base_domain = parsed_url.netloc
            if parsed_url.netloc == base_domain:
                process_url(link, visited, base_domain)


def scrape():
    while True:
        action = input(
            "Enter 'url' to add a URL, 'query' to ask a question, or 'exit' to quit: ").lower()
        if action == 'url':
            url = input("Enter the URL to scrape and index: ")
            process_url(url, visited=set())  # Add visited parameter
            print("URL processed and indexed.")
        elif action == 'query':
            query = input("Enter your query: ")
            answer = query_handler.answer_query(query, OPENAI_API_KEY)
            print(f"Answer: {answer}")
        elif action == 'exit':
            break
        else:
            print("Invalid action. Please try again.")


if __name__ == "__main__":
    scrape()
