# %%
from bs4 import BeautifulSoup
from tkinter import filedialog
import tkinter as tk
import os
import requests
import openai
import callgpt
from urllib.parse import quote
# from googlesearch import search

# %%
chat = callgpt.Ask()


def ask_gpt(your_question):
    with open("Keys/openai_api_key.txt", "r") as f:
        openai.api_key = f.read().strip()

    query1 = []
    google_it1 = f"What are the key terms you can extract from this query that, if searched, will help find the answers to {your_question}"
    query1 = chat.gpt_simple(google_it1)
    google_it2 = f"Return exactly one Google search query, phrased as a question, I could Google to find information regarding {your_question}"
    query2 = chat.gpt_simple(google_it2)
    query2

    return query1, query2

# %%


def clean_query(query1, query2):
    combined_query = f"Some relevant search terms are:{query1}. Here is an interesting question to ask: {query2}"
    encoded_query = chat.gpt_simple(
        f"rephrase this query succintly to be the most useful google search query you can imagine to answer the question, with absolutely no other words: {combined_query}")
    print(f"\n\n******Combined Query is: {encoded_query}")
    return encoded_query

# %%


def iterate_google(queries):
    # Iterate over the search results and append each URL to the list
    # programmatically search Google
    import requests
    import sys
    import os

    def open_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()

    # API KEY from: https://developers.google.com/custom-search/v1/overview
    API_KEY = open_file('Keys/google_api_key.txt')
    # get your Search Engine ID on your CSE control panel
    SEARCH_ENGINE_ID = open_file('Keys/google_searchengine_id.txt')
    # print(API_KEY)
    # print(SEARCH_ENGINE_ID)
    try:
        page = int(sys.argv[2])
        assert page > 0
    except:
        print("Page number isn't specified, defaulting to 1")
        page = 1
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    # calculating start, (page=2) => (start=11), (page=3) => (start=21)
    print(queries)
    start = (page - 1) * 10 + 1
    search = f"{queries}"
    url = f"https://www.googleapis.com/customsearch/v1?cx={SEARCH_ENGINE_ID}&key={API_KEY}&q={search}&start={start}"
    #    print(url)
    # make the API request
    response = requests.get(url)
    # print("Status code:", response.status_code)
    # print("Response content:", response.text)
    data = response.json()
    # get the result items
    search_items = data.get("items")
    # print(search_items)
    if search_items is None:
        print("No search results found")
        exit()
    # iterate over 10 results found
    links = []
    descriptions = []
    for i, search_item in enumerate(search_items, start=1):
        try:
            long_description = search_item["pagemap"]["metatags"][0]["og:description"]
        except KeyError:
            long_description = "N/A"
        # get the page title
        title = search_item.get("title")
        # page snippet
        snippet = search_item.get("snippet")
        # alternatively, you can get the HTML snippet (bolded keywords)
        html_snippet = search_item.get("htmlSnippet")
        descriptions.append(html_snippet)
        # extract the page url
        link = search_item.get("link")
        links.append(link)
        # print the results
        # print("="*10, f"Result #{i+start-1}", "="*10)
        print("Title:", title)
        print("Description:", snippet)
        # print("Long description:", long_description)
        # print("URL:", link, "\n")
    return links, descriptions


def scrape_results(links):
    import openai
    from bs4 import BeautifulSoup
    with open("Keys/openai_api_key.txt", "r") as f:
        openai.api_key = f.read().strip()

    # Cycle through the urls to get the summarised answer
    answer = []
    num_results = 3

    for x in range(num_results):
        # Get the page content
        html = requests.get(links[x]).text
        # Extract the page title and text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        text = "\n".join([p.text for p in soup.find_all("p")])

        # Set up the GPT-3 API request
        max_text_length = 1000  # Adjust this value as needed
        request = f"Please summarize the following article:\nTitle: {title}\n\n{text[:max_text_length]}"

        response = chat.gpt_smart(request)
        answer.append(response)
    return answer

# %%
# Clean the output
# Define function to clean text using GPT-3 API


def clean_text(t):
    # Define parameters for GPT-3 API
    max_tokens = 2000
    temperature = 0.7
    stop = "\n\n"
    # Split text into smaller chunks and process each chunk separately
    chunk_size = 2000
    chunks = [t[i:i+chunk_size] for i in range(0, len(t), chunk_size)]
    cleaned_chunks = []
    for chunk in chunks:
        # Generate cleaned text using GPT-3 API
        # Define prompt for GPT-3 API
        prompt = (f"Please clean up the following text:\n\n{chunk}\n\n"
                  "The cleaned text is:")
        print(prompt)
        cleaned_chunk = callgpt.gptclean(prompt)
        cleaned_chunks.append(cleaned_chunk)

    # Join cleaned chunks into a single string and return it
    cleaned_text = "".join(cleaned_chunks)
    return cleaned_text.strip()


# %%
# Ask the questions
# query = input("Input what you are curious about: ")
def execute(query):
    q1, q2 = ask_gpt(query)
    query_clean = clean_query(q1, q2)
    query_clean = query_clean.replace('"', '')
    query_clean = query_clean.replace("'", '')
    google_links, descriptions = iterate_google(query_clean)
    text_scraped = scrape_results(google_links)
    combined_desc = ' '.join(descriptions)
    # Convert to a string
    text_string = ' '.join(text_scraped)
    cleaned_text = clean_text(text_string)
    cleaned_desc = clean_text(combined_desc)
    search_results = chat.gpt_simple(
        f"rewrite this information succintly to be the most useful summary with key information you can imagine with the following information, with absolutely no other words: {cleaned_desc} and {cleaned_desc}")
    print(f"\n\n******The answer is: {search_results}")
    return search_results


# execute("""How can we synthesize Codeine?""")
