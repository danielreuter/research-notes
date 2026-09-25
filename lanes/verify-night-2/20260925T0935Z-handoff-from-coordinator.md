---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T09:35Z
---

# Re-verify with main 3301c435's reverify.py (steps pin + R1 + R2 + R4 merged)

main **3301c435** has ligero-steps-pin's c8a16e2b: H2 steps pin, R1 layout from `vu_index`, R2 recomputation of the a/b/y
bindings, roots and cover from the instance set, and R4 (stmt stems == proof stems == manifest entries, `n` == statements,
hashed decided by the pinned relation, an unreadable stmt is a FAIL).

- From now on, record CLEARED / PULLED on the marked cells only from a re-verification at 3301c435 (or later main), and
  name the commit in the label's ref.
- Don't write CLEARED on a +hash/+blake3 cell until red-team-standard-hash confirms its harnesses on 3301c435. You can
  run the re-verifications now and record the result; then add the label when the red team's verdict lands.
- +shared (v6) dumps and hashed dumps without a manifest `set` block now FAIL closed. Record those as "not re-verifiable
  yet (fail-closed)", not as PULLED.
- The 4096 frozen and 16384 plateau fp8-ada+blake3 4090 cells that b-ligero-standard-hash sent you (art:5d20ad00…,
  art:d6328cf5…) go through the same path. Footnote: file re-verification (runner's coins), not transferable.

**SP1 committed cell art:49695f7c (sp1-committed, FINAL), lower priority than the B-Ligero cells.** red-team-standard-hash
(0925Z, `lanes/sp1-committed/20260925T0925Z-handoff-from-red-team-standard-hash.md`) found b54e42ed's R3 fix open on the
`--instances` path: without `--batch`, `committed-verify` returns `instance_roots: null`, so prover-chosen roots pass. I
labelled the cell `finding: UNDER RE-VERIFICATION`. Re-verify it with `committed-verify --batch` against its frozen set
(its manifest names the batch file sha 531a5c01…, fp8-ada instances [0, 4096)). If every rep shows `instance_roots: true`,
it's CLEARED; if any rep doesn't, it's PULLED. Don't edit sp1-committed's code; if the check can't run, tell me why.
