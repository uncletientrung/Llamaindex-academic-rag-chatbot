from llama_index.llms.ollama import Ollama

from src.generation.prompts import REWRITE_PROMPT
from src.generation.chat_history import format_history_for_rewrite


llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0,
)


def rewrite_question(
    question: str,
    history: list[dict],
) -> str:
    """
    Viết lại câu hỏi hiện tại thành câu hỏi độc lập
    dựa trên lịch sử hội thoại.
    """

    # Không có history thì không cần rewrite
    if not history:
        return question

    history_text = format_history_for_rewrite(
        history=history,
    )

    prompt = REWRITE_PROMPT.format(
        chat_history=history_text,
        question=question,
    )

    print("\n" + "=" * 60)
    print("QUERY REWRITE")
    print("=" * 60)

    print("\nORIGINAL QUESTION:")
    print(question)

    print("\nCHAT HISTORY:")
    print(history_text)

    response = llm.complete(prompt)

    rewritten_question = response.text.strip()

    print("\nREWRITTEN QUESTION:")
    print(rewritten_question)

    print("=" * 60)

    return rewritten_question