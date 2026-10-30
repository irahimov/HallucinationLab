"""holdout2-dən kor etiketləmə vərəqi: etiketlər və hakim nəticəsi çıxarılır, sıra qarışdırılır."""
import csv, json, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = [json.loads(l) for l in open(ROOT / "tests/data/holdout2.jsonl", encoding="utf-8") if l.strip()]
random.Random(42).shuffle(rows)

out = ROOT / "results/blind_sheet.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "context", "claim", "label"])
    w.writeheader()
    for r in rows:
        w.writerow({"id": r["id"], "context": r["context"], "claim": r["claim"], "label": ""})
print(f"yazıldı: {out} ({len(rows)} sətir)")
