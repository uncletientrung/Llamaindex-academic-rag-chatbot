from pathlib import Path

import pymupdf
import pytest
from PIL import Image

import pdf_ingestion
from pdf_ingestion import find_ocr_evidence_bboxes, load_pdf_documents


def test_scanned_pdf_requires_configured_deepdoc(monkeypatch):
    monkeypatch.delenv(pdf_ingestion.DEEPDOC_PATH_ENV, raising=False)
    monkeypatch.setattr(pdf_ingestion, "_DEEPDOC_OCR", None)

    with pytest.raises(RuntimeError, match="DEEPDOC_VIETOCR_PATH"):
        pdf_ingestion._get_deepdoc_ocr()


def test_pdf_page_with_two_columns_is_split_in_reading_order(tmp_path: Path):
    pdf_path = tmp_path / "two-columns.pdf"
    pdf = pymupdf.open()
    page = pdf.new_page(width=600, height=800)

    for row in range(4):
        page.insert_text((40, 100 + row * 30), f"LEFT COLUMN TEXT LINE {row}")
        page.insert_text((330, 100 + row * 30), f"RIGHT COLUMN TEXT LINE {row}")

    pdf.save(pdf_path)
    pdf.close()

    documents = load_pdf_documents(pdf_path, group_name="test")

    assert len(documents) == 2
    assert "LEFT COLUMN TEXT LINE 0" in documents[0].text
    assert "LEFT COLUMN TEXT LINE 3" in documents[0].text
    assert "RIGHT COLUMN TEXT LINE 0" in documents[1].text
    assert documents[0].metadata["page_label"] == "1"
    assert documents[0].metadata["source_column"] == 1
    assert documents[1].metadata["source_column"] == 2
    assert not documents[0].metadata["ocr_used"]


def test_pdf_page_with_three_columns_is_split_in_reading_order(tmp_path: Path):
    pdf_path = tmp_path / "three-columns.pdf"
    pdf = pymupdf.open()
    page = pdf.new_page(width=750, height=800)
    column_x = (40, 280, 520)

    for row in range(4):
        for column, x_position in enumerate(column_x, start=1):
            page.insert_text(
                (x_position, 100 + row * 30),
                f"COLUMN {column} LINE {row}",
            )

    pdf.save(pdf_path)
    pdf.close()

    documents = load_pdf_documents(pdf_path, group_name="test")

    assert len(documents) == 3
    for column, document in enumerate(documents, start=1):
        assert f"COLUMN {column} LINE 0" in document.text
        assert f"COLUMN {column} LINE 3" in document.text
        assert document.metadata["source_column"] == column


def test_scanned_pdf_page_uses_vietnamese_ocr_and_keeps_word_bboxes(
    tmp_path: Path,
    monkeypatch,
):
    group_dir = tmp_path / "scans"
    group_dir.mkdir()
    pdf_path = group_dir / "scan.pdf"
    pdf = pymupdf.open()
    page = pdf.new_page(width=600, height=250)
    page.draw_rect(page.rect, color=(1, 1, 1), fill=(1, 1, 1))
    pdf.save(pdf_path)
    pdf.close()

    class FakeDeepDocOCR:
        drop_score = 0.5

        def __call__(self, image):
            assert image.shape == (750, 1800, 3)
            return [
                (
                    [[240, 600], [900, 600], [900, 660], [240, 660]],
                    ("CỘNG TY CỔ PHẦN VÀ HỒ SƠ PHÁP LÝ", 1.0),
                )
            ]

    monkeypatch.setattr(
        pdf_ingestion,
        "_get_deepdoc_ocr",
        lambda: FakeDeepDocOCR(),
    )
    documents = load_pdf_documents(pdf_path, group_name="scans")

    assert len(documents) == 1
    assert documents[0].metadata["ocr_used"]
    assert "CỘNG TY CỔ PHẦN" in documents[0].text
    assert documents[0].metadata["ocr_words"]
    assert documents[0].metadata["ocr_words"][0] == {
        "text": "CỘNG TY CỔ PHẦN VÀ HỒ SƠ PHÁP LÝ",
        "x": 80 / 600,
        "y": 200 / 250,
        "width": 220 / 600,
        "height": 20 / 250,
    }
    review_file = tmp_path / "scans__scan.txt"
    assert review_file.is_file()
    assert "CỘNG TY CỔ PHẦN VÀ HỒ SƠ PHÁP LÝ" in review_file.read_text(
        encoding="utf-8"
    )
    assert "--- Trang 1 | Cột 1 ---" in review_file.read_text(encoding="utf-8")
    assert all(
        0 <= word[coordinate] <= 1
        for word in documents[0].metadata["ocr_words"]
        for coordinate in ("x", "y", "width", "height")
    )

    evidence = find_ocr_evidence_bboxes(
        documents[0].text,
        documents[0].metadata["ocr_words"],
    )
    assert evidence
