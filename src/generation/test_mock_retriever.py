from src.generation.mock_retriever import mock_retrieve


# ============================================================
# TEST 1
# Chỉ tìm trong Quy định học bổng
# ============================================================

nodes = mock_retrieve(
    #query="Điều kiện để được nhận học bổng là gì?",
    query="Điểm rèn luyện để nhận học bổng là bao nhiêu?",
    label="Quy định học bổng",
)

print("\nKẾT QUẢ TEST:")
print(f"Tìm được {len(nodes)} nodes.")

#chay code python -m src.generation.test_mock_retriever de test