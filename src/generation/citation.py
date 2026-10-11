from llama_index.core.schema import NodeWithScore


def build_citations(
    source_nodes: list[NodeWithScore],
) -> list[dict]:
    """
    Chuyển source_nodes của LlamaIndex thành dữ liệu citation
    dễ sử dụng cho UI và chat history.

    Mỗi citation gồm:
        - file_name
        - page
        - label
        - score
        - text
    """

    citations = []

    for index, item in enumerate(source_nodes, start=1):

        node = item.node
        metadata = node.metadata

        citation = {
            "index": index,

            "file_name": metadata.get(
                "file_name",
                "Không rõ tài liệu",
            ),

            "page": metadata.get(
                "page_label",
                "Không rõ",
            ),

            "label": metadata.get(
                "label",
                "Không rõ",
            ),

            "score": item.score,

            "text": node.text,
        }

        citations.append(citation)

    return citations
#ham in citantion ra
def print_citations(citations: list[dict]) -> None:
    """
    In citation ra terminal để debug.
    """

    print("\n")
    print("=" * 60)
    print("SOURCE CITATIONS")
    print("=" * 60)

    if not citations:
        print("Không có nguồn tham khảo.")
        print("=" * 60)
        return

    for citation in citations:

        print(f"\n[Nguồn {citation['index']}]")

        print(
            f"File  : {citation['file_name']}"
        )

        print(
            f"Page  : {citation['page']}"
        )

        print(
            f"Label : {citation['label']}"
        )

        score = citation["score"]

        if score is not None:
            print(f"Score : {score:.3f}")

        print(
            f"Text  : {citation['text']}"
        )

    print("\n" + "=" * 60)