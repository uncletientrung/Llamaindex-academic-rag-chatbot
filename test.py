from llama_index.core import Document, SummaryIndex, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from pprint import pprint
# =========================
# 1. Tạo Document
# =========================

documents = [
    Document(text="Paul Graham là một lập trình viên và nhà đầu tư."),
    Document(text="Paul Graham đồng sáng lập Y Combinator."),
    Document(text="Y Combinator là một vườn ươm startup nổi tiếng.")
]

# =========================
# 2. Document -> Nodes
# =========================

parser = SentenceSplitter(
    chunk_size=100,
    chunk_overlap=0
)

nodes = parser.get_nodes_from_documents(documents)

print("=" * 60)
print("NODES")
# pprint(vars(nodes))
print("=" * 60)

for i, node in enumerate(nodes):
    print(f"\nNode {i}")
    
    print("ID:", node.node_id)
    print("Text:", node.text)
    print("Metadata:", node.metadata)


# =========================
# 3. Tạo SummaryIndex
# =========================

summary_index = SummaryIndex(nodes)

print("\n" + "=" * 60)
print("SUMMARY INDEX")


pprint(vars(summary_index))

print("=" * 60)

print("Class:", type(summary_index))
print("Index ID:", summary_index.index_id)

print("\nIndex struct:")
print(summary_index.index_struct)

print("=" * 60)
for node_id, node in summary_index.docstore.docs.items():
    print("=" * 60)
    print("ID:", node_id)
    print("Type:", type(node))
    print("Text:", node.text)
    print("Metadata:", node.metadata)



# # =========================
# # 4. Tạo VectorStoreIndex
# # =========================

# vector_index = VectorStoreIndex(nodes)

# print("\n" + "=" * 60)
# print("VECTOR STORE INDEX")
# print("=" * 60)

# print("Class:", type(vector_index))
# print("Index ID:", vector_index.index_id)

# print("\nIndex struct:")
# print(vector_index.index_struct)


# # =========================
# # 5. Xem StorageContext
# # =========================

# print("\n" + "=" * 60)
# print("SUMMARY STORAGE")
# print("=" * 60)

# print(summary_index.storage_context)

# print("\n" + "=" * 60)
# print("VECTOR STORAGE")
# print("=" * 60)

# print(vector_index.storage_context)