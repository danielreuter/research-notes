---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: draft · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T04:20Z · status: plan for root; CPU prep can start now, GPU waits on gate G0

# vLLM re-baseline epoch (step 6): plan, sequencing and per-row cost

Daniel approved re-recording all 13 rows with a $250 GPU budget. The vyv- guard is re-armed: cap $1,005 ($755.03 + $250), deadline
2026-09-28T18:00Z, trip cleared, logged in `dm.log`.

## 1. What becomes the record (digests move once)

"Step 6" (`docs/fine-query-plan.md` §5) is the switch to `Q_word` v1 as the query of record:
- the manifest's query header and `replay_partition` change;
- the tapped interior values become required identities;
- run roots move.

For `Q_word` v1 (no recompute) to hold on every row, every opt-in it depends on has to become the default in the same change.

| # | Switch | Rows it moves | Code state |
|---|---|---|---|
| S1 | `Q_word` v1 as the partition of record (`verity/partition/v1`, #111), replacing `Q_module_body_v1` | all 13 (manifests, roots) | #111 queued; the switch itself: new PR |
| S2 | Program ids pinned independently of module paths (the `SRC` static no longer embeds the wrapper's module path: `609750e4` → `bfb0f1db` today) | all 13 (Program digests) | new PR |
| S3 | Taps on by default: norm scales (#90), guarded max + `MS` (#95/#102), router softmax (#96), vocab range (#96) | all rows with attention or norms; MoE rows; TP rows | merged, opt-in: flip the defaults |
| S4 | Constructions as the record: MoE `indexed-read-ordered` (#86), FA3 `check-inf-per-iteration` (#105), `weight_only_calls="once"` (#109), FP8 `SHARED_SCALE` (#106 + #128), shared-greedy sampler (#101 PR) | #67/#68/#70/#75; #73/#74; #57; #74; stochastic rows (#101) | merged, opt-in. **Switch points still open:** the eager Match fold for `once` and for the FP8 shared tile; the `scale_products` committer source (#128's function, not yet wired); the frontend rule for the shared-greedy sampler |
| G0a | #197: top-p `splits` as a constant (#101 → `79caee21…`) | #101 | in tonight's M0 train |
| G0b | The lowering lane's composite top-p keep word (bc-9916bbb1) | #101 | in progress |
| G0c | The `AmpereBF16TcDot16` v1/v2 re-key (core side: the consolidation coordinator, bc-e373566b) | every L40S row | agreed 06:48Z: id-only change to core `AmpereBF16TcDot16_v2`; core side #221 (`996f14e1`) in the ~07:05Z train; S4 binds v2 and should land after #223 (`de3d49b0`) or rebase over it |

**Not in scope unless Daniel adds it** (each moves digests again later if left out):
- E4: the committers on SHA-512;
- E4b: the IR digests on SHA-512;
- E6: roots binding the partition digest;
- E7: serialized renames;
- serving commits in M0's format as the record (#119 is opt-in).

**Decision for Daniel:** include E4/E4b/E6 now, so digests truly move once, or accept a second move later. This plan assumes they're
out.

## 2. Sequence

1. **Now, on CPU (lane `vllm-epoch-prep`, brief below):**
   - the S1–S4 switch PRs;
   - the rebaseline tooling (one `expected/` write per row, digests out);
   - CPU A/Bs of the switch on stored Builds, where they exist (#4, #57, #73, #74, #101, and #67/#70/#75 from the programs artifacts);
   - the pod plan per row.
2. **Gate G0:** #197, the composite keep word and the re-key on main, then the S1–S4 PRs on main.
   - Merges go through `check` + `research merge`.
   - I review each switch PR as usual, with the checker showing 0 recomputes on all 13 rows' program graphs rebuilt from main.
3. **GPU re-record (lane `vllm-epoch-run`):** 13 rows on 7 pods in parallel. For each row: Build, Match and Commit at the new main,
   then a manifest-verify.
   - Every verdict is expected to match the row's class, or be explained.
   - One `rebaseline.py write` per row, after its run passes.
4. **Out:** each row's new digests (step, request and workload Programs; manifest; run root; partition digest), to the research
   coordinator (bc-8ece7cde) and the sweep lane (bc-ea1c2c4f) as a single table, row by row as they land.

"Builds" in the CPU prep: a Build can't run on a CPU-only host (vLLM's CUDA ops won't load; verify-optins, 06:55Z). So the CPU prep
does the switch code and A/Bs on stored Builds. The new-main Builds run on the GPU pods in step 3, since they only exist once G0 lands.

## 3. Per-row cost

The estimates come from the last epoch's measured times (`docs/vllm-epoch-review.md`, the overnight re-runs), serving-view's
Builds and verify-optins' runs. The rates are secure-cloud: L40S $1.09/h per GPU, H100 SXM $3.49/h per GPU. Each time includes the
bootstrap (about 0.3 h).

| Row | Config | Pod (why) | Hours | $ |
|---|---|---|---:|---:|
| #101 | Llama-3.2-1B B1 i256 o32, stochastic | 1× L40S with ≥ 94 GB host RAM, or 2× L40S. Root, 05:41Z: the 102 M-gate sampler Call is cut with a raised `max_gates` on about 60 GB, after #231 grows the Program to about 23.26e9 word gates | 1.5 | 3.3 |
| #4 | SmolLM2-135M B16 i1024 o128 | 1× L40S (Build 1.25 h measured) | 3.0 | 3.3 |
| #57 | Gemma-2-2B B8 | 2× L40S (host RAM) | 3.5 | 7.6 |
| #67 | OLMoE B32 | 2× L40S (measured about 3.9 h) | 4.0 | 8.7 |
| #68 | OLMoE B32 arrivals | 2× L40S (Build 2.6 h + Commit 0.85 h measured) | 4.0 | 8.7 |
| #70 | OLMoE TP2 B8 | 2× L40S, `tp_stage.sh` | 3.0 | 6.5 |
| #23 | Llama-3.2-1B B64 | 4× L40S (Commit needs > 251 GB host RAM) | 3.0 | 13.1 |
| #60 | Mistral-7B B8 | 4× L40S (> 251 GB host RAM) | 4.0 | 17.4 |
| #11 | Llama-3.2-1B B1 i4096 o512 | 4× L40S (planner: about 486 GiB Build; ≥ 512 GB host) | 6.0 | 26.2 |
| #39 | Qwen2.5-1.5B B1 i4096 o512 | 4× L40S (same) | 6.0 | 26.2 |
| #75 | Qwen3-30B-A3B TP2 | 2× H100 (the Commit OOMed on L40S per rank) | 4.0 | 27.9 |
| #73 | Qwen3-4B B8, H100 | 2× H100, 503 GB (Commit OOM at 251 GB) | 5.0 | 34.9 |
| #74 | Qwen3-4B-FP8 B8, H100 | 2× H100, 503 GB | 5.0 | 34.9 |
| **Total** | | | | **about $216** |

- **Contingency:** about $34 inside the $250, enough for one L40S-row rerun or a partial H100 rerun. Not enough for a full H100 row
  twice.
  - If an H100 row fails once for a non-code reason, I'll send you an estimate before rerunning it.
- **Pods, in parallel, so everything fits before 18:00Z:**
  - H100-a: #73, then #75;
  - H100-b: #74;
  - 4×L40S-a: #11, then #23;
  - 4×L40S-b: #39, then #60;
  - 2×L40S-a: #67, then #68;
  - 2×L40S-b: #57, then #70;
  - 1×L40S: #101, then #4.
  - The longest chain is about 10 h. **The GPU start must be by about 08:00Z** for everything to finish by 18:00Z. If G0 lands later,
    drop or defer the lowest-priority rows (I'd defer #11/#39, the capacity-bound ones, first), or ask for a deadline step.
- **Capacity risks:** ≥ 512 GB L40S hosts (#11/#39) weren't in stock on 09-26, and H100 availability varies. If a shape isn't
  available, the run lane asks me, and I'll ask you before substituting a more expensive shape.

## 3a. Root's ruling (06:43Z): one row per pod

- **13 pods in parallel**, one row each, at about the same cost (each row pays only its own hours, plus about $0.3 more of bootstrap
  per pod).
- **Start** when G0 plus S1–S4 are on main (realistically 10:00–11:30Z). The $250 cap and the 18:00Z deadline stand.
- **If the start slips past about 12:00Z:** defer #11 first, then any row whose estimate can't finish by 18:00Z.
- **Wave 2:** #57, #74 and #39 start when their fixes are on main (S1b; #244).
- **Never record a GREEN row as FAIL.**

## 3b. Root's ruling (05:03Z): #57 and #74

- Host-evaluated sources for their Call-level boundaries land as **S1b**, right after S1.
- #57 and #74 run **last** in the GPU window.
- If S1b isn't on main by about **12:30Z**, #57 and #74 are deferred to a follow-up epoch and keep their old records.
- **Never re-record a GREEN row as FAIL to meet the window.** This applies to every row: a GREEN row that would come out FAIL is
  deferred, not written.

## 4. Lanes (to launch)

- **`vllm-epoch-prep`** (CPU, $0): S1–S4 and the tooling. It needs the owners' help:
  - cross-call-check, for `Q_word` and the program graphs;
  - normtap, for the tap defaults;
  - verify-optins' evidence, for the constructions.
  - Brief: `internal/lane-briefs/vllm-epoch-prep.md`.
- **`vllm-epoch-run`** (GPU, $250 cap, starts at G0). It runs the pod plan above and the writes, and posts the digest table. I'll write
  its brief once G0 is in sight.
- **The re-key:** I'll agree it with the consolidation coordinator (bc-e373566b) via `lanes/coordinator/`. I couldn't find a lane
  folder for it.


**Update 10:25Z:** #11 is deferred to the follow-up epoch with its old record kept. The S-stack reaches main about 11:45Z, past #11's 11:30Z latest start. Wave 1 is the other nine rows.

**Update 11:35Z:** #57 is deferred: S1b's host evaluation is about 16.4 h per Commit, against the 90-minute stop. #74 runs in wave 2 after #253. #39 depends on #244, which is not on main.
**Update 11:38Z (root):** #74 is funded if S1b lands in time; the sweep reserve is $48 at a measured $7.55/h. #39 is deferred, blocked on #244 and unfunded. Wave 2 is #74 only.
**Update 14:46Z (root):** #74 is deferred; at 1 pair it needs about 5.4 h. Deferred rows: #11, #39, #57 and #74 (follow-up epoch), plus #60, #67, #68 and #75 (the 17:30Z rule). Running or planned: #73, #4, #23 and #101 (train H); #70 had no pod by its 14:30Z latest start, per the guard at 14:30Z.
**Update 15:45Z:** #101 is deferred with its old record (the train-H attempt failed: `NvLogf_v1` is not in the registry). Main is `432edb3b` (train H). Rows re-recorded today: #4, #73 and #23 only, which may run to 20:00Z.

## Follow-up epoch (the carry list, kept current)

**Rows, with their old records kept until each one re-records:**

| Row | Why it was deferred | What the follow-up needs |
|---|---|---|
| #11 | its latest start was missed (the S-stack merged late) | 4× (or 2×) L40S-class, ≥ 512 GB host |
| #39 | blocked on #244 (`GemmBias_v1`) and unfunded | #244 on main; ≥ 512 GB host |
| #57 | S1b's host evaluation is about 16.4 h per Commit | norm-chain and softcap row kernels, a faster exact Gemm, or a `CLAIMS` tap of the pre-softcap `lm_head` |
| #23 (18:57Z) | its Commit admission needs about 483 GiB against the pod's 351 GiB | a host of ≥ 512 GB; resume from its side-stored Build |
| #4 (16:53Z) | its Commit PASSed on a FAIL-class row | an audit of whether the PASS is genuine; any class change goes to Daniel |
| #101 (only if it misses tonight) | four Build or Match defects (#288, #297, #309, then the fold's sampler construction) | the fold-construction fix; later, a shared-greedy v2 |

**Code, before the follow-up epoch:**
- #298 and #301 (the manifest of record and `query.word_check`);
- Builds stored before #301 get one strict manifest rebuild at Commit.
- **The call-boundary stop is stale for the follow-up epoch:** S1b (#253) is on main and covers `call_boundaries` for #74 and #57. The follow-up's row driver must run the Match and Commit for those rows instead of stopping (today's #74 stopped at 21:18Z under the old rule, though its Commit couldn't have ended before about 00:30Z anyway).
- **#70 (TP2 MoE)** has the same incomplete manifest as #75 (13,888 unbound peer bindings, MoE 'two producers'), and gets the same population fix.


---

# Follow-up epoch: draft plan (29 Sep, 00:10Z). Nothing launched

This supersedes the carry list above.

**Where the epoch ended** (`lanes/vllm-coordinator/20260928T2359Z-handoff-from-vllm-epoch-run-final.md`):
- **Written:** #73 only, under rule (a), with its coverage backfill pending #325.
- **Deferred:** the other 12 rows, each keeping its old record.
- **Spent:** $145.07 of $250 (at most $146.51).

## Prerequisites, all on main before GO, in this order

1. **#337 + #338:** the vLLM suite gated in `check`, and the Tools closure over all of `verity/**`. This goes first because it moves Tools identity: no attempt or Build stored before it is reused, and **every row rebuilds**.
2. **The epoch's pending fixes:** #298 and #301 (manifest of record and `query.word_check`, via D3′), #321 (the fold follows the Program's sampler construction) and #325 (the harness coverage check). Then the #73 coverage backfill commit.
3. **The TP2 MoE two-producer fix** (prep lane):
   - the MoE block's `AllReduce2` output modelled as its own member, so `tp_peer_binding.n_unbound` is 0 on #75's and #70's stored Builds (CPU);
   - `build manifest` exits non-zero on `complete False` for a row of record.
   - It gates #70 and #75.
4. **#101's G4 fold-count defect** (prep and lowering lanes): the address map declares 32 more instances than the component (the v2 top-p selects). The fix is shown bijective on try 5's stored Build and records (`art:0e6911da`, `art:55029fe0`) on CPU. It gates #101.
5. **Lift the call-boundaries stop** in the row driver: `call_boundaries` stops a row only if some identity has no attached source (`call_boundary_source` coverage below 100%). With S1b on main, #74 and #57 then run to Commit.
6. **The regression resolver fix:** the harness fetches the row's frozen reference from the store, verified against its sha256 pins. This replaces `side_record.sh`.
7. **The pod-side stops, the lesson of #68:**
   - `stop_after` and each stage deadline run inside the pod job, as `epoch_row.sh` stage markers plus the job's own `--timeout`;
   - the store and `preserved` run before the job exits;
   - custody keys are valid for the job's full timeout plus 1 h;
   - the backstops are the control pod's `research pods guard` for cap and deadline. Nothing the row's outcome depends on runs on a VM.
8. **Conditional rows:**
   - #39 needs #244 (`GemmBias_v1`) on main;
   - #57 needs its host evaluation under about 90 min per Commit (norm-chain and softcap row kernels, a faster exact Gemm, or a `CLAIMS` tap of the pre-softcap `lm_head`);
   - #4 needs the audit of its FAIL-class PASS, whose class change goes to Daniel.

## Rows, the order and the shapes

The estimates use this epoch's measured stages: Builds of 3–4 h; the Match 0.5–1 h; the Commit 1.5–2.5 h without the manifest rebuild (#298), plus about 10 min per pair after the first; the store about 10 min. Every row runs at its record's pair count. There's no time window, only the budget; launch as stock appears.

| Order | Row | Shape | Est. h | Est. $ | Gate |
|---|---|---|---:|---:|---|
| 1 | #74 | 2× H100 secure, ≥ 500 GB | 7.5 | ~~52~~ **75** (root, 13:18Z: $52 would end in the Match) | prereq 5 |
| 2 | #11 | 2–4× L40S-class, ≥ 512 GB | 9 | 30 | — |
| 3 | #23 | 2× L40S-class, ≥ 512 GB (Commit admission 483 GiB) | 8 | 18 | — |
| 4 | #60 | 2× L40S-class, ≥ 376 GB | 7.5 | 16 | — |
| 5 | #67 | 2× L40/L40S, ≥ 240 GB | 8 | 14 | — |
| 6 | #68 | 2× L40S, ≥ 240 GB (its Build was lost) | 7.5 | 16 | — |
| 7 | #75 | 2× L40S TP2, ≥ 377 GB, `COMMIT_GPU_UTIL=0.70` | 6.5 | 14 | prereq 3 |
| 8 | #70 | 2× L40S TP2 | 5.5 | 12 | prereq 3 |
| 9 | #101 | 1× L40S-class, ≥ 94 GB, 1 pair, raised sampler `max_gates` | 2.5 | 3 | prereq 4 |
| 10 | #4 | 1× L40S, 3 pairs | 5 | 6 | the audit first |
| 11 | #39 | 2–4× L40S-class, ≥ 512 GB | 9 | 30 | #244 |
| 12 | #57 | 2× L40S | 7 | 15 | the host-eval speedup |
| 13 | canary + `known_roots.json` re-pin | 1× L40S | 1 | 2 | after the last row is written |

**Budget:**
- Core rows (1–10 plus the canary): about $183.
- Conditional #39 and #57: about $45.
- Total about $228. With a 15% contingency, **request a $260 cap**, or $210 if #39 and #57 stay deferred.
- The same controls as before: the committed-spend-plus-cap rule, the balance test with the $25 floor, and the `vyv-` guard owned by the vLLM coordinator.

**Also carried:** #325's coverage backfill of #73; the `test_no_dead_modules` `spec.py` fix; and #337's known-failure owners (`lanes/coordinator/20260928T2223Z-plan-from-vllm-coordinator-337-known-failures.md`).

**Approved (2026-09-29T00:18Z, Daniel via root):**
- A $260 cap, including #39 and #57 if their gates clear.
- **GO** once prerequisites 1–7 are on main.
- The same controls as before: the committed-spend-plus-cap rule, the balance test with the $25 floor, and the `vyv-` guard (CAP = spend at GO + $260).
- #4's class change goes to Daniel.

**If the balance test fails at launch:** write one line to `lanes/vllm-coordinator/` and message root with the top-up needed. Never shrink the cap.
- At 00:17Z the balance was about $286. $260 plus the $25 floor plus other lanes' burn doesn't fit, so a top-up of about $50 or more is likely needed, depending on other lanes at the time.

**Correction (2026-09-29T00:18Z, root):** RunPod tops itself up automatically. Don't request top-ups; the spending controls are the 0 cap and the `vyv-` guard.
- If the balance test fails at launch, the automatic top-up hasn't landed yet. Wait for it and retry the launch; don't stop the epoch.

**Update (2026-09-29T13:20Z, root):** #74's cap is raised to $75, within the $260 line. The row caps now total about $251 including #39 and #57. The top-up shortfall is about $73 for the full core, or about $118 with #39 and #57.
