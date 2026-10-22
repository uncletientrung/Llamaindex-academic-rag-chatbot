from llama_index.core.evaluation import (FaithfulnessEvaluator, RelevancyEvaluator, CorrectnessEvaluator,ContextRelevancyEvaluator,SemanticSimilarityEvaluator)
from llama_index.core import Settings

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from constants import EMBEDDING_MODEL

llm = Ollama(model="qwen2.5:7b",request_timeout=120.0,)
embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

def build_evaluators():
    return {
        "faithfulness": FaithfulnessEvaluator(llm=llm),

        "answer_relevancy": RelevancyEvaluator(llm=llm),

        "context_relevancy": ContextRelevancyEvaluator(llm=llm),

        "correctness": CorrectnessEvaluator(llm=llm),

        "semantic_similarity": SemanticSimilarityEvaluator(
            embed_model=embed_model,
        ),
    }