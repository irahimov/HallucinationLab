"""Qərəzlilik: eyni faktın ad/region/cins dəyişmiş versiyası eyni hakim qərarını almalıdır."""
import json, pathlib, sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from faithfulness import judge, ParseError

ROOT = pathlib.Path(__file__).resolve().parents[1]


def safe_judge(claim, context):
    try:
        return judge(claim, context)
    except ParseError:
        return "PARSE_ERROR"


def main():
    pairs = [json.loads(l) for l in open(ROOT / "tests/data/bias_pairs.jsonl", encoding="utf-8")]
    rows, flips, compared, correct = [], 0, 0, 0
    for p in pairs:
        a = safe_judge(p["claim_a"], p["context_a"])
        b = safe_judge(p["claim_b"], p["context_b"])
        row = {"id": p["id"], "group": p["group"], "expected": p["expected"], "a": a, "b": b}
        if a != "PARSE_ERROR" and b != "PARSE_ERROR":
            compared += 1
            flip = a != b
            flips += flip
            correct += (a == p["expected"]) + (b == p["expected"])
            row["flip"] = flip
        rows.append(row)
        print(row, flush=True)
    print(json.dumps({
        "pairs": len(pairs),
        "compared": compared,
        "flip_rate": round(flips / compared, 3) if compared else None,
        "accuracy_on_compared_claims": round(correct / (2 * compared), 3) if compared else None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
