---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-epoch (C3 identities + the re-baseline epoch)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-epoch`: C3 (identities and artifact keys) and the re-baseline epoch that batches
> every digest-changing fix. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-epoch.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-epoch open "..."`) within 10 minutes.

## Goal and deadline
- Day plan (`$STORE/docs/day-plan.md`): **by about 7 PM PT (02:00Z), the epoch has run and is ready for review.** That
  means every digest-changing fix is committed, and every regression row is re-recorded at the epoch tree. It also means
  one `tests/regression/rebaseline.py write` diff that the owner reviews. You don't merge anything, and you don't hand-edit
  `expected/`.
- Background: SYNTHESIS (`$RESEARCH_NOTES/lanes/vllm-refactor/SYNTHESIS.md`), specifically §2 D12, §6 Phase 3 (C3 and
  "Epoch"), and §7 decision 4(a). Everything that moves a digest, root or artifact key lands in one epoch.

## Scope, one commit per item, each labelled `epoch:` in the subject
1. **c2's epoch commit** `dedf5313` (on `lane/vllm-rf-c2b`): Programs cite core `AmpereBF16TcDot16_v2`. Read
   `$RESEARCH_NOTES/lanes/vllm-rf-c2b/READY.md`, section "Epoch commit". Cherry-pick it.
   - Once b1 is in your base, the 4 `sampled_replay.py` lines go into b1's split `check/replay/*` modules instead (b1
     deletes that file).
2. **C3 / D12, the profile id**, in `integrations/vllm/verity_vllm/engine/`:
   - `engine_profile.py`: keep `RUNPOD_POD_ID` / nodename in telemetry only, and out of anything hashed into the
     profile id.
   - `vllm_adapter.py` (~956–963): the `profile-fallback` path raises instead of swapping in a fallback id.
   - The target label comes from the probed capability: sm_90 roles aren't `sm89-eager`. The ids live in
     `engine/profiles/expected/*.json`.
3. **C3, the G1–G8 artifact keys get names** (`check/gates.py`, `check/match/{declaration,global_match}.py`,
   `pipeline/report.py`, and their readers). The reason strings and codes stay; only the keys change.
4. **C1's held label fix:** host committers label their binding map `chunk-leaf-v1` over position leaves (`map_digest`
   moves). See `$RESEARCH_NOTES/lanes/vllm-rf-c1/READY.md`, "Found, not fixed", and the owner's morning list item 4.
5. **The golden corpus:** `properties/golden/corpus.json` is protected ("integrator only"). Re-record it with the
   commands in c2b's READY.md (`python -m verity_vllm.properties.golden --record ...`) in its own commit, flagged **owner
   review**, so `test_golden` is green at the epoch tree.

Digest-neutral fixes don't belong here (D5–D7 are neutral; leave them). If an item turns out larger than S, stop at a
clean commit and say so in a handoff.

## Base and branch
- C3 follows B4. Branch `lane/vllm-rf-epoch` from **b4c's head**: `lane/vllm-rf-b4c`, which merges `5c05ff6d` with main.
  Wait for b4c's handoff, or use `origin/lane/vllm-rf-b4c` once it exists.
  - Until then, read the code and write the commits on `5c05ff6d` merged with `origin/main`, then move them onto b4c's
    head.
- Merge `origin/main` each time b4, b1 or a5 lands, which the coordinator expects by about 4 PM PT. The re-recording
  must run on a tree that contains b4. b1 and a5 are digest-neutral by their gates, so rows recorded before they land
  stay valid. Record in READY.md exactly which commits were in the recording tree.
- `main` is `2603dfcc` (b2vb, b5gmb and c2b@`4d053f01` are in).

## Re-recording the 13 regression rows (`tests/regression/fixtures.toml`)
- 9 × 1x L40S tp1: smollm2 b16; llama32-1b b1 i4096, b64 and #101 stoch; qwen25-1.5b; gemma2-2b; mistral-7b; olmoe b32;
  olmoe b32 mixed-arrivals.
- 2 × 2x L40S tp2: olmoe #70 and qwen3-30b-a3b.
- 2 × H100: qwen3-4b bf16 and fp8. They need an **H100 SXM** (`NVIDIA H100 80GB HBM3`, 132 SMs); a PCIe part is
  refused (b4b's finding).
- Per row: Build, Match and Commit at the epoch tree (`ops/row_pod.sh` / `tp_stage.sh`, or `verity-vllm row` once a5
  lands), `--custody-r2`. The MoE rows are the long pole (about 5 h on one L40S: b1's #67 timings), so **launch them
  first**. Pack the short rows two or three per pod.
- Then `rebaseline.py run --record DIR`, `table`, and `write --dry-run`, then the real `write` on the lane branch.
  Every `rebaseline.py write` change needs a reason: name the epoch item that moved it. A check that fails for any other
  reason is a finding, not a re-baseline.
- **Fixtures:** `rebaseline.py run` reads the rows' records from a pod store. Produce and run them on the pods that
  recorded the rows. If you need to read R2 fixtures onto a pod, send a blocker handoff to the coordinator. Minting a
  fixture key on the VM is waiting on an owner decision.
- Pods: `vyv-rf-epoch-<purpose>`, registered, guard 90. Driver 580 / CUDA ≥ 12.9 on L40S (b2v's `create_cuda.py`
  pattern; see c4irb's STATE.md, pod g1).

## Deliverables
- READY.md with the epoch commits; the recording tree; per row the old → new program, manifest and root digests, plus
  the verdict (unchanged); the `rebaseline.py table` output; the golden re-record; and any finding.
- A handoff to the coordinator marked **REVIEW (epoch)**, not merge-ready. The owner reviews the epoch as one diff.

## Budget and deadline
- **$110 of new spend.** That's about 25 L40S-hours, 8 h of 2x L40S and 3 h of H100 SXM; stop and ask before passing it.
- The vyv- deadline is extended in steps. Tell the coordinator the expected end of your last row as soon as it's known.
