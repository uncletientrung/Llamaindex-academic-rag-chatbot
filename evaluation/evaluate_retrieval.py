
import time
import statistics

from llama_index.core.schema import QueryBundle
from llama_index.core.postprocessor import SentenceTransformerRerank
from constants import RERANKER_MODEL


def benchmark_query(index, question, top_k=10):
    query_bundle = QueryBundle(query_str=question)

    # 1. Đo vector retrieval
    retriever = index.as_retriever(similarity_top_k=top_k)

    start = time.perf_counter()
    candidates = retriever.retrieve(query_bundle)
    retrieval_ms = (time.perf_counter() - start) * 1000

    # Baseline: lấy 3 kết quả đầu tiên theo vector score
    baseline_top3 = candidates[:3]

    # 2. Đo reranker trên đúng tập candidates
    reranker = SentenceTransformerRerank(
        model=RERANKER_MODEL,
        top_n=3,
    )

    start = time.perf_counter()
    reranked_top3 = reranker.postprocess_nodes(
        candidates,
        query_bundle=query_bundle,
    )
    rerank_ms = (time.perf_counter() - start) * 1000

    return {
        "baseline_nodes": baseline_top3,
        "reranked_nodes": reranked_top3,
        "retrieval_ms": retrieval_ms,
        "rerank_ms": rerank_ms,
        "baseline_total_ms": retrieval_ms,
        "reranked_total_ms": retrieval_ms + rerank_ms,
    }


def benchmark_dataset(index, questions):
    results = []

    for question in questions:
        result = benchmark_query(index, question)
        results.append(result)

    baseline_times = [
        r["baseline_total_ms"] for r in results
    ]
    reranked_times = [
        r["reranked_total_ms"] for r in results
    ]

    print("Số câu hỏi:", len(results))
    print(
        "Baseline latency trung bình:",
        round(statistics.mean(baseline_times), 2), "ms"
    )
    print(
        "Reranker latency trung bình:",
        round(statistics.mean(reranked_times), 2), "ms"
    )
    print(
        "Baseline median:",
        round(statistics.median(baseline_times), 2), "ms"
    )
    print(
        "Reranker median:",
        round(statistics.median(reranked_times), 2), "ms"
    )

    return results
