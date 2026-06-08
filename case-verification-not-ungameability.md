# BuildLog — verifiable case · 2026-06-08
## Verification ≠ un-gameability: a verifier is a comparator, not an oracle

_Every claim below is backed by a re-runnable, public source named beneath it. Method and
outcomes only — no edge, no signals, no PII crosses the membrane._

### The setup (public)
In April 2026, Berkeley/RDI showed all **8** major agent benchmarks could be driven to
**near-perfect scores without solving a single task** — by attacking the *grader*, not by being
smarter. (Six hit 100% or ~100%; GAIA ~98%, OSWorld 73% — with zero or near-zero LLM reasoning.)
The canonical example: a `conftest.py` pytest hook that rewrites every test's outcome to `passed`.
> source: <https://rdi.berkeley.edu/blog/trustworthy-benchmarks-cont/>

### The question we put to our own tool
Does a deterministic verification primitive survive that class of attack? We tested
[`verity-core`](https://github.com/StellarRequiem/verity-core) — whose `verify()` has **no LLM in
the scoring path**, just field-by-field numeric reconciliation — and we report the *limit*, not
just the win.

### What holds
Given an **independent** grader's ground truth, `verify()` REFUSEs a fabricated result-claim and
PASSes a genuine one — deterministically:

```
1. genuine,    independent truth -> PASS
2. fabricated, independent truth -> REFUSE
3. fabricated, POISONED evidence -> PASS
```
> source: `pip install "git+https://github.com/StellarRequiem/verity-core@main"`, then run the
> 18 lines below. (Verified against `verity/verify.py` at commit `fc50c8a6`.)

```python
from verity.verify import verify
V = lambda r: r["verdict"]
# A deterministic build/test grade is out-of-sample + leakage-free, so asserting these is honest.
base = {"task_id": "fix-build", "tests_total": 12, "out_of_sample": True, "leakage_checked": True}

# 1) GENUINE: claim matches an INDEPENDENT grader's ground truth
print("1. genuine,    independent truth ->", V(verify({**base, "tests_passed": 12, "build_ok": True},
        evidence={"tests_passed": 12, "build_ok": True})))
# 2) FABRICATION (à la the conftest force-pass): claim says 12/12; independent grader says 3/12
print("2. fabricated, independent truth ->", V(verify({**base, "tests_passed": 12, "build_ok": True},
        evidence={"tests_passed": 3,  "build_ok": False})))
# 3) THE CATCH: same fabrication, but evidence is the agent's OWN (poisoned) grader output
print("3. fabricated, POISONED evidence ->", V(verify({**base, "tests_passed": 12, "build_ok": True},
        evidence={"tests_passed": 12, "build_ok": True})))
```

### The honest gap — read line 3 again
Same fabrication; but when the "evidence" is the agent's *own* poisoned grader output, `verify()`
**PASSes the fake.** That is the whole lesson:

> **`verify()` is a deterministic *comparator*, not an oracle.** It does not fetch, recompute, or
> authenticate the ground truth it is handed — by design (no network I/O). So the un-gameability is **not**
> in the comparator; it lives in **grader-isolation** — running the truth-grader where the agent
> can't reach it. A re-runnable proof only ever proves "an isolated grader emitted X." Skip the
> isolation and the strongest deterministic verifier on earth still passes the fraud (line 3).

Two further limits we logged rather than hid: a *non-finite* claimed value downgrades REFUSE→WARN,
and the ML-rigor pack will false-REFUSE a genuine task-result (e.g. a small sample) — both
reproducible from the same `verify()` API, both the kind of thing a "verified" label hides if you
don't look.

### Why publish the limit
The same discipline that gates the work gates the *marketing* of it: don't claim, show. A verifier
nobody could break is a verifier nobody tested. We broke ours, on purpose, and told you where the
seam is — so you can build the part that actually matters (isolation) instead of trusting a label.

— **StellarRequiem**

---
_Re-run any source command above to verify every line yourself._
