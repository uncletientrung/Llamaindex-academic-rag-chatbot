from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings


Settings.llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0,
)

def get_embedded_model():
    embed_model = HuggingFaceEmbedding(
        model_name="AITeamVN/Vietnamese_Embedding",
        embed_batch_size=32
    )
    return embed_model