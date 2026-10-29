"""Retrieval testi: hit@1, hit@3, MRR. Gold parça = açar sözünü ehtiva edən tək parça."""
import json, pathlib
import numpy as np
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
EMBED_URL = "http://localhost:11434/api/embed"
SOURCES = ["tests/data/judge_labels.jsonl", "tests/data/holdout2.jsonl"]


def load_chunks() -> list[str]:
    seen, chunks = set(), []
    for name in SOURCES:
        for line in open(ROOT / name, encoding="utf-8"):
            ctx = json.loads(line)["context"]
            if ctx not in seen:
                seen.add(ctx)
                chunks.append(ctx)
    return chunks


def embed(texts, model, prefix=""):
    r = requests.post(EMBED_URL, json={"model": model, "input": [prefix + t for t in texts]}, timeout=300)
    r.raise_for_status()
    v = np.array(r.json()["embeddings"], dtype=float)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def metrics(ranks: list[int]) -> dict:
    n = len(ranks)
    return {
        "n": n,
        "hit@1": round(sum(r <= 1 for r in ranks) / n, 3),
        "hit@3": round(sum(r <= 3 for r in ranks) / n, 3),
        "mrr": round(sum(1 / r for r in ranks) / n, 3),
    }


def gold_indices(questions, chunks):
    gold = []
    for q in questions:
        hits = [i for i, c in enumerate(chunks) if q["key"] in c]
        if len(hits) != 1:
            raise SystemExit(f"{q['id']}: açar {q['key']!r} {len(hits)} parçada tapıldı. Düzəlt.")
        gold.append(hits[0])
    return gold


def run(model, doc_prefix="", q_prefix=""):
    chunks = load_chunks()
    questions = [json.loads(l) for l in open(ROOT / "tests/data/retrieval_questions.jsonl", encoding="utf-8")]
    gold = gold_indices(questions, chunks)
    D = embed(chunks, model, doc_prefix)
    Q = embed([q["question"] for q in questions], model, q_prefix)
    order = np.argsort(-(Q @ D.T), axis=1)
    ranks = [int(np.where(order[i] == g)[0][0]) + 1 for i, g in enumerate(gold)]
    return {"model": model, "n_chunks": len(chunks), **metrics(ranks)}


if __name__ == "__main__":
    out = {
        "bge-m3": run("bge-m3"),
        "nomic-embed-text": run("nomic-embed-text", "search_document: ", "search_query: "),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
