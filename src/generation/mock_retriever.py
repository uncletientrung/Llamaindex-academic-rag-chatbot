from llama_index.core.schema import TextNode, NodeWithScore

#moc gia lap retriver tra ve

MOCK_NODES = [

    # --------------------------------------------------------
    # LABEL: QUY ĐỊNH HỌC BỔNG
    # --------------------------------------------------------

    NodeWithScore(
        node=TextNode(
            text=(
                "Sinh viên có điểm trung bình học kỳ từ 3.2 trở lên "
                "được xem xét học bổng khuyến khích học tập."
            ),
            metadata={
                "file_name": "hoc_bong_2025.pdf",
                "page_label": "3",
                "label": "Quy định học bổng",
            },
        ),
        score=0.94,
    ),

    NodeWithScore(
        node=TextNode(
            text=(
                "Điểm rèn luyện của sinh viên phải đạt từ 80 điểm "
                "trở lên để đáp ứng điều kiện xét học bổng."
            ),
            metadata={
                "file_name": "hoc_bong_2026.pdf",
                "page_label": "5",
                "label": "Quy định học bổng",
            },
        ),
        score=0.89,
    ),

    NodeWithScore(
        node=TextNode(
            text=(
                "Sinh viên bị kỷ luật từ mức khiển trách trở lên "
                "trong học kỳ sẽ không thuộc diện xét học bổng "
                "khuyến khích học tập."
            ),
            metadata={
                "file_name": "hoc_bong_2026.pdf",
                "page_label": "6",
                "label": "Quy định học bổng",
            },
        ),
        score=0.82,
    ),

    # --------------------------------------------------------
    # LABEL: QUY ĐỊNH ĐĂNG KÝ MÔN
    # --------------------------------------------------------

    NodeWithScore(
        node=TextNode(
            text=(
                "Trong mỗi học kỳ, sinh viên đăng ký tối thiểu "
                "14 tín chỉ và tối đa 25 tín chỉ."
            ),
            metadata={
                "file_name": "dang_ky_mon.pdf",
                "page_label": "7",
                "label": "Quy định đăng ký môn",
            },
        ),
        score=0.95,
    ),

    NodeWithScore(
        node=TextNode(
            text=(
                "Sinh viên thực hiện đăng ký học phần trong thời gian "
                "do nhà trường công bố trên hệ thống đăng ký học phần."
            ),
            metadata={
                "file_name": "quy_che_tin_chi.pdf",
                "page_label": "10",
                "label": "Quy định đăng ký môn",
            },
        ),
        score=0.86,
    ),

    NodeWithScore(
        node=TextNode(
            text=(
                "Sinh viên được phép điều chỉnh hoặc hủy học phần "
                "đã đăng ký trong thời gian điều chỉnh đăng ký "
                "theo thông báo của nhà trường."
            ),
            metadata={
                "file_name": "hoc_vu_2026.pdf",
                "page_label": "12",
                "label": "Quy định đăng ký môn",
            },
        ),
        score=0.80,
    ),
]


# ============================================================
# MOCK RETRIEVER
# ============================================================

def mock_retrieve(
    query: str,
    label: str | None = None,
) -> list[NodeWithScore]:
    """
    Giả lập Retrieval.

    Sau này Retrieval thật chỉ cần có interface tương tự:

        retrieve(query, label) -> list[NodeWithScore]

    Generation sẽ không cần quan tâm dữ liệu được lấy
    từ Qdrant hay từ mock.
    """

    print("\n" + "=" * 60)
    print("MOCK RETRIEVAL")
    print("=" * 60)

    print(f"Question: {query}")
    print(f"Selected label: {label}")

    # Nếu không chọn label hoặc chọn "Tất cả"
    # thì cho phép lấy Node của mọi label.
    if label is None or label == "Tất cả":
        results = MOCK_NODES

    else:
        # Đây là mô phỏng metadata filtering.
        results = [
            item
            for item in MOCK_NODES
            if item.node.metadata.get("label") == label
        ]

    print(f"Number of nodes: {len(results)}")

    # Log các Node để kiểm tra
    for index, item in enumerate(results, start=1):

        metadata = item.node.metadata

        print(f"\n--- NODE {index} ---")
        print(f"Score : {item.score}")
        print(f"Label : {metadata.get('label')}")
        print(f"File  : {metadata.get('file_name')}")
        print(f"Page  : {metadata.get('page_label')}")
        print(f"Text  : {item.node.text}")

    print("=" * 60)

    return results