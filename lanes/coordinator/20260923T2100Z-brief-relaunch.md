---
lane: coordinator
kind: brief
created: 2026-09-23T21:00Z
status: open
---

> **Rules superseded (2026-09-24T01:00Z):** the standing lane rules (§0 and similar sections) now live in `~/.research/notes/kb/LANE-CONTRACT.md`, which wins where they differ. This brief's lane-specific content stands.

# Brief: relaunch of six stalled lanes + two device-wave scouts (21:00Z → FINALs 23:00–23:30Z)

Six lanes went silent together at ~19:00Z (no commits, no notes, pods idle at 0 % GPU, no processes): share-logup, ajtai-leaf,
blake3-leaf, fp4-decode, live-2, ligerito-verify-rs. Their work up to then is committed and pushed (ajtai-leaf also has 2 uncommitted
files in its worktree). Each gets a fresh lane that CONTINUES it; two new lanes de-risk tonight's device wave.

## 0. Rules for every lane (read first)

* **Branch:** create `lane/<you>` (e.g. `lane/share-logup-2`) at your predecessor's tip, in a NEW worktree
  `~/projects/verity-main-wt/<you>`:
  `git -C ~/projects/verity-main-wt/main worktree add -b lane/<you> ~/projects/verity-main-wt/<you> <predecessor-tip>`.
  Never commit to the predecessor's branch or worktree (read them freely). If the predecessor's branch gains commits after 21:00Z, stop
  and write that to your notes: two writers on one lane is a bug.
* **Standing rules:** `~/.research/notes/lanes/coordinator/20260923T1630Z-brief-leaf-campaign.md` §0 (worktrees, tests, one pod,
  `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, laptop disk, DISCREPANCIES cap, notes format) and the Wave-2 brief §0–§2 it points at
  apply verbatim, except where this brief says otherwise. Never merge into main; the coordinator merges.
* **Your predecessor's report is your starting point.** Read it end to end before touching code, and its evidence/ dir.
* **New tooling you may use** (from `lane/qol`, not yet on main; run it with
  `PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src ~/projects/verity-main-wt/main/.venv/bin/python -m research ...`):
  `research pods ssh <pod-name> [-- CMD]` (port looked up) and `research pods sync <pod-name> [SRC]` (ships the worktree's git-visible
  files to `/workspace/src`, rsync or tar fallback). `backends/direct/ligero/pod_bootstrap.sh` in that tree is an idempotent pod
  bootstrap (writes `/workspace/env.sh`); your reused pod is already bootstrapped, so you likely don't need it.
* **Custody:** anything that exists only on a pod is lost when the pod goes. Before terminating a pod: every result/gate/dump you cite is
  `research data put` + `research data push` (R2 creds: `set -a; source ~/.config/verity/r2.env; set +a`), and your note lists the art ids.
  Check with `research data sql "SELECT id, remote FROM artifacts WHERE ..."` that `remote = 1`.
* **Labels:** `research data label` is being tightened: use vocabulary keys (`research data vocab`); put measurements in the result JSON,
  not labels. No `verified=` labels (coordinator's job).
* **Notes:** `~/.research/notes/lanes/<you>/20260923T2100Z-report-<you>.md`, `CHECKPOINT <sha> (<HH:MM>Z) <state>` line at the top every
  ~30 min (the coordinator treats > 45 min of silence as a dead lane), and a `## FINAL` at the end with numbers, art ids, branch tip,
  pod cost, what's left. Deadlines below are hard: write FINAL with what you have.
* **Pods:** terminate yours at FINAL (`research pods terminate <id>`); budget per lane below; H100 = `--gpu "NVIDIA H100 80GB HBM3"`.

## 1. Lanes

### 1.1 `share-logup-2`: make the committed column nearly free (THE headline). Pod: `vy-share-logup` kx69zewzhawgy1 (4090, warm). $6; H100 ≤ 1 h allowed. FINAL 23:30Z.
Predecessor `lane/share-logup` @ `1054caf` (rebased onto leaf-iface 720820d), report `lanes/share-logup/20260923T1630Z-report-share-logup.md`.
State: tile64 row sharing via post-commitment fingerprint, paired G/H proofs per sub-batch; Rust verifies the pair (13/13); gates 0
failures both modes; 4090 bench 4096 VUs l=16384 interactive: **prover 0.41 s + hints 0.14 s = 0.55 s** vs included-hash 0.62 s vs bare
`--pipeline 4` 0.16 s. The 0.55 s is UNPIPELINED; bare unpipelined is ~0.49 s, so sharing already costs only ~+12 %.
Goal: **committed tile64 at `--pipeline 4` ≤ 1.3× bare `--pipeline 4` on the same pod** (≈ ≤ 0.21 s): pipeline the paired G/H proofs
through `prove_many` (per-stream state; open-fixes found hint graphs must be per stream: `lane/open-fixes` a0ff818), move the 0.14 s
hints to the device, then the next bottleneck. Then the other relations (`bf16-hopper`, `fp8-hopper`, `bf16-ampere` `+shared`) with Rust
pins + gates, so the device wave can run every target. Keep the worst-case (unshared) path intact as the drill-down.

### 1.2 `ajtai-leaf-2`: finish the Ajtai leaf. Pod: `vy-ajtai-leaf` qam33gj60dv60g (warm). $3. FINAL 23:00Z.
Predecessor `lane/ajtai-leaf` @ `d40399f` + **2 uncommitted files** in `~/projects/verity-main-wt/ajtai-leaf` (`leaf/ajtai.py`,
`ligero-verify/tests/relations.rs`): read `git -C ~/projects/verity-main-wt/ajtai-leaf diff`, carry what is sound into your branch.
Its stage-4 pod run `r20260923-185031-aee0` (cargo test, conformance, fixtures for both relations → `leaf.rs::PINS`, gates) is on the pod
only: recover it. Deliver: pins + fixtures, gates 0 failures, re-measured `fp8-ada+ajtai-n64` (was 1.055 s vs Poseidon2 0.648 vs bare
0.214) and `bf16-hopper+ajtai-n128` (was 5.79 s, 3.4 s of it the old per-sub-batch hints) at `--pipeline 4`, Rust batch accepting.
If share-logup-2 lands its pipelined pair by ~22:30Z, also measure `+shared` with the Ajtai leaf (the leaf cost is then per tile).

### 1.3 `blake3-leaf-2`: finish the BLAKE3 leaf. Pod: `vy-blake3-leaf` ghpl8iy5s629sq (warm). $3. FINAL 23:00Z.
Predecessor `lane/blake3-leaf` @ `30abee8`, report `lanes/blake3-leaf/…report….md` (FINAL was never written). The x4 pin is stale after
the half-block/role change (schema `blake3-keyed/row/v2`, params 6654cdb9…): re-gate, re-pin, fixtures, Rust accept, then bench
`fp8-ada+blake3` and `bf16-hopper+blake3` at `--pipeline 4` against bare and Poseidon2 on the same pod. Same `+shared` note as 1.2.

### 1.4 `fp4-decode-2`: 5090 column 2. Pod: `vy-fp4-decode-3` k39j0s2bvhlljf (4090, warm); a 5090 if stock appears. $4. FINAL 23:00Z.
Predecessor `lane/fp4-decode` @ `98c95b1`, report `lanes/fp4-decode/20260923T1700Z-report-fp4-decode.md`. `fp4-nvf4+poseidon2` composes
(4442 rows/unit, gate 2048 VUs 0 failures on the 4090). Its bench `r20260923-182920-9002` (4096 VUs, l=16384, --zk interactive, local
coins, dump rep 1) ran on the pod but was never recorded: recover and push it. Deliver: Rust pinned + batch-accepting dump, bare
`fp4-nvf4` control on the same device, and if a 5090 is obtainable (`--gpu "NVIDIA GeForce RTX 5090"`, try every ~20 min), the 5090
pair (bare 5090 cell is 0.0714 s).

### 1.5 `live-2b`: the live-verifier tax, and the runbook for tonight. Pods: `vy-live2` qd3grivhbfqurw (prover 4090) + `vy-live2-verifier` 1x8f33k0qa2lkx (verifier, serving since ~19:00Z). $4. FINAL 23:00Z.
Predecessor `lane/live-2` @ `71dbab0`, report `lanes/live-2/20260923T1700Z-report-live-2.md` (§3: the ~2× tax is lost overlap, not
blocking; bf16-hopper 25–42 s sessions = data-connection loss + cubic cwnd collapse; fix under test = bbr on the DATA connection). Deliver:
bbr validated (≥ 5 clean bf16-hopper sessions at depth 4, p90 RTT, no > 5 s session), the tax with bbr for fp8-ada and bf16-hopper,
decide the defaults, and a **device-wave RUNBOOK** in your note: where to run the verifier (region vs the prover pods; RunPod has no
same-DC route), how to rebuild `ligero-verify` from the integration branch on it, which env knobs, what `t.total` vs `t.total_live`
the table should report.

### 1.6 `verify-rs-2`: the Ligerito Rust verifier must reject forgeries (BLOCKING). No pod (laptop CPU; a CPU pod if you want). $2. FINAL 23:00Z.
Predecessor `lane/ligerito-verify-rs` @ `ff9d4c3`, report `lanes/ligerito-verify-rs/20260923T1700Z-report-ligerito-verify-rs.md`.
Red team (`lanes/red-team-ligerito/`, FINAL 19:54Z) F10: `ref.py` and `refpcs.rs` never absorb the evaluation point / value / dims into
the transcript, so the release binary ACCEPTS forged fixtures. Deliver: absorb them in `refpcs.rs` (and a patch for ligerito-design's
`ref.py` in the same shape, since that lane has ended), forged fixtures committed as must-reject (`*.proof.neg` in `batch --dir`), F11
canonical-encoding checks, F5 batch target, and LGSC0003 (sumcheck-2 landed a data-driven round schedule at 20:40Z: `lane/ligerito-
sumcheck-2` 91a9509). `ligerito-relation` (running, 61096b30) consumes your verifier: coordinate through a handoff note in its notes dir.

### 1.7 `v3-scout` (NEW): pick tonight's headline configs. H100 ≤ 1.5 h + A100 ≤ 0.5 h. $8. FINAL 23:00Z.
Base `lane/open-fixes` @ `5e6b3e3` (the v3 pipelined-prover fix a0ff818: per-stream hint graphs). open-fixes measured `fp8-ada-v3`
`--pipeline 4` = **0.1547 s vs v1 0.1795 s** on the same 4090 (−13.8 %, Rust 13/13). v3 relations are private-operand-safe, so they
qualify for the Table 2 headline. Measure, local coins, 4096 VUs, l=16384, Rust batch accepting: H100 `bf16-hopper-v3` and
`fp8-hopper-v3` vs `bf16-hopper` / `fp8-hopper` v1 at depth 4 and depth 8 (80 GB: `--batch 16384` and try 32768); A100 `bf16-ampere-v3`
vs v1. Deliver a table and a recommendation per target: relation, batch, depth, expected t.total, peak memory.

### 1.8 `hints-fused` (NEW): unlock folding for the private-safe relations. 4090. $5. FINAL 23:30Z.
Base `lane/open-fixes` @ `5e6b3e3`. Findings so far: prover time is ~95 % per-sub-batch fixed cost, so columns per VU (folding) is the
lever; v2x4 (public-selection) halved t.total, but for v3 (private-safe) folding is SLOWER because hint generation dominates (fold-private,
open-fixes: "v3x4 hint-gen dominated"; relmin-lookup: hint gen 0.05 s flat = 1/3 of the x4 prover). Goal: a fused device hint kernel for
the v2/v3 families (privsel/pubsel `hints.py`), byte-identical hints (differential vs the current path), per-stream safe, so that
`fp8-ada-v3x4 --pipeline 2|4` beats `fp8-ada-v3 --pipeline 4` (0.155 s) on the same pod. Report the new floor and what dominates next.

## 2. Coordinator appendix (I append here; re-read at every checkpoint)
* 21:00Z: launched the eight lanes above. Integration (lane/integration + GPU merge-val) starts ~23:00Z; the device wave ~00:00Z.
* 21:15Z → `verify-rs-2` (PRIORITY ORDER): (1) F10 committed by 22:00Z (red-team-ligerito-2 starts from your branch then); (2) an
  **LGTO0001 reader** in `ligerito-verify` — `ligerito-relation` (running) has 4096-VU dumps (4 x 1024-VU proofs on a 4090, one 4096-VU
  proof on an A100, ~0.7 MB/proof) and its Rust verification is blocked on exactly this (its report "Status by deliverable" 2; fixture +
  format published 18:55Z in `lanes/ligerito-relation/`); (3) LGSC0003; (4) F11; (5) F5.
* 21:15Z → everyone: `research notes status` (in `lane/qol` c5342ca; same PYTHONPATH as the pods helpers) is how the coordinator sees you.
  `research notes checkpoint <lane> open|blocked|final "<text>"` writes the line for you (commit = HEAD of the cwd).
* 21:40Z → everyone: agents today have LOST CONTEXT mid-lane (ligerito-relation at ~21:20Z concluded its own recent edits belonged to
  "another instance" and stopped). If your memory seems to end earlier than your branch/notes: your report and `git log lane/<you>` are
  yours — continue from them, do not stop. Commit often so the next agent (or you) can resume.

## 3. Second relaunch (22:25Z): the 21:00Z lanes all stopped at ~21:15Z

Every lane launched at 21:00-21:15Z stopped between 21:06Z and 21:18Z (no commits, no notes, no laptop processes; the harness still holds
their sessions, so they cannot be resumed). Successor lanes are named `<lane>-3` (red teams `-3` too), branch `lane/<lane>-3` created at the
predecessor's tip, same pods. §0 applies. **New rules:** CHECKPOINT at least every 20 min, commit every meaningful step (a successor must be
able to continue from your branch + report alone), and put your art ids in the report as you create them. Integration moves to ~00:00Z,
the device wave to ~01:00Z; FINALs below.

| lane | predecessor tip | predecessor state (its report: `lanes/<pred>/…`) | pod(s) to reuse | FINAL |
|---|---|---|---|---|
| share-logup-3 | share-logup-2 cfdcf65 | pipelined G/H pair through prove_many; hint syncs removed (private_decode on device) | kx69zewzhawgy1 4090 | 00:00Z |
| ajtai-leaf-3 | ajtai-leaf-2 1cf9178 | pins+fixtures 107f40b (fp8-ada+ajtai-n64 sys 18d91532, 4858 rows); pipelined hashed runner `prove_vus_many` | qam33gj60dv60g 4090 | 23:45Z |
| blake3-leaf-3 | blake3-leaf-2 1db0008 | gates 0 failures both relations; v2 pins | ghpl8iy5s629sq 4090 | 23:45Z |
| fp4-decode-3 | fp4-decode-2 d86e014 | recovered r20260923-182920-9002 (proof art:7c5453a3, verdict pinned); fp4+poseidon2 through the pipelined prover | lx80c24sagdao0 5090 (+ k39j0s2bvhlljf 4090: terminate once custody is clean) | 23:45Z |
| live-2c | live-2b c72114a | bbr validated cross-region (12/12 bf16-hopper depth-4 accepted) | qd3grivhbfqurw prover; verifiers 1x8f33k0qa2lkx (EU-CZ) + pitmqu0zrycw5i (EU-RO): keep ONE for the device wave, say which | 23:45Z |
| v3-scout-2 | v3-scout 5e6b3e3 | H100 l=16384 p4: bf16-hopper-v3 0.2406 s vs v1 0.2955 (Rust-accepted, pinned) | x2b0ahxr8g7k0s H100 + u3nsufkequsg76 A100 | 23:30Z |
| hints-fused-2 | hints-fused ff52e47 | fused kernel `hints_fused.py` hooked into pubsel/privsel hints_v2/v3 (LIGERO_F…); LIGERO_REFERENCE_HINTS=0 knob | em6u0t7azwt5gu 4090 | 00:00Z |
| red-team-leaf-3 | red-team-leaf-2 (notes only) | G1 reproduced: Ajtai `check_system_key` (F6) is a pattern scan; B=0 chain + decoy key rows | none | 23:45Z |
| red-team-ligerito-3 | red-team-ligerito-2 83d5d75 | V1 found; re-check the V1 fix (ligerito-relation-2 cf9a63a), LGSC0004 ZK masks (ligerito-sumcheck-3 c675bd5), LGTO0001 reader (verify-rs-3 1f30710) | none | 00:30Z |
