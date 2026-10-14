from pathlib import Path
from ingestion import DocumentIngestionPipeline
from constants import SIMILARITY_CUTOFF
from llama_index.core.postprocessor import SimilarityPostprocessor


class NodePostprocessorFactory:
    def __init__(self, similarity_cutoff: float = SIMILARITY_CUTOFF):
        self.similarity_cutoff = similarity_cutoff

    def build(self) -> list:
        return [
            SimilarityPostprocessor(
                similarity_cutoff=self.similarity_cutoff
            )
        ]

    