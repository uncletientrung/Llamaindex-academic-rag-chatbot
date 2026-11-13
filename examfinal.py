from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from pathlib import Path
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

from llama_index.extractors.entity import EntityExtractor
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from promts.promt_extractor import (
    TITLE_NODE_PROMT,
    TITLE_COMBINE_PROMT,
    KEYWORD_PROMT,
)
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core.vector_stores import SimpleVectorStore
from constants import (
    SUPPORTED_EXTENSIONS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    EMBEDDING_MODEL,
)
from rich.pretty import pprint
from pdf_ingestion import load_pdf_documents
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.postprocessor import SimilarityPostprocessor, SentenceTransformerRerank


CHUNK_SIZE, CHUNK_OVERLAP = 24, 6
word_tokenizer = lambda text: text.split()

DATA = {
    "quy_che" :[
        "Sinh vien duoc tot nghiep khi tich luy du so tin chi quy dihn. Diem trung binh tich luy phai dat tu 2.00 tro len. Sinh Vien Khong bi truy cu trach nhiem hinh su",
        "Sinh vien bi canh bao hoc vu khi diem trung binh duoi 1.00. SInh vien bi canh bao 2 lan lien tiep se bi buoc thoi hoc",
    ],
    "hoc_phi" :[
        "Hoc phi duoc tinh theo so tin chi dang ky trong ky, sinh vien nop hoc phi truoc han se khong bi tinh phi tre han",
    ],
}

Settings.llm = Ollama(model="qwen2.5:3b",request_timeout=120.0, temperature=0.7)
Settings.embed_model = MockEmbedding(embed_dim=16)


def get_nodes(documents, folder_name: str):  # Hàm lấy các nodes đã extractor và embed
    split = SentenceSplitter(chunk_size= 24, chunk_overlap=6, tokenizer= word_tokenizer)
    transform = [ split,
        Settings.embed_model
    ]
    ingestion = IngestionPipeline(transformations=transform)
    nodes = ingestion.run(documents=documents)

    for node in nodes:
        node.metadata["folder_name"] = folder_name 
    return nodes

def build_indexes(nodes):
    return VectorStoreIndex(nodes= nodes)

def build_retriever(index, group_name, top_k: int =2):
    filters = MetadataFilters( # Lọc theo tên folder của index
        filters=[
            MetadataFilter(
                key="folder_name",
                value=group_name,
            ),
        ]
    )
    return index.as_retriever(similarity_top_k=top_k, filters=filters)
all_nodes=[]
for group_name, texts in DATA.items():
    docs = [Document(text=text) for text in texts]
    nodes = get_nodes(docs, folder_name=group_name)
    print(f"{group_name} : {len(docs)} văn bản -> {len(nodes)} node | folder_name hợp lệ: {all(node.metadata.get('folder_name') == group_name for node in nodes)}")
    all_nodes.extend(nodes)

index = build_indexes(all_nodes)
print("Tổng số node trong index:", len(all_nodes))
QUESTION = "SInh vien bi canh bao hoc vu khi nao?"
for group_name in DATA.keys():
    res = build_retriever(index, group_name=group_name, top_k=3).retrieve(QUESTION)
    print(f"Retriever [{group_name}] top_k = 3 -> {len(res)} node | Nhóm: {sorted({r.node.metadata.get('folder_name') for r in res})}")

# -------------------------------------------
print("========================PHẦN B ========================")

SCORES = {"n1": 0.82, "n2": 0.31, "n3": 0.29, "n4": 0.25, "n5": 0.10}
RERANK_SCORE = {"n1": 0.42, "n2": 0.95, "n3": 0.70, "n4": 0.99, "n5": 0.10}
SIMILARITY_CUTOFF, RERANK_TOP_N = 0.3, 2
candidates = [NodeWithScore(node=TextNode(id_=i, text=f"đoạn {i}"), score=score) for i, score in SCORES.items()]

def postprocess(nodes):
    filtered_nodes = SimilarityPostprocessor(similarity_cutoff=SIMILARITY_CUTOFF).postprocess_nodes(nodes)
    rerank_map = {node_id: score for node_id, score in RERANK_SCORE.items()}
    reranked_nodes = sorted(
        filtered_nodes,
        key=lambda item: rerank_map.get(item.node.node_id, -1.0),
        reverse=True,
    )
    return [item.node.node_id for item in reranked_nodes[:RERANK_TOP_N]]


before_postprocess = [n.node.node_id for n in candidates]
after_postprocess = [n.node.node_id for n in SimilarityPostprocessor(similarity_cutoff=SIMILARITY_CUTOFF).postprocess_nodes(candidates)]
final = postprocess(candidates)
print("Trước:", before_postprocess)
print("Sau cutoff:", after_postprocess)
print("Sau rerank top:", final)

for k in[1,2]: 
    print(f"quy che top_k = {k} -> {len(build_retriever(index, 'quy_che', top_k=2).retrieve(QUESTION))} node")
print(f"nhóm không tồn tại -> {len(build_retriever(index, 'khong_co', top_k=2).retrieve(QUESTION))} node")