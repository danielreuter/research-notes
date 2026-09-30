---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20260930T2253Z-handoff-from-hash-cut-change3-merge-request-572
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c)
to: the research coordinator; cc vllm-coordinator, the RTX PRO coordinator (bc-2aa33ad8), the MVP lane (bc-dd22acf8), accounting-merge
created: 2026-09-30T22:53Z (3:53 PM PDT)
---

# Merge request: [#572](https://github.com/danielreuter/verity/pull/572) at `d20e4d16`, `-h2` as a switch in the sm_120 pipeline, check passed

Daniel approved `-h2` on the served path at 1:36 PM PDT (`lanes/accounting/20260930T2039Z-rulings-from-daniel-pouw-decisions.md`). This lands the switch; `-h1` stays the scheme default, and a caller picks `-h2` by the scheme's name.

- **[#572](https://github.com/danielreuter/verity/pull/572)** (`cursor/pearl-c-sm120-h2-switch-b0c4`) at **`d20e4d163fadedce17aab79df696bce200655655`**, a draft stacked on #540. It contains `main` `e15dc1ef` (train TCQ). Trains TLU and TIS landed after that; they merge into it without conflict.
- **Check:** `r20260930-223854-ba99` on vy-nebius-2, 3:39 to 3:51 PM PDT: `validation: passed` on every step, `lean-agreement` included. Suites whose inputs hadn't changed since `r20260930-214715-86da` reused its passes (`verity-vllm`: 4,589 passed); `verity-pouw-benchmarks` ran in full, 182 passed and 2 skipped.
- **Grant needed:** `vllm-coordinator` (it touches `integrations/vllm/`), requested in `lanes/vllm-coordinator/20260930T2253Z-handoff-from-hash-cut-change3-grant-572.md`. No Lean and nothing under `backends/flock/`, so no statement reviewer and no red team.

## What #572 itself changes

- **The hashing switch.** A Pearl-C scheme's name ends in its hashing format (`pearl-c-sm120-v1-h1`, `-h2`), and the scheme holds the format's data: `PearlC.commitment_hash` (`TREE_HASH[hashing]`) and `PearlC.digest_keys`.
- **GPU 1's pipeline:** `run.Pipeline(hashing="h1"|"h2")`. Under `-h2`, A's and B's rows go through `hash_rows_b3s`, with the segment level keys derived in the same kernel (GPU 1's `997ac6bd`), and the tile tree's leaves through `hash_leaves_b3s`. The cubin includes `hash_h2.cuh`.
- **The device path (`pouw_pearl_c_device.py`)** reads every format fact from the scheme and keeps no table of its own (finding 3 of `docs/pouw/vllm-integration-api.md`).
- **Core:** `verity.commitments.merkle.domain_message`, public and new: the framed message whose digest is `CommitmentDomain.domain_id`, which `CommitmentDomain` now computes from it too. Domain ids are unchanged. The device path hashes it with native BLAKE3, where it used to import `_FRAME` and `_uint`.
- **What the first check found.** `r20260930-210032-629c` at `2b2aa982` failed 7 `verity-vllm` tests that came with #540's and #389's content. They're fixed here:
  - P1: the core function above;
  - P7: `find_spec`, not a quiet `except ImportError`;
  - P8: two allowlist entries, the scheme names' and GPU 1's ship's `sm_120` literals;
  - P10: `commit.py`'s cap lowered to 1,764;
  - `test_pouw_native` compares the pool's reads sorted;
  - `test_tp_moe_members` re-pins the two stored TP2 MoE manifests, because the manifest records `query.required.NAMED_RESIDUALS`, which #389's line extends with `NcpLinearRow_v1` and `NcpLinearRowBias_v1`. With those two entries removed, olmoe's `build-global` wrote the old pin byte for byte.
- **What the second check found.** `r20260930-214715-86da` at `ee47ec2c` hung in `benchmarks/pouw`'s `test_fixture_agrees_with_the_scheme`, and so had the first. Node 2's Python 3.14 defaults a `multiprocessing.Pool` to forkserver, whose workers can't import a module the tests loaded from its path, so `pool.map` waits forever. `d20e4d16` makes the benches' pools fork, as `integrations/vllm`'s do. #596's check `r20260930-204400-e88e` is stuck on the same test (`internal/pouw/rtx-pro/server.md`, 3:40 PM PDT).

## What landing it carries

Nothing below is on `main` yet, so landing #572 lands all of it:
- [#540](https://github.com/danielreuter/verity/pull/540) at its head `120c26ed` (draft, the MVP e2e on the RTX PRO 6000), and the PRs #540 stacks: [#389](https://github.com/danielreuter/verity/pull/389), [#433](https://github.com/danielreuter/verity/pull/433), [#435](https://github.com/danielreuter/verity/pull/435), [#510](https://github.com/danielreuter/verity/pull/510) and [#532](https://github.com/danielreuter/verity/pull/532), each at its head.
- [#449](https://github.com/danielreuter/verity/pull/449) through `61d0298d`. #449's four later commits (`98f85402`, `9add5f57`, `0ecd64d4` `unit_seed_a`, `5f6a31c7`) are not in it.
- GPU 1's `pearl-c-sm120` kernel branch through `9f1e33b1`, plus `997ac6bd`. Its hashing forms (`0e339c1e`, `92285aab`) are not in it.

## Order

The Pearl-C chain ([#449](https://github.com/danielreuter/verity/pull/449) → [#548](https://github.com/danielreuter/verity/pull/548) → [#534](https://github.com/danielreuter/verity/pull/534)) lands first, through accounting-merge. Once it's on `main`, I'll merge `main` into #572 and record a new check. Any conflict would be in `protocols/pouw`'s Pearl-C files, since #449 moved on after `61d0298d`. A train with #572 behind that chain does the same in one check.

[#591](https://github.com/danielreuter/verity/pull/591) (decode's spread and the benches) is stacked on #572 and current with it at `eda6340d`. It's not part of this request.
