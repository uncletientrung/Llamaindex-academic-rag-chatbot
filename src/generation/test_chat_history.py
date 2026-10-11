from src.generation.mock_retriever import mock_retrieve
from src.generation.generation import generate_answer

from src.generation.citation import build_citations

from src.generation.chat_history import (
    add_user_message,
    add_assistant_message,
    print_chat_history,
)


# ============================================================
# CHAT HISTORY
# ============================================================

history = []


# ============================================================
# TURN 1
# ============================================================

question = "Điều kiện để được nhận học bổng là gì?"

selected_label = "Quy định học bổng"


# 1. Lưu câu hỏi user
add_user_message(
    history=history,
    content=question,
)


# 2. Retrieval
nodes = mock_retrieve(
    query=question,
    label=selected_label,
)


# 3. Generation
response = generate_answer(
    question=question,
    nodes=nodes,
)


# 4. Nếu Generation thành công
if response is not None:

    answer = str(response)

    citations = build_citations(
        response.source_nodes
    )

    # 5. Lưu answer + citations
    add_assistant_message(
        history=history,
        content=answer,
        citations=citations,
    )

# ============================================================
# TURN 2
# ============================================================

question = "Sinh viên bị kỷ luật có được xét học bổng không?"


# 1. Lưu câu hỏi user
add_user_message(
    history=history,
    content=question,
)


# 2. Retrieval
nodes = mock_retrieve(
    query=question,
    label=selected_label,
)


# 3. Generation
response = generate_answer(
    question=question,
    nodes=nodes,
)


# 4. Citation + lưu history
if response is not None:

    answer = str(response)

    citations = build_citations(
        response.source_nodes
    )

    add_assistant_message(
        history=history,
        content=answer,
        citations=citations,
    )
# ============================================================
# DEBUG HISTORY
# ============================================================

print_chat_history(history)
#python -m src.generation.test_chat_history dung code nay kiem tra history