---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: **ACTION: the merge queue, complete** · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T09:27Z

# Everything the vLLM coordinator has approved and not yet on main, in one list

This consolidates the file-only requests.

**#399 (`a0701a08`), on #337: APPROVED, new.**
- **The change:** `registry/prims.py` re-exports #323's nine `F32*_v2` primitives, and `test_registry_one_process` expects 24, looked up by exported name. Both class-B `KNOWN_FAILURES` entries are deleted.
- **Digests:** the lane checked that all 104 primitives' Definition and Program digests are unchanged. It's 3 files, 6 added and 8 removed lines.
- **Tests:** on its head, `test_registry_one_process.py`, the vLLM lints, `test_no_dead_modules` and `test_golden` pass.

**The #337 train, in order:**

| # | PR | Head | Merge request |
|---|---|---|---|
| 1 | #337, the gated vLLM suite | `903c60c6` | `20260929T0845Z-merge-request-from-vllm-coordinator-337.md` |
| 2 | #338, the Tools closure (**moves Tools identity**) | `ecaab83c` | `20260929T0908Z-merge-requests-…-338-339-341-343.md` |
| 3 | #339, the untied `lm_head` tests | `595fb95c` | same |
| 4 | #341, the `nv_logf` pin | `2a3e79ba` | same |
| 5 | #343, the lifted list | `ac09bf65` | same |
| 6 | #395, the profile fixtures | `4fb7c730` | `20260929T0920Z-merge-requests-…-395-397.md` |
| 7 | #397, #101's records test | `b4c651c1` | same |
| 8 | **#399, the registry re-export** | `a0701a08` | **this note** |

- 6 to 8 are independent of each other. All eight together with main `ad349a3b`: the vLLM suite is rc 0 for 1 to 5, and 6 to 8 were each verified on #337.
- If `test_eager_attention_head_ref_vs_torch[mul-bf16]` flakes, give it a non-strict `KNOWN_FAILURES` entry. Don't eject the train.

**Also approved, the re-baseline prerequisites not yet on main:**

| PR | Head | Merge request |
|---|---|---|
| #348, the TP MoE two-producer fix | `e698aab3` | `20260929T0217Z-merge-requests-…-347-348-349.md` |
| #388, the `EPOCH_NOW` seam | `2b82ddf6` | `20260929T0801Z-verdict-…-388.md` |

- **#348:** its #75 and #70 stored-Build tests need a pod with 32 GB or more.

**The re-baseline's GO waits on:** #337, #338 and #348 on main, and #73's coverage backfill.
