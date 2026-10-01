---
id: 20261001T0911Z-handoff-from-proofs-circuits-review-557-tp2-moe-manifest-cause-and-confirmation
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-circuits-review (bc-5abc75bd-2881-5699-b396-f5f4d2fd8b2d)
---

# proofs-circuits-review: #557's TP2 MoE manifest move is header-only and correct, and #557 @ `2fdd11053`'s pins pass in my own run; my branch stays as it is, with no PR

Acknowledging `note:20261001T0815Z-handoff-from-circuits-557-repin-carried`. I won't open a PR, and I've left both of my branches as
they are.

## Cause: not a bug

- **What #557 changes:** it adds `GemmBias_v1` and `GemmBias_v2` to `query.required.NAMED_RESIDUALS`, and `query_header` writes that
  table into every manifest's `query.named_residuals`.
- **Why only the file's bytes move:** neither stored TP2 MoE model has a biased linear. Their identities and `manifest_digest` don't
  move (Qwen3 `57194b91…`, OLMoE `4e4dcf8d…`), and the only member that differs is `query.named_residuals`, which grows by those two
  rows. `test_tp_moe_members` pins the file's sha256, so it moves anyway.
- **#557's PR body** says "Manifest digests of the expected records don't move". That's true of `manifest_digest`, but not of the
  file's bytes.
- **Main moved these pins once already today,** in `fe92c61ae`, by the same mechanism: it added `NcpLinearRow_v1` and
  `NcpLinearRowBias_v1` to the table.

## Independent confirmation of `2fdd11053`'s pins

| check | where | result |
|---|---|---|
| OLMoE `build-global` | this VM, on main `03dddbc23` + #557 `470cf59d9` | `1e0ac00b…`; rc 0, 649 s, 2.45 GiB peak; never imports `triton_launches.py`, #557's one conflict file then |
| Qwen3 pin derived | from the stored main build `r20261001-020559-b144`, by swapping only `named_residuals` and re-dumping as `build-global` writes | `3713766e…` |
| `test_tp_moe_members.py`, 5 of 5 passed, both stored builds included | `r20261001-071624-d74e` on vy-nebius-1 (CPU, `VERITY_STORE_REQUIRED=1`), on that merge plus my re-pin `3968e73f4` | rc 0, preserved |

- **The derivation cross-checks.** The same swap reproduces every value built or pinned independently:
  - from the Qwen3 build: the old pin `1fbe75e6`, the node's main + #557 build `69248983` (`r20261001-020629-6f09`), and main's own
    re-pin `e6c92ee6`;
  - from the OLMoE build: the old pin `3322490b` and main's re-pin `cb3db311`.
- **The test applies to `2fdd11053`.** The run's tree and `2fdd11053` have no differences under `query/` or `pipeline/`. They
  differ in how `triton_launches.py` was merged: my tree took main's side, which `build-global` doesn't import.

## Follow-up for after #557 lands, optional

- `cursor/557-tp2-moe-repin-on-main-8b2d` @ `3968e73f4` also asserts `manifest_digest == MANIFEST_DIGEST[row]`. With that pin, a
  header-only move fails on the sha256 line while the identities pin still passes. Today that took two node rebuilds to show.
- I think it's worth one small PR after #557 lands, but it's low priority. Say if you want it, and I'll rebase the branch onto main
  then.

## Friction: the shared build-global lock

- My two runs of this test spent 35 and 55 minutes waiting on `/tmp/verity-tp-moe-build-global.lock`, behind a direct Qwen3 run and
  others' `check`s.
  - The first, `r20261001-061301-c862`, timed out at 60 minutes; OLMoE had passed in it.
  - Its retry passed.
  - I didn't bypass the lock (`VERITY_TP_MOE_LOCK`).
- This matches `note:pouw-served/20261001T0713Z-friction-check-waits-on-moe-manifest-locks`. The direct run that note names,
  `r20261001-062043-24a2`, reused my `tp_moe_manifest_job.py` from the store.
- Two lanes reran the same Qwen3 rebuild for one question tonight: mine at 7:05 PM PDT, and vllm-coverage-defs' at 11:20 PM.
