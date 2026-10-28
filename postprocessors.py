from constants import (SIMILARITY_CUTOFF, RERANK_TOP_N, RERANKER_MODEL)
from llama_index.core.postprocessor import SimilarityPostprocessor, SentenceTransformerRerank
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle

class NodePostprocessorFactory:
    def __init__(self, similarity_cutoff: float = SIMILARITY_CUTOFF):
        self.similarity_cutoff = similarity_cutoff
        self.rerank_top_n = RERANK_TOP_N

        self.reranker = SentenceTransformerRerank(
            model= RERANKER_MODEL,
            top_n=self.rerank_top_n,
        )

    def build(self) -> list:
        return [
            DebugNodePostprocessor(),
            SimilarityPostprocessor(
                similarity_cutoff=self.similarity_cutoff
            ),
            self.reranker,
            DebugNodePostprocessor()
        ]


class DebugNodePostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self,
        nodes: list[NodeWithScore],
        query_bundle: QueryBundle = None,
    ) -> list[NodeWithScore]:

        print("\n========== NODES SAU POSTPROCESSOR ==========")
        print(f"Số lượng node: {len(nodes)}")

        for i, item in enumerate(nodes, start=1):
            print(f"\n--- Node {i} ---")
            print(f"Node ID: {item.node.node_id}")
            print(f"Score: {item.score}")
            # print(f"Metadata: {item.node.metadata}")
            print(f"Text:\n{item.node.get_content()}")

        print("==============================================\n")

        return nodes