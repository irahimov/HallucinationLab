# HallucinationLab

Evaluates an LLM-as-judge used for faithfulness checking of RAG answers, and reports where it fails. Local models only (Ollama, qwen3:4b as judge).

## Problem

A RAG answer can sound correct while claiming things the retrieved context does not support. A faithfulness score is only as good as the judge that produces it, so the judge is validated before its scores are used.

## Components

- `src/faithfulness.py`: claim splitting, judge (qwen3:4b, temperature 0, thinking disabled), and a strict verdict parser that raises `ParseError` on anything other than SUPPORTED, CONTRADICTED or UNSUPPORTED. Free text is never counted as UNSUPPORTED.
- `src/judge_eval.py`: agreement, Cohen's kappa, confusion matrix and error counts against hand labels. Refuses to run on unlabelled rows.
- `src/retrieval_eval.py`: hit@1, hit@3 and MRR for bge-m3 and nomic-embed-text.
- `src/unanswerable_eval.py`: refusal rate on questions the corpus cannot answer.
- `src/robustness_eval.py`: top-1 stability under typos, mixed Azerbaijani/English and paraphrase.
- `src/bias_eval.py`: flip rate and accuracy on counterfactual pairs.
- `src/repeat_eval.py`: verdict stability across repeated runs.
- `tests/`: 10 unit tests for splitting, parsing, kappa and retrieval metrics.

All labels and questions were written by the author and committed before the corresponding evaluation was run. Commit order is in the git history.

## Results

### 1. Judge vs hand labels, set 1 (`tests/data/judge_labels.jsonl`, 30 claims)

| Metric | Value |
|---|---|
| Strict agreement (parse errors counted as wrong) | 0.80 (24/30) |
| Agreement on parsed verdicts only | 0.96 (24/25) |
| Cohen's kappa (parsed only) | 0.94 |
| Parse errors | 5 (4 on UNSUPPORTED claims) |

Two labels (s18, s28) are under review. They have not been changed. The review is recorded in the git history; any change would go into a new `judge_labels_v2.jsonl`.

### 2. Judge vs hand labels, set 2 (`tests/data/holdout2.jsonl`, 20 claims)

| Metric | Value |
|---|---|
| Agreement | 0.30 (6/20) |
| Cohen's kappa | -0.11 |
| Parse errors | 0 |

After seeing the judge output, the author re-read the 14 disagreements and found that the context supports the judge's verdict in every case (`results/holdout2_review.md`). This points to label error rather than judge error. However, this re-read was done by the author after seeing the judge output, so it is not independent. The headline figure stays at 0.30 until a blind second annotator has relabelled the set.

The two label sets disagree strongly (0.80 vs 0.30). The judge's reliability is therefore not established.

### 3. Retrieval (`results/retrieval_console.log`)

| Model | hit@1 | hit@3 | MRR |
|---|---|---|---|
| bge-m3 | 1.00 | 1.00 | 1.00 |
| nomic-embed-text | 0.87 | 0.97 | 0.93 |

Corpus: 17 chunks. Questions: 30, written by the author. The bge-m3 result is likely a ceiling effect of a small corpus and author-written questions, so it shows direction, not capability.

### 4. Unanswerable questions (`results/unanswerable_console.log`, `results/rerun_u05.log`)

Refusal rate 0.90 (9/10). The failure on u05 ("highest credit rate") reproduced in all three reruns: the model answered "14%". The context states 14% as a rate but does not say it is the highest. This is a stable finding, not noise.

### 5. Robustness (`results/robustness_console.log`)

| Model | Top-1 stability | Variant hit@1 |
|---|---|---|
| bge-m3 | 1.00 | 1.00 |
| nomic-embed-text | 0.78 | 0.89 |

n = 9 variants. Too small for firm conclusions.

### 6. Counterfactual bias: inconclusive (`results/bias_console.log`, `results/rerun_p3.log`, `results/p3_control.log`)

Five pairs, author-written. Pair p3 (Gəncə/Bakı) gave a flip in one pipeline run: SUPPORTED for Gəncə, UNSUPPORTED for Bakı. Repeated runs did not reproduce it. In a control with the exact pipeline prompt, Gəncə returned PARSE_ERROR three times, and Bakı returned UNSUPPORTED, PARSE_ERROR and UNSUPPORTED. Four of six control calls produced no usable label.

The flip is therefore not reported as evidence of bias. Both p3 claims also generalise their context by dropping "kredit". Under a strict context-only reading both would be UNSUPPORTED, so the author labels (SUPPORTED) are themselves questionable and were not changed. Five pairs are too few to estimate bias rates.

### 7. Repeat stability (`results/repeat_console.log`)

5 of 5 claims gave the same verdict in all 5 runs at temperature 0. Stability is not correctness: all five claims were in the labelled set, and their verdicts matched the labels in every run.

## Format failures

The judge does not reliably return a single label. This is the most consistent finding in the project.

| Test | Parse errors |
|---|---|
| Judge vs set 1 (30 claims) | 5 |
| Judge vs set 2 (20 claims) | 0 |
| Bias control (6 calls) | 4 |
| p3 rerun | 1 parse error, 2 timeouts (120 s read timeout) |

These counts are the ones recorded in `results/`. They have not been aggregated across all logs.

## Limitations

- All data is synthetic, short and written by one author. No real bank documents.
- Labels are not independently checked. The set 1 vs set 2 disagreement is unresolved.
- Retrieval corpus is 17 chunks, too small to rank embedding models reliably.
- Robustness (9 variants) and bias (5 pairs) sets are too small for rates to be meaningful.
- One judge model, one prompt. The prompt was not tuned on these sets.
- Judge format failures are frequent, especially on UNSUPPORTED claims. Not yet resolved. Any prompt change must be evaluated on a new set.
- Ollama read timeouts (120 s) occurred during the p3 rerun. Their cause was not investigated.
- Refusal detection in `unanswerable_eval.py` is keyword-based and was checked by reading the answers.

## Not done

- RAGAS comparison: packages installed, not configured for local Ollama.
- Blind second annotator for set 2.
- Resolution of labels s18 and s28.
- Aggregating PARSE_ERROR counts across all logs.
- Investigating raw judge output on format failures (is `</think>` closed, is the answer too long?).
- Real document corpus.

## Process notes

- An early judge run on unlabelled `holdout.jsonl` was discarded and not reported. A guard now prevents running the judge on unlabelled rows.
- The p3 rerun commit message ("three times each") overstated the runs. Only two p3 reruns completed, both with a flip. The commit message remains in history and is corrected here.
- Earlier wording in this README called the Bakı verdict a "clear judge error" and presented a 0.25 flip rate as bias evidence. Both statements are withdrawn.
- A first-pass reading of the 14 holdout2 disagreements was done after seeing judge output. It is recorded as author reading, not independent review.
