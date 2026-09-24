---
id: vllm-rf-f56/state
lane: vllm-rf-f56
kind: state
status: active
created: 2026-09-24T17:40Z
---
# vllm-rf-f56: collectives guard and FA-tap exactness (D16, D17) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D16, D17), §4 (P5, P8); survey maps `survey-observe-acquire-tp.md` §5.2, `survey-program-query-corr.md` Map 4.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f56`, branch `lane/vllm-rf-f56` from `72884c8a`.
- **Laptop helpers:** `/tmp/rff56/research.sh` (research launcher wrapper); recovered deleted xcheck sources `/tmp/rff56/fa{2,3}_tap_xcheck.py` (from `ca5d65e8^`).
- **Scope:**
  - D16a: one MoE collective class list used by `tp/partial_source.py` and `tp/worker.py`, living in quarantine or a profile; check which list the TP regression rows exercised.
  - D16b: quarantine `AllReduceSumBf16` order vs `b1_tp2.allreduce_order`; fix to NCCL's recorded order or refuse world >= 3.
  - D16c: refuse world > 2 on Build/Commit (emit `collective: null` etc.); list what the refusal disables (TP4 work, commit 40f40a21, tp-n lane).
  - D17: FA-tap exactness property check with a record (FA2 on L40S, FA3 on H100), beside `check/noninterference.py`, digest citable.
- **Acceptance:** gates (a), (b); 2-GPU pod TP2 regression row (shared-expert MoE if one exists) verdict unchanged; world > 2 refusal tested; FA-tap records on L40S + H100 preserved via research; contradicted evidence listed in READY.md.

## Findings so far
- D16b evidence for world 4 EXISTS: research artifact `art:53e58b1ce31bd9365f808dfde9746d9cec75df22cb74e7b1218b510d333aa599` (TP4 llama32-1b B8 match record, `match/tp2_match.json`): provenance pass, 1056/1056 all-reduces equal the descending chain order [3,2,1,0]; `alt_ascending_equal` 32 (embedding all-reduces only). Commit `b33386e0` moved b1_tp2 AllReduce v1 -> v2 for the same reason (precedent: body meaning changed -> identity bump).
- Quarantine family `AllReduceSumBf16` is used only by `tp/collective_link.py` (research tool, no Build/Commit caller) + tests; `registry_version()` hashes only `registry.prims`/`registry.b1` sources, so editing the quarantine changes no Program/derive digest.
- D17: cited `fa2_tap_xcheck.py` / `fa3_tap_xcheck.py` existed at `integrations/vllm/verity_capture/sweep/` and were deleted in `ca5d65e8` (cleanup 3/3). Hidden-source `evidence` strings go only into the free-text coverage declaration (no digest).
- D16a: no regression fixture row is shared-expert MoE (OLMoE #70, Qwen3-30B-A3B #75 are the TP2 rows; neither has shared experts).
- by-name lint (`tests/test_no_by_name_rules.py` + `tests/by_name_allowlist.json`) pins `MOE_SITE_CLASSES` / `MOE_COLLECTIVE_CLASSES` tables and their predicates: moving the list needs allowlist entry updates.

## Done
- 17:40Z worktree created.
- 18:47Z resumed after the 18:02Z Cursor restart: worktree clean at `72884c8a` (no commits yet), no `vyv-rf-f56` pod exists, nothing of this lane running. Gate (b) baseline now in `vllm-rf-a1/baseline.md` (65 failures+errors listed by cause; judge gate (b) as nothing outside that list).
- Laptop scratch from before the restart: `/tmp/rff56/{r70,r75,tp4match}` (match/commit records of rows #70, #75 and the TP4 match artifact).

## Running
- nothing

## Next
1. Implement D16b (quarantine v2 reading `b1_tp2.allreduce_order`), D16a (one class list), D16c (guard + emit raise), D17 (`check/fa_tap_exactness.py`).
2. Pods: CPU gates (a)/(b); 2-GPU TP2 row; L40S FA2 + H100 FA3 records (tap builds via `ops/pod_fa2_tap.sh` / `ops/pod_fa3_tap.sh`).

## Open questions
- none yet

## Found, not fixed
- none yet
