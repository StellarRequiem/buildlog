"""BuildLog must enforce the membrane: scrub PII, cite re-runnable sources, never
surface the private side. These tests pin all three."""
import buildlog


def test_scrub_redacts_real_name_and_email():
    assert "StellarRequiem" in buildlog.scrub("docs: byline — built by Alex Price")
    assert "Alex Price" not in buildlog.scrub("Alex Price shipped it")
    assert "Alexander Price" not in buildlog.scrub("Alexander Price")
    assert "[email-redacted]" in buildlog.scrub("ping alexanderprice91@yahoo.com please")


def test_render_runs_and_cites_sources():
    out = buildlog.render()
    assert out.startswith("# BuildLog")
    assert "> source:" in out               # every section cites a re-runnable command
    assert "Alex Price" not in out          # the identity firewall holds in generated content
    assert "@yahoo" not in out              # no email leaks


def test_only_public_repos_are_surfaced():
    # the private side of the membrane must NEVER appear in the report set
    for private in ("Yggdrasil", "operator", "bughunt", "assembly", "enterprise", "ops", "stamper"):
        assert private not in buildlog.PUBLIC_REPOS
