#!/usr/bin/env python3
"""Recompute the published ASM evaluation numbers from released per-question / per-scenario data.

Standalone: Python 3.8+ standard library only. It does NOT need, call, or contain the ASM memory system.
It only re-scores already-graded results:

  data/exp002_lme_oracle100_labels.jsonl  - EXP-002, LongMemEval ORACLE, 100-question stratified subset,
                                             one row per (question, method), GPT-4o judge label.
  data/exp001f_c3_per_scenario.json        - EXP-001F, closed set c3, correct answers per (scenario, method).

Usage:  python3 eval/score.py [--data DIR]
"""
import argparse, itertools, json, math, os, random, statistics
from collections import defaultdict

Z = 1.959963984540054


def wilson(k, n):
    p = k / n; den = 1 + Z * Z / n
    mid = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return mid - half, mid + half


def mcnemar_exact(b, c):
    d = b + c
    if not d:
        return 1.0
    return min(1.0, 2 * sum(math.comb(d, k) for k in range(min(b, c) + 1)) / 2 ** d)


def exp002(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    by = {(r["question_id"], r["method"]): r for r in rows}
    methods = sorted({r["method"] for r in rows})
    print("EXP-002  LongMemEval ORACLE, 100-question stratified subset (NOT the official 500-question result)")
    print(f"{'method':<14}{'correct':>8}{'acc %':>8}{'Wilson 95% CI':>18}{'ctx tok':>9}{'evid.recall':>12}")
    for m in methods:
        rs = [r for r in rows if r["method"] == m]
        k = sum(r["judge_label"] for r in rs); n = len(rs); lo, hi = wilson(k, n)
        ctx = statistics.mean(r["context_tokens_chars_div4"] for r in rs)
        ev = [r["evidence_recall"] for r in rs if r["evidence_recall"] is not None]
        evs = f"{statistics.mean(ev):.3f}" if ev else "n/a"
        print(f"{m:<14}{k:>8}{100*k/n:>8.1f}{f'{100*lo:.1f}-{100*hi:.1f}':>18}{ctx:>9.0f}{evs:>12}")
    print("\nBy question type (correct / n):")
    types = sorted({r["question_type"] for r in rows})
    print(f"{'type':<28}" + "".join(f"{m:>14}" for m in methods))
    for t in types:
        line = f"{t:<28}"
        for m in methods:
            rs = [r for r in rows if r["method"] == m and r["question_type"] == t]
            line += f"{sum(r['judge_label'] for r in rs):>9} / {len(rs):<2}"
        print(line)
    print("\nPaired ASM minus other (stratified bootstrap, 10,000 repeats, seed 2002; exact McNemar):")
    qids = sorted({r["question_id"] for r in rows})
    for other in [m for m in methods if m != "asm"]:
        strata = defaultdict(list); b = c = 0
        for q in qids:
            x, y = int(by[q, "asm"]["judge_label"]), int(by[q, other]["judge_label"])
            strata[by[q, "asm"]["stratum"]].append(x - y); b += x == 1 and y == 0; c += x == 0 and y == 1
        n = sum(map(len, strata.values())); rng = random.Random(2002); boot = []
        for _ in range(10000):
            boot.append(sum(sum(rng.choice(v) for _ in v) for v in strata.values()) / n)
        boot.sort(); diff = sum(sum(v) for v in strata.values()) / n
        print(f"  asm - {other:<13} {100*diff:+.0f} pp  95% CI [{100*boot[249]:+.0f}; {100*boot[9749]:+.0f}]"
              f"  asm-only {b}, other-only {c}, McNemar p = {mcnemar_exact(b, c):.4f}")


def signflip(diffs, delta=0.0):
    d = [x - delta for x in diffs]; obs = abs(sum(d)); hits = 0; total = 0
    for signs in itertools.product((1, -1), repeat=len(d)):
        total += 1; hits += abs(sum(s * x for s, x in zip(signs, d))) >= obs - 1e-12
    return hits / total


def exp001f(path):
    data = json.load(open(path, encoding="utf-8"))["rows"]
    acc = defaultdict(dict); n = defaultdict(dict)
    for r in data:
        acc[r["method"]][r["scenario"]] = r["correct"]; n[r["method"]][r["scenario"]] = r["questions"]
    print("\nEXP-001F  closed set c3 (12 synthetic scenarios x 18 questions = 216 per method)")
    for m in sorted(acc):
        k = sum(acc[m].values()); t = sum(n[m].values())
        print(f"  {m:<16} {k:>3} / {t}  = {100*k/t:.1f}%")
    scen = sorted(acc["asm_new"])
    print("\nPaired ASM v4.2 (asm_new) minus other, per-scenario differences;"
          " exact sign-flip test over all 2^12 sign patterns, CI by test inversion (0.05 pp grid):")
    for other in ("full_history", "bm25", "llm_summary"):
        diffs = [100 * (acc["asm_new"][s] / n["asm_new"][s] - acc[other][s] / n[other][s]) for s in scen]
        mean = statistics.mean(diffs); p = signflip(diffs)
        grid = [round(mean + i * 0.05, 2) for i in range(-600, 601)]
        inside = [g for g in grid if signflip(diffs, g) > 0.05]
        bwt = (sum(x > 0 for x in diffs), sum(x == 0 for x in diffs), sum(x < 0 for x in diffs))
        print(f"  vs {other:<13} {mean:+.1f} pp  exact 95% CI [{min(inside):+.1f}; {max(inside):+.1f}]  p = {p:.5f}"
              f"  scenarios better/tied/worse {bwt[0]}/{bwt[1]}/{bwt[2]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    a = ap.parse_args()
    exp002(os.path.join(a.data, "exp002_lme_oracle100_labels.jsonl"))
    exp001f(os.path.join(a.data, "exp001f_c3_per_scenario.json"))
