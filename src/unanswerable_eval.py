"""Cavabsız suallar: model yalnız kontekstə görə cavab verməli, cavab yoxdursa imtina etməlidir."""
import json, pathlib, sys
import numpy as np
import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from retrieval_eval import load_chunks, embed, ROOT

GEN_URL = "http://localhost:11434/api/chat"
GEN_MODEL = "qwen3:4b"
REFUSAL_MARKERS = ["yoxdur", "bilmirəm", "tapılmadı", "cavab verə bilmə", "müəyyən edə bilmə",
                   "not contain", "does not", "not mention", "not provided"]

PROMPT = """Answer the question using ONLY the context below.
If the context does not contain the answer, reply exactly: Bu sualın cavabı verilən mətndə yoxdur.

Context: {context}
Question: {question}"""


def generate(context, question):
    r = requests.post(GEN_URL, json={
        "model": GEN_MODEL, "stream": False, "think": False,
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": PROMPT.format(context=context, question=question)}],
    }, timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"].rsplit("</think>", 1)[-1].strip()


def is_refusal(answer: str) -> bool:
    a = answer.lower()
    return any(m in a for m in REFUSAL_MARKERS)


def main():
    chunks = load_chunks()
    D = embed(chunks, "bge-m3")
    qs = [json.loads(l) for l in open(ROOT / "tests/data/unanswerable.jsonl", encoding="utf-8")]
    results = []
    for q in qs:
        qv = embed([q["question"]], "bge-m3")[0]
        top = chunks[int(np.argmax(D @ qv))]
        ans = generate(top, q["question"])
        results.append({"id": q["id"], "refused": is_refusal(ans), "answer": ans})
        print(results[-1], flush=True)
    rate = sum(r["refused"] for r in results) / len(results)
    print(json.dumps({"n": len(results), "refusal_rate": round(rate, 3)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
