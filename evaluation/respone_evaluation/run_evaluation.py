import csv
import json
from pathlib import Path

from test import RAGService
from evaluators import build_evaluators


DATASET_PATH = Path("evaluation/response_evaluation/dataset.json")

RESULT_PATH = Path("evaluation/response_evaluation/results/evaluation.csv")
    
def main():
    rag = RAGService()
    evaluators = build_evaluators()

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for i, item in enumerate(dataset, start=1):
        query = item["query"]
        reference = item.get("reference")
        group = item.get("group", "all") # Nếu không có thuộc tính group thì trả về all

        print(f"[{i}/{len(dataset)}] {query}")

        try:
            result = rag.answer_with_context(
                question=query,
                group=group,
            )

            contexts = result["contexts"]
            response = result["response"]

            row = {
                "query": query,
                "reference": reference or "",
                "response": response,
                "contexts": json.dumps(
                    contexts,
                    ensure_ascii=False,
                ),
            }

            # Không có context thì không thể chấm đầy đủ các tiêu chí dựa trên context.
            if not contexts:
                row["status"] = "no_context"
                rows.append(row)
                continue

            # Faithfulness
            eval_result = evaluators["faithfulness"].evaluate(
                query=query,
                contexts=contexts,
                response=response,
            )
            row["faithfulness_score"] = eval_result.score
            row["faithfulness_feedback"] = eval_result.feedback

            # Answer Relevancy
            eval_result = evaluators["answer_relevancy"].evaluate(
                query=query,
                response=response,
            )
            row["answer_relevancy_score"] = eval_result.score
            row["answer_relevancy_feedback"] = eval_result.feedback

            # Context Relevancy
            eval_result = evaluators["context_relevancy"].evaluate(
                query=query,
                contexts=contexts,
            )
            row["context_relevancy_score"] = eval_result.score
            row["context_relevancy_feedback"] = eval_result.feedback

            # Chỉ chấm hai tiêu chí này khi có đáp án chuẩn
            if reference:
                # Correctness 
                eval_result = evaluators["correctness"].evaluate(
                    query=query,
                    response=response,
                    reference=reference,
                )
                row["correctness_score"] = eval_result.score
                row["correctness_feedback"] = eval_result.feedback

                #Semantic Similarity
                eval_result = evaluators[
                    "semantic_similarity"
                ].evaluate(
                    response=response,
                    reference=reference,
                )
                row["semantic_similarity_score"] = eval_result.score
                row["semantic_similarity_feedback"] = (
                    eval_result.feedback
                )

            row["status"] = "evaluated"
            rows.append(row)

        except Exception as exc:
            print(f"Lỗi khi đánh giá câu hỏi: {exc}")
            rows.append({
                "query": query,
                "reference": reference or "",
                "status": "error",
                "error": str(exc),
            })

    # Ghi toàn bộ cột, kể cả các cột có thể không xuất hiện
    # ở một số mẫu vì thiếu reference hoặc gặp lỗi.
    columns = sorted({
        key
        for row in rows
        for key in row
    })

    with open(RESULT_PATH, "w", newline="", encoding="utf-8-sig",) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Đã lưu kết quả tại: {RESULT_PATH}")


if __name__ == "__main__":
    main()