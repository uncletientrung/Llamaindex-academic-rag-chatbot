from src.generation.query_rewriter import rewrite_question

from src.generation.mock_retriever import mock_retrieve

from src.generation.generation import generate_answer

from src.generation.citation import build_citations

from src.generation.chat_history import (
    add_user_message,
    add_assistant_message,
    print_chat_history,
)


# ============================================================
# HISTORY
# Giả lập Turn 1 đã xảy ra
# ============================================================

history = [
    {
        "role": "user",
        "content": "Điều kiện để được nhận học bổng là gì?",
    },

    {
        "role": "assistant",
        "content": (
            "Sinh viên cần có điểm trung bình học kỳ "
            "từ 3.2 trở lên và điểm rèn luyện từ 80 điểm "
            "để được xét học bổng."
        ),
        "citations": [],
    },
]


# ============================================================
# TURN 2
# ============================================================

question = "Còn điểm rèn luyện thì sao?"

selected_label = "Quy định học bổng"


# ============================================================
# 1. REWRITE
#
# QUAN TRỌNG:
# history lúc này CHƯA chứa question mới.
# ============================================================

rewritten_question = rewrite_question(
    question=question,
    history=history,
)


# ============================================================
# 2. LƯU CÂU GỐC CỦA USER
# ============================================================

add_user_message(
    history=history,
    content=question,
)


# ============================================================
# 3. RETRIEVAL
#
# Retrieval dùng câu ĐÃ REWRITE,
# không dùng câu mơ hồ ban đầu.
# ============================================================

nodes = mock_retrieve(
    query=rewritten_question,
    label=selected_label,
)


# ============================================================
# 4. GENERATION
#
# Generation cũng dùng câu đã được làm rõ.
# ============================================================

response = generate_answer(
    question=rewritten_question,
    nodes=nodes,
)


# ============================================================
# 5. CITATION + HISTORY
# ============================================================

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
# 6. DEBUG
# ============================================================

print_chat_history(history)

#chay test nay de coi hoi tiep coi llm hieu lich su khong 
# python -m src.generation.test_conversation