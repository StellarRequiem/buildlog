# BuildLog — a verifiable content engine

[![ci](https://github.com/StellarRequiem/buildlog/actions/workflows/ci.yml/badge.svg)](https://github.com/StellarRequiem/buildlog/actions/workflows/ci.yml)

Generates publishable digests where **every figure is backed by a re-runnable,
public source**: the [calibration-log](https://github.com/StellarRequiem/calibration-log)
track record, the [verity](https://github.com/StellarRequiem/verity-core) primitive,
and the public repos' git activity. The same verification discipline that gates the
work gates the *marketing* of the work — **don't claim, show**.

```sh
python buildlog.py              # print today's digest
python buildlog.py > today.md   # capture it
```

Every section names the command that produced its figures — re-run any of them to
verify the numbers yourself.

## The membrane

BuildLog reads **only public sources**, scrubs PII to the **StellarRequiem**
pseudonym, and never touches the private edge — no signals, weights, strategy,
templates, or credentials. The private repos are excluded by construction; the
identity firewall is enforced in generated content (`scrub()`).
