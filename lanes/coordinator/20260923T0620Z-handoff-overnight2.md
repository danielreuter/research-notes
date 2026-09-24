---
id: r21/coordinator/20260923T0620Z-handoff-overnight2
campaign: r21
lane: coordinator
kind: handoff
status: active
repo: verity-main
origin: chat fc58f329 (coordinator session), 2026-09-23 06:20Z
---

# Overnight 2 (Sep 23, 05:45Z -> 12:30Z): plan of record

## User decisions (05:39Z, verbatim intent)

"Let's not get too fancy. Idc about 2x. Let's get this working with the ZK-friendly hash. Please price that into our
runs. In the morning I want to see massively hill-climbed results for each of these targets with 1. no commitments
2. ZK-friendly hashes as part of the proof."

Earlier tonight: Fiat-Shamir dropped from the matrix (no FS runs); a live verifier on a separate machine is the
verification story (everything persisted; anyone can ask for a fresh proof); latency is a first-class axis; the
commitment design is Poseidon2-over-BabyBear hashing of the operand rows *inside* the relation (W, x private via ZK),
NOT the algebraic leaf/v2 (randomizer budget / re-randomization) option.

## Morning deliverable

Table 2 with two columns per target (A100 bf16-ampere, H100 bf16-hopper, H100 fp8-hopper, RTX 4090 fp8-ada, RTX 5090
fp4-nvf4), interactive ZK, live-verifier verified where the runbook worked:

1. `authentication=excluded` (bare relation) - hill-climbed vs tonight's baseline
   (A100 1.78 s | H100 bf16 0.727 s | H100 fp8 0.397 s | 4090 fp8 2.246 s | 5090 nvf4 1.636 s, main 6babe27).
2. `authentication=included-hash` - same proof + Poseidon2 digests of the operand rows checked against Merkle roots.
   Headline = `sharing=tile64x64` (64 distinct x rows x 64 distinct W columns, each hashed once, VUs bound via
   lookups); drill-down = `sharing=none` (every VU hashes its own x row + W column). If hash-relation is not mergeable
   by the freeze, column 2 shows the cost-model number (+70-88 % from auth-integration s2c) marked as such.

Plus: before/after per lane, comms/verifier table (proof B/s at the proved rate, statement bytes for v4 vs v5, verifier
wall + CPU), budget, open items.

## Wave 1 lanes (background Tasks; ids in the coordinator todo)

| lane | pod | owns | target |
|---|---|---|---|
| hp2-host | 4090 dev, H100 <= 1.5 h | protocol.py host phases, proof writer, witness_device, streams | bf16-hopper <= 0.35 s, fp8-hopper <= 0.20 s, byte-identical |
| enc-hopper | H100 all night (<= 7.5 h) | encode_simt, Merkle/hash kernels (moved to commit_gpu.py), fusion; arity only as option | encode+merkle 0.16 -> <= 0.05 s |
| relmin-lookup | 4090 | relations.py/compile.py unit compilers, new v2 relation names + Rust pins | >= 2x fewer rows/unit, same accepted set |
| fp4-fast | 5090 | fp4/*, chain.py width validation, coins_sha256 manifest lines | 1.636 -> <= 0.5 s, l sweep |
| live-verifier | 4090 <= 4 h + CPU pod | live.py, `--verifier tcp://`, verifier= hook, contract t.total_live | RUNBOOK by 10:15Z; serve Wave 2 |
| hash-relation | 4090 | poseidon2 gadget, relchain assembly, statement v5, leaf/v2h committer, Rust v5 | committed column measured on 4090; worst case then tile |
| honing-code | none | tools/research code + tests only; NO store mutations | coordinator runbook for the store pass |

Ownership boundaries are written into each brief; expected small merges: chain.py (fp4-fast validation vs
hash-relation end components), relchain.py (fp4-fast manifest lines vs hash-relation assembly vs live-verifier coin
hook), run.py flags (several lanes, one flag each), protocol.py (hp2-host internals vs live-verifier hook vs
enc-hopper call site).

## Coordinator loop

- Every ~90 min: read each lane note's top "CHECKPOINT <sha>" line; merge mergeable checkpoints into main in order
  hp2-host, enc-hopper, fp4-fast, relmin-lookup, live-verifier, hash-relation, honing-code. Hygiene: `git status
  --short` clean before/after, `rg -l '^<<<<<<< '` empty, laptop pytest subset, `cargo check` on vy-sp1 for Rust
  deltas, push after every merge. Independently verify any dumps lanes pulled (`/tmp/*/verify_record.py` pattern,
  Rust `ligero-verify batch --target-bits 128`, labels `--by coordinator`).
- Pods: `uv run research pods list` each sweep; expected vy-hp2-host, vy-enc-hopper, vy-relmin, vy-fp4-fast,
  vy-live-verifier (+ a 4090), vy-hash-relation, plus vy-control/vy-sp1; other session's vyv-* are not ours.
  Ceiling tonight ~ $12/h; planned total ~ $90 against the $220 cap.
- Disk: keep >= 4 GB free (`/tmp/store_evict.py --target-free-gb 6`); lanes were told to check before `data pull`.
- 10:15Z checkpoints collected; 10:30Z FREEZE main; launch Wave 2 device lanes (A100 `NVIDIA A100-SXM4-80GB`, H100
  `NVIDIA H100 80GB HBM3`, 4090, 5090 with image runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04):
  per target quick operating-point sweep at >= 128 bits for both columns, final 3-rep int-ZK runs against the live
  verifier, dumps pulled, snapshots `dev-<gpu>-v1`, labels `--by dev-<gpu>`; only live-verifier writes `verified=`.
- 12:30Z: merge all, render Table 2 (two columns), verification from bytes, DECISION_DRAFT addendum, Notion dossier,
  morning summary.

## Sweep log

- 06:45Z sweep 1: pods up; disk 1.2 GB -> verified 4 fixture/v1 on R2, evicted 2.8 GB; live-verifier d55c9c3 ff-merged.
- 07:55Z sweep 2: disk 151 MB -> evicted 2.2 GB + trees/ 2.4 GB; watchdog under launchd. Merged hp2-host a1f199d
  (relchain.py conflict vs live hook resolved by hand: set_statement re-added in prove_vus; `--pipeline` path only when
  `live is None`), enc-hopper 429f8ea, fp4-fast 063c607, relmin-lookup 0055c41 -> main 02c3321. relmin v2 = PUBLIC
  SELECTION (verifier recomputes products/alignments; unusable for private operands) -> finding, not Table 2; launched
  relmin-private for private-operand v3 units.
- 08:55Z sweep 3: merged hp2-host 820dc9d (six commits), relmin d4ef0f9, live-verifier 83d1de3 -> main 9d35c4e; Rust 37
  + bench 155 + research 162 green. hp2-host H100 baseline (main 6babe27 on Xeon 8462Y+ host): bf16-hopper int-ZK 0.662 s,
  fp8-hopper 0.379 s (their own numbers pending). Live verifier SERVING at tcp://213.173.105.69:30899 (EU-RO-1) since
  06:24Z; 4 concurrent 4096-VU sessions accepted. hash-relation: 13 commits (Poseidon2 w24 in relation, statement v5,
  Rust v5 + pins, negatives, tile layout, PROTOCOL.md 8d) but NO NOTE yet. 3.9 GB pending run-files being pushed by
  relmin-lookup's own `push --pending`; watchdog evicts after.

## Wave 2 brief template (fill: FROZEN_SHA, column-2 flags from hash-relation's note/run.py)

Lane `dev-<gpu>` (A100 bf16-ampere | H100 bf16-hopper + fp8-hopper | 4090 fp8-ada | 5090 fp4-nvf4), deadline 12:15Z:
1. Worktree at FROZEN_SHA (detached, no commits unless a gate fails -> report immediately, don't fix silently).
2. Pod: `research pods create --name vy-dev-<gpu> --gpu "<id>" --cloud SECURE --disk 100 --require-reference-part`
   (5090: `--image runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04`); bootstrap per ada-ref/fp4-proof
   recipes; register in machines.toml by hand if needed.
3. GATES FIRST on frozen main: `run.py gate <relation>` for the lane's relations (+ hashed variants) - the merge of
   hp2-host/live-verifier in relchain.py was resolved by hand without a GPU.
4. Column 1 (bare, `authentication=excluded`): (A) speed: `--pipeline 3` local coins, int-ZK, 3 reps, dumps ->
   coordinator verifies from bytes (D7: not transferable); (B) live: `--verifier tcp://213.173.105.69:30899` (runbook (b)
   in live-verifier note; `live probe` first; if RTT > 100 ms or throughput < 200 Mbps note it and continue), sequential,
   int-ZK, 3 reps -> `verified=accepted --by live-verifier` via runbook (c) `live record`. Report t.total (A), t.total (B),
   t.total_live (B), net.rtt_ms.
5. Column 2 (`authentication=included-hash`): hash-relation flags (`--auth included-hash`; `--tile 64x64` headline
   `sharing=tile64x64`; worst case `sharing=none`), same (A)/(B) treatment where the live verifier supports v5 (check
   its note; else coordinator-verified from bytes with Rust `ligero-verify` v5).
6. Operating-point mini-sweep (l in {8192, 16384, 32768} x rate) at >= 128 bits for each column; pick the best; final rows.
7. Contract-valid, labels `--by dev-<gpu> --ref <run>` (relation, authentication, hash, sharing, note=host CPU/VRAM/load),
   `research data pull` (df check / evict), `push --pending`, snapshot `dev-<gpu>-v1`; terminate pod; note with the
   before/after table vs tonight's baseline (A100 1.78 | H100 0.727/0.397 | 4090 2.246 | 5090 1.636).
   Budget: A100 $4 | H100 $7 | 4090 $2 | 5090 $3.

## Column-2 definition note (to state in the morning report)

The committed column's cost depends on operand sharing inside a proof. Real inference shares W columns across tokens
and x rows across output columns; the frozen 4096-VU workload as generated has independent operands per VU. Column 2
therefore reports the tile arrangement as headline (same FLOPs, same relation, same 4096 VUs) and the independent-VU
arrangement as the worst case. Both are `authentication=included-hash`, differing in the `sharing=` label.
