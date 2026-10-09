



from src.retrieval.retriever import create_retriever
from src.ingestion.Index import create_all_indexes

vector_store_index = create_all_indexes['vector']
query_engine = vector_store_index.as_query_engine(similar_top_k = 5)

while True:

    question = input("\nBạn hỏi: ")

    if question.lower() in ["exit", "quit"]:
        break

    response = query_engine.query(question)

    print("\nTrả lời:")
    print(response)