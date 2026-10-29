"""Təkrarlanma: eyni iddia N dəfə hakimə verilir. Neçə qaçışda eyni cavab çıxır?"""
import json, pathlib, sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from faithfulness import judge, ParseError

ROOT = pathlib.Path(__file__).resolve().parents[1]
IDS = ["s01", "s02", "s03", "s12", "s20"]
N = 5

rows = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "tests/data/judge_labels.jsonl", encoding="utf-8")}
stable = 0
for i in IDS:
    r = rows[i]
    seen = []
    for _ in range(N):
        try:
            seen.append(judge(r["claim"], r["context"]))
        except ParseError:
            seen.append("PARSE_ERROR")
    is_stable = len(set(seen)) == 1
    stable += is_stable
    print(i, {"label": r["label"], "verdicts": dict(Counter(seen)), "stable": is_stable}, flush=True)
print(json.dumps({"stable_claims": stable, "of": len(IDS), "runs_per_claim": N}, ensure_ascii=False))
