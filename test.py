import fitz

from llama_index.core import Document


pdf = fitz.open("quyet_dinh.pdf")

documents = []

for page_number, page in enumerate(pdf):

    text = page.get_text("text")

    print(f"Trang {page_number + 1}: {len(text)} ký tự")

    if text.strip():
        documents.append(
            Document(
                text=text,
                metadata={
                    "page": page_number + 1
                }
            )
        )

print("Tổng documents:", len(documents))

print("\n===== TEST TEXT =====")
print(documents[0].text[:3000])
