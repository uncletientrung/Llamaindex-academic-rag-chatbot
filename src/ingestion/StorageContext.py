import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.docstore import SimpleDocumentStore

from ingestion.Embedded import get_embedded_model
from ingestion.IngestionPipeline import get_processed_nodes
from llama_index.core import StorageContext, VectorStoreIndex


def get_Storage_context():
    embed_model = get_embedded_model()
    nodes = get_processed_nodes()
    client = QdrantClient(path="./qdrant_data")
    vector_store = QdrantVectorStore(collection_name="composable", client=client)
    if os.path.exists("./docstore.json"):
        docstore = SimpleDocumentStore.from_persist_path("./docstore.json")
    else:
        docstore = SimpleDocumentStore()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )
    storage_context.docstore.add_documents(nodes)
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model
    )
    storage_context.docstore.persist("./docstore.json")
