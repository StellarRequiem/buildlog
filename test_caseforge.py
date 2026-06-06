"""CaseForge must be honest AND keep the membrane shut: non-empty Markdown that
cites a re-runnable source, surfaces the REAL numbers (Brier or prediction count),
and never leaks the operator's real name or email. These tests pin all of it."""
import re

import caseforge


def test_output_is_nonempty_markdown_starting_with_hash():
    out = caseforge.case_study()
    assert isinstance(out, str)
    assert out.strip()                      # non-empty
    assert out.startswith("#")              # Markdown heading


def test_cites_a_rerunnable_source():
    out = caseforge.case_study()
    assert "> source:" in out               # the section names its source command
    assert "CalibrationLog" in out          # the canonical scorer is cited by name


def test_membrane_holds_no_pii():
    out = caseforge.case_study()
    assert "Alex Price" not in out          # real name never crosses the membrane
    assert "Alexander Price" not in out
    assert "@yahoo" not in out              # no email leaks


def test_surfaces_the_real_brier_or_prediction_count():
    """The case study must show a real, scorer-derived figure — not a vibe.

    Either the numeric Brier score (a float like 0.2628) or, if nothing is
    resolved yet, the integer prediction count must appear in the output.
    """
    out = caseforge.case_study()
    cal = caseforge.track_record()
    brier = cal.get("brier")
    if brier is not None:
        # the exact 4-dp Brier the scorer printed must be in the text, honestly
        assert f"{brier:.4f}" in out
    else:
        # no resolved predictions — at minimum the real total must be surfaced
        assert str(cal.get("total", 0)) in out
    # and a bare numeric figure is present regardless
    assert re.search(r"\d", out)


def test_does_not_inflate_a_no_skill_result():
    """If the real Brier is at/above the 0.25 no-skill line, the text must NOT
    claim a demonstrated edge — it must say so plainly."""
    out = caseforge.case_study()
    cal = caseforge.track_record()
    brier = cal.get("brier")
    if brier is not None and brier >= caseforge.NO_SKILL_BRIER:
        assert "no demonstrated edge" in out.lower() or "no edge" in out.lower()
