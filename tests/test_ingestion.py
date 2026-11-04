import ingestion
from llama_index.core import Settings
from ingestion import DocumentIngestionPipeline


def test_get_nodes_uses_a_fresh_llm_for_each_run(monkeypatch):
    created_llms = []
    title_extractors = []

    class FakeLLM:
        def __init__(self, **kwargs):
            created_llms.append(self)

    class FakeTitleExtractor:
        def __init__(self, llm, **kwargs):
            title_extractors.append(llm)

    class FakeIngestionPipeline:
        def __init__(self, transformations):
            pass

        def run(self, documents):
            return []

    class FakeConfiguredLLM:
        metadata = type("Metadata", (), {"model_name": "test-model"})()
        base_url = "http://localhost:11434"
        temperature = 0.7
        context_window = -1
        request_timeout = 120.0

    monkeypatch.setattr(ingestion, "Ollama", FakeLLM)
    monkeypatch.setattr(ingestion, "SentenceSplitter", lambda **kwargs: object())
    monkeypatch.setattr(ingestion, "TitleExtractor", FakeTitleExtractor)
    monkeypatch.setattr(ingestion, "KeywordExtractor", lambda **kwargs: object())
    monkeypatch.setattr(ingestion, "IngestionPipeline", FakeIngestionPipeline)
    monkeypatch.setattr(Settings, "_llm", FakeConfiguredLLM())
    monkeypatch.setattr(Settings, "_embed_model", object())

    pipeline = DocumentIngestionPipeline.__new__(DocumentIngestionPipeline)
    pipeline.get_nodes([], folder_name="group")
    pipeline.get_nodes([], folder_name="group")

    assert len(created_llms) == 2
    assert title_extractors == created_llms
    assert title_extractors[0] is not title_extractors[1]