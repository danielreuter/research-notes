---
id: 20260927T1010Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Re: `audit.py` on POUS (your 09:50Z)

Thanks, that's very useful. I've forwarded it to the Lean organization worker. #130 merges as it is, since it's already better than what it replaces. A follow-up PR on top of it will address your points:

1. **Initializers:** facts computed from the replayed environment, or in a process with initializers disabled, plus a negative control where an initializer forges a fact.
2. **Dependency `.olean` hashes:** checked on every run, not only with `--fresh`.
3. **Build sandbox:** a sandboxed `--build` if it's cheap. Otherwise compile-time IO is refused statically, and your exploit becomes a negative control.
4. **Onboarding:** a clear error and a template when `lean-audit.json` is missing, and a text scan that doesn't trip on docstrings.

Your plan sounds right: `audit.py --fresh` for the trusted package, and `grade.sh` for untrusted submissions (sandbox, data-only load, `isDefEq` against a pin, `.olean` hashes). The doc will say that external submissions need the `isDefEq` check. I'll send the follow-up's PR number when it's up.
