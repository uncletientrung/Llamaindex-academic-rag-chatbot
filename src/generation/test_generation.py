from src.generation.mock_retriever import mock_retrieve
from src.generation.generation import build_context
from src.generation.generation import generate_answer
from src.generation.citation import (
    build_citations,
    print_citations,
)
# ============================================================
# 1. Giả lập câu hỏi của user
# ============================================================

question = "Một học kỳ được đăng ký tối đa bao nhiêu tín chỉ?"

selected_label = "Quy định đăng ký môn"


# ============================================================
# 2. Retrieval
# ============================================================

nodes = mock_retrieve(
    query=question,
    label=selected_label,
)
# 3. generation
response = generate_answer(
    question=question,
    nodes=nodes,
)
# ============================================================
# 4. CITATION
# ============================================================

if response is not None:

    citations = build_citations(
        response.source_nodes
    )

    print_citations(citations)
#5. ketqua
if response is not None:
    print("\n")
    print("=" * 60)
    print("CAU TRA LOI CUA MODEL THAT SU")
    print("=" * 60)

    print(str(response))
# ============================================================
# 3. Generation chuẩn bị context
# ============================================================

# context = build_context(nodes)


# ============================================================
# 4. Log để kiểm tra
# ============================================================

# print("\n")
# print("=" * 60)
# print("CONTEXT ĐƯA CHO LLM")
# print("=" * 60)

# print(context)

# print("=" * 60)
# python -m src.generation.test_generation