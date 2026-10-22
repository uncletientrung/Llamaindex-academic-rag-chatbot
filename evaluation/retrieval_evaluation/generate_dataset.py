
import json
from pathlib import Path
from typing import Any

from llama_index.core import Settings
from llama_index.core.evaluation.dataset_generation import DatasetGenerator

from test import RAGService


DATASET_PATH = Path("evaluation/retrieval_evaluation/dataset.json")

# Số câu hỏi cần sinh cho mỗi node nguồn
NUM_QUESTIONS_PER_CHUNK = 1


def get_indexed_nodes(rag: RAGService) -> list[Any]: #Lấy các node đang có trong docstore của những index hiện tại
    nodes_by_id = {}

    for group_name, index in rag.indices.items():
        docstore = getattr(index, "docstore", None)
        if docstore is None:
            print(f"Bỏ qua index '{group_name}': không có docstore.")
            continue

        for node_id, node in docstore.docs.items():
            nodes_by_id[node_id] = node

    nodes = list(nodes_by_id.values())

    if not nodes:
        raise ValueError(
            "Không tìm thấy node trong các index. "
            "Hãy kiểm tra quá trình load/build index và storage."
        )

    print(f"Tổng số node: {len(nodes)}")
    print(f"Số nhóm tài liệu: {len(rag.indices)}")

    return nodes


def get_node_text(node: Any) -> str:
    """Lấy nội dung văn bản của node."""
    try:
        return node.get_content()
    except (AttributeError, TypeError):
        return str(getattr(node, "text", "") or "")


def generate_questions_for_node(node: Any, generator: DatasetGenerator) -> list[str]:
    """Sinh câu hỏi từ một node bằng DatasetGenerator."""
    questions = generator.generate_questions_from_nodes(num=1)
    return [q.strip() for q in questions if q and q.strip()]


def main() -> None:
    rag = RAGService()
    nodes = get_indexed_nodes(rag)

    llm = Settings.llm
    if llm is None:
        raise RuntimeError(
            "Settings.llm chưa được cấu hình. "
            "Hãy khởi tạo LLM trước khi sinh dataset."
        )

    queries: dict[str, str] = {}
    corpus: dict[str, str] = {}
    relevant_docs: dict[str, list[str]] = {}

    # Lưu corpus bằng chính ID của node trong index
    for node in nodes:
        node_id = str(node.node_id)
        text = get_node_text(node)

        if text.strip():
            corpus[node_id] = text

    if not corpus:
        raise ValueError("Không tìm thấy nội dung văn bản hợp lệ trong các node.")

    print(f"Số node trong corpus: {len(corpus)}")

    # Sinh câu hỏi riêng cho từng node để biết node nguồn của mỗi câu hỏi.
    for index, node in enumerate(nodes, start=1):
        node_id = str(node.node_id)
        source_text = get_node_text(node).strip()

        if not source_text or node_id not in corpus:
            continue

        print(f"[{index}/{len(nodes)}] Đang xử lý node {node_id}")

        # Mỗi generator chỉ nhận đúng một node nguồn.
        generator = DatasetGenerator(
            nodes=[node],
            llm=llm,
            num_questions_per_chunk=NUM_QUESTIONS_PER_CHUNK,
            show_progress=False,
        )

        try:
            generated_questions = generator.generate_questions_from_nodes(num=1)
        except Exception as exc:
            print(f"  Không sinh được câu hỏi: {exc}")
            continue

        for question in generated_questions:
            question = question.strip()

            if not question:
                continue

            # Dùng số thứ tự để tránh trùng key nếu câu hỏi bị lặp.
            query_id = str(len(queries))

            queries[query_id] = question
            relevant_docs[query_id] = [node_id]

    if not queries:
        raise RuntimeError(
            "Không sinh được câu hỏi nào. "
            "Hãy kiểm tra LLM, API key và nội dung node."
        )

    dataset = {
        "queries": queries,
        "corpus": corpus,
        "relevant_docs": relevant_docs,
    }

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

    with DATASET_PATH.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu dataset: {DATASET_PATH.resolve()}")
    print(f"Số câu hỏi: {len(queries)}")
    print(f"Số node trong corpus: {len(corpus)}")
    print(f"Số query có nhãn relevant: {len(relevant_docs)}")


if __name__ == "__main__":
    main()
