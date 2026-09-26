---
cursor:
  subagentId: "bc-6d082f2c-9c48-534c-9ae6-46bf3724b4a7"
---

lane: red-team-hm96 · kind: report · status: final · created: 2026-09-26T21:40Z · repo: danielreuter/verity · origin: PR #88 @ f1df809f

CHECKPOINT (21:40Z) [final] PR #88 @ f1df809f: GRANT WITH CONDITIONS. C1: hm96 must fail closed off the host path (F1, medium).
C2: doc fixes (F2, F3). art:6f13f90a; `finding` labels on r20260926-204634-0958 and art:b3a08e21.

# red-team-hm96: review of `hm96-sha256/v1` (PR #88)

The verdict, the six numbered findings and what holds are in the handoff
`lanes/coordinator/20260926T2140Z-handoff-from-red-team-hm96.md`. This report records only how the review ran.

## How it ran

- **Checkouts:** throwaway worktrees at `/tmp/rt-hm96` (f1df809f) and `/tmp/rt-hm96-base` (2431e3c1), `uv sync` in each, and CPU
  torch 2.14 for the `failopen` probe and the vLLM commit tests.
- **`evidence/recompute_hm96.py`:** stdlib and numpy only, with no verity import.
  - It recomputes every entry of `vectors.json` from the spec text.
  - It adds a pure-Python SHA-256 for the length-extension negatives, the GF(2) ranks, and the witness-key equivocation demo.
- **`evidence/vllm_hm96_attacks.py`** has three modes:
  - `identity` fingerprints the default path; run it on base and head and diff the outputs;
  - `attacks` runs the hm96 negatives against the committer;
  - `failopen` is the F1 probe.
- **Script copies:** the store mount served a stale copy of an edited script once, so the runs used copies in `/tmp/rt-ev`. The
  artifact holds the exact files that ran.

## Handoffs

- **Received:** `lanes/red-team-hm96/20260926T2115Z-handoff-from-coordinator.md`, the brief, acted on in full.
- **Sent:** `lanes/coordinator/20260926T2140Z-handoff-from-red-team-hm96.md`, the verdict. It asks the coordinator to forward
  F6 to flock-netlist.

## FINAL

~~~text
tip: none, review only (target cursor/hm96-sha256-leaves-18a8 @ f1df809f, base main@2431e3c1)        merge-with: none
known-failures: none    pod: none (CPU only); $0
artifacts: art:6f13f90a1df4df8f587b98851b957414bfccd275de6ef0896b22b9321856f43d
~~~

- **No code pushed.** C1's fix belongs on PR #88's branch, and whoever the coordinator assigns can take `failopen` as its negative
  test.
- **Labels:**
  - `finding` by red-team-hm96 on `r20260926-204634-0958`, with ref `art:6f13f90a`;
  - the same on `art:b3a08e21`;
  - both written through to R2.
