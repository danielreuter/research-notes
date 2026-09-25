---
lane: coordinator
kind: handoff
from: ligero-steps-pin
created: 2026-09-25T09:35Z
---

# steps pin + R1/R2 ready: c8a16e2b

Tip: `lane/ligero-steps-pin` @ **c8a16e2b** (pushed). It is origin/main 5631e667 plus the commits below, and it merges
cleanly into origin/main 94b1c4d2 (checked with `git merge-tree`). Everything is additive: no statement digest changed,
no pin changed, no new files beyond tests. Evidence: **art:61aedd2762f64fe16c5189c5378cab94dc86b221188922931a1fe85d307ad7b7**
(logs and JSON of every run below, plus the pod scripts). Pod `vy-ligero-steps-pin`, rustc 1.98.1, CPU.

## What is pinned where

**H2, steps per relation.** Most of this was already on main from lane steps-pin (c5cf7f6d / 3781590e):
- Rust `relation.rs`: `Relation.steps` / `k_ops`, next to `sys_id` / `table_digest`.
- Rust `verify.rs::check_vu_shape` runs in every mode, including `--allow-any-system`:
  - bare K == `k_ops`;
  - hashed K == 1536;
  - `steps <= leaf::max_steps` (the Ajtai ring degree n);
  - pinned: `steps == Relation.steps`.
- Python: `RelationHooks.steps` / `.max_steps`, and `protocol.layout_error` at the top of `protocol.verify`.

This lane closed the remaining gap, the Python +shared (v6) verifier (236020a6, 1571143b):
- `SharedHashedRunner.hooks` and `.hooks_h` now carry `steps = rel.steps`;
- `serialize.verify_files` runs the shape check and K == 1536 for v6 as well as v5 (a v6 header's K is not in the digest).
- On main, Python ACCEPTED a v6 header rewritten to K = 768; it is refused now.

**R1, x/W taken from `vu_index` plus the committed layout.** b-ligero-standard-hash's 3af90e71, cherry-picked unchanged as
71905f0f (I reviewed it):
- Rust `auth::layout_error` in `check_hashed`, and Python `hashauth.layout_error` in `verify_hash_auth`.
- The rule: if tree counts a == b == y, then x = W = vu; if a*b == y (a tile), then x = vu // nb and W = vu % nb; any other
  shape is refused.

**R2, reverify recomputes the commitments.** de2fa317, cherry-picked as 3e98dc55 (it needs core `frame_v3`, hence the merge
of main at c733b7f4). `reverify.commitment_problems` recomputes the a/b/y bindings (`hashauth.binding_digest`), the counts and
the roots from the manifest's instance set, and requires each rep's `vu_index` to cover [0, total_vus) exactly once.

**R4, statements that were never proven (red-team-standard-hash, 08:35Z).** Fixed on this branch in 06176b41, 24ab6c7d,
943d5e96 and c8a16e2b:
- Each rep's `.stmt` stems must equal its `.proof` stems and its manifest entries. A manifest entry is refused if it has a
  statement but no proof, pairs a proof with another sub-batch's statement, or lists the same proof twice.
- `batch`'s `n` must equal the number of statements in the rep.
- A dump counts as hashed when its **pinned relation** names a leaf (`+hash`, `+blake3`, ...), whatever its statements carry.
- In a hashed dump, an unreadable statement is a FAIL.
- A v6 (+shared) dump fails closed, with its own reason.

**About 806a2f73 (your 09:15Z handoff).** I did not cherry-pick it. It changes the same lines as c8a16e2b, and c8a16e2b has
its behaviour (an unreadable statement in a hashed dump is a problem, not an exception) on top of 24ab6c7d. The 3
reverify_test cases it fixes pass at c8a16e2b, as the results below show.

## Tests at c8a16e2b (pod runs lsp-final, lsp-r12, lsp-rtsh)

- `cargo test --release`: 33 + 7 + 27 passed. The 33 include the new `layout_fixes_x_and_w_from_the_vu_index`, and the
  `refuse(...)` cases now include "VU 0 on VU 1's (x, W)".
- `pytest hashauth_test.py reverify_test.py steps_pin_test.py`: **50 passed** (13:27).

## Negatives (every one refused as expected)

**H2 (steps):**
- steps_pin_test covers the red-team collide pairs (n64 steps 96, n128 steps 192), n64 steps 32, and forged bare and
  +poseidon2 steps-32 proofs; header rewrites of every family; the v5 K; the +shared forged steps-32 pair; and v6 headers
  rewritten to steps 32 and K 768. All are refused by Python and by `$LIGERO_VERIFY` pinned.
- red-team `rtsh_steps_e2e` (fp8-ada+blake3): steps 48 is accepted pinned; steps 64 is refused by Python (the shape check)
  and by Rust (not the pinned system).
- Its steps-32 case cannot be built: the blake3 gadget refuses rows of 1 chunk, so the honest prover crashes. This is a limit
  of the harness, not a verifier result.

**R1 (layout):**
- `hashauth_test::test_a_vu_on_another_vus_operands_is_refused` uses the red-team's 2-VU remap fixture (production
  instance-set bindings): VU 0 on VU 1's (x, W) under honest x / W roots. Python and Rust both refuse it with "a VU's x row /
  W column is not the one its index fixes in the committed layout".
- red-team `rtsh_remap_e2e --set-binding`: not reproduced (rc 1).

**R2 / R4 (`hashauth_test::test_reverify_recomputes_the_trees_and_the_cover`):**
- the remap forgery's y root is refused against the recomputed set;
- also refused: a statement without a proof, a VU claimed twice, a set digest mismatch, a stmt-only manifest entry, crossed
  manifest pairs, a duplicate proof entry, and an unreadable statement;
- the honest remap dump passes;
- red-team `rtsh_orphan_e2e --vus 3`: not reproduced (rc 1). The control PASSES; the orphan-stmt and stmt-entry variants
  FAIL.

**Red-team re-test.** red-team-standard-hash re-ran its three harnesses on 24ab6c7d (art:cd2c38ea…): R1 remap, R4 orphan and
forged steps are all refused. It also ran them on 806a2f73 with the same verdicts. It asked to re-run on the declared tip,
since c8a16e2b ≠ 24ab6c7d + 806a2f73 + 943d5e96.

## Regression: every existing verified statement still verifies

At this tip (lsp-r12), Rust `batch` PINNED over every sub-batch, plus Python `verify_files` on the first and last sub-batch
of each dump. **9/9 accepted**, which means the R1 layout rule accepts both the honest unshared dumps and the tile (+shared)
dumps:

| Dump | Artifact | Sub-batches accepted |
|---|---|---|
| fp8-ada bare T2 | art:2c8d5089 | 13/13 |
| fp8-ada+poseidon2 T2 | art:527e99be | 13/13 |
| fp8-ada+blake3 fixture | art:a2e7503c | 1/1 |
| bf16-hopper+blake3 fixture | art:78121b22 | 1/1 |
| fp8-ada-x4+blake3 fixture (steps 12) | art:51b6e9e0 | 1/1 |
| fp8-ada shared-local | art:fa2be398 | 13/13 |
| bf16-hopper shared-local | art:b460261f | 25/25 |
| fp8-ada bare-local | art:c1e415de | 13/13 |
| bf16-hopper bare-local | art:62395cc9 | 25/25 |

R2 over the same dumps (`r2_dumps.py`):
- fp8-ada+poseidon2 T2 (4096 VUs): trees recomputed from the set, roots equal, cover complete: **PASS** (58 s on CPU).
- The bare dumps are not hashed, so there is nothing to check.

The ligero pytest regression list:
- First run, at the H2 tip: 132 passed, 1 skipped, and 1 failure that also fails on main.
- Second run, at this tip (lsp-r12, conformance `[blake3]` deselected): still running; so far 92 of 171, with only the same
  known failure. The count will be in my FINAL.

## Known failures and limits (please read)

- `live_test.py::test_shared_pair_every_coin_from_the_verifier[None]` also fails on main ("G: parameters give 2^-99.86 ...
  requested 2^-100").
- The conformance `[blake3]` cases were not run: on CPU, one case took more than 40 min. blake3 is covered by blake3_test and
  the three +blake3 fixtures.
- **Behaviour change in `reverify.py` (by design, fails closed):**
  - +shared (v6) dumps now FAIL: "shared-row layouts are not recomputed". This affects fa2be398 and b460261f.
  - Hashed dumps without a manifest `set` block now FAIL. That includes the three +blake3 fixtures, whose manifests are not
    bench-shaped anyway.
  - To re-verify a +shared result, a manifest `set.tile` block and a tile recomputation (`tile_instances`) are still needed.
    That is not done here. The shared-local manifests name the *unshared* set digest.
- R2 is enforced in `reverify.py` only. `ligero-verify` alone still checks just the openings under the statement's roots,
  plus the R1 layout. That is by design: the binary has no instance set.
