# Tìm hiểu LlamaIndex và xây dựng chatbot RAG hỗ trợ tra cứu quy định học vụ từ tài liệu nội bộ

## 1. Giới thiệu

Đây là đồ án môn học với mục tiêu **tìm hiểu LlamaIndex và ứng dụng LlamaIndex để xây dựng hệ thống RAG (Retrieval-Augmented Generation)** hỗ trợ tra cứu thông tin từ các tài liệu quy định học vụ nội bộ.

Hệ thống cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên, sau đó hệ thống thực hiện quá trình:

```text
User Query
    ↓
Retrieval
    ↓
Relevant Nodes
    ↓
Response Synthesis
    ↓
LLM
    ↓
Final Answer
```

Thay vì yêu cầu mô hình ngôn ngữ tự sinh câu trả lời dựa trên kiến thức có sẵn, hệ thống trước tiên tìm kiếm các đoạn thông tin liên quan trong kho tài liệu nội bộ, sau đó sử dụng các đoạn thông tin này làm context cho LLM tạo câu trả lời.

### Mục tiêu của đề tài

* Tìm hiểu kiến trúc và các thành phần chính của **LlamaIndex**.
* Tìm hiểu quy trình xây dựng một hệ thống **RAG**.
* Xây dựng pipeline xử lý tài liệu nội bộ.
* Xây dựng cơ chế truy xuất các Node liên quan đến câu hỏi.
* Sử dụng LLM để tổng hợp câu trả lời dựa trên context được truy xuất.
* Xây dựng giao diện chatbot bằng **Streamlit**.
* Hỗ trợ quản lý tài liệu theo từng nhóm/label.
* Hiển thị nguồn tài liệu được sử dụng để tạo câu trả lời.
* Lưu và hiển thị lịch sử hỏi đáp.

---

# 2. Công nghệ sử dụng

| Công nghệ           | Vai trò                                  |
| ------------------- | ---------------------------------------- |
| **Python**          | Ngôn ngữ lập trình chính                 |
| **LlamaIndex**      | Framework chính để xây dựng pipeline RAG |
| **RAG**             | Bài toán và kiến trúc chính của hệ thống |
| **Embedding Model** | Chuyển văn bản/query thành vector        |
| **Vector Store**    | Lưu trữ và tìm kiếm vector               |
| **LLM**             | Sinh câu trả lời dựa trên context        |
| **Streamlit**       | Xây dựng giao diện web                   |
| **PDF/DOCX**        | Nguồn tài liệu nội bộ                    |

---

# 3. Kiến trúc tổng quan

Hệ thống được chia thành 3 thành phần chính:

```text
┌────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                           │
│                         app.py                             │
│                                                            │
│  📚 Documents     💬 Chat RAG     🕘 History     👤 Auth │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                       LlamaIndex                           │
│                                                            │
│  Ingestion        →       Retrieval       →   Generation  │
│                                                            │
│  Document                 Retriever            Response    │
│      ↓                    ↓                    Synthesizer │
│  Node / Chunk             ↓                    ↓           │
│      ↓                  Reranker               LLM        │
│  Embedding                 ↓                    ↓           │
│      ↓              Relevant Nodes         Final Answer  │
│  Vector Store                                             │
└────────────────────────────────────────────────────────────┘
```

---

# 4. Cấu trúc thư mục

Project được chia thành các module độc lập để 3 thành viên có thể phát triển song song và hạn chế xung đột khi merge Git.

```text
project/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   └── # Tài liệu đầu vào
│
├── storage/
│   └── # Index / Vector Store được persist
│
├── src/
│   │
│   ├── config.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── parser.py
│   │   ├── pipeline.py
│   │   └── index.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   ├── filter.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   ├── synthesizer.py
│   │   ├── prompt.py
│   │   └── query_engine.py
│   │
│   └── ui/
│       ├── __init__.py
│       ├── chat.py
│       ├── sidebar.py
│       └── components.py
│
└── README.md
```

## Phân chia module

### `app.py`

File khởi chạy ứng dụng Streamlit và điều phối các thành phần giao diện.

```text
app.py
 ├── Authentication
 ├── Document Management
 ├── Chat RAG
 └── History
```

### `src/ingestion/`

Phụ trách quá trình đưa tài liệu vào hệ thống:

```text
Document
    ↓
Document Loader
    ↓
Node Parser / Chunking
    ↓
Metadata
    ↓
Embedding
    ↓
Vector Store / Index
```

Các file chính:

* `loader.py`: đọc PDF/DOCX và tạo `Document`.
* `parser.py`: chia tài liệu thành các Node.
* `pipeline.py`: xây dựng `IngestionPipeline`.
* `index.py`: tạo, lưu và load Index/Vector Store.

### `src/retrieval/`

Phụ trách quá trình tìm kiếm thông tin liên quan:

```text
User Query
    ↓
Retriever
    ↓
Metadata Filter
    ↓
Vector / Keyword / Hybrid Retrieval
    ↓
Reranker / Node Postprocessor
    ↓
Relevant Nodes
```

Các file chính:

* `retriever.py`: tạo Retriever.
* `filter.py`: xử lý Metadata Filter.
* `hybrid.py`: xử lý Hybrid Retrieval nếu được sử dụng.
* `reranker.py`: rerank các Node được truy xuất.

Trong LlamaIndex, Node Postprocessor có thể xử lý các Node sau Retrieval và trước Response Synthesis, bao gồm các cơ chế như reranking, metadata filtering hoặc similarity filtering.

### `src/generation/`

Phụ trách quá trình tạo câu trả lời:

```text
Relevant Nodes
      ↓
Response Synthesizer
      ↓
Prompt + Context
      ↓
LLM
      ↓
Final Answer
```

Các file chính:

* `llm.py`: cấu hình LLM.
* `synthesizer.py`: cấu hình Response Synthesizer.
* `prompt.py`: quản lý prompt.
* `query_engine.py`: kết nối Retrieval với Generation.

### `src/ui/`

Chứa các thành phần giao diện Streamlit:

* `chat.py`: giao diện chatbot.
* `sidebar.py`: menu điều hướng.
* `components.py`: các component dùng chung.

---

# 5. Luồng hoạt động nghiệp vụ chính

## 5.1. Quản lý tài liệu

Người dùng có thể tạo các nhóm tài liệu bằng **Label**.

Ví dụ:

```text
📁 Quy định học bổng
    ├── quy-dinh-hoc-bong.pdf
    ├── dieu-kien-hoc-bong.pdf
    └── muc-hoc-bong.docx

📁 Quy định tín chỉ
    ├── quy-che-dao-tao.pdf
    └── quy-dinh-dang-ky-hoc-phan.pdf

📁 Quy định học phí
    └── quy-dinh-hoc-phi.pdf
```

Một Label có thể chứa nhiều tài liệu.

Khi tài liệu được đưa vào hệ thống, quá trình xử lý chính là:

```text
PDF / DOCX
    ↓
Document Loader
    ↓
Document
    ↓
Chunking
    ↓
TextNode
    ↓
Metadata
    ↓
Embedding
    ↓
Vector Store
```

Các Node được tạo ra từ quá trình xử lý tài liệu có thể chứa nội dung văn bản cùng metadata như tên file, trang, đường dẫn và các thông tin liên quan.

---

# 6. Luồng RAG

Đây là luồng nghiệp vụ chính của hệ thống.

```text
                    ┌──────────────┐
                    │   Documents │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │  Ingestion   │
                    └──────┬───────┘
                           ↓
                     Documents
                           ↓
                       Chunking
                           ↓
                         Nodes
                           ↓
                       Embedding
                           ↓
                    Vector Store
                           │
                           │
                           │
User Query ────────────────┘
     │
     ↓
Embedding Query
     ↓
Query Vector
     ↓
Retriever
     ↓
Similarity Search
     ↓
Top-K Nodes
     ↓
Node Postprocessor / Reranker
     ↓
Relevant Nodes
     ↓
Response Synthesizer
     ↓
Prompt + Context
     ↓
LLM
     ↓
Response
     ↓
Final Answer
```

Với Vector Retrieval, query được chuyển thành vector, sau đó được sử dụng để tìm kiếm các Node có độ tương đồng cao trong Vector Store. Kết quả Retrieval có thể được biểu diễn dưới dạng `NodeWithScore`, trong đó mỗi Node đi kèm điểm tương đồng.

---

# 7. Luồng hỏi đáp cụ thể

Ví dụ người dùng hỏi:

> **"Điều kiện rút học phần là gì?"**

Hệ thống thực hiện:

### Bước 1 — Nhận Query

```text
Điều kiện rút học phần là gì?
```

### Bước 2 — Embedding Query

Query được chuyển thành vector bằng Embedding Model.

```text
User Query
     ↓
Embedding Model
     ↓
Query Vector
```

### Bước 3 — Retrieval

Retriever tìm kiếm các Node phù hợp trong Vector Store.

```text
Query Vector
     ↓
Vector Store
     ↓
Similarity Search
     ↓
Top-K Nodes
```

Ví dụ:

```text
Node 1 → score = 0.91
Node 2 → score = 0.83
Node 3 → score = 0.78
```

### Bước 4 — Postprocessing / Reranking

Các Node được xử lý hoặc sắp xếp lại nhằm chọn context phù hợp hơn cho LLM.

```text
Retrieved Nodes
       ↓
Reranker / Filter
       ↓
Relevant Nodes
```

### Bước 5 — Response Synthesis

Các Node liên quan được đưa vào Response Synthesizer cùng với Query.

```text
Query
  +
Relevant Nodes
  ↓
Response Synthesizer
```

### Bước 6 — LLM

LLM nhận prompt chứa câu hỏi và context từ tài liệu.

```text
Prompt
  +
Context
  ↓
LLM
  ↓
Answer
```

### Bước 7 — Trả kết quả

Hệ thống hiển thị:

```text
🤖 Câu trả lời

Theo quy định..., việc rút bớt học phần
được thực hiện trong thời hạn...

📚 Nguồn:
- quyet_dinh.pdf
- Trang 1
```

Response của LlamaIndex có thể chứa cả câu trả lời và các `source_nodes`, giúp hệ thống hiển thị nguồn tài liệu được sử dụng trong quá trình sinh câu trả lời.

---

# 8. Giao diện Streamlit

Giao diện chính được triển khai trong:

```text
app.py
```

Hệ thống gồm các khu vực chính:

```text
┌───────────────────────────────────────────────────────┐
│                    Academic RAG                       │
├───────────────┬───────────────────────────────────────┤
│               │                                       │
│ 💬 Hỏi đáp    │          Chat RAG                    │
│               │                                       │
│ 📚 Tài liệu   │   User: Điều kiện học bổng là gì?   │
│               │                                       │
│ 🕘 Lịch sử    │   AI: Theo quy định...              │
│               │                                       │
│ 👤 Tài khoản  │   📚 Nguồn tài liệu                  │
│               │                                       │
│ 🚪 Đăng xuất  │   [ Nhập câu hỏi... ]               │
└───────────────┴───────────────────────────────────────┘
```

### Các chức năng giao diện

#### 1. Đăng nhập / Đăng xuất

Cho phép người dùng đăng nhập và đăng xuất khỏi hệ thống.

#### 2. Quản lý tài liệu

Cho phép:

* Tạo Label.
* Upload nhiều PDF/DOCX vào một Label.
* Quản lý các nhóm tài liệu.

#### 3. Hỏi đáp RAG

Cho phép người dùng nhập câu hỏi và nhận câu trả lời từ hệ thống RAG.

#### 4. Lịch sử

Lưu và hiển thị các câu hỏi/câu trả lời trước đó trong phiên làm việc.

---

# 9. Cài đặt

## Yêu cầu

* Python 3.10+
* Git
* Môi trường ảo Python
* LLM local 
* Các thư viện được khai báo trong `requirements.txt`

---

## Tạo môi trường ảo

### Windows

```bash
python -m venv .venv
```

Kích hoạt:

```bash
.venv\Scripts\activate
```

### Linux / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 11. Cài đặt thư viện

Sau khi kích hoạt môi trường ảo:

```bash
pip install -r requirements.txt
```

Các package LlamaIndex sẽ được bổ sung theo Embedding Model, LLM, Reader và Vector Store mà project sử dụng.

---

# 12. Chạy ứng dụng

Từ thư mục gốc của project:

```bash
streamlit run app.py
```

Sau khi chạy thành công, Streamlit sẽ cung cấp địa chỉ truy cập ứng dụng, thường là:

```text
http://localhost:8501
```

Mở địa chỉ trên trình duyệt để sử dụng hệ thống.

---

# 13. Quy trình sử dụng

### Bước 1 — Đăng nhập

Đăng nhập vào hệ thống.

### Bước 2 — Tạo Label

Ví dụ:

```text
Quy định học bổng
```

### Bước 3 — Upload tài liệu

Upload các tài liệu liên quan:

```text
quy-dinh-hoc-bong.pdf
dieu-kien-hoc-bong.pdf
muc-hoc-bong.docx
```

### Bước 4 — Xử lý tài liệu

Hệ thống thực hiện:

```text
Document
 ↓
Chunking
 ↓
Node
 ↓
Metadata
 ↓
Embedding
 ↓
Vector Store / Index
```

### Bước 5 — Đặt câu hỏi

Ví dụ:

```text
Điều kiện để được học bổng là gì?
```

### Bước 6 — RAG Retrieval

Hệ thống tìm các Node liên quan đến câu hỏi.

### Bước 7 — Sinh câu trả lời

Các Node được sử dụng làm context cho LLM.

### Bước 8 — Hiển thị kết quả

Hệ thống trả về:

* Câu trả lời.
* Nguồn tài liệu.
* Thông tin liên quan đến Node được sử dụng.

---

# 14. Git Workflow

Để 3 thành viên làm việc song song, project sử dụng các branch riêng:

```text
main
 │
 ├── feature/ingestion
 ├── feature/retrieval
 └── feature/generation-ui
```

Mỗi thành viên chủ yếu chỉnh sửa module của mình:

```text
feature/ingestion
    ↓
src/ingestion/

feature/retrieval
    ↓
src/retrieval/

feature/generation-ui
    ↓
src/generation/
src/ui/
app.py
```

Các module giao tiếp với nhau thông qua interface rõ ràng:

```text
load_index()
     ↓
VectorStoreIndex
     ↓
retrieve(index, query)
     ↓
List[NodeWithScore]
     ↓
generate_response(query, nodes)
     ↓
str
```

Cách tổ chức này giúp giảm việc nhiều thành viên cùng chỉnh sửa một file và hạn chế conflict khi merge.

---

# 15. Mục tiêu của hệ thống

Hệ thống hướng tới việc minh họa cách **LlamaIndex hỗ trợ xây dựng một ứng dụng RAG trên dữ liệu nội bộ**, từ khâu xử lý tài liệu, indexing, retrieval cho đến response synthesis và hiển thị kết quả.

Luồng cốt lõi của hệ thống:

```text
                DOCUMENTS
                    │
                    ▼
              ┌───────────┐
              │ Ingestion │
              └─────┬─────┘
                    │
                    ▼
                  Nodes
                    │
                    ▼
                Embedding
                    │
                    ▼
               Vector Store
                    │
                    │
                    ▼
USER QUERY ──►  Retrieval
                    │
                    ▼
                 Rerank
                    │
                    ▼
             Relevant Nodes
                    │
                    ▼
          Response Synthesizer
                    │
                    ▼
                   LLM
                    │
                    ▼
              FINAL ANSWER
                    │
                    ▼
              Streamlit UI
```

Đây là pipeline RAG cốt lõi được sử dụng để giải quyết bài toán **tra cứu quy định học vụ từ tài liệu nội bộ**.
