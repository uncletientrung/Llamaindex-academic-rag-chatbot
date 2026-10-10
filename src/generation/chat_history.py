def add_user_message(
    history: list[dict],
    content: str,
) -> None:
    """
    Thêm câu hỏi của user vào lịch sử chat.
    """

    history.append(
        {
            "role": "user",
            "content": content,
        }
    )


def add_assistant_message(
    history: list[dict],
    content: str,
    citations: list[dict] | None = None,
) -> None:
    """
    Thêm câu trả lời của assistant vào lịch sử chat.

    citations được lưu cùng câu trả lời để sau này
    có thể render lại đúng nguồn của từng message.
    """

    history.append(
        {
            "role": "assistant",
            "content": content,
            "citations": citations or [],
        }
    )


def print_chat_history(
    history: list[dict],
) -> None:
    """
    In toàn bộ lịch sử chat ra terminal để debug.
    """

    print("\n")
    print("=" * 60)
    print("CHAT HISTORY")
    print("=" * 60)

    if not history:
        print("Chưa có lịch sử chat.")
        print("=" * 60)
        return

    for index, message in enumerate(history, start=1):

        role = message.get("role")
        content = message.get("content", "")

        print(f"\nMESSAGE {index}")

        if role == "user":
            print("USER:")
            print(content)

        elif role == "assistant":
            print("ASSISTANT:")
            print(content)

            citations = message.get("citations", [])

            if citations:

                print("\nSOURCES:")

                for citation in citations:

                    file_name = citation.get(
                        "file_name",
                        "Không rõ tài liệu",
                    )

                    page = citation.get(
                        "page",
                        "Không rõ",
                    )

                    score = citation.get("score")

                    print(
                        f"- {file_name} "
                        f"(Trang {page})"
                    )

                    if score is not None:
                        print(
                            f"  Score: {score:.3f}"
                        )

    print("\n" + "=" * 60)

#ham chuyen toan bo history cho llm doc
def format_history_for_rewrite(
    history: list[dict],
    max_messages: int = 6,
) -> str:
    """
    Chuyển lịch sử chat thành text để dùng cho bước
    contextualize/rewrite câu hỏi.

    Chỉ lấy một số message gần nhất để tránh history
    quá dài.
    """

    if not history:
        return "Không có lịch sử hội thoại."

    recent_history = history[-max_messages:]

    history_parts = []

    for message in recent_history:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":
            history_parts.append(
                f"Người dùng: {content}"
            )

        elif role == "assistant":
            history_parts.append(
                f"Trợ lý: {content}"
            )

    return "\n".join(history_parts)