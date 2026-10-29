# HallucinationLab

Evaluates an LLM-as-judge used for faithfulness checking of RAG answers, and reports where it fails. Local models only (Ollama).

## Problem
A RAG answer can sound correct while claiming things the retrieved context does not support. A faithfulness score is only as good as the judge that produces it, so the judge is validated first.

## Components
- `src/faithfulness.py`: claim splitting, judge (qwen3:4b, temperature 0, thinking stripped), strict verdict parser that raises on anything other than SUPPORTED / CONTRADICTED / UNSUPPORTED.
- `src/judge_eval.py`: agreement, Cohen's kappa, confusion, parse-error counts against hand labels. Refuses to run on unlabelled rows.
- `src/retrieval_eval.py`: hit@1, hit@3, MRR for bge-m3 and nomic-embed-text.
- `src/unanswerable_eval.py`: refusal rate on questions the corpus cannot answer.
- `src/robustness_eval.py`: top-1 stability under typos, mixed AZ/EN and paraphrase.
- `src/bias_eval.py`: flip rate and accuracy on counterfactual pairs (name, region, gender).
- `src/repeat_eval.py`: verdict stability across repeated runs.

All labels and questions were written by the author and committed before the corresponding evaluation was run.

## Results

### Judge vs hand labels (`tests/data/judge_labels.jsonl`, 30 claims)
| Metric | Value |
|---|---|
| Strict agreement (parse errors counted as wrong) | 0.80 (24/30) |
| Agreement on parsed verdicts | 0.96 (24/25) |
| Cohen's kappa (parsed) | 0.94 |
| Parse errors | 5 (4 on UNSUPPORTED) |

Two labels (s18, s28) are under review and have not been changed.

### Judge vs hand labels, second set (`tests/data/holdout2.jsonl`, 20 claims)
| Metric | Value |
|---|---|
| Agreement | 0.30 (6/20) |
| Cohen's kappa | -0.11 |
| Parse errors | 0 |

The author re-read the 14 disagreements after seeing the judge output and found the context supports the judge in every case (`results/holdout2_review.md`). This points to label error, not judge error. The re-read is not independent. The headline number stays at 0.30 until a blind second annotator relabels the set.

Note: the two label sets disagree strongly (0.80 vs 0.30). The judge's reliability is not established.

### Retrieval (`results/retrieval_console.log`)
| Model | hit@1 | hit@3 | MRR |
|---|---|---|---|
| bge-m3 | 1.00 | 1.00 | 1.00 |
| nomic-embed-text | 0.87 | 0.97 | 0.93 |

Corpus: 17 chunks. Questions: 30, written by the author. Ceiling effect likely.

### Unanswerable questions (`results/unanswerable_console.log`)
Refusal rate 0.90 (9/10). Failure: u05 ("highest credit rate"), the model answered 14% from a context that only states a 14% rate and does not say it is the highest.

### Robustness (`results/robustness_console.log`)
| Model | Top-1 stability | Variant hit@1 |
|---|---|---|
| bge-m3 | 1.00 | 1.00 |
| nomic-embed-text | 0.78 | 0.89 |

n = 9 variants.

### Counterfactual bias (`results/bias_console.log`)
Pairs: 5. Compared: 4 (one parse error on p5, context A). Flip rate 0.25 (p3: Gəncə SUPPORTED, Bakı UNSUPPORTED). Accuracy on compared claims 0.875. One flip in four pairs is not evidence of systematic bias. It is an observed inconsistency with unknown cause.

### Repeat stability (`results/repeat_console.log`)
5 of 5 claims gave the same verdict in all 5 runs at temperature 0. Stability is not correctness: these claims were also in the first labelled set, and the verdicts matched the labels.

## Limitations
- All data is synthetic, short, and written by one author. No real bank documents.
- Labels are not independently checked. Holdout2 disagreement is unresolved.
- Retrieval corpus is 17 chunks: too small to rank embedding models reliably.
- Robustness (9) and bias (4 compared pairs) sets are too small for rates to be meaningful.
- One judge model, one prompt. The prompt was not tuned on these sets.
- Parse failures occur on UNSUPPORTED claims and are counted, not hidden.
- Refusal detection in `unanswerable_eval.py` is keyword-based. It was checked by reading the answers.

## Not done
- RAGAS comparison: packages installed, not configured for local Ollama.
- Blind second annotator for holdout2.
- Resolution of s18 and s28.
- Real document corpus.

## Process notes
- An early run on unlabelled `holdout.jsonl` was discarded and not reported. A guard now prevents running the judge on unlabelled rows.
- Labels were committed before each judge run, and the commit history shows the order.
