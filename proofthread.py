#!/usr/bin/env python3
"""ProofThread — a launch/announcement thread generator for the BuildLog engine.

Drafts a tweet-sized thread (a hook, 3–4 substance posts, a CTA) announcing a
PUBLIC StellarRequiem repo. The discipline is BuildLog's: don't *claim* — *show*,
with a source anyone can re-run. Every substance post names what shipped AND a
verifiable figure with the public git/file command that produced it.

The membrane holds the same way it does in buildlog.py:
  • reads ONLY public StellarRequiem repos — never the private side (Yggdrasil,
    operator, bughunt, assembly, enterprise, ops, stamper) and never the trading
    edge (signals / weights / strategy / credentials);
  • every generated post is run through buildlog.scrub() so the operator's real
    name never auto-amplifies and emails are stripped — public standing is
    StellarRequiem;
  • stdlib only, subprocess for git, defensive — never crashes on missing data.

Usage:  python proofthread.py [repo]      # print a thread to stdout
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Reuse the membrane filter and the public-repo allowlist from the engine so
# there is ONE definition of "what's publishable", not two that can drift.
from buildlog import HOME, PUBLIC_REPOS, scrub

TWEET_LIMIT = 280


def _run(cmd: list[str]) -> str:
    """Run a command, returning trimmed stdout or "" on any failure (defensive)."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def _is_public(repo: str) -> bool:
    """A repo is reportable only if it's on the StellarRequiem public allowlist."""
    return repo in PUBLIC_REPOS


def _headline(repo_dir: Path) -> str:
    """The README headline — first non-title, non-empty line (defensive on missing)."""
    readme = repo_dir / "README.md"
    if not readme.exists():
        return ""
    try:
        for raw in readme.read_text(errors="replace").splitlines():
            line = raw.strip().strip("*_").strip()
            if not line or line.startswith("#"):
                continue
            return line
    except Exception:
        return ""
    return ""


def _git_facts(repo_dir: Path, days: int = 14) -> dict:
    """Recent git activity for a repo — figures only, each from a re-runnable command."""
    since = f"{days} days ago"
    log_cmd = f"git -C ~/{repo_dir.name} log --since '{since}' --format='%ad %s' --date=short"
    out = _run(["git", "-C", str(repo_dir), "log", "--since", since,
                "--format=%ad %s", "--date=short"])
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]

    commit_count = len(lines)
    # Distinct commit days = shipping cadence, straight from the date column.
    days_active = len({ln.split(" ", 1)[0] for ln in lines if " " in ln})
    # The latest commit: date + subject (what most-recently shipped).
    latest_date, latest_subject = "", ""
    if lines:
        first = lines[0]
        latest_date, _, latest_subject = first.partition(" ")
    return {
        "log_cmd": log_cmd,
        "since_days": days,
        "commits": commit_count,
        "days_active": days_active,
        "latest_date": latest_date,
        "latest_subject": latest_subject,
    }


def _fit(text: str) -> str:
    """Scrub, then guarantee the post is <= TWEET_LIMIT chars (truncate w/ ellipsis)."""
    text = scrub(text).strip()
    if len(text) <= TWEET_LIMIT:
        return text
    # Truncate to the limit, reserving one char for the ellipsis; re-scrub is a
    # no-op on already-clean text but cheap insurance against slicing a token.
    return scrub(text[: TWEET_LIMIT - 1].rstrip() + "…")


def thread(repo: str = "verity-core", max_posts: int = 6) -> list[str]:
    """Draft a launch/announcement thread for a PUBLIC StellarRequiem repo.

    Reads the repo's recent git activity and README headline (public sources
    only) and returns a list of tweet-sized, scrubbed posts: a hook, 3–4
    substance posts (each naming what shipped + a verifiable figure with its
    source), and a CTA. Never crashes on missing data; refuses non-public repos.
    """
    posts: list[str] = []

    if not _is_public(repo):
        # Membrane refusal — never reach into a private repo for content.
        return [_fit(
            f"(ProofThread refused: '{repo}' is not on the public StellarRequiem "
            f"allowlist — the membrane only publishes public work.)"
        )]

    repo_dir = HOME / repo
    if not (repo_dir / ".git").exists():
        return [_fit(
            f"(No public git history found for '{repo}' at ~/{repo} — nothing to announce.)"
        )]

    facts = _git_facts(repo_dir)
    headline = _headline(repo_dir)

    # ── 1. The hook ──────────────────────────────────────────────────────────
    hook = f"🧵 Shipping in public: {repo}."
    if headline:
        hook += f"\n\n{headline}"
    hook += "\n\nEvery number below cites a public command you can re-run. Don't claim — show. 👇"
    posts.append(_fit(hook))

    # ── 2–5. Substance posts: each = what shipped + a figure + its source ─────
    substance: list[str] = []

    if facts["commits"]:
        substance.append(
            f"What shipped: {facts['commits']} commits in the last "
            f"{facts['since_days']} days across {facts['days_active']} active days.\n\n"
            f"Pace you can audit, not assert.\n"
            f"src: {facts['log_cmd']} | wc -l"
        )

    if facts["latest_subject"]:
        substance.append(
            f"Latest ({facts['latest_date']}):\n"
            f"\"{facts['latest_subject']}\"\n\n"
            f"The newest brick, straight from the log — no roadmap theater.\n"
            f"src: git -C ~/{repo} log -1 --format='%ad %s' --date=short"
        )

    if headline:
        substance.append(
            f"What it is: {headline}\n\n"
            f"Read the one-liner yourself — it's the first line of the public README.\n"
            f"src: head ~/{repo}/README.md"
        )

    # A reproducibility post — the whole point is that you can re-derive it all.
    substance.append(
        f"Why trust it? You don't have to. Clone the repo, run each `src:` line, "
        f"and the figures fall out of your own machine — not my marketing.\n"
        f"src: git clone https://github.com/StellarRequiem/{repo}"
    )

    # Keep 3–4 substance posts, leaving room for hook + CTA within max_posts.
    room_for_substance = max(1, max_posts - 2)
    for body in substance[:room_for_substance]:
        posts.append(_fit(body))

    # ── 6. The CTA ───────────────────────────────────────────────────────────
    cta = (
        f"Built by StellarRequiem — standing earned on verifiable work, not vibes.\n\n"
        f"⭐ {repo}: github.com/StellarRequiem/{repo}\n"
        f"Re-run any source above. If a number doesn't hold, tell me. 🔎"
    )
    posts.append(_fit(cta))

    return posts[:max_posts]


if __name__ == "__main__":  # pragma: no cover
    name = sys.argv[1] if len(sys.argv) > 1 else "verity-core"
    for i, post in enumerate(thread(name), 1):
        print(f"--- post {i} ({len(post)} chars) ---")
        print(post)
        print()
