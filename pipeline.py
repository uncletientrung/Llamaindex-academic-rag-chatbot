from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    KeywordExtractor,
)
from llama_index.extractors.entity import EntityExtractor
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from src.promts.promt_extractor import (
    TITLE_NODE_PROMT,
    TITLE_COMBINE_PROMT,
    KEYWORD_PROMT,
)
from llama_index.core import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core.vector_stores import SimpleVectorStore


class Pipeline:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    def __init__(self, data_dir="data"):
        # =========================
        # 1. Cấu hình
        # =========================
        Settings.llm = Ollama(model="qwen2.5:3b",request_timeout=120.0,)
        Settings.embed_model = HuggingFaceEmbedding(model_name="AITeamVN/Vietnamese_Embedding")

        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.nodes = None
        self.storage_context = None

    def get_files(self) -> list[str]:
        return [
                str(path)
                for path in self.data_dir.rglob("*") # rglob("*") là duyệt đệ quy tất cả các 
                if path.is_file()
                and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]

    def get_nodes(self, documents):
        split = SentenceSplitter(chunk_size= 800, chunk_overlap=200)
        titleEx = TitleExtractor(
            llm=Settings.llm,
            nodes=5,
            node_template=TITLE_NODE_PROMT,
            combine_template=TITLE_COMBINE_PROMT,
        )
        keywordEx = KeywordExtractor(
            llm= Settings.llm,
            keywords=5,
            prompt_template= KEYWORD_PROMT
        )

        transform = [ split,
                    #   titleEx, keywordEx,
            # EntityExtractor(prediction_threshold=0.5),
            # SummaryExtractor(summaries=["prev", "self"]),
            # QuestionsAnsweredExtractor(questions=3),
            Settings.embed_model
        ]
        ingestion = IngestionPipeline(transformations=transform)
        nodes = ingestion.run(documents = documents)
        return nodes

    def get_storage(self):
        storage = StorageContext(
            docstore=SimpleDocumentStore(),
            index_store=SimpleIndexStore(),
            vector_stores={
                "default": SimpleVectorStore()
            },
            graph_store=SimpleGraphStore(),
        )
        return storage

    
    def load_document(self): # Trả về mảng document được đọc ra
        files= self.get_files()
        if not files:
            return []
        return SimpleDirectoryReader(input_files=files).load_data()

    def build_index(self):
        documents = self.load_document()
        if not documents:
            self.nodes = []
            self.storage_context = None
            return None
        
        self.nodes = self.process_documents(documents)
        if not self.nodes:
            return None
        
        self.storage_context = self.get_storage()

        vector_index = VectorStoreIndex(nodes=self.nodes, storage_context=self.storage_context)
        return vector_index

    def process_documents(self, documents):
        if not documents:
            return []

        return self.get_nodes(documents)