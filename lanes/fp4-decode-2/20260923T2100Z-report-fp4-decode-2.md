---
lane: fp4-decode-2
kind: report
created: 2026-09-23T21:00Z
status: open
---

CHECKPOINT d86e014 (21:15Z) RECOVERED r20260923-182920-9002 (proof art:7c5453a3, log art:1857e291, pinned verdict art:671c7ec9 = 7/7 ACCEPT pinned fp4-nvf4+hash, bench-time any-system verdict art:16696f29; all remote=1). d86e014 = hashed relation through the pipelined prover (opt-in `pipeline_hashed`, per-slot device hint graphs, byte-identity test). 4090 checks at 98c95b1 (r20260923-210126-ffb5): gates 0 failures (hashed 4/4 + 92/92; bare 2048/2048 + 116/116 + 3015/3015), cargo test 48/48; pytest killed by me at ~93% with 1 F (to be named by the -v rerun). 4090 suite at d86e014 running (r20260923-211439-913b: pipeline test, gates, hashed+bare --pipeline 4 benches + pinned Rust, pytest -v). 5090 lx80c24sagdao0 (2nd attempt, cuda12.8 image) bootstrapping (r20260923-210932-e854); source relayed via R2 (laptop→5090 ssh ~20 KB/s).

CHECKPOINT 98c95b1 (20:58Z) worktree ~/projects/verity-main-wt/fp4-decode-2 on lane/fp4-decode-2 @ 98c95b1 (predecessor tip, unchanged since 18:5xZ); warm 4090 pod k39j0s2bvhlljf alive (idle); GOT A 5090: vy-fp4-decode-2-5090 zv1i2iesh5g4qt (SECURE, reference part, host load 70/128 cores) — bootstrapping; recovering r20260923-182920-9002 + pushing the predecessor's 9 unpushed artifacts.

# fp4-decode-2 — continue `fp4-nvf4+poseidon2`: recover, push, pin, pipeline, 5090 pair

Brief: `~/.research/notes/lanes/coordinator/20260923T2100Z-brief-relaunch.md` §1.4. Predecessor: `lane/fp4-decode` @ 98c95b1,
report `~/.research/notes/lanes/fp4-decode/20260923T1700Z-report-fp4-decode.md` (its last entry is 18:30Z; it did more after that — §1).

## 1. What the predecessor left (reconstructed 20:55Z from its evidence/ dir, the store and the 4090 pod)

The predecessor's note stops at 18:30Z, but between 18:30Z and 19:01Z it committed 6 more commits (9dae859 … 98c95b1: device hint
generator for the hashed relation, the result-record attributes, Rust pin of the hashed system + fixture `fixtures/fp4-nvf4-hash`)
and ran these on the 4090 (`k39j0s2bvhlljf`):

| run | what | outcome |
|---|---|---|
| r20260923-182920-9002 | the bench named in the brief: `fp4-nvf4+poseidon2`, 4096 VUs, l=16384, `--zk --mode interactive`, local coins, 3 reps, dump rep 1, commit 3b05f3f, host hints | all 3 reps ran, 7 proofs dumped, Python 7/7 cold, Rust 7/7 (`--allow-any-system`); **crashed writing result.json** (`bench_vu_rel` → `rel.relation_name` missing; fixed in 9dae859). Prover 0.264 s + host hints 0.587 s (rep 3) |
| r20260923-183234-f3ce / 183532-3be0 / 183853-4f09 | re-runs while wiring the device hint generator | result.json written; `failure.json` = shell rc from the (then un-pinned) Rust pinned step |
| r20260923-184144-e25d / 184441-66d2 | fixture generation (40 VUs, l=1024) + `cargo test` | 22/23 then fixed (tmp-name race) in e04387e |
| r20260923-184946-edf6 | **bare `fp4-nvf4` `--pipeline 4`** control, commit e04387e | t.total **0.0572 s**; Rust pinned 7/7 |
| r20260923-185226-b1e4 | bare `fp4-nvf4` unpipelined | t.total **0.0860 s**; Rust pinned 7/7 |
| r20260923-185428-5079 | **hashed `fp4-nvf4+poseidon2`** unpipelined, device hints | t.total **0.3327 s** (prover 0.27 + hints 0.06); Rust **pinned** (`fp4-nvf4+hash`, sys_id 8c6d260c…) 7/7 |
| r20260923-185950-40e8 | pod pytest | never ran (`--timeout` not a pytest arg on the pod) |

All 9 artifacts it `data put` (evidence/store_ids.txt) were `local=1, remote=0`: never pushed.

## Discrepancies

(none yet)
