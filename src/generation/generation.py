from llama_index.core.schema import NodeWithScore
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.llms.ollama import Ollama
from src.generation.prompts import QA_PROMPT

# ============================================================
# LLM
# ============================================================

llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0,
)



#retriever se tra ve các list node tương thích, sau dó ta truyền vô hàm này để tạo context dưa
# LLM đọc
def build_context(nodes: list[NodeWithScore]) -> str:
    """
    Nhận các Node từ Retrieval và ghép nội dung của chúng
    thành context để sau này đưa cho LLM.
    """

    if not nodes:
        return ""

    context_parts = []

    for index, item in enumerate(nodes, start=1):
        node = item.node
        metadata = node.metadata

        file_name = metadata.get("file_name", "Không rõ")
        page = metadata.get("page_label", "Không rõ")
        label = metadata.get("label", "Không rõ")

        context_part = (
            f"[Nguồn {index}]\n"
            f"Loại tài liệu: {label}\n"
            f"Tệp: {file_name}\n"
            f"Trang: {page}\n"
            f"Nội dung: {node.text}"
        )

        context_parts.append(context_part)

    context = "\n\n".join(context_parts)

    return context


# ============================================================
# RESPONSE SYNTHESIZER
# ============================================================

response_synthesizer = get_response_synthesizer(
    llm=llm,
    text_qa_template=QA_PROMPT,
    response_mode="compact",
)


# ============================================================
# GENERATION
# ============================================================

def generate_answer(
    question: str,
    nodes: list[NodeWithScore],
):
    """
    Nhận:
        question: câu hỏi của user
        nodes: các Node Retrieval trả về

    Trả:
        Response của LlamaIndex.
    """

    print("\n" + "=" * 60)
    print("GENERATION")
    print("=" * 60)

    print(f"Question: {question}")
    print(f"Number of source nodes: {len(nodes)}")

    # Không có Node nào thì không cần gọi LLM.
    if not nodes:
        print("Không có Node phù hợp.")

        return None

    # LlamaIndex thực hiện response synthesis.
    response = response_synthesizer.synthesize(
        query=question,
        nodes=nodes,
    )
#log answer
    print("\nANSWER:")
    print(str(response))

    print("=" * 60)

    return response