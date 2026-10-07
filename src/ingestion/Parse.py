import os
from llama_index.core import SimpleDirectoryReader
def create_Parse():
    if os.path.exists("./data"):
        normal_docs = SimpleDirectoryReader("./data").load_data()
    return normal_docs
