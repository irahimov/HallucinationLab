"""Dayanıqlıq: sualın yazılış dəyişiklikləri top-1 parçanı dəyişdirirmi?"""
import json, sys, pathlib
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from retrieval_eval import load_chunks, embed, gold_indices, ROOT

MODELS = [("bge-m3", "", ""), ("nomic-embed-text", "search_document: ", "search_query: ")]


def top1(D, texts, model, qp):
    Q = embed(texts, model, qp)
    return np.argmax(Q @ D.T, axis=1)


def main():
    chunks = load_chunks()
    base = [json.loads(l) for l in open(ROOT / "tests/data/retrieval_questions.jsonl", encoding="utf-8")]
    variants = [json.loads(l) for l in open(ROOT / "tests/data/robust_variants.jsonl", encoding="utf-8")]
    by_id = {q["id"]: q for q in base}
    gold_by_id = {q["id"]: g for q, g in zip(base, gold_indices(base, chunks))}
    out = {}
    for model, dp, qp in MODELS:
        D = embed(chunks, model, dp)
        base_top = top1(D, [q["question"] for q in base], model, qp)
        base_map = {q["id"]: int(base_top[i]) for i, q in enumerate(base)}
        v_top = top1(D, [v["question"] for v in variants], model, qp)
        same = sum(int(v_top[i]) == base_map[v["orig"]] for i, v in enumerate(variants))
        hit = sum(int(v_top[i]) == gold_by_id[v["orig"]] for i, v in enumerate(variants))
        out[model] = {
            "n_variants": len(variants),
            "top1_same_as_original": round(same / len(variants), 3),
            "variant_hit@1": round(hit / len(variants), 3),
        }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
