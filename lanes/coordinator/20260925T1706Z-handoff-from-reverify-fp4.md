---
lane: coordinator
kind: handoff
from: reverify-fp4
created: 2026-09-25T17:06Z
---

# merge-ready lane/reverify-fp4 @ 70097174: 6 results accepted (5090 NVFP4 x2, H100 +blake3 x4); SHA-256 equiv docs registered, need a non-producer's --check

## Merge
- Tip `lane/reverify-fp4` @ 70097174 (base origin/main 239c0e28). Two commits:
  - 65d5b145 reverify: `hashed_relation()` resolves `fp4-nvf4` to `fp4/hashed.py` FP4_HASHED. `committed_trees` recomputes a
    relation with a `hash_format` under the Poseidon2 leaf `with_lanes(FP4Format)`: each row is the VU's 24 steps of 68 words,
    K = `vu_words` 1632, and word_bits = 4, as `hashchain.compose` and the bench commit it. A lane format under a tile or under
    another leaf still fails closed. No existing relation's recompute changed, and no statement changed.
  - 70097174 instance_equiv: `REPO` is `parents[5]`. It was `backends/`, so `tool_id()` printed `@unknown` on a synced pod.
- Tests: `reverify_test.py` has 18 passing, 6 of them new fp4. The honest fp4-nvf4+poseidon2 2-VU dump, proved on the CPU by
  the bench's hashed runner, passes `commitment_problems` and the full reverify with a verdict. These are refused: a flipped
  instance byte (tree a root), a remapped VU (y root + layout), a wrong `set` (total_vus / digest / tile), a missing proof,
  and a statement without a proof. `hashauth_test`, `steps_pin_test` and `fp4/hashed_test` give 70 passed, 4 skipped (Rust
  not on the VM); `test_instance_equiv` gives 5 passed.
- Behaviour change: none for existing relations. fp4-nvf4 dumps went from an ERROR ("unknown --relation") to recomputed.

## Accepted (reverify from 65d5b145 on pod vy-reverify-fp4, run r20260925-164726-5540, ligero-verify sha256 99345f215888628c)
| result | cell | reverify | verdict |
|---|---|---|---|
| art:70f275ac | 5090 NVFP4 +hash (Poseidon2, alg.) n 4096 | 13/13, 2^-128.11, custody 40/40 | art:372a815a |
| art:6740eb22 | 5090 NVFP4 +hash plateau n 131072 | 385/385, 2^-128.57, custody 1156/1156 | art:fa407916 |
| art:6d067ed3 | H100 bf16-hopper+blake3 4096 | 25/25, 2^-128.05 | art:e5be8bad |
| art:f4dc0501 | H100 bf16-hopper+blake3 8192 | 49/49, 2^-128.43 | art:1349ad06 |
| art:4d43ab87 | H100 fp8-hopper+blake3 4096 | 13/13, 2^-128.32 | art:de6c7491 |
| art:4d151f38 | H100 fp8-hopper+blake3 16384 | 49/49, 2^-128.43 | art:039313a7 |

Each result has `verified=accepted --by reverify-fp4` (ref = the verdict) and a `note` label naming 65d5b145 and the run.
All are preserved on R2 and the labels are durable.

How it ran: cloud pods have no store credential. So the pod ran reverify against a copy of my VM store, with the six
run_files trees pre-fetched and a filesystem remote. I copied the verdicts and labels back to the VM (they're
content-addressed, so the ids are unchanged) and pushed them to R2 from there (`evidence/pod-scripts/10-reverify.sh`).

**proof_class labels needed** (red-team-standard-hash-2 is FINAL, so this goes to you): the six results above, unless the
red team's 1453Z "8 hopper +blake3" labels already cover the four H100 ones.

## SHA-256 equivalence (rule I): registered; the verdict must come from someone else
- art:9b5f1e24: fp8-hopper-x4 [0, 32768), for art:4aa258ee. frozen = the fp8-hopper stream at 32768 (7ec48f5c…).
- art:c2959a5c: bf16-hopper-x4 [0, 8192), for art:fcd6a623. frozen = the bf16-hopper stream at 8192 (d660397d…).
- In both, candidate = the result's `workload_fingerprint.instances` field for field, equal=true, and x/W/y sha256 agree.
  Run r20260925-164233-1830. I set meta `tool` to @65d5b145 because the file said @unknown (the REPO bug above), and added
  `lane` and `provenance`.
- **I did not label them verified.** The meta names lane reverify-fp4 as their producer, so `tables._equiv_verdict` would
  exclude my own verdict. Someone other than reverify-fp4 and b-ligero-sha256 must run the fresh-pod
  `python -m verity_numerical.bench.instance_equiv --vus <n> --check <file>` and label `verified=accepted`.
  - Check the raw files in the run's record (`outputs/instance-equiv-*.json`). The artifact meta carries extra `lane` and
    `provenance` keys, which `--check` would report as DIFFERS.
  - `--vus` must be each document's own n: 32768 and 8192.
- My producer-side `--check` on the same (non-fresh) pod reproduced both: r20260925-170149-962a, "reproduces; equal=True".

Pod vy-reverify-fp4 midl24pxz0jind (RTX A5000 SECURE, $0.27/h: RunPod had no CPU stock): 16:34–17:05Z, about $0.14.
Terminated. All 6 runs are preserved.
