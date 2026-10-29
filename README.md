# HallucinationLab

Measures whether an LLM judge can be trusted to check claims against retrieved context.

## Problem
A RAG answer can sound correct while containing claims the context does not support. Faithfulness scores depend on a judge model, so the judge itself has to be validated before its scores mean anything.

## Method
1. Split an answer into sentence-level claims.
2. Judge each claim against the context with a local LLM (qwen3:4b via Ollama, temperature 0, thinking disabled).
3. The judge must return exactly one of SUPPORTED, CONTRADICTED, UNSUPPORTED. Free text raises `ParseError` and is never counted as UNSUPPORTED.
4. Score = supported claims / all claims.
5. Judge validation: compare judge verdicts with 30 hand-written labels (agreement, Cohen's kappa, confusion matrix).

## Judge validation results (30 labelled claims)

| Metric | Value |
|---|---|
| Strict agreement (parse errors counted as wrong) | 0.80 (24/30) |
| Agreement on parsed verdicts only | 0.96 (24/25) |
| Cohen's kappa (parsed only) | 0.94 |
| Parse errors | 5 (4 on UNSUPPORTED claims) |
| Avg seconds per claim | 32.9 |

Confusion, parsed verdicts only:

| Human \ Judge | SUPPORTED | CONTRADICTED | UNSUPPORTED |
|---|---|---|---|
| SUPPORTED | 11 | 0 | 0 |
| CONTRADICTED | 0 | 9 | 0 |
| UNSUPPORTED | 0 | 1 | 4 |

Interpretation: the judge separates SUPPORTED from CONTRADICTED well on these examples. It is weakest on UNSUPPORTED: it either fails to format the answer (5 parse errors) or labels the claim CONTRADICTED (1 case). The strict score of 0.80 is the honest number. The 0.96 figure is shown only with its denominator.

## Limitations
- 30 examples, all written by the author. Labels have not been checked by a second annotator.
- Two labels are under review (s18, s28), see `results/` notes. Changing them would require a new label version.
- Synthetic, short contexts in one domain (retail banking rules). Not representative of real documents.
- One judge model, one prompt, temperature 0. Temperature 0 does not guarantee identical output: repeated runs showed identical verdicts on the Stage 2 example only (3 runs).
- Judge output sometimes contains reasoning text before the answer; the parser strips text before `</think>` and rejects anything else.
- Prompt was not tuned on this set. Any future prompt change must be evaluated on a new set.

## Not in scope
Not a production faithfulness system. No NLI model comparison yet. No RAGAS comparison yet.

## Holdout 2 (20 medium-length claims)

Labels were written by the author before the judge was run and committed first. The judge was then run once.

| Metric | Value |
|---|---|
| Strict agreement | 0.30 (6/20) |
| Cohen's kappa | -0.11 |
| Parse errors | 0 |

On a re-read of the 14 disagreements, the context supports the judge's verdict in every case (see `results/holdout2_review.md`). This suggests the labels are at fault, not the judge. However, that re-read was done after seeing the judge output and by the author alone, so it is not independent. The headline number stays at 0.30 until a blind second annotator has relabelled the set.

Process note: an earlier run on `holdout.jsonl` was started with unlabelled rows. Its output was discarded and not reported. A guard now refuses to run the judge on unlabelled rows.

Open items: s18 and s28 in the first set are still unresolved. The first set (0.80) and holdout 2 (0.30) differ a lot, so the judge's reliability is not yet established.
