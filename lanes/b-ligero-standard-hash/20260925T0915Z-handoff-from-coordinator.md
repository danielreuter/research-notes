---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T09:15Z
---

# Your 0906Z decisions: XOB waits and gets a new scheme name; no live-verifier run is required; tile stays fail-closed

**806a2f73.** Agreed. I'll merge it together with ligero-steps-pin's "ready" fix, and I've told them to include it. If
their ready tip lacks it, I'll merge your branch right after theirs.

**1. XOB gadget: not now.** The overnight target is the first verified B-Ligero BLAKE3 full-relation cell on the pinned
`+blake3`. Don't disturb it. Once that cell is CLEARED, wire XOB under a **new scheme name**, not a re-pin: a re-pin would
make every `+blake3` cell provisional (TABLES.md, "Red-team review of statement changes"), while a new name leaves them
standing. Its cells stay provisional until a `red-team-*` audit grants the class. Until then, keep 8dace837 on your branch
as a prototype, and record the 0.776× rows-per-block figure in your drill-down notes as a prototype result, not a cell.

**2. Interactive-mode cells: no live-verifier run is required for Table 2.** Per TABLES.md, "Table 2", the footnote must
say who verified and how. A file re-verification that replays the runner's coins is admissible, labelled "not transferable
evidence". So the verify-night-2 footnotes will say "file re-verification (runner's coins), not transferable". A live
verifier with its own coins is the stronger footnote: do one only if it's cheap on a pod you already have, after the
steps-pin/R4 merge, on the 4096 frozen cell.

**3. Shared/tile dumps: fail-closed is correct.** Keep it. Carrying `tile` in the manifest's `set` is a follow-up after
the R4 merge; it's not blocking. Until it lands, no tile/shared dump goes to verify-night-2.

**Next, as you planned:** the device-vs-host commit-evidence smoke on the 4090, re-measuring the x1 cell with main's GPU
committer, then the fp8-ada-x4 fold probe.
