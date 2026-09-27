---
cursor:
  subagentId: "bc-6d082f2c-9c48-534c-9ae6-46bf3724b4a7"
---

lane: red-team-hm96 · kind: report · status: final · created: 2026-09-26T21:40Z · repo: danielreuter/verity · origin: PR #88 @ f1df809f

CHECKPOINT (03:29Z) [final] PR #83 @ b32e1a7b (M0's ChaCha20 hm96 salts): GRANT WITH CONDITIONS. C1 before M1's masks: the prover
checks both reps' level-0 roots before any proof leaves (F1). art:145996e9; `finding` label on r20260927-022832-8b16.
CHECKPOINT (22:56Z) [final] PR #93 @ cd00f704: GRANT WITH CONDITIONS. C1: the Hashes lines of frame-v3 §6 and vllm-v1 §10 must
name the SHA-256 identity and domain digests (F1). C2: Daniel decides whether E4 extends to them. #88's C1 holds. art:29dc2ccb.
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

## Follow-up: PR #93 (E4, SHA-512 commitments) @ cd00f704

The verdict and findings are in `lanes/coordinator/20260926T2256Z-handoff-from-red-team-hm96.md`.

- **Checkouts:** throwaway worktrees at `/tmp/rt93` (cd00f704) and `/tmp/rt93-base` (a53900df, main with #88's C1 and C2). CPU
  torch went into head only, for `failclosed.py` and gkr.
- **New scripts in `evidence/`:**
  - `recompute_sha512.py` recomputes the three `*_sha512.json` files with no verity import;
  - `negatives_sha512.py` attacks the reference verifiers and the vLLM gate;
  - `failclosed.py` re-runs #88's fail-open probe.

  #88's `recompute_hm96.py` and `vllm_hm96_attacks.py` were re-run for the SHA-256 regression.
- **Handoffs received:** `lanes/red-team-hm96/20260926T2255Z-handoff-from-coordinator.md`, the #93 brief, acted on in full.
- **Handoffs sent:** `lanes/coordinator/20260926T2256Z-handoff-from-red-team-hm96.md`.

~~~text
tip: none, review only (target cursor/sha512-commitments-18a8 @ cd00f704, base main@a53900df)        merge-with: none
known-failures: backends/gkr/tests collection error on head and base without torch (passes on head with CPU torch)    pod: none; $0
artifacts: art:29dc2ccbbe75c4e9bc43caa720e1636795e2ed34f81b0d1915e2572be4f7cf95
~~~

**Labels:** `finding` by red-team-hm96 on `r20260926-221723-71aa`, `r20260926-221754-0cce`, `art:b9bb217f` and `art:a7a8ccce`, all
with ref `art:29dc2ccb` and written through to R2.

## Follow-up: PR #83 @ b32e1a7b (M0's hm96-sha512 salts from ChaCha20 under a fresh per-proof OS key)

The verdict and findings are in `lanes/coordinator/20260927T0329Z-handoff-from-red-team-hm96.md`.

- **How it ran:**
  - a code read of the single commit `b32e1a7b`, in a throwaway worktree at `/tmp/rt83`;
  - M0's note, which is only on the notes remote, read from a shallow sparse clone;
  - `evidence/chacha_salts_check.py`, which compares M0's Rust and device ChaCha20 (extracted verbatim, built with rustc and
    g++), an RFC 7539 implementation and OpenSSL;
  - M0's L40S selftest results, read from run `r20260927-022832-8b16`.
- **Handoffs received:**
  - `lanes/red-team-hm96/20260927T0312Z-handoff-from-coordinator.md`, the brief;
  - `lanes/red-team-hm96/20260927T0235Z-handoff-from-flock-netlist.md`, M0's note, on the notes remote.

  Both were acted on in full.
- **Handoffs sent:** `lanes/coordinator/20260927T0329Z-handoff-from-red-team-hm96.md`. It asks the coordinator to forward C1 to
  flock-netlist.

~~~text
tip: none, review only (target cursor/flock-netlist-m0-4d6a @ b32e1a7b)        merge-with: none
known-failures: none    pod: none (CPU only); $0
artifacts: art:145996e9c209ca518420a7c98f46094750bf652887116fa4152cd5382176786c
~~~

**Label:** `finding` by red-team-hm96 on `r20260927-022832-8b16`, with ref `art:145996e9`, written through to R2.
