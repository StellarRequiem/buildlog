"""ProofThread must hold the same membrane BuildLog does: every post tweet-sized,
PII scrubbed, and the figures grounded in REAL public git activity. These tests
pin all of it."""
import proofthread


def test_thread_is_non_empty():
    posts = proofthread.thread()
    assert isinstance(posts, list)
    assert len(posts) >= 1


def test_every_post_is_tweet_sized():
    posts = proofthread.thread("verity-core")
    for p in posts:
        assert len(p) <= 280, f"post over the limit ({len(p)} chars): {p!r}"


def test_scrub_holds_no_pii_leaks():
    # The identity firewall: the real name and the operator's email never appear
    # in any generated post, on any repo.
    for repo in ("verity-core", "calibration-log", "verity-demo"):
        for p in proofthread.thread(repo):
            assert "Alex Price" not in p
            assert "Alexander Price" not in p
            assert "@yahoo" not in p


def test_reads_real_git_activity():
    # A known public repo with real history must yield a multi-post thread
    # (hook + substance + CTA), not the empty/refusal fallback.
    posts = proofthread.thread("verity-core")
    assert len(posts) >= 3, "a repo with real git history should produce a full thread"
    blob = "\n".join(posts)
    # Substance posts cite re-runnable public commands and name what shipped.
    assert "src:" in blob
    assert "git -C ~/verity-core" in blob or "git clone" in blob
    assert "verity-core" in blob


def test_refuses_private_repos():
    # The membrane: a private repo name must never produce a real thread.
    for private in ("Yggdrasil", "operator", "bughunt", "assembly", "stamper"):
        posts = proofthread.thread(private)
        assert len(posts) == 1
        assert "refused" in posts[0].lower()


def test_missing_public_repo_does_not_crash():
    # A public-allowlist name that isn't checked out locally degrades gracefully.
    # (Use a real allowlist entry; if it happens to exist, a normal thread is
    #  also acceptable — the point is no exception is raised.)
    posts = proofthread.thread("office-kit")
    assert isinstance(posts, list) and len(posts) >= 1
