from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import unicodedata
from typing import Any

import pymupdf
import pytesseract
from llama_index.core import Document
from PIL import Image
from pytesseract import Output


OCR_MIN_ALPHANUMERIC_CHARS = 40 # nếu có ít hơn 40 ký tự chữ hoặc số thì trang đó cần OCR.
OCR_LANGUAGE = "vie"
OCR_RENDER_SCALE = 3 # render PDF với hệ số phóng đại 3 lần
FULL_WIDTH_BLOCK_RATIO = 0.72 # block rộng ít nhất 72% chiều rộng trang được xem là block trải rộng toàn trang.
MIN_COLUMN_GUTTER_RATIO = 0.025 # khe phân cách cột phải đủ rộng, tối thiểu 2,5% chiều rộng trang, mới được cân nhắc là gutter.
# 2 số cuối là ngưỡng heuristic để suy đoán bố cục, không phải quy tắc chính xác cho mọi tài liệu.

def _normalized_words(text: str) -> list[str]:
    # Chuẩn hóa một đoạn văn bản thành danh sách token để so sánh văn bản nguồn với kết quả OCR, 
    # kể cả khi có khác biệt về chữ hoa, chữ thường hoặc dấu tiếng Việt.
    normalized = unicodedata.normalize("NFKD", text).casefold()
    normalized = "".join(
        character
        for character in normalized
        if not unicodedata.category(character).startswith("M") # Loại bỏ các dấu Unicode thuộc nhóm M ví dụ ắ thành a
    )
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE) # Trả về 1 mảng  ví dụ Xin chào VN  => ["xin", "chao", "VN"]
    # Hàm này bỏ dấu để so sánh, chứ không sửa văn bản gốc. Ngoài ra, việc loại dấu có thể khiến các từ khác nghĩa trở 
    # thành giống nhau, nên không nên dùng riêng kết quả chuẩn hóa làm văn bản hiển thị cho người dùng.


def find_ocr_evidence_bboxes(source_text: str, ocr_words: list[dict[str, Any]],) -> list[dict[str, float]]:
    # Mục địch: Tìm các từ trên ảnh OCR tương ứng với một đoạn văn bản nguồn, sau đó trả về tọa độ của các từ tìm được.
    # Cái này dùng để cho highlight lên frontend

    source_words = _normalized_words(source_text) # Chuẩn hóa văn bản nguồn
    indexed_words = [ # Tách và lập chỉ mục các từ OCR
        (index, token)
        for index, word in enumerate(ocr_words)
        for token in _normalized_words(word.get("text", ""))
    ]
    indexed_tokens = [token for _, token in indexed_words] 
    if not source_words or not indexed_tokens:
        return []

    match_start = None # Tìm chuỗi khớp hoàn toàn
    for offset in range(len(indexed_tokens) - len(source_words) + 1):
        if indexed_tokens[offset:offset + len(source_words)] == source_words:
            match_start = offset
            break

    match_length = len(source_words)
    if match_start is None:
        window_size = min(8, len(source_words))
        if window_size < 3:
            return []
        for source_offset in range(0, len(source_words) - window_size + 1, max(1, window_size - 2)):
            fragment = source_words[source_offset:source_offset + window_size]
            for offset in range(len(indexed_tokens) - window_size + 1):
                if indexed_tokens[offset:offset + window_size] == fragment:
                    match_start = offset
                    match_length = window_size
                    break
            if match_start is not None:
                break

    if match_start is None:
        return []

    word_indexes = {
        indexed_words[index][0]
        for index in range(match_start, match_start + match_length)
    }
    return [
        {
            key: float(word[key])
            for key in ("x", "y", "width", "height")
        }
        for index, word in enumerate(ocr_words)
        if index in word_indexes
    ]


def _text_blocks(page: pymupdf.Page) -> list[dict[str, Any]]:
    # Trích xuất văn bản có sẵn trong PDF bằng PyMuPDF, gom các từ theo từng dòng và tạo các block văn bản kèm bounding box.

    lines: dict[tuple[int, int], list[tuple[Any, ...]]] = defaultdict(list) # Định nghĩa kiểu dữ liệu
    for word in page.get_text("words"): # Lấy các từ trên trang
        x0, y0, x1, y1, text, block_number, line_number, word_number = word
        if text.strip():
            lines[(block_number, line_number)].append(
                (x0, y0, x1, y1, text, word_number)
            )

    blocks = []
    for words in lines.values():
        words.sort(key=lambda word: word[5])
        blocks.append({
            "text": " ".join(word[4] for word in words),
            "bbox": (
                min(word[0] for word in words),
                min(word[1] for word in words),
                max(word[2] for word in words),
                max(word[3] for word in words),
            ),
            "words": [],
        })
    return blocks


def _ocr_blocks(
    image: Image.Image,
    scale_x: float,
    scale_y: float,
) -> list[dict[str, Any]]:
    try:
        data = pytesseract.image_to_data(
            image,
            lang=OCR_LANGUAGE,
            config="--psm 3",
            output_type=Output.DICT,
        )
    except pytesseract.TesseractNotFoundError as error:
        raise RuntimeError(
            "Không tìm thấy Tesseract OCR. Cài Tesseract và thêm vào PATH."
        ) from error
    except pytesseract.TesseractError as error:
        raise RuntimeError(
            "Không chạy được Tesseract OCR. Hãy kiểm tra đã cài language data vie."
        ) from error

    lines: dict[tuple[int, int, int], list[dict[str, Any]]] = defaultdict(list)
    for index, raw_text in enumerate(data["text"]):
        text = raw_text.strip()
        try:
            confidence = float(data["conf"][index])
        except (TypeError, ValueError):
            continue
        if not text or confidence < 0:
            continue

        x0 = float(data["left"][index]) / scale_x
        y0 = float(data["top"][index]) / scale_y
        x1 = (float(data["left"][index]) + float(data["width"][index])) / scale_x
        y1 = (float(data["top"][index]) + float(data["height"][index])) / scale_y
        lines[
            (
                int(data["block_num"][index]),
                int(data["par_num"][index]),
                int(data["line_num"][index]),
            )
        ].append({
            "text": text,
            "bbox": (x0, y0, x1, y1),
        })

    blocks = []
    for words in lines.values():
        blocks.append({
            "text": " ".join(word["text"] for word in words),
            "bbox": (
                min(word["bbox"][0] for word in words),
                min(word["bbox"][1] for word in words),
                max(word["bbox"][2] for word in words),
                max(word["bbox"][3] for word in words),
            ),
            "words": words,
        })
    return blocks


def _column_gutters(
    blocks: list[dict[str, Any]],
    page_width: float,
) -> list[float]:
    # Tìm các khe dọc phân cách cột văn bản trên trang PDF.
    # Ví dụ, với trang có hai cột, hàm cố gắng tìm một tọa độ x nằm giữa cột trái và cột phải. Với ba cột, nó có thể tìm hai tọa độ.
    
    candidates = [
        block for block in blocks
        if block["bbox"][2] - block["bbox"][0] < page_width * FULL_WIDTH_BLOCK_RATIO
    ]
    x_edges = sorted({
        coordinate
        for block in candidates
        for coordinate in (block["bbox"][0], block["bbox"][2])
        if page_width * 0.2 < coordinate < page_width * 0.8
    })

    candidates_by_position: dict[float, float] = {}
    for left_edge, right_edge in zip(x_edges, x_edges[1:]):
        gap = right_edge - left_edge
        if gap < page_width * MIN_COLUMN_GUTTER_RATIO:
            continue

        midpoint = (left_edge + right_edge) / 2
        left_blocks = [
            block for block in candidates
            if (block["bbox"][0] + block["bbox"][2]) / 2 < midpoint
        ]
        right_blocks = [
            block for block in candidates
            if (block["bbox"][0] + block["bbox"][2]) / 2 > midpoint
        ]
        if len(left_blocks) < 2 or len(right_blocks) < 2:
            continue

        left_extent = max(block["bbox"][2] for block in left_blocks)
        right_extent = min(block["bbox"][0] for block in right_blocks)
        actual_gap = right_extent - left_extent
        if actual_gap < page_width * MIN_COLUMN_GUTTER_RATIO:
            continue

        gutter = (left_extent + right_extent) / 2
        score = min(len(left_blocks), len(right_blocks)) * actual_gap
        candidates_by_position[gutter] = max(
            candidates_by_position.get(gutter, 0.0),
            score,
        )

    selected = []
    for gutter, score in sorted(
        candidates_by_position.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        if all(
            abs(gutter - existing) >= page_width * MIN_COLUMN_GUTTER_RATIO
            for existing in selected
        ):
            selected.append(gutter)

    return sorted(selected)


def _reading_order(
    blocks: list[dict[str, Any]],
    page_width: float,
) -> list[tuple[int, dict[str, Any]]]:
    # Sắp xếp các block theo thứ tự đọc hợp lý, đặc biệt với PDF có nhiều cột.
    # Nếu chỉ sắp xếp theo tọa độ từ trên xuống dưới rồi từ trái sang phải, một trang hai cột có thể bị đọc sai thứ tự.
    # Thay vì xen kẽ đoạn bên trái và bên phải theo từng dòng, hàm cố gắng đọc hết từng cột trong từng vùng nội dung.

    gutters = _column_gutters(blocks, page_width)
    if not gutters:
        return [
            (1, block)
            for block in sorted(blocks, key=lambda block: (block["bbox"][1], block["bbox"][0]))
        ]

    spanning = [
        block for block in blocks
        if block["bbox"][2] - block["bbox"][0] >= page_width * FULL_WIDTH_BLOCK_RATIO
    ]
    columns = [block for block in blocks if block not in spanning]
    anchors = sorted(spanning, key=lambda block: (block["bbox"][1], block["bbox"][0]))
    ordered = []
    previous_y = float("-inf")

    def column_index(block: dict[str, Any]) -> int:
        center = (block["bbox"][0] + block["bbox"][2]) / 2
        return sum(center >= gutter for gutter in gutters) + 1

    def append_columns(section: list[dict[str, Any]]) -> None:
        for column_number in range(1, len(gutters) + 2):
            ordered.extend(
                (column_number, block) for block in sorted(
                    (
                        block for block in section
                        if column_index(block) == column_number
                    ),
                    key=lambda block: (block["bbox"][1], block["bbox"][0]),
                )
            )

    for anchor in anchors:
        anchor_y = anchor["bbox"][1]
        section = [
            block for block in columns
            if previous_y <= (block["bbox"][1] + block["bbox"][3]) / 2 < anchor_y
        ]
        append_columns(section)
        ordered.append((0, anchor))
        previous_y = anchor["bbox"][3]

    remaining = [
        block for block in columns
        if (block["bbox"][1] + block["bbox"][3]) / 2 >= previous_y
    ]
    append_columns(remaining)
    return ordered


def _normalized_bbox(
    bbox: tuple[float, float, float, float],
    page_width: float,
    page_height: float,
) -> dict[str, float]:
    x0, y0, x1, y1 = bbox
    return {
        "x": max(0.0, min(1.0, x0 / page_width)),
        "y": max(0.0, min(1.0, y0 / page_height)),
        "width": max(0.0, min(1.0, (x1 - x0) / page_width)),
        "height": max(0.0, min(1.0, (y1 - y0) / page_height)),
    }


def load_pdf_documents(file_path: str | Path, group_name: str) -> list[Document]:
    # dùng để đọc nội dung file PDF, tự động nhận diện trang cần OCR, sắp xếp văn bản theo bố cục đọc và chuyển nội
    # dung thành các đối tượng Document kèm metadata
    
    path = Path(file_path).resolve()
    documents = []

    with pymupdf.open(path) as pdf:
        for page_index, page in enumerate(pdf):
            blocks = _text_blocks(page)
            page_text = "\n".join(block["text"] for block in blocks)
            use_ocr = sum(character.isalnum() for character in page_text) < OCR_MIN_ALPHANUMERIC_CHARS
            ocr_used = False

            if use_ocr:
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(OCR_RENDER_SCALE, OCR_RENDER_SCALE),
                    alpha=False,
                )
                image = Image.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples,
                )
                blocks = _ocr_blocks(
                    image,
                    pixmap.width / page.rect.width,
                    pixmap.height / page.rect.height,
                )
                ocr_used = True

            ordered_blocks = _reading_order(blocks, page.rect.width)
            columns: dict[int, list[dict[str, Any]]] = defaultdict(list)
            for column_number, block in ordered_blocks:
                columns[column_number].append(block)

            for column_number, column_blocks in sorted(columns.items()):
                text = "\n".join(block["text"] for block in column_blocks).strip()
                if not text:
                    continue

                page_bbox = (
                    min(block["bbox"][0] for block in column_blocks),
                    min(block["bbox"][1] for block in column_blocks),
                    max(block["bbox"][2] for block in column_blocks),
                    max(block["bbox"][3] for block in column_blocks),
                )
                metadata: dict[str, Any] = {
                    "file_name": path.name,
                    "file_path": str(path),
                    "folder_name": group_name,
                    "page_label": str(page_index + 1),
                    "page_number": page_index + 1,
                    "source_page": page_index + 1,
                    "source_column": column_number,
                    "source_bbox": _normalized_bbox(
                        page_bbox,
                        page.rect.width,
                        page.rect.height,
                    ),
                    "ocr_used": ocr_used,
                }

                if ocr_used:
                    metadata["ocr_words"] = [
                        {
                            "text": word["text"],
                            **_normalized_bbox(
                                word["bbox"],
                                page.rect.width,
                                page.rect.height,
                            ),
                        }
                        for block in column_blocks
                        for word in block["words"]
                    ]

                documents.append(Document(
                    text=text,
                    metadata=metadata,
                    excluded_embed_metadata_keys=[
                        "source_bbox",
                        "source_column",
                        "ocr_used",
                        "ocr_words",
                    ],
                    excluded_llm_metadata_keys=[
                        "source_bbox",
                        "source_column",
                        "ocr_used",
                        "ocr_words",
                    ],
                ))

    return documents
