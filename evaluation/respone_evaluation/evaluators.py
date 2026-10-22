from llama_index.core.evaluation import (FaithfulnessEvaluator, RelevancyEvaluator, CorrectnessEvaluator,ContextRelevancyEvaluator,SemanticSimilarityEvaluator)
from llama_index.core import Settings

def build_evaluators():
    return {
        "faithfulness": FaithfulnessEvaluator(llm=Settings.llm),
        "relevancy": RelevancyEvaluator(llm=Settings.llm),
        "correctness": CorrectnessEvaluator(llm=Settings.llm),
        "context_relevancy": ContextRelevancyEvaluator(llm=Settings.llm),
        "semantic_similarity": SemanticSimilarityEvaluator(embed_model=Settings.embed_model),
    }