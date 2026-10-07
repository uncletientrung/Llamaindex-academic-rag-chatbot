import os
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    KeywordExtractor,
)
from llama_index.extractors.entity import EntityExtractor

from ingestion.Embedded import get_embedded_model
from ingestion.Parse import create_Parse

def get_processed_nodes():
    embed_model = get_embedded_model()
    documents = create_Parse()
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=10),
            TitleExtractor(nodes=5),
            EntityExtractor(prediction_threshold=0.5),
            SummaryExtractor(summaries=["prev", "self"]),
            QuestionsAnsweredExtractor(questions=3),
            KeywordExtractor(keywords=10),
            embed_model
        ]
    )
    nodes = pipeline.run(documents=documents)
    return nodes

