from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    TreeIndex,
    KeywordTableIndex,
    PropertyGraphIndex
)
from src.ingestion.IngestionPipeline import get_processed_nodes
from src.ingestion.StorageContext import get_Storage_context

def create_all_indexes():
    nodes = get_processed_nodes()
    storage_context= get_Storage_context()
    vector_index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
    summary_index = SummaryIndex(nodes=nodes, storage_context=storage_context)
    tree_index = TreeIndex(nodes=nodes, storage_context=storage_context)
    keyword_index = KeywordTableIndex(nodes=nodes, storage_context=storage_context)
    graph_index = PropertyGraphIndex(nodes=nodes, storage_context=storage_context)
    storage_context.persist(persist_dir="./storage")
    return {
        "vector": vector_index,
        "summary": summary_index,
        "tree": tree_index,
        "keyword": keyword_index,
        "graph": graph_index
    }