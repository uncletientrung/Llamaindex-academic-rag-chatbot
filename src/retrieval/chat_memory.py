from llama_index.core.memory import Memory
from llama_index.core.storage.chat_store import SimpleChatStore


def create_memory(session_id: str = "default"):
    chat_store = SimpleChatStore()
    memory = Memory.from_defaults(
        session_id=session_id,
        chat_store=chat_store,
        token_limit=4000,
    )
    return memory