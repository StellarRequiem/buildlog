#!/usr/bin/env python3
"""BuildLog — a verifiable content engine.

Generates a publishable digest where EVERY figure is backed by a re-runnable,
public-safe source: the calibration-log track record, the verity primitive, and
the public StellarRequiem repos' git activity. Nothing on the private side of the
membrane — no trading edge, no signals/weights, no PII — ever appears: BuildLog
reads only public sources, and each section names the command that produced it.

The thesis, applied to content: don't *claim* — *show*, with a source anyone can
re-run. The same verification discipline that gates the work also gates the
marketing of the work.

Usage:  python buildlog.py            # print today's digest to stdout
        python buildlog.py > OUT.md   # capture it
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
from pathlib import Path

HOME = Path.home()

# ── the membrane filter ──────────────────────────────────────────────────────
# The operator's real identity is partially-public, but a content engine must
# never AUTO-amplify PII: BuildLog redacts the real name to the pseudonym and
# strips emails from anything it surfaces (commit subjects, etc.). This is the
# F1 firewall enforced in generated content — public standing is StellarRequiem.
_PII_SUBS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"Alexander Price|Alex Price", re.IGNORECASE), "StellarRequiem"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[email-redacted]"),
]


def scrub(text: str) -> str:
    """Redact PII so nothing on the private side of the identity firewall is published."""
    for pattern, repl in _PII_SUBS:
        text = pattern.sub(repl, text)
    return text

# The public (StellarRequiem) repos BuildLog may report activity from. Private
# repos (Yggdrasil, operator, bughunt, assembly, enterprise, ops, stamper) are
# DELIBERATELY excluded — they live on the other side of the membrane.
PUBLIC_REPOS = [
    "verity-core", "calibration-log", "firewall", "scope-gate", "grounded",
    "reality-anchor", "sentinel", "office-kit", "classroom", "verified-ai-labor",
    "forest-blue-team-guardian", "cus-core", "verity-demo",
]


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def track_record() -> dict:
    """The public prediction track record — OUTCOMES ONLY (the edge stays private).

    Reads the append-only, hash-chained predictions.jsonl directly and counts
    defensively (schema-tolerant): total lines, and how many carry a probability
    (a forecast) vs. an outcome (a resolution).
    """
    src = "~/calibration-log/predictions.jsonl"
    p = HOME / "calibration-log" / "predictions.jsonl"
    rows: list[dict] = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    forecasts = [r for r in rows if any(k in r for k in ("prob", "probability", "p"))]
    resolved = [r for r in rows if any(k in r for k in ("outcome", "resolved", "result"))]
    return {"source": src, "entries": len(rows),
            "forecasts": len(forecasts), "resolutions": len(resolved)}


def verification_primitive() -> dict:
    """verity-core: the count of canonical domain packs (each a re-runnable file)."""
    src = "ls ~/verity-core/truths/*.yaml"
    d = HOME / "verity-core" / "truths"
    packs = sorted(p.stem for p in d.glob("*.yaml")) if d.exists() else []
    return {"source": src, "packs": len(packs), "names": packs}


def shipped(days: int = 7) -> dict:
    """What shipped across the public repos in the last `days` — straight from git."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    src = f"git -C <repo> log --since {since} --format='%ad %s' --date=short"
    commits: list[tuple[str, str]] = []
    for name in PUBLIC_REPOS:
        repo = HOME / name
        if not (repo / ".git").exists():
            continue
        out = _run(["git", "-C", str(repo), "log", "--since", since,
                    "--format=%ad %s", "--date=short"])
        for line in out.splitlines():
            if line.strip():
                commits.append((name, line.strip()))
    commits.sort(key=lambda c: c[1], reverse=True)
    return {"source": src, "since": since, "commits": commits,
            "repos": len([r for r in PUBLIC_REPOS if (HOME / r / ".git").exists()])}


def render(days: int = 7) -> str:
    today = datetime.date.today().isoformat()
    cal, ver, ship = track_record(), verification_primitive(), shipped(days)
    L: list[str] = [
        f"# BuildLog — verifiable digest · {today}",
        "",
        "_Every figure below is backed by a re-runnable, public source named beneath it. "
        "Outcomes and tools only — no edge, no signals, no PII crosses the membrane._",
        "",
        "## The track record",
        f"- **{cal['forecasts']}** forecasts logged · **{cal['resolutions']}** resolved · "
        f"**{cal['entries']}** total entries — append-only, hash-chained.",
        f"  > source: `{cal['source']}`",
        "",
        "## The verification primitive",
        f"- **{ver['packs']}** canonical domain packs: {', '.join(ver['names']) or '—'}.",
        f"  > source: `{ver['source']}`",
        "",
        f"## What shipped (last {days} days)",
        f"- **{len(ship['commits'])}** commits across **{ship['repos']}** public repos since {ship['since']}.",
    ]
    for name, line in ship["commits"][:30]:
        L.append(f"  - `{name}` — {scrub(line)}")
    L += [f"  > source: `{ship['source']}`", ""]
    L.append("---")
    L.append("_Generated by BuildLog. Re-run any source command above to verify every number yourself._")
    return "\n".join(L)


if __name__ == "__main__":  # pragma: no cover
    print(render())
