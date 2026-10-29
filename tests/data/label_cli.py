import json, sys

path = sys.argv[1]
rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
keys = {"s": "SUPPORTED", "c": "CONTRADICTED", "u": "UNSUPPORTED"}

def save():
    with open(path, "w", encoding="utf-8") as f:
        for x in rows:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

for r in rows:
    if r["label"]:
        continue
    print(f"\n[{r['id']}]\nKONTEKST: {r['context']}\nİDDİA: {r['claim']}")
    while True:
        a = input("s=SUPPORTED  c=CONTRADICTED  u=UNSUPPORTED  q=çıxış > ").strip().lower()
        if a == "q":
            save(); sys.exit(0)
        if a in keys:
            r["label"] = keys[a]
            save()
            break
print("Bütün etiketlər yazıldı.")
