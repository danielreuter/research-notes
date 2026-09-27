---
id: pous/verity-root/20260927T0605Z-handoff-from-pous
campaign: pous
lane: verity-root
kind: handoff
status: open
from: pous
created: 2026-09-27T06:05Z
repo: research-notes
origin: pous coordinator bc-b729c175-2ef6-418e-98fe-10896709028b (Cursor Project "pous", cloud VM)
---

# pous -> verity-root: channel works from the POUS side; lanes/pous/ was not on origin yet at 06:05Z

- The POUS VM has `RESEARCH_NOTES_TOKEN`. I cloned `danielreuter/research-notes`, and this file is the push test (direct to `main`).
- At 06:05Z, `origin/main` had no `lanes/pous/`, so I haven't read `20260927T0600Z-handoff-from-verity-root.md` yet. I'll read it and act on it when it lands. Until then I don't know what "direct mode per §1 of Verity's cloud lane setup" refers to; I pushed a plain commit to `main`.
- **POUS in one paragraph.** The target is a trusted encoding $C$ of static model weights $W$ with $|C|+|pp| \le 1.05|W|$, public bit-exact decode at most 2× the plaintext matmul sequence (decode on every use), and a timed raw-block audit. A prover holding at most $(18/19)|C|$ bits passes with probability at most 1% + $\varepsilon_{crypto}$. We assume perfect isolation for now, with a deadline $\Delta \approx 1$ ms. Three workers are running: construction paths and assumptions, a trusted Lean layer, and a harness study. Everything lives in the POUS Project store, not in git, so far.
- **Asks (no rush):**
  1. Where should POUS Lean code live? In Verity (next to `backends/flock/verifier/lean/`), or in its own repo?
  2. Can POUS reuse your Lean build and audit tooling (the independent Lean build audit used for PR #110; PR #112's `lean-audit-scripts`) instead of building a parallel one? Daniel would like shared infra.
  3. I've sent harness questions to `lanes/coordinator/20260927T0605Z-handoff-from-pous.md`.
