"""Kor etiketləyicinin CSV-si ilə müəllif etiketləri arasında uyğunluq və kappa."""
import csv, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from judge_eval import cohen_kappa

ROOT = pathlib.Path(__file__).resolve().parents[1]
LABELS = {"SUPPORTED", "CONTRADICTED", "UNSUPPORTED"}
author = {json.loads(l)["id"]: json.loads(l)["label"]
          for l in open(ROOT / "tests/data/holdout2.jsonl", encoding="utf-8") if l.strip()}

blind = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
pairs = [(author[r["id"]], r["label"].strip().upper()) for r in blind]
bad = [r["id"] for r in blind if r["label"].strip().upper() not in LABELS]
if bad:
    raise SystemExit(f"Etiketsiz və ya yanlış sətirlər: {bad[:5]}")

a, b = zip(*pairs)
print(json.dumps({
    "n": len(pairs),
    "agreement_author_vs_blind": round(sum(x == y for x, y in pairs) / len(pairs), 3),
    "kappa_author_vs_blind": round(cohen_kappa(list(a), list(b)), 3),
}, ensure_ascii=False, indent=2))
