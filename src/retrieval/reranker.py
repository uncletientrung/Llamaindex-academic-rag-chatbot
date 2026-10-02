from llama_index.core.postprocessor import SentenceTransformerRerank

def create_reranker(nodes):
    reranker = SentenceTransformerRerank(
        model="AITeamVN/Vietnamese_Reranker",
        top_k=1,
    )
    reranked_nodes = reranker.postprocess_nodes(nodes)
    return reranked_nodes