# Adaptive Semantic Memory: Strong Project-State Results, Mixed Generalization to Long-Term Personal Memory

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23279014.svg)](https://doi.org/10.5281/zenodo.23279014)

Bohdan Chernyshuk, independent researcher, Ukraine. radoautodrops@gmail.com

Evaluation results, scoring rules, a standalone scoring script and a toy demo for ASM, a memory layer for long-running LLM agents. **The ASM implementation is not included.** Preliminary study, not independently reproduced.

**EXP-001F - internal closed set c3** (built by the author; 216 questions per method, same Qwen3-235B reader):

| Method | Accuracy | Mean context, tokens |
|---|---|---|
| **ASM v4.2** | **85.6%** | **489** |
| Full history | 72.7% | 6,164 |
| BM25 | 56.5% | 294 |
| LLM summary | 42.1% | 472 |

**EXP-002 - LongMemEval ORACLE, 100-question stratified subset** (public benchmark; not the official 500-question result; GPT-4o judge):

| Method | Accuracy | Mean context, tokens |
|---|---|---|
| Full history | **66%** | 7,683 |
| BM25 | 58% | 995 |
| **ASM v4.2** | 49% | 949 |
| LLM summary | 49% | 305 |

Strong on project/agent state (internal set), weaker than BM25 and full history on long-term personal memory (public subset). Details, confidence intervals and limitations below.

## The problem

In long conversations an agent loses track of what is true *now*: which facts were updated or refuted, which decisions were cancelled or replaced, which goals and constraints still apply, and why things happened. The usual workaround is to re-send the whole history on every call. That gets more expensive as the conversation grows and does not remove the errors: in these tests the full-history reader still repeats stale values and follows instructions planted inside quoted documents.

## What ASM does (high level only)

ASM keeps a compact, source-linked record of the current state of a conversation (facts, goals, constraints and decisions, each with a status and the turn it came from). For each question the reader model gets only the relevant part of this state within a fixed token budget (512 tokens in EXP-001F, 1,024 in EXP-002) instead of the raw history. Quoted or forwarded material is kept apart from the user's own goals and rules. Implementation details (memory format, extraction, revision logic) are intentionally not part of this release.

## Result 1 - EXP-001F: internal closed set c3 (positive)

- **Internal closed set c3**, built by the author: 12 synthetic long-dialogue scenarios, 18 questions each = **216 questions per method**. Generated after the method was frozen; checked for no overlap with earlier sets. Success criteria pre-registered in git before the first paid call.
- Same reader for all methods: Qwen3-235B-A22B (`qwen/qwen3-235b-a22b-2507`, reasoning off), temperature 0, strict JSON output. Paired comparison on identical questions.

| Method | Accuracy (216 q) | 95% CI, scenario-clustered bootstrap | Mean context, tokens |
|---|---|---|---|
| **ASM v4.2** | **85.6%** | 84.3-87.0 | **489** |
| Full history | 72.7% | 68.5-76.9 | 6,164 |
| BM25 retrieval | 56.5% | 53.2-59.7 | 294 |
| LLM summary | 42.1% | 34.7-49.1 | 472 |

ASM used about **12.6x less context** than full history (489 vs 6,164 tokens), as reported from private run logs; these context measurements are not in the release.

Diagnostic condition: the same reader given ASM-style context built from a hand-made reference memory (no automatic extraction) scored 84.7% (CI 82.4-87.0), 0.9 pp below the full ASM pipeline, so on this set extraction was not the accuracy bottleneck.

Paired differences, ASM minus baseline; exact 95% CI from a sign-flip permutation test over the 12 scenarios (all 4,096 sign patterns):

| ASM v4.2 vs | Difference | Exact 95% CI | p (exact, two-sided) | Scenarios better / tied / worse |
|---|---|---|---|---|
| Full history | **+13.0 pp** | +8.4 to +17.8 | 0.00098 | 11 / 1 / 0 |
| BM25 | **+29.2 pp** | +25.6 to +33.3 | 0.00049 | 12 / 0 / 0 |
| LLM summary | **+43.5 pp** | +34.3 to +52.8 | 0.00049 | 12 / 0 / 0 |

Per question type (correct / n), selected (private run logs; counts not released):

| Question type | ASM v4.2 | Full history | BM25 | LLM summary |
|---|---|---|---|---|
| Planted instruction inside a quoted document | **11/12** | 0/12 | 1/12 | 0/12 |
| Multi-step cause | 24/24 | 21/24 | 0/24 | 2/24 |
| Decision lifecycle | 24/24 | 12/24 | 12/24 | 9/24 |
| Look-alike entity names | 12/12 | 10/12 | 3/12 | 7/12 |
| Superseded decision | 10/12 | 12/12 | 11/12 | 4/12 |
| Revising a conclusion after an upstream fact changes | **0/12** | 6/12 | 0/12 | 0/12 |
| Telling an intention from a decision | **0/12** | 2/12 | 0/12 | 0/12 |

Sources: `docs/exp001f-report.md`, `results/exp001f/final-analysis.json` (accuracy, CI, context, per-type), `docs/exp001f-audit.md` (exact paired CIs) in the private project repository.

## Result 2 - EXP-002: LongMemEval ORACLE, 100-question stratified subset (negative)

Frozen ASM v4.2 on a **100-question stratified subset of the LongMemEval ORACLE variant** (cleaned release; stratified by question type and abstention, seed 2002). **This is not the official 500-question result.** Same Qwen3-235B reader for all methods; answers graded with the official LongMemEval GPT-4o judge (`gpt-4o-2024-08-06`, upstream prompts), blind to method. Budget 1,024 tokens (characters / 4) for the compressed methods.

| Method | Accuracy (100 q) | 95% CI (Wilson) | Mean context, tokens (chars / 4) | Evidence recall |
|---|---|---|---|---|
| Full history | **66%** | 56.3-74.5 | 7,683 | 100% |
| BM25 retrieval | 58% | 48.2-67.2 | 995 | 77.5% |
| ASM v4.2 | 49% | 39.4-58.7 | 949 | 40.7% |
| LLM summary | 49% | 39.4-58.7 | 305 | 0%* |

Evidence recall is mean per-question evidence recall over 95 questions per method with non-null recall fractions. It is not the percentage of questions with any evidence present. *The summary rewrites text, so literal-turn recall is zero by construction; this does not measure semantic coverage.

Paired, ASM minus other (stratified bootstrap, 10,000 repeats; exact McNemar):

| Comparison | Difference | 95% CI | McNemar p |
|---|---|---|---|
| ASM - BM25 | -9 pp | -17 to -1 | 0.064 (borderline, not significant at 0.05) |
| ASM - full history | -17 pp | -26 to -8 | 0.0015 |
| ASM - LLM summary | 0 pp | -10 to +10 | 1.0 |

ASM scored 6/27 on multi-session questions, versus 11/27 for BM25 and 17/27 for full history. Its lowest observed type accuracy was single-session-preference (1/6). It abstained correctly on 5 of 6 unanswerable questions (too few for a claim). Mean per-question evidence recall was 40.7% for ASM versus 77.5% for BM25, consistent with evidence selection being a limitation.

Source: `docs/exp002-oracle-report.md`, `results/exp002o/final-analysis.json` (EXP-002 worktree of the private repository).

**The two experiments use different task sets and are not directly comparable.** Together they suggest ASM is promising for agent / project state tracking (cancelled and replaced decisions, provenance, injected instructions), but it is **not** a general personal-memory system yet.

## Limitations (read before citing)

- **Internal benchmark.** EXP-001F uses the internal closed set c3: synthetic, non-English (mixed Ukrainian/Russian) dialogues that I generated, one reader model, and has not been reproduced externally.
- **External benchmark: negative.** On the LongMemEval ORACLE 100-question subset ASM trails BM25 and full history. The S (long-history) variant has not been tested.
- **Decisions not clearly better.** On the 72 decision-related questions of the internal closed set c3 ASM is +2.8 pp over full history, 95% CI -2.8 to +8.3 (includes zero).
- **Failing question types.** Revising a conclusion after an upstream fact changes (0/12) and telling an intention from a decision (0/12).
- **False updates.** The memory-update step's false-update rate on the internal closed set c3 is 20.5% (pre-registered target <= 10%); its recall of decision accept / cancel / replace events is 93.8%.
- **Accounting flag.** 12 API calls in the internal closed set c3 run timed out and were retried. An offline audit confirmed all 216 questions of every method were answered and graded once and the spend was recorded conservatively. Under the strict pre-registered accounting rule the run remains formally flagged `valid: false`; I have not changed that flag. Excluding the 3 affected reader questions gives ASM 85.4% vs full history 72.3% (audit).
- **Small samples.** 12 scenarios (internal closed set c3) and 100 questions (EXP-002): only differences of roughly 10 pp are detectable on EXP-002.
- **Cost of ASM per question is higher** than full history on the internal closed set c3 at this scale because of the memory-update calls (about $0.00099 vs $0.00046 per question, `exp001f-report.md`), even though the reader context is ~12.6x smaller.

## Cost and process

- All paid experiments to date cost about **$1.87** in total (OpenRouter key counter), including **$0.44** for the internal closed set c3 run (key delta) and **$0.42** for EXP-002.
- Pre-registered criteria, frozen configuration with SHA-256 manifest, replayable response cache. Experiment code reviewed by a second AI system before each paid run.

## What is in this repository

| Path | Content |
|---|---|
| `data/exp002_lme_oracle100_labels.jsonl` | 400 rows: LongMemEval question ID, type, stratum, method, GPT-4o judge label, context size, evidence recall, reader answer |
| `data/exp001f_c3_per_scenario.json` | correct answers per anonymised scenario of the internal closed set c3 and method, incl. the diagnostic reference-memory condition (no dialogue text) |
| `eval/demo/` | runnable synthetic toy example: input dialogue, questions, hand-written reader outputs, and a simplified grader showing the scoring rules (no ASM code) |
| `eval/score.py` | standalone re-scoring (stdlib only): accuracy, Wilson CI, per-type tables, paired bootstrap, McNemar, exact sign-flip CI |
| `report/asm-eval-report.pdf` (+ `.md` source) | short PDF summary of both experiments |
| `LICENSE`, `LICENSE-CC-BY-4.0.txt` | MIT for code and LongMemEval-derived content; CC BY 4.0 for our labels, measurements, report and README text; see `THIRD_PARTY_NOTICES.md` |
| `CITATION.cff` | citation metadata |
| `THIRD_PARTY_NOTICES.md` | full MIT attribution for LongMemEval-derived content |
| `CHANGELOG.md` | documentation corrections; no data changes |
| `SHA256SUMS` | SHA-256 digests of included release files (excluding this manifest itself) |

`python3 eval/score.py` reproduces c3 per-method accuracies and paired differences, sign-flip CIs/p-values and scenario counts; LongMemEval subset accuracies, Wilson CIs, mean context estimates, mean per-question evidence recall, paired bootstrap CIs, McNemar p-values, multi-session and abstention counts. c3 marginal bootstrap CIs are independently reproducible from the released scenario counts: use one shared Python RNG seeded 1001, 20,000 draws per method in order ASM / full history / BM25 / summary / diagnostic, sampling 12 scenarios with replacement per draw in sorted scenario order; sort the resulting accuracies and take percentile indices 499 and 19499 (zero-based).

The following are reported from private run logs and are not reproducible from released data: c3 context-token sizes and the inputs to the 12.6x ratio, c3 per-type counts, the decision subset, extraction diagnostics, accounting/retry exclusion and costs.

Run the scorer (about 15 s). `python3 eval/demo/demo.py` shows the answer format and scoring rules on a toy example.

## What is not released, and why

- The ASM implementation (memory format, update / extraction step and its prompts, context selection, revision logic).
- Internal closed set c3 dialogues, questions and gold memory: the scenario generator and gold annotations mirror the memory schema, so they would reveal design details. Aggregated per-scenario correct and question counts are released; c3 per-type counts are not included.
- Raw API call logs (they contain the memory-update prompts).

I can share methodology, grading rules and per-question logs for an independent check on public benchmarks on request.

## License

Code in `eval/` is released under MIT (`LICENSE`). Our evaluation labels and aggregate measurements, report and README text are under CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`) to the extent we hold the rights. No LongMemEval dialogues or conversation histories are redistributed. `data/exp002_lme_oracle100_labels.jsonl` contains question IDs, question types and reader answers derived from LongMemEval, including answers that may quote benchmark text. This LongMemEval-derived content is under MIT, not CC BY 4.0; see `THIRD_PARTY_NOTICES.md`.

The archive contains one finalized release snapshot. `SHA256SUMS` records the SHA-256 digest of each included file except itself. Internal review and publication instructions are excluded.

## Citation

Chernyshuk, B. (2026). *Adaptive Semantic Memory: Strong Project-State Results, Mixed Generalization to Long-Term Personal Memory* (preliminary study). https://github.com/AutoDrops/asm-eval, DOI: [10.5281/zenodo.23279014](https://doi.org/10.5281/zenodo.23279014). See `CITATION.cff`.
