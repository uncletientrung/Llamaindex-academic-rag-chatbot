SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALL_GROUPS = "all" # value của khi chọn tất cả nhóm

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 200
PDF_OCR_VERSION = "tesseract-vie-1"

SIMILARITY_TOP_K = 10

SIMILARITY_CUTOFF = 0.25

RERANK_TOP_N = 3

RERANKER_MODEL = "kiencnt2205/vietnamese-legal-reranker-bge-base"

EMBEDDING_MODEL = "AITeamVN/Vietnamese_Embedding"
