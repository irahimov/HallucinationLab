"""Hakimi əl etiketləri ilə müqayisə edir: uyğunluq, Cohen kappa, xəta sayları."""
import json, sys, time, pathlib
from collections import Counter

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from faithfulness import judge, ParseError

LABELS = ("SUPPORTED", "CONTRADICTED", "UNSUPPORTED")


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    labels = set(a) | set(b)
    p_observed = sum(x == y for x, y in zip(a, b)) / n
    p_expected = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    if p_expected == 1:
        return 1.0
    return (p_observed - p_expected) / (1 - p_expected)


def run(labels_path: str, out_path: str) -> dict:
    rows = [json.loads(l) for l in open(labels_path, encoding="utf-8") if l.strip()]
    bad = [r.get("id") for r in rows if r.get("label") not in LABELS]
    if bad:
        raise SystemExit(f"Etiketsiz və ya yanlış etiketli nümunələr var (ilk 5): {bad[:5]}. Hakim işlədilmədi.")
    records = []
    with open(out_path, "w", encoding="utf-8") as out:
        for r in rows:
            t = time.time()
            try:
                verdict = judge(r["claim"], r["context"])
            except ParseError:
                verdict = "PARSE_ERROR"
            except requests.RequestException:
                verdict = "TIMEOUT_OR_CONN"
            rec = {"id": r["id"], "human": r["label"], "judge": verdict,
                   "seconds": round(time.time() - t, 1)}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()  # kəsilsə, tamamlanmış nəticələr itmir
            records.append(rec)
            print(rec, flush=True)

    # Yalnız hakimin üç etiketdən birini verdiyi nümunələr müqayisəyə girir.
    # Xətalar gizlədilmir, ayrıca sayılır.
    valid = [r for r in records if r["judge"] in LABELS]
    human = [r["human"] for r in valid]
    judged = [r["judge"] for r in valid]

    return {
        "n_total": len(records),
        "n_compared": len(valid),
        "parse_errors": sum(r["judge"] == "PARSE_ERROR" for r in records),
        "timeouts_or_conn": sum(r["judge"] == "TIMEOUT_OR_CONN" for r in records),
        "agreement": round(sum(h == j for h, j in zip(human, judged)) / len(valid), 3) if valid else None,
        "kappa": round(cohen_kappa(human, judged), 3) if valid else None,
        "avg_seconds": round(sum(r["seconds"] for r in records) / len(records), 1),
        "confusion_human_vs_judge": {
            f"{h}->{j}": c for (h, j), c in sorted(Counter(zip(human, judged)).items())
        },
    }


if __name__ == "__main__":
    labels = sys.argv[1] if len(sys.argv) > 1 else "tests/data/judge_labels.jsonl"
    out = sys.argv[2] if len(sys.argv) > 2 else "results/judge_eval.jsonl"
    print(json.dumps(run(labels, out), indent=2, ensure_ascii=False))
