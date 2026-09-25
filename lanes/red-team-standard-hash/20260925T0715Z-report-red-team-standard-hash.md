---
lane: red-team-standard-hash
kind: report
created: 2026-09-25T07:15Z
status: open
---

CHECKPOINT 57e77c14 (07:16Z) [open] pod vy-red-team-sh (cpu3c 4vCPU) syncing; R1 candidate BREAK: (vu,x,W) triple prover-chosen in v5 verify (Rust+Py) -> wrong y under honest x/W roots; R2: reverify.py recomputes no root/binding/coverage; e2e 57e77c14 pending
# red-team-standard-hash: red team of tonight's committed-relation statements

Worktree `~/projects/verity-main-wt/red-team-standard-hash`, branch `lane/red-team-standard-hash`, base main 00ffe398.
Pod `vy-red-team-sh` (04txgm7j3b0nob, cpu3c 4 vCPU, $0.12/h; 16-vCPU flavors had no capacity at 07:00Z). Budget $10, FINAL 16:00Z.
Scope: decision doc §3/§5/§6.2/§6.4 row "red-team-standard-hash": per statement the hash gadget, digest publication, the native
tree check (domain derivation, node/level/index, vllm-v1 path shape + root fields), the `steps` pin.

## Findings (numbering R1..)

| id | statement | severity | status | evidence |
|---|---|---|---|---|
| R1 | every v5 hashed statement (`+blake3`, `+poseidon2`, `+ajtai-*`), ligero-verify + Python | BREAK (candidate; e2e pending) | code read | `auth.rs::check_hashed`, `hashauth.verify_hash_auth`, `redteam/rtsh_remap_e2e.py` @57e77c14 |
| R2 | B-Ligero independent re-verification (`reverify.py`) | BLOCKING (candidate) | code read | `reverify.py::verify_tree` |

### R1: the (vu, x, W) leaf triple is prover-chosen
Both verifiers check only that each VU's x digest opens at `x_index[v]` under root a, its W digest at `w_index[v]` under
root b, its y word at `vu_index[v]` under root y. Nothing derives `x_index`/`w_index` from `vu_index` and the committed set's
layout (the honest prover uses x = W = vu unshared, `(v // nw, v % nw)` for a tile: `relchain.auth_for`). The statement digest
absorbs the triple, which binds the challenges to it but does not make it correct. So a committer serving a wrong y_v gets it
accepted by proving VU v on any committed (row a, column b) whose product equals y_v (with 4096 x 4096 candidate pairs and 22-bit
outputs, a match for an arbitrary wrong value is likely). Fix: the verifier derives the triple (unshared: x = W = vu; tile:
from (nx, nw) in the verifier's expectation) and refuses any other; the Python verifier the same.

### R2: independent re-verification recomputes nothing from the instance set
`reverify.py` (writes `verified=accepted`) checks custody, the system pin and a Rust `batch` accept. It never recomputes the
three roots from the instance set, never checks the trees' `binding` (the frame-v3 domain: `binding_digest(dataset, manifest,
lo, hi, K, tree, schema)`) or `count`, and never checks the VU coverage of the claimed range. Rust reads binding, owner, count
and root from the statement (`format.rs::read_tree_refs`), so the frame-v3 "verifier-derived domain" is prover-described in
B-Ligero. TABLES.md admissibility 6 requires "the statement's commitments and public words recomputed from the instance set".

## Log
* 06:58Z start; contract, TABLES, decision doc, red-team-leaf-3 report read; inbox empty.
* 07:00Z pod: cpu3c 16/8, cpu5c, cpu3g, cpu3m no capacity; cpu3c 4 vCPU created (04txgm7j3b0nob), registered, bound.
* 07:03Z `research pods sync` (245 MB over the laptop uplink, slow).
* 07:10Z R1/R2 from code reading; 57e77c14 e2e harness `rtsh_remap_e2e.py`.
