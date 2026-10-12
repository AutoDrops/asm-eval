First public release of the ASM evaluation results.

**What is included**
- Results of two experiments, the per-question / per-scenario data behind them, a standalone scorer (`eval/score.py`, Python standard library only) that reproduces the supported metrics described below, a synthetic toy demo of the scoring rules (`eval/demo/`), and a PDF report.
- The ASM implementation itself is not included.

**Results**
- EXP-001F, internal closed set c3 (built by the author; 216 questions per method, pre-registered, same Qwen3-235B reader): ASM v4.2 85.6%, full history 72.7%, BM25 56.5%, LLM summary 42.1%, with about 12.6x less context than full history.
- EXP-002, LongMemEval ORACLE, 100-question stratified subset (not the official 500-question result; GPT-4o judge): full history 66%, BM25 58%, ASM 49%, LLM summary 49%. ASM is weaker than BM25 and full history on long-term personal memory.

Preliminary study by an independent researcher (Ukraine); not independently reproduced. See the Limitations section of the README.

License: MIT for code and LongMemEval-derived content; CC BY 4.0 for our contributions (see THIRD_PARTY_NOTICES.md).

`python3 eval/score.py` reproduces c3 per-method accuracies and paired differences, sign-flip CIs/p-values and scenario counts; LongMemEval subset accuracies, Wilson CIs, mean context estimates, mean per-question evidence recall, paired bootstrap CIs, McNemar p-values, multi-session and abstention counts. c3 marginal bootstrap CIs are independently reproducible from the released scenario counts: use one shared Python RNG seeded 1001, 20,000 draws per method in order ASM / full history / BM25 / summary / diagnostic, sampling 12 scenarios with replacement per draw in sorted scenario order; sort the resulting accuracies and take percentile indices 499 and 19499 (zero-based).

The following are reported from private run logs and are not reproducible from released data: c3 context-token sizes and the inputs to the 12.6x ratio, c3 per-type counts, the decision subset, extraction diagnostics, accounting/retry exclusion and costs.

Code in `eval/` is released under MIT (`LICENSE`). Our evaluation labels and aggregate measurements, report and README text are under CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`) to the extent we hold the rights. No LongMemEval dialogues or conversation histories are redistributed. `data/exp002_lme_oracle100_labels.jsonl` contains question IDs, question types and reader answers derived from LongMemEval, including answers that may quote benchmark text. This LongMemEval-derived content is under MIT, not CC BY 4.0; see `THIRD_PARTY_NOTICES.md`.
