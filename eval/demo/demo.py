#!/usr/bin/env python3
"""Runnable demo of the INPUT / OUTPUT FORMAT and the SCORING RULES used in the ASM evaluations.

Everything here is a SYNTHETIC TOY EXAMPLE (eval/demo/toy_example.json, hand-written). It does not contain or call
ASM, and it says nothing about how ASM builds its memory. The grader below is a SIMPLIFIED, English-only
illustration of the rules of the real grader used on the internal closed set c3; the real grader also handles
Ukrainian/Russian negation and hedging. EXP-002 (LongMemEval) was graded by the official LongMemEval GPT-4o judge
instead, not by these rules.

Rules (per question, first match wins):
  format_error       reader output is not strict JSON {"answer": ..., "source": ...}  -> counted as wrong
  justified_unknown  question is unanswerable and the answer is an "insufficient information" marker
                     with no concrete value                                            -> counted as CORRECT
  false_unknown      question is answerable but the reader says "insufficient information"
  wrong              question is unanswerable but the reader gives a value (hallucination)
  correct            a gold alias appears as a whole token sequence, not negated ("not X", "instead of X");
                     for provenance questions the `source` turn must also match
  stale_or_injected  a stale, cancelled or injected value appears (not negated)
  provenance_error   provenance question with the wrong source turn
  wrong              anything else
Accuracy = (correct + justified_unknown) / questions.

Run:  python3 eval/demo/demo.py
"""
import json, os, re

UNKNOWN = re.compile(r"\b(insufficient information|unknown|not enough information|no data)\b", re.I)
NEG_BEFORE = re.compile(r"\b(not|no longer|instead of|never)\s+(\w+\s+){0,1}$", re.I)


def mentions(text, value):
    """Whole-token, case-insensitive match that is not directly negated ('not server A')."""
    for m in re.finditer(r"(?<![\w])" + re.escape(value) + r"(?![\w])", text, re.I):
        if not NEG_BEFORE.search(text[:m.start()]):
            return True
    return False


def grade(raw, gold):
    try:
        out = json.loads(raw); answer, source = str(out["answer"]), out.get("source")
    except (ValueError, KeyError, TypeError):
        return "format_error"
    says_unknown = bool(UNKNOWN.search(answer))
    has_value = any(mentions(answer, v) for v in gold["aliases"] + gold["stale"]) or bool(re.search(r"\d", answer))
    if not gold["answerable"]:
        return "justified_unknown" if says_unknown and not has_value else "wrong"
    if says_unknown and not any(mentions(answer, a) for a in gold["aliases"]):
        return "false_unknown"
    if any(mentions(answer, a) for a in gold["aliases"]):
        if gold.get("check_source") and source not in gold["aliases"]:
            return "provenance_error"
        return "correct"
    if any(mentions(answer, s) for s in gold["stale"]):
        return "stale_or_injected"
    if gold.get("check_source"):
        return "provenance_error"
    return "wrong"


def main():
    ex = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toy_example.json"), encoding="utf-8"))
    print("SYNTHETIC TOY EXAMPLE - illustrates format and scoring rules only; no ASM code involved.\n")
    print("Dialogue:")
    for t in ex["dialogue"]:
        print(f"  [{t['turn']}] {t['role']}: {t['text']}")
    qs = ex["questions"]
    for method, outs in ex["example_reader_outputs"].items():
        if method.startswith("_"):
            continue
        print(f"\n{method}:")
        ok = 0
        for q in qs:
            outcome = grade(outs[q["qid"]], q["gold"]); ok += outcome in ("correct", "justified_unknown")
            print(f"  {q['qid']} {q['category']:<20} {outs[q['qid']]:<62} -> {outcome}")
        print(f"  accuracy = {ok}/{len(qs)} = {100*ok/len(qs):.0f}%")


if __name__ == "__main__":
    main()
