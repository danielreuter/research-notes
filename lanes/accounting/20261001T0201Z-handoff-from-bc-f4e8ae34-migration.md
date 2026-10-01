---
id: 20261001T0201Z-handoff-from-bc-f4e8ae34-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-f4e8ae34 (the vLLM integration API and its MVP migration)
---

# bc-f4e8ae34 -> compute-accounting and my replacement: migration handoff. Nothing in flight, nothing only on my VM

Answers `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. The backlog rows are "vLLM integration API" (done-but-unmerged) and "#578's deferred schedule" (parked); Daniel decides on both.

**Where to start:**
- **The design and checklist:** the pous store's `docs/pouw/vllm-integration-api.md`, §3 is the live checklist.
- **The heads, and the history with the MVP lane:** `internal/pouw/rtx-pro/handoffs/vllm-api-migration-heads.md`, newest entry first.
- **My status:** `internal/vllm-integration/vllm-api-lane-status.md`.

## 1. Branches and PRs (all on origin; nobody else pushes to them)

**#567,** `cursor/vllm-linear-api-skeleton-e318` at `b4354fdc`, base `main`.
- **What it is:** `verity_pouw.serving` (the hashing formats, the Pearl-C scheme grammar, the schedules, `PassCommitment`, and the kernel-variant and gate data) and `verity_vllm.linear.api` (the `Stack`). It's additive and touches no MVP file.
- **State:** green, ready, merge-requested.
  - The recorded `check` `r20260930-165503-4d59` passed every step on `b4354fdc`, which contains `main` `b1134766`.
  - The merge request is `lanes/coordinator/20260930T1711Z-handoff-from-pous-567-vllm-linear-api-merge-request.md`.
- **Left:** the research coordinator's train. `main` is now `4860d817`, so the train re-checks the merged tree.

**The migration stack,** all draft PRs, each stacked on the one before. The bottom sits on #564 (`cursor/pouw-decode-deferred-4f91` at `a895ade7`, bc-dd22acf8's):
- **#573,** `cursor/vllm-mig1-guards-e318` at `5591a44d`: `keeps_weight_copy` for Pearl-C and ncp-v2, so POUS beside them is refused; kernel modules named by their sources' SHA-256, with `kernel_source_sha256` in the manifest.
- **#576,** `cursor/vllm-mig2-hash-format-e318` at `77c02abf`: the hashing keys and tree hash from `HASH_FORMATS` through the scheme, with `TREE_HASH`, `tree_hash()` and `variant()` gone; `weight_roots(kernel, weights, scheme)`.
- **#578,** `cursor/vllm-mig3-schedule-e318` at `e265ea72`: the schedule as data.
  - `deferred` puts the main lane at the greatest priority, joined to vLLM's stream by events, and the tile hashing on a side lane at the least. `deferred-caller` is #564's first cut.
  - The ring comes from the side steps' IO, and the priorities are recorded.
- **#585,** `cursor/vllm-mig4-install-stack-e318` at `e177a161`: one install path. `e2e.py`, `profile_decode.py` and `vllm_bench.py` attach a `Stack` through `verity_vllm.linear.vllm_site` (`engine.hooks`); the modes are arms and the timed generates are passes.

**The state of the stack:**
- **CPU tests green at every head:** `test_pearl_c_vllm.py` passes at each (25 to 33 passed, 1 skipped), and so do `tests/protocol_options`, `tests/linear` and the root wall-clock lint.
- **Byte identity:** the RecordingDev retained passes match #564's, file for file. The manifests add only `kernel_source_sha256` and `schedule`.
- **The kernel tree** `benchmarks/pouw/pearl_c_sm120/` is byte-identical to GPU 1's `9f1e33b1` in every head.
- **Window 5,** on #585 at `bed66b08`, serial (`r20260930-181144-19f9`; verify `r20260930-182720-80d9`, ACCEPT/ACCEPT/REJECT), is **panel attempt 103: 1.718× prefill, 4.145× decode** over eager FP8. Pearl-C's decode went from 70.2 to 60.8 ms a step; FP8's got faster still.
- **No recorded `check`** has run on the stack heads. They land with, or after, #540 and #564, the MVP line they sit on.

**Already settled, nothing to do:** [#596](https://github.com/danielreuter/verity/pull/596) (bc-ccd30e80, on #593, on #585) carries #572's `-h2` and the kernel changes (the comment on #596, 20:00Z). The stack stays `-h1` only.

## 2. Runs and jobs in flight

**None.** My only runs were the two recorded checks, `r20260930-162056-6994` and `r20260930-165503-4d59`. Both are done, passed, and have custody on R2 (the default with `--on`). I have no fill jobs and nothing on node 2.

## 3. Half-done state

- **Nothing is only on my VM any more:**
  - Every commit is on origin, and the worktrees are clean.
  - The CPU byte-identity scripts are now in the pous store: `internal/vllm-integration/manifest-dump.py` (one retained pass from a checkout on the recording stand-in) and `manifest-diff.py` (compares two passes and names any difference).
  - Usage: `python manifest-dump.py <checkout> <out dir> serial|deferred|deferred-caller`, then `python manifest-diff.py <base dir> <head dir> kernel_source_sha256 schedule`.
- **The store files to keep current:** `docs/pouw/vllm-integration-api.md` §3, `internal/pouw/rtx-pro/handoffs/vllm-api-migration-heads.md` and `internal/vllm-integration/vllm-api-lane-status.md`.

## 4. The next step for each kept item, and what I'd stop

1. **#567:** merge it in the research coordinator's train. If the train asks for a fresh head, merge `main` into the branch and re-record (`check.py --record --on vy-nebius-2` from a clean worktree at the head).
2. **The stack, once #567 is on `main`:**
   - Merge `main` into #573, then #573 into #576, and so on up to #585. Merge, don't rebase: the stack's copies of #567's commits are cherry-picks with the same content.
   - At each head, run `test_pearl_c_vllm.py`, `integrations/vllm/tests/{protocol_options,linear}` and the root `tests/test_no_wall_clock.py`, then push.
   - Each PR leaves draft when #540 and #564 head for `main`.
3. **`KernelVariant.config`** (bc-1a23b70c, #590, server.md 18:15Z; my answer is in the heads file at 01:01Z):
   - after #567 lands, a small PR on `main`: the run-time forms (`PEARLC_A_FORMS` and the like) as canonical JSON in the variant's id, so a gate or pin covers its form;
   - then `KernelPackage.load` and `select` take and pin it, when the loader lands.
4. **#578's deferred schedule** (parked; Daniel decides):
   - the untimed profile on #585's head: `window.sh MODE=profile SCHEDULE=serial`, then `deferred-caller`, then `deferred`, on one card;
   - then a window with `SCHEDULE=deferred` if it pays.
5. **What I'd stop:** the "Later" steps in §3 of the doc. Those are moving executors into `linear/impl`, the forward scope, TP, POUS's one codec copy, and the pass verifier into `verity_pouw`. Do them only when a consumer needs them; they're plumbing and move no number.

## 5. Traps

- **Frozen commits:** never rewrite or force-push a commit a run cites.
  - bc-dd22acf8's frozen commits are `9f31150f`, `8ca97148` and `38f5a277`.
  - #585's `bed66b08` is cited by window 5 (attempt 103).
  - The stack moves only by merges.
- **Keep the stack kernel-identical to `9f1e33b1`.** Don't merge #572, #591 or #596 into it; they change GPU 1's tree and need their own ship and gate. #596 is the line that carries `-h2`.
- **The dead-module keep list:** `integrations/vllm/tests/dead_code_keep.json` names `verity_vllm.linear`, `.api` and `.vllm_site`. Once an integration root reaches a module, its entry has to go, or `test_keep_list_only_shrinks` fails.
- **Check slots:** record checks on vy-nebius-2's slots (CPUs 128–191), which `node_ops` pauses during timed windows. vy-nebius-1's CPUs 8–95 are the research coordinator's train slots.
- **Notes stamps:** `research notes sync` refuses a file stamped ahead of the clock. Use `date -u +%Y%m%dT%H%MZ`.
- **GitHub auth:** the broker's PATH is per checkout (`<checkout>/.git/verity-auth/bin`). A successor installs it in its own checkout and checks that `token.json` has `source = broker`.
- **The migration's re-checks on the card** go through bc-2aa33ad8, in the sequence in `internal/pouw/rtx-pro/handoffs/pouw-mvp-migration.md` (bc-dd22acf8's), and never on a tree a running window or verify uses.

After this handoff I start no new work. I answer my replacement's questions here.
