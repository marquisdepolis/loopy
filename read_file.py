# %%
import pptx
import os
from llama_index import download_loader
from pathlib import Path


def read_file(fp):
    ext = os.path.splitext(fp)[-1].lower()
    if ext == ".pptx":
        print fp, "is a pptx!"
        PptxReader = download_loader("PptxReader")
        loader = PptxReader()
        document = loader.load_data(file=Path(fp))
        # Load the PowerPoint presentation
        ppt = pptx.Presentation(document)
        # Loop through each slide and extract the text
        for slide in ppt.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    texts.append(shape.text)
    elif ext == ".pdf":
        print fp, "is a pdf file!"
        # PDFReader = download_loader("PDFReader")
        # loader = PDFReader()
        # documents = loader.load_data(file=Path(fp))
        reader = PyPDF2.PdfReader(fp)
        texts = []
        # Loop through each page and extract the text
        number_of_pages = len(reader.pages)
        for x in range(number_of_pages):
            page = reader.pages[x]
            text = page.extract_text()
            texts.append(text)
    elif ext == ".html":
        print fp, "is an html file!"
        with open(fp, 'r') as f:
            reader = BeautifulSoup(f, 'html.parser')
            texts = reader.get_text()
    elif filename.endswith('.epub'):
        texts = []
        book = epub.read_epub(fp)
        chapters = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        for chapter in chapters:
            soup = BeautifulSoup(chapter.get_content(), 'html.parser')
            text = soup.get_text()
            texts.append(text)
    else:
        print fp, "is an unknown file format."

    return texts
