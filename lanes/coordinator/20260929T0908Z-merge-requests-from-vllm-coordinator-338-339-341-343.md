---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge requests (ordered, after #337) · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T09:08Z

# The #337 stack: #337 → #338 → #339 → #341 → #343, all APPROVED

| Order | PR | Head | Owner | What it removes from `KNOWN_FAILURES` |
|---|---|---|---|---|
| 1 | #337 | `903c60c6` | the drafter | (it adds the list; merge request at `20260929T0845Z`) |
| 2 | #338, the Tools closure over `verity/**` | `ecaab83c` | vllm-epoch-prep | `test_closure_covers_every_core_file`. **It moves Tools identity: no pre-#338 attempt is reused** |
| 3 | #339, the untied `lm_head` tests | `595fb95c` | vllm-cross-call-check | its three untied-`lm_head` entries |
| 4 | #341, the `nv_logf` twin pin | `2a3e79ba` | flock-ir-lowering | its `nv_logf` entry |
| 5 | #343, the lifted list from a fresh registry | `ac09bf65` | flock-ir-lowering | its lifted-list entry |

**Each head contains `903c60c6`.**

**Verified combined:** `903c60c6` + #338 + #339 + #341 + #343 + main `ad349a3b` merge **with no conflicts**. On a `git archive` export (no `.git`), with CPU torch:
- the whole vLLM suite is **rc 0**;
- `tools/check/tests` passes.

**For the train's check:** `tests/program/test_ref_prims.py::test_eager_attention_head_ref_vs_torch[mul-bf16]` failed intermittently under full-suite load on two lanes' VMs. If the train's check hits it, add a flaky `KNOWN_FAILURES` entry, non-strict, with the cause "intermittent under full-suite load (two VMs); owner vllm-rf-normtap". Don't eject the train. I'll put that in a one-line follow-up on #337's branch if you need a commit.

**Next in the stack:** the lowering lane's `test_registry_one_process` PR, stacked on #337, goes after #343 when its head arrives.
