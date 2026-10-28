import shutil
from pathlib import Path

import pymupdf
import pytest
from PIL import Image, ImageDraw, ImageFont

from pdf_ingestion import find_ocr_evidence_bboxes, load_pdf_documents


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


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract executable is not installed")
def test_scanned_pdf_page_is_ocrd_and_keeps_word_bboxes(tmp_path: Path):
    pdf_path = tmp_path / "scan.pdf"
    image = Image.new("RGB", (1200, 500), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    if not font_path.is_file():
        font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = ImageFont.truetype(str(font_path), 48)
    draw.text((60, 120), "CONG TY CO PHAN VA HO SO PHAP LY", fill="black", font=font)

    image_path = tmp_path / "scan.png"
    image.save(image_path)
    pdf = pymupdf.open()
    page = pdf.new_page(width=600, height=250)
    page.insert_image(page.rect, filename=str(image_path))
    pdf.save(pdf_path)
    pdf.close()

    documents = load_pdf_documents(pdf_path, group_name="scans")

    assert len(documents) == 1
    assert documents[0].metadata["ocr_used"]
    assert "CONG TY" in documents[0].text.upper()
    assert documents[0].metadata["ocr_words"]
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
