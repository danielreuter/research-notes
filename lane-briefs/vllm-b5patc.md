---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-b5patc (split the fold's pattern module), successor of b5patb

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-b5patc`, the successor of `vllm-rf-b5patb` (its session ended at the 9:03 AM PT
> laptop restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-b5patc.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-b5patc open "..."`) within 10 minutes.

## Predecessor and branch
- b5patb: agent bc-c7bcfa82 (itself successor of b5pat, bc-c87a1519). Notes: `$RESEARCH_NOTES/lanes/vllm-rf-b5patb/STATE.md`
  and READY.md (draft).
- Head: `lane/vllm-rf-b5patb` @ **`4537961b`** (on main `33e4d8d1`; `integrations/vllm` identical to the gated
  `ba852261`). It merges cleanly with `origin/main` `8a3aa083` (allowlists and README only overlap with c1).
- **No code work is expected.** Create `lane/vllm-rf-b5patc` at `4537961b` only if you must commit. Otherwise the merge
  request names `lane/vllm-rf-b5patb` @ `4537961b`.

## Pods (yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-b5pat-big` (cpu3m 32 vCPU / 256 GB) | 8n2373g922sb59 | 1.76 | gate (a) at `ba852261`, run `r20260925-122214-cc3f` (`/workspace/b5pat/gate_a.sh`, logs `/workspace/b5pat/logs/a_head.{log,xml}`), about 94%, ETA about 9:30 AM PT |
| `vyv-rf-b5pat-cpu` (cpu3g 16 vCPU) | andiw61o3shls8 | 0.64 | idle. The rebased lints and gate (b) at `4537961b`, run `r20260925-142622-edbe`, are done; jdiff in `/workspace/b5patb/jdiff_rb_vs_{head,base}.txt` |

## Already recorded (don't redo)
Gate (b) at `ba852261` against `10996616` (4001 = 4001, 0 changes); the #101 re-fold is byte-identical head vs base
vs record (`r20260925-141717-7caf`); code identities; the split verified 84/84 verbatim.

## Next
1. The rebased gate (b) (`edbe`) shows one flip, `tests.commit.test_roundtrip::test_transient_storage_is_released`
   (passed to failed; failures and errors 62 to 63). b1 saw the same test flip on its own tree. It's in c1's
   `commit/` area, not yours. Show it's unstable: rerun just that test about 5 times each at head and base on the cpu
   pod, record the counts, and list it in READY.md.
2. **Hand over, don't terminate:** the cpu pod goes to `vllm-rf-b1c` for its re-gate, once step 1 is done.
3. Gate (a): when it ends, copy a23b's base XML from gate-tools to the big pod, and compare test by test with
   `baseline-jdiff.py`. The run predates `--custody-r2`, so launch a custody-copy run on the same pod (as c4irb did:
   a `--custody-r2` run that copies the old run dir into its own), and record the `art:` id. Then drain and terminate big.
4. READY.md (status off DRAFT), then the merge-ready handoff.

## Budget
$3 of new spend.
