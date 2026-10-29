from ingestion import DocumentIngestionPipeline
from evaluation.evaluate_retrieval import benchmark_dataset

pipeline = DocumentIngestionPipeline(data_dir="data")
indices = pipeline.build_indexes()

index = indices["Tác phẩm Lão Hạc"]

questions = [
    "Tác giả truyện ngắn Lão Hạc là ai?",
    "Lão Hạc gọi con chó của mình tên là gì?",
    "Con trai của lão Hạc đi đâu?",
    "Vì sao con trai lão Hạc bỏ đi?",
    "Ai là người kể chuyện trong truyện ngắn Lão Hạc?",
    "Ông giáo có mối quan hệ như thế nào với lão Hạc?",
    "Lão Hạc làm nghề gì để kiếm sống?",
    "Lão Hạc sống trong hoàn cảnh gia đình như thế nào?",
    "Vợ của lão Hạc mất khi nào?",
    "Lão Hạc quyết định bán cậu Vàng vì lý do gì?",
    "Lão Hạc cảm thấy thế nào sau khi bán cậu Vàng?",
    "Lão Hạc sang nhà ông giáo để làm gì?",
    "Lão Hạc gửi ông giáo giữ hộ tài sản gì?",
    "Lão Hạc dành tiền để làm gì cho con trai?",
    "Lão Hạc đã làm gì để chuẩn bị cho cái chết của mình?",
    "Lão Hạc xin Binh Tư thứ gì?",
    "Binh Tư làm nghề gì?",
    "Lão Hạc chết bằng cách nào?",
    "Ai là người chứng kiến những biểu hiện đau đớn của lão Hạc trước khi chết?",
    "Truyện ngắn Lão Hạc được viết bởi nhà văn thuộc giai đoạn văn học nào?"
]

results = benchmark_dataset(index, questions)