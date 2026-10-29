import json, sys
from collections import Counter

LABELS = {"SUPPORTED", "CONTRADICTED", "UNSUPPORTED"}
path = sys.argv[1] if len(sys.argv) > 1 else "tests/data/judge_labels.jsonl"

rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
errors = []
for r in rows:
    for key in ("id", "context", "claim", "label"):
        if not r.get(key):
            errors.append(f"{r.get('id', '?')}: '{key}' boşdur")
    if r.get("label") not in LABELS:
        errors.append(f"{r.get('id', '?')}: etiket düzgün deyil: {r.get('label')!r}")

ids = [r.get("id") for r in rows]
if len(ids) != len(set(ids)):
    errors.append("təkrarlanan id var")
if len(rows) < 30:
    errors.append(f"ən azı 30 nümunə lazımdır, indi {len(rows)}")

print("paylanma:", dict(Counter(r.get("label") for r in rows)))
if errors:
    print("XƏTALAR:"); print("\n".join(errors)); sys.exit(1)
print(f"OK: {len(rows)} nümunə")
