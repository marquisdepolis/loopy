# main.py
import scraper
import embedder
import indexer
import query_handler
import spacy

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

OPENAI_API_KEY = open_file("openai_api_key.txt")

def process_url(url):
    text = scraper.scrape_data(url)
    text_chunks = query_handler.split_text_into_chunks(text, 2048)  # Adjust the max_chunk_size as needed

    for chunk in text_chunks:
        embedding = embedder.embed_data(chunk, OPENAI_API_KEY)
        indexer.update_index(url, embedding, chunk)

def main():
    while True:
        action = input(
            "Enter 'url' to add a URL, 'query' to ask a question, or 'exit' to quit: ").lower()
        if action == 'url':
            url = input("Enter the URL to scrape and index: ")
            process_url(url)
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
    main()
