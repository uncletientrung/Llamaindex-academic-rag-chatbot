
def create_retriever(index):
    return index.as_retriever(similarity_top_k=5)