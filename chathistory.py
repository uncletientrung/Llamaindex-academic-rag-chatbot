from pathlib import Path
from uuid import uuid4

from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.llms import ChatMessage, MessageRole


class ChatHistoryStore:
    def __init__(self, path="storage/chat_store.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            self.chat_store = SimpleChatStore.from_persist_path(persist_path=str(self.path) )
        else:
            self.chat_store = SimpleChatStore()
            self._persist() # Nếu chưa có file thì tạo json chứa cấu trúc mà simpleChatStore đọc được

    def _persist(self):
        self.chat_store.persist(persist_path=str(self.path))

    def create_conversation(self) -> str:
        conversation_id = str(uuid4())
        self.chat_store.set_messages(conversation_id, [])
        self._persist()
        return conversation_id

    def get_conversations(self) -> list[dict]:
        conversations = []
        for conversation_id in self.chat_store.get_keys(): # Lấy danh sách id của chatstore
            messages = self.get_messages(conversation_id)

            first_user_message = ""
            for msg in messages:
                if msg.role == MessageRole.USER:
                    first_user_message = msg.content
                    break

            conversations.append({
                "conversation_id": conversation_id,
                "title": first_user_message[:60],
                "message_count": len(messages),
            })

        return conversations

    def get_messages(self, conversation_id: str):
        return self.chat_store.get_messages(conversation_id)

    def add_message(self, conversation_id: str, role: str, content: str,):
        if role not in ("user", "assistant"):
            raise ValueError("Role không hợp lệ")
        if role == "user":
            message_role = MessageRole.USER
        else:
            message_role = MessageRole.ASSISTANT
            
        message = ChatMessage(
            role=message_role,
            content=content,
        )
        self.chat_store.add_message(conversation_id, message)
        self._persist()

    def delete_conversation(self, conversation_id: str):
        self.chat_store.delete_messages(conversation_id)
        self._persist()