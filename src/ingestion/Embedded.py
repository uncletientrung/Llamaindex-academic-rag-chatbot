from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_embedded_model():
    embed_model = HuggingFaceEmbedding(
        model_name="AITeamVN/Vietnamese_Embedding",
        embed_batch_size=32
    )
    return embed_model