import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore

from llama_index.core import StorageContext


def get_Storage_context():
    client = QdrantClient(path="./qdrant_data")
    vector_store = QdrantVectorStore(collection_name="composable", client=client)
    if os.path.exists("./storage/docstore.json"):
        docstore = SimpleDocumentStore.from_persist_path("./storage/docstore.json")
    else:
        docstore = SimpleDocumentStore()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )
    return storage_context
