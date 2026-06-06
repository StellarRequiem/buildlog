#!/usr/bin/env python3
"""CaseForge — an HONEST case-study generator for the BuildLog content engine.

Where buildlog.py renders a rolling digest, CaseForge writes a single, durable
case study around one claim: *a paper-trading track record, verified rather than
asserted*. It reads the same public source BuildLog does — the calibration-log
Yggdrasil track, scored by the canonical
`CalibrationLog('tracks/yggdrasil.jsonl').score()` — and reports the REAL Brier
score and calibration table, even when (as today) the result is near the
no-skill line. That is the whole point: the honest "no edge yet" is a publishable
deliverable, and inflating it would defeat the verification discipline the case
study is about.

Every figure names a re-runnable, public-safe command. Nothing on the private
side of the membrane — trading edge, signals, weights, strategy, credentials,
PII — ever crosses into the output: CaseForge reuses buildlog.scrub() on ALL
generated text and reads only the public calibration-log track.

Usage:  python caseforge.py            # print the case study to stdout
        python caseforge.py > CASE.md  # capture it
"""
from __future__ import annotations

from pathlib import Path

# Reuse the membrane filter and the public-track scorer from BuildLog so there is
# exactly one definition of each — scrub() (the F1 PII firewall) and the
# calibration-log read pattern. Importing means the case study can never drift
# from the digest on what "public-safe" or "the track record" means.
from buildlog import scrub, track_record

HOME = Path.home()

# 0.25 is the Brier score of a coin-flip on a 50/50 market — the no-skill line.
# We compare honestly against it rather than against a flattering baseline.
NO_SKILL_BRIER = 0.25


def _verdict(brier: float | None, resolved: int | None) -> str:
    """An honest, non-inflated read of the Brier score against the no-skill line.

    NEVER claims an edge the number doesn't support. At/above 0.25 we say so
    plainly; just-below with a thin sample we call provisional, not proven.
    """
    if brier is None or not resolved:
        return ("No resolved predictions to score yet — there is no edge to claim, "
                "and CaseForge will not invent one.")
    margin = NO_SKILL_BRIER - brier
    if brier >= NO_SKILL_BRIER:
        deficit = brier - NO_SKILL_BRIER  # >= 0 here
        return (f"Brier {brier:.4f} is **at or above** the {NO_SKILL_BRIER} no-skill line "
                f"(+{deficit:.4f} worse than a coin-flip): on this sample the track shows "
                "**no demonstrated edge**. Stated honestly, not buried.")
    if resolved < 30:
        return (f"Brier {brier:.4f} edges the {NO_SKILL_BRIER} no-skill line by only "
                f"{margin:.4f} on **{resolved}** resolved calls — well inside noise for a "
                "sample this small. Treat as **provisional, not proven**; the honest verdict "
                "is *no edge established yet*.")
    return (f"Brier {brier:.4f} beats the {NO_SKILL_BRIER} no-skill line by {margin:.4f} over "
            f"**{resolved}** resolved calls — a measured, modest signal. Still paper, still "
            "small; reported as-is.")


def _calibration_table() -> list[str]:
    """The predicted-vs-actual calibration buckets, straight from the scorer.

    Defensive: returns an empty list (no table) if the package or track is
    unavailable, so the case study never crashes on missing data.
    """
    cl = HOME / "calibration-log"
    track = cl / "tracks" / "yggdrasil.jsonl"
    try:
        import sys
        if str(cl) not in sys.path:
            sys.path.insert(0, str(cl))
        from calibration_log import CalibrationLog  # type: ignore
        buckets = CalibrationLog(str(track)).score().get("buckets") or []
    except Exception:
        return []
    if not buckets:
        return []
    rows = ["| predicted range | avg predicted | actual frequency | n |",
            "|---|---|---|---|"]
    for b in buckets:
        rows.append(f"| {b.get('range', '?')} | {b.get('pred', '?')} | "
                    f"{b.get('actual', '?')} | {b.get('n', '?')} |")
    return rows


def case_study() -> str:
    """Render the honest case study as Markdown.

    Setup → method → result (the REAL Brier, never inflated) → verifiability.
    Reads the public calibration-log track via the same scorer BuildLog uses;
    all generated text passes through scrub() before it is returned.
    """
    cal = track_record()
    total = cal.get("total") or 0
    resolved = cal.get("resolved")
    pending = cal.get("pending")
    brier = cal.get("brier")
    chain_ok = cal.get("chain_ok")
    source = cal.get("source", "calibration-log scorer")

    # The single re-runnable command a reader pastes to reproduce every figure.
    repro = ("cd ~/calibration-log && python -c \"from calibration_log import "
             "CalibrationLog as C; print(C('tracks/yggdrasil.jsonl').score())\"")

    chain_line = (
        "✓ intact — append-only, hash-chained" if chain_ok
        else "unverified" if chain_ok is None
        else "BROKEN — do not trust until repaired")

    L: list[str] = [
        "# Case study: a paper track record you can re-run, not just read",
        "",
        "_An honest case study. Every figure below is produced by one public command, "
        "named at the end — re-run it and you get these exact numbers. No edge, no "
        "signals, no strategy, no PII crosses the membrane; only outcomes do._",
        "",
        "## The setup",
        "",
        "A local paper-trading system logs each directional call **before** the fact — "
        "a probability and a resolution date — to an append-only, hash-chained "
        "calibration log. The wager is paper; the record is real. The question this "
        "case study answers is not *did it win* but *is the scorecard trustworthy* — "
        "and what it says once you trust it.",
        "",
        "## The method",
        "",
        "- **Verity-gated:** a prediction is committed before its outcome is known, so "
        "the score can't be back-fit to what happened.",
        "- **Append-only, hash-chained:** every entry links to the previous by hash, so "
        "the history can't be quietly rewritten — tampering breaks the chain.",
        "- **Scored by a canonical, public scorer**, not a bespoke spreadsheet: the same "
        "`score()` anyone can run over the same public track.",
        "",
        "## The result (stated honestly)",
        "",
        f"- **{total}** predictions logged"
        + (f" · **{resolved}** resolved" if resolved is not None else "")
        + (f" · **{pending}** still open" if pending is not None else "")
        + ".",
        (f"- **Brier score: {brier:.4f}** (0.25 = no-skill coin-flip, 0.0 = perfect)."
         if brier is not None else
         "- **Brier score: not yet computable** — no resolved predictions."),
        f"- Hash-chain: {chain_line}.",
        "",
        _verdict(brier, resolved),
        "",
    ]

    table = _calibration_table()
    if table:
        L += ["### Calibration (predicted vs. actual)", ""]
        L += table
        L += ["",
              "_Read this honestly: where the 'actual frequency' column tracks the "
              "'avg predicted' column, the probabilities are well-calibrated; where it "
              "diverges, they are not. Both are shown._",
              ""]

    L += [
        "## Why you can believe it",
        "",
        "Nothing here rests on my word. The number is whatever the scorer prints over a "
        "hash-chained log you can clone. If the chain were tampered with, the verdict "
        "above would read **BROKEN** instead of intact. Re-run the source and check.",
        "",
        f"> source: `{source}`",
        f"> reproduce: `{repro}`",
        "",
        "---",
        "_Generated by CaseForge (BuildLog content engine). An inflated case study would "
        "defeat its own thesis — so this one reports the real Brier, near the no-skill "
        "line and all. Re-run the source command to verify every figure yourself._",
    ]

    # MEMBRANE: scrub ALL generated text before returning — no real name, no email
    # ever leaves the engine, regardless of what the upstream source contained.
    return scrub("\n".join(L))


if __name__ == "__main__":  # pragma: no cover
    print(case_study())
