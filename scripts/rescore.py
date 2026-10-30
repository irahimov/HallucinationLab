"""Mövcud hakim nəticələrini verilmiş etiket faylı ilə yenidən hesablayır (hakim yenidən işə salınmır)."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from judge_eval import cohen_kappa

LABELS = {"SUPPORTED", "CONTRADICTED", "UNSUPPORTED"}
labels_path = sys.argv[1]
gold = {json.loads(l)["id"]: json.loads(l)["label"] for l in open(labels_path, encoding="utf-8") if l.strip()}
recs = [json.loads(l) for l in open("results/judge_eval.jsonl", encoding="utf-8")]

strict = sum(gold[r["id"]] == r["judge"] for r in recs) / len(recs)
parsed = [r for r in recs if r["judge"] in LABELS]
h = [gold[r["id"]] for r in parsed]
j = [r["judge"] for r in parsed]
print(json.dumps({
    "labels": labels_path,
    "n": len(recs),
    "strict_agreement": round(strict, 3),
    "parsed_n": len(parsed),
    "parsed_agreement": round(sum(a == b for a, b in zip(h, j)) / len(parsed), 3),
    "kappa_parsed": round(cohen_kappa(h, j), 3),
}, ensure_ascii=False, indent=2))
