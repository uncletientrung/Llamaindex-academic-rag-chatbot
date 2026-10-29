
from pathlib import Path
from pdf_ingestion import load_pdf_documents

def export_pdf_ocr_to_txt():
    # Đường dẫn file PDF đầu vào
    pdf_path = Path("data/Tác phẩm Lão Hạc/testOCR.pdf")

    # File TXT đầu ra
    output_path = Path("data/Tác phẩm Lão Hạc/testOCR_ocr.txt")

    if not pdf_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")

    # Đọc PDF bằng pipeline OCR hiện tại
    documents = load_pdf_documents(
        pdf_path,
        group_name="Tác phẩm Lão Hạc"
    )

    # Ghép nội dung của toàn bộ documents
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i, doc in enumerate(documents, start=1):
            f.write(f"\n{'=' * 30}\n")
            f.write(f"DOCUMENT {i}\n")
            f.write(f"{'=' * 30}\n\n")
            f.write(doc.get_content())
            f.write("\n")

    print(f"Đã xuất {len(documents)} documents ra:")
    print(output_path.resolve())

if __name__ == "__main__":
    export_pdf_ocr_to_txt()
