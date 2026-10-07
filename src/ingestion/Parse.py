import os

from llama_index.core import SimpleDirectoryReader
from llama_parse import LlamaParse
def create_Parse():
    all_docs = []
    if os.path.exists("./data/normal"):
        normal_docs = SimpleDirectoryReader("./data/normal").load_data()
        all_docs.extend(normal_docs)

    if os.path.exists("./data/complex"):
        pdf_parser = LlamaParse(result_type="markdown")
        complex_docs = SimpleDirectoryReader(
            "./data/complex",
            file_extractor={".pdf": pdf_parser}
        ).load_data()
        all_docs.extend(complex_docs)

    return all_docs
