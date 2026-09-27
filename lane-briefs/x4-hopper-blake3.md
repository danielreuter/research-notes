---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Lane x4-hopper-blake3: H100 keyed-BLAKE3 Table 2 cells at the x4 fold

Budget $40 · FINAL 7 PM PT (02:00Z) · base `origin/main` (`cd963fd4` or later) · branch `lane/x4-hopper-blake3`.
Read first: `internal/lane-briefs/cloud-lane-setup.md` (sections 1, 4, 5, 6: notes token, pods, idle while waiting),
`$RESEARCH_NOTES/kb/LANE-CONTRACT.md`, `$RESEARCH_NOTES/kb/TABLES.md` (rules I, M and plateau).

## Why

Table 2 at `cd963fd4`: H100 BF16 and E4M3 keyed-BLAKE3 are 2.8e8×, from x1 runs (blake3-80gb). The same H100s under SHA-256
at the x4 fold are 1.0–1.1e8× (art:4aa258ee, art:fcd6a623), and the 4090 keyed-BLAKE3 x4 cell is 1.9e7× (art:ecccca50). An
x4 keyed-BLAKE3 cell on each H100 row should land well under the SHA-256 ones.

## Goal

A verified, red-team-labelled B-Ligero cell for `fp8-hopper-x4+blake3` and `bf16-hopper-x4+blake3` (H100 SXM5 80GB), each
at its throughput plateau. Optionally the same under `blake3-xob` (the XOR-output-bits leaf, 0.78× the rows; on main
since `38a8d35d`, pinned for fp8-ada only). Measure it only if the pins and gate come cheap, and report both.

## Steps

1. **Pins.** Neither relation has a `leaf.rs` PINS row under blake3. Generate fixtures and gate them on an H100:
   `b-ligero-standard-hash`'s `10-pins-gates.sh` does exactly this (`LEAF=blake3 RELS="fp8-hopper-x4 bf16-hopper-x4"`).
   Copies: the notes clone's `lanes/b-ligero-standard-hash/evidence/pod-scripts/` (with `lib.sh`, `15-rust.sh`); the
   coordinator's gate of the same flow is `lanes/coordinator/evidence/70-xob-cherry-gate.sh`. Every gate must pass all
   86 negatives. Commit the two PINS rows and send a **merge-ready handoff** to `lanes/coordinator/` with the tip, the
   gate run ids and the system digests.
2. **Class grant.** In the same handoff, ask for the red-team review. The coordinator routes it; `fp8-ada-x4+blake3` was
   granted with conditions at 1226Z, and this is the hopper extension of that grant.
3. **Plateau sweep** on the pinned tree (don't wait for the merge; the verifier reverifies at the pinned tree): x4 at
   4096 / 8192 / 16384 / 32768 instances with the allocator defaults in `env.sh` (glibc `MALLOC_*`, merged `767115db`).
   Register each result (`bench-result/v1`) at once and `--preserve` it. Label every number with its profile.
4. **Rule I.** Re-packed x4 sets need an `instance-equiv/v1` document per plateau size. Use
   `python -m verity_numerical.bench.instance_equiv --vus <n>`, register it, and **don't** label it verified (you're
   its producer). reverify-fp4's handoff `lanes/coordinator/20260925T1706Z-handoff-from-reverify-fp4.md` shows the exact
   shape and the pitfalls: `--vus` equals the document's own n, and `--check` reads the raw file, not the artifact meta.
5. **Handoff for verification:** result art ids, equivalence art ids and the pinned tree to `lanes/coordinator/`. A
   non-producer verifies and labels; you don't.

## Pods and rules

- One H100 SXM 80GB (`vy-x4-hopper-blake3-h100`, `--register --project verity --guard 60`). Run everything through
  `research run --on ... --custody-r2 --custody-ttl 8h`. **End your turn while a job runs** (setup section 6: a `WAITING`
  checkpoint with the run id, the check-back time and your agent id).
- Terminate the pod at FINAL; say the spend.
