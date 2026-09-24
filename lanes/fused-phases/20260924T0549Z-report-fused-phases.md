---
lane: fused-phases
kind: report
created: 2026-09-24T05:49Z
status: final
---

CHECKPOINT 9989797f (06:44Z) [final] 9989797f: phase-sum fixed (median rep; 5/5 seeded pre/post proofs identical; A/B -1.9% = noise), 15 equiv files re-derive at tip, bf16-ampere on frozen, tile refs fixed; 5 fp8-ada cells PRESERVED (v3x4 p8 art:06be3b23 0.0963 s); left: U + equiv labels; pod terminated, $1.04
CHECKPOINT 7b74c31 (06:23Z) [open] seeded pre/post IDENTICAL: v3x4-p8, v3-p8, v1-p4 (pre-fix v3-p8 1.058x, v1-p4 1.019x t.total; post 1.000x); gates 0F: fp8-ada v3x4 art:5541519b v3 art:e735215f v1 art:661074a8, ampere v3x4 art:70183281 v3 art:e5120ed6; equiv --check 15/15 at tip. Next: A/B, FINAL
CHECKPOINT 73a1250 (06:14Z) [open] 5 fp8-ada cells PRESERVED: v3x4 p8 art:06be3b23 p4 art:91c62994, v3 p8 art:7f294d16 p4 art:d0789c44, v1 p4 art:2d685314; tables: v1 only U, v3/v3x4 U + equiv label (art:574f3519/d40f5065). Next: seeded pairs, pytest, A/B, equiv --check
CHECKPOINT a337e7b (06:08Z) [open] 4090 fp8-ada: seeded v3x4-p8 pre/post proofs IDENTICAL (13/13); v3x4 p8 art:06be3b23 (t.total 0.0963) p4 art:91c62994 (0.1050), buckets=t.total, contract ok, not contended; bf16-ampere-v3 gate 0 failures. Next: v3 p8/p4, v1 p4, seeded pairs, tables
CHECKPOINT 9989797f (05:55Z) [open] HANDOFF 9989797f fill lanes can start (lanes/coordinator/20260924T0554Z-handoff-from-fused-phases.md): phase-sum fixed, 15 equiv files, bf16-ampere v2/v3 on frozen, --tile refs were mislabeled frozen (fixed; art:6e2c0d79 must not count). tables-fix 0539Z: meta.lane set. Next: 4090 cells
CHECKPOINT none (05:49Z) [open] 5b30c99b: (a) fix = t.total+buckets from ONE median rep (phases.py, unit test); (b) derived-relation digests name the relation, numbers equal: 15 instance-equiv files PRESERVED (fp8-ada-v3x4 art:d40f5065); bf16-ampere v2/v3 -> frozen vu-k1536. inbox 0540Z used as pre-fix ref. Next: gate, 4090 cells, handoff

## FINAL

~~~text
tip: lane/fused-phases @ 9989797f (base lane/post-wave@3adf4c28)        merge-with: none
known-failures: none    pod: terminated 06:44Z (vy-fused-phases 3tvd7rspgbn8e1, up from 05:20Z at $0.74/h); $1.04
artifacts: art:06be3b23 art:91c62994 art:7f294d16 art:d0789c44 art:2d685314 art:55460a98 art:3e2d5867 art:986f091f art:e8448a57 art:de0b9b68 art:5541519b art:e735215f art:661074a8 art:70183281 art:e5120ed6 art:b4036618 art:4d77a13a art:bc167660 art:91ef2cd9 art:a5d5fb94 art:68466c4a art:574f3519 art:f355573b art:d40f5065 art:f70cf39f art:b5584b28 art:5133f6c1 art:95df4a8e art:bfd18a1d art:9c8c306c art:539af2c6 art:8036d0ba art:59193d43 art:0749fa9d art:4cd768c2
~~~

Outcome: all four deliverables done. The three commits on lane/post-wave (ca0d77e6, 5b30c99b, 9989797f) were handed off
at 05:54Z (`lanes/coordinator/20260924T0554Z-handoff-from-fused-phases.md`, `lanes/verify-night/20260924T0554Z-...`); the
tip has not moved since. tables-fix's 06:08Z note already routes a 4090 cell through art:68466c4a (fp8-ada-v2).

**(a) Phase sum: fixed in the runners, not the fused path.** `relchain.bench_vu_rel` and `vu.bench_vu` took the per-key
median of every lap over the reps; with `--pipeline` each rep's buckets sum to that rep's prover time, but per-bucket
medians mix reps (timed rep 1 is ~4x slower), so their sum exceeded the median t.total. From ca0d77e6 t.total and all
six buckets come from ONE rep, the one with the median prover time (`phases.median_rep`; `validation.evidence.phase_rep`).
The contract check is untouched. Unit test `backends/direct/ligero/phases_test.py` (torch-free; it also shows the old
aggregation failing `contract.validate_measurements`). The same seeded runs show the bug on v1 too (pre-fix v1 p4 1.019x).

Seeded pairs (os.urandom from `random.Random(20260924)`, 3 reps; pre = the lane's changed files restored from 3adf4c28):

| cell | pre t.total, sum/t.total | post t.total, sum/t.total | proofs + statements |
|---|---|---|---|
| v3x4 l=4096 p8 | 0.0986, 1.0059 | 0.1016, 1.0000 | 13 / 13 identical |
| v3x4 l=4096 p4 | 0.1115, 1.0009 | 0.1035, 1.0000 | 13 / 13 identical |
| v3 l=16384 p8 | 0.1328, **1.0576 (contract fails)** | 0.1355, 1.0000 | 13 / 13 identical |
| v3 l=16384 p4 | 0.1473, 1.0081 | 0.1421, 1.0000 | 13 / 13 identical |
| v1 l=16384 p4 | 0.1912, **1.0193 (contract fails)** | 0.1920, 1.0000 | 13 / 13 identical |

Timing, idle-GPU A/B on the same pod (fp8-ada-v3x4 l=4096 p8, genuine coins, 5 reps, alternating pre / post / pre /
post): median per-rep prover+hints 0.099 / 0.099 / 0.105 / 0.099 s; reps 2-5 mean 0.1005 s pre vs 0.0986 s post (-1.9 %,
inside the 4.6 % spread between the two pre runs), so unchanged within noise. The pre-fix runs reported sum/t.total 1.0090
and **1.0602 (contract fails)**, the post-fix runs 1.0000 (`evidence/pod-out/runs/ab*`, `runs.txt`).

**(b) Instances, three causes.** (1) The derived relations (`-v2 -v3 -v2x4 -v3x4 -x4` of fp8-ada, bf16-hopper,
fp8-hopper) prove the same numbers as v1; `relchain.instances_digest` hashes the relation name into the manifest.
`verity_numerical.bench.instance_equiv` (5b30c99b) writes the BRIEF §5 file from both loaders' canonical x, W, y: 15 files,
all `equal: true`, PRESERVED, unlabeled, `meta.lane = fused-phases`; `--check` on the registered copies re-derives all 15 at
9989797f on the pod (`evidence/pod-out/equiv-check.log`). (2) Runner bug: bf16-ampere-v2/-v3/-v2x4/-v3x4 drew their own
synthetic set; they now read the frozen `vu-k1536` set (gates 0 F: v3x4 256 VUs art:70183281, v3 64 VUs art:e5120ed6).
(3) New: `--tile NxM` runs carried the frozen ref while proving `relchain.tile_instances` (x, W, y all differ): from
9989797f they name their tile; wave-4090-2's shared committed cell art:6e2c0d79 must not count. fp4-nvf4 already carries the
frozen ref at `--total-vus 4096` and has no derived relation.

**Validation (4090, fp8-ada, lane tip, genuine coins, 5 reps; bench.summary: contract ok, not contended, `other` 0.0000):**

| cell | t.total s | bench-result | run-files | tables.py reasons left |
|---|---|---|---|---|
| fp8-ada-v3x4 l=4096 p8 | 0.0963 | art:06be3b23 | art:55460a98 | U; I until art:d40f5065 is labeled (tables-fix renderer) |
| fp8-ada-v3x4 l=4096 p4 | 0.1050 | art:91c62994 | art:3e2d5867 | U; I until art:d40f5065 is labeled |
| fp8-ada-v3 l=16384 p8 | 0.1398 | art:7f294d16 | art:986f091f | U; I until art:574f3519 is labeled |
| fp8-ada-v3 l=16384 p4 | 0.1291 | art:d0789c44 | art:e8448a57 | U; I until art:574f3519 is labeled |
| fp8-ada l=16384 p4 | 0.1799 | art:2d685314 | art:de0b9b68 | U only |

U = not independently verified; I = instances differ (the frozen renderer at this tip lists I without the equivalence).
No phase-sum, contract, B, K, security, proof-class, authentication or SKU reason on any of them
(`evidence/pod-scripts/70-reasons.sh`, all reasons from the json render). Gates, lane tip, 0 failures: fp8-ada-v3x4 341
VUs l=4096 1 honest / 99 negatives art:5541519b, fp8-ada-v3 64 VUs 1 / 92 art:e735215f, fp8-ada 64 VUs 1 / 92
art:661074a8. Pod pytest (phases_test, test_instance_equiv, fold_test, hints_fused_test): 124 passed.

Left for others: verify-night / coordinator label the 15 equivalence files (`research data label ART verified accepted`)
and independently verify the five results; tables-fix's renderer (bdaf2c44) must be in for the equivalences to count.

Handoffs received: `20260924T0539Z-handoff-from-tables-fix.md` (register equivalences with a producer: done, `meta.lane =
fused-phases` on all 15; its renderer names that producer), `20260924T0540Z-handoff-coordinator.md` (wave-4090-2's
overshoot as the before-fix reference: used, plus same-pod seeded pre-fix runs above). Sent: coordinator and verify-night
handoffs at 05:54Z. kb: `pods-4090.md` (phase-sum cause, tile refs, this pod's cells), new `bench-instances.md`.
Evidence: `evidence/pod-scripts/` (every script that ran), `evidence/pod-out/` (runs.txt, result.json + log of every run,
gates, equivalence and check logs, pytest), `evidence/registered.txt`.
