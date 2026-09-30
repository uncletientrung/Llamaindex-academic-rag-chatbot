from liteparse import LiteParse

pdf_path = "quyet_dinh.pdf"

parser = LiteParse(
    ocr_enabled=True,
    output_format="markdown",
)

result = parser.parse(pdf_path)

print("=" * 80)
print("MARKDOWN RESULT")
print("=" * 80)

print(result.text)
