---
id: vllm-refactor/coordinator-state
lane: vllm-refactor
kind: state
updated: 2026-09-24T19:30Z
---
# vllm-refactor: coordinator state (resume from here)

**Handed off at 19:25Z** to the Cursor Project coordinator: `../vllm-coordinator/20260924T1925Z-handoff-for-project-coordinator.md`. Where the two differ, the handoff is current.

**Owner's standing rule (22:17Z):** decide housekeeping yourself (disk cleanup, eviction, which files to keep), using the safe default. Never delete anything not verified in R2 by direct hash, keep custody receipts, and never touch live-lane files. Report only the outcome. Surface to the owner only three things: spending beyond agreed caps, changes to agreed semantics or acceptance criteria, and irreversible loss.

**Coordinator since 19:20Z: Cursor agent bc-ba6cec03** (`../vllm-coordinator/20260924T1920Z-took-over.md`). It doesn't merge into `main`: the research coordinator is the single owner of `main` merges, and merge requests go to the owner through the Project coordinator. At 19:27Z a23 was superseded by **a23b** (agent bc-87224e5e-6d37-56de-a9ee-c75c627ef9c0, branch `lane/vllm-rf-a23b` from `c1cf11ef`, worktree `rf-a23b`, notes `vllm-rf-a23b`, pod `vyv-rf-a23`), with the `fixtures/W11*` move first so that f3 can do D15 on top of it. At 19:25Z the pods were a1, a23, f24 and f3 at $0.64/h each, plus f1-g1 and f1-tp2 (2x L40S each) at $2.18/h each: $6.92/h in total.

## Where things stand
- **Survey:** done, 673 findings. The synthesis is `SYNTHESIS.md` in this directory; its gate text and A4 ordering were corrected by the coordinator.
- **Owner decisions** (17:20Z), all as recommended:
  - merge cleanup-2 into main and branch from main;
  - start Phase 0 and A1 to A3 now;
  - value checks over opened values inside Commit now, with a separate verifier later;
  - delete CMT-1, `engine_rs` and the dead PoC paths;
  - refuse world > 2.
- **Merge:** `lane/vllm-cleanup-2` went into `main` at `72884c8a` (17:24Z, `--no-ff`). The only extra changes relative to cleanup-2 are in `tools/research`. No references to the removed package paths remain outside the integration.
- **Budget and deadline:**
  - The CAP file on `vy-control-verity` is 600. Spend was $238.67 when it was raised; the tally has run since 2026-09-23 under tag `2026-09-23-vyv-rebuild`.
  - The rate cap is $45/h.
  - The deadline daemon terminates `vyv-` pods at 03:00Z. **Re-armed at 01:03Z to 05:00Z, then at 03:02Z to 07:00Z, then at 05:01Z to 09:00Z, then at 07:01Z to 11:00Z** (REARM lines in dm.log). Extend by at most 4 h per step, and only while lanes need pods.
  - `/root/dm/budget_cap.py` on the pod (sha256 `3f273597…`) is the **veritor** variant: byte-identical to the uncommitted `~/projects/veritor/zk/campaign/budget_cap.py`, with `--rate-action newest`. Verity's `tools/research/src/research/pods/budget_cap.py` is veritor's committed HEAD version and lacks that option. In verity, `research pods guard` has replaced budget_cap.py and deadline.sh, and its `--rate-max` sheds the newest pods by default. At a switchover, move to `research pods guard --baseline <spent>` rather than porting the option. Don't restart with verity's budget_cap.py, `rearm.sh` or `deadman.sh`: `--rate-action` would be rejected, and without it a rate spike trips and terminates every `vyv-` pod.
  - Three daemons run on `vy-control-verity`, all vLLM's, as checked at 19:31Z: `budget_cap.py` (pid 8950), `deadline.sh vyv- 1790305200` (pid 20985) and `balance_floor.py` (pid 7241). The balance floor terminates every `vyv-` pod when the account balance drops below $25. It's only a backstop: the account auto-tops-up below about $100, so report only if the balance falls below about $90 without refilling. The binding limits are the $600 cap and the deadline. The owner's rule: push the deadline back a few hours at a time, never in one big jump, so it still works as a dead-man switch.
- Of the six lanes, a1, f1, f24, f3 and f56 are subagents of the old chat (eb746331), which can't be messaged while they run; steer them only through their files or pods, or restart them. a23b is the vLLM coordinator's own background subagent. Don't delete the old chat. Its role: `../vllm-coordinator/20260924T1945Z-setup-for-old-chat.md`.
- Gate (a) credential route: `20260924T1942Z-gate-a-credential-route.md`.
- **Watcher:** the other coordinator's notes watcher excludes `vllm*` lanes, which is why the refactor lanes are named `vllm-rf-*`.

## Lanes (local subagents launched from chat eb746331; the brief is `LANE_BRIEF.md`)
| lane | scope | agent id | branch | notes dir |
|---|---|---|---|---|
| a1 | baseline and guardrail lints | 0071dbd5-fc85-40a2-b188-0ff3b70d93a3 | lane/vllm-rf-a1 | ~/.research/notes/lanes/vllm-rf-a1 |
| a23 | dead code, data and paths | 910daceb-3d03-4c35-abd4-3ef36049a9a6 | lane/vllm-rf-a23 | …/vllm-rf-a23 |
| f1 | D1 opened-value replay | ca142d03-cbdd-4db6-921c-ad007244aa4b | lane/vllm-rf-f1 | …/vllm-rf-f1 |
| f24 | D5, D6, D7, D10, D11, D13 | 1d5dba5f-1f4a-44b3-b2b7-01aa308edc91 | lane/vllm-rf-f24 | …/vllm-rf-f24 |
| f3 | D3, D4, D14, D15 | 4d8eb3fd-689f-4551-a6ef-9439c59c06e6 | lane/vllm-rf-f3 | …/vllm-rf-f3 |
| f56 | D16, D17 | fec8581f-4b57-4899-81f1-ead76e01ceee | lane/vllm-rf-f56 | …/vllm-rf-f56 |

The canvas agent (742f18e5-2fc5-4a71-b848-36d442816381) is building a canvas of the survey and plan.

## Incidents
- **About 18:02Z:** the agent process of the veritor window restarted (new pid 89761). f1, f3 and f56 died with it and were resumed at 18:46-18:48Z through `Task resume` (context kept).
  - For a1 and a23, the resume returned "Agent host session already exists", so both are alive or hung.
  - a1 last wrote at 18:29Z and f24 was editing at 18:44Z.
  - a23 has written nothing since 18:02Z. If it is still silent at about 19:05Z, launch a fresh a23 on a new branch, lane/vllm-rf-a23b, from origin/lane/vllm-rf-a23.
- **Liveness probe:** `Task resume <id>` fails with "session already exists" when the agent is alive; otherwise it restarts the agent with its context. Subagent transcripts stop updating after a host restart, even for survivors, so they are not a liveness signal.
- **The baseline at 72884c8a is not green:** gate (b) has 65 failures and errors. Lanes judge "no new failures" against `vllm-rf-a1/baseline.md`.

## If a lane dies
Relaunch a fresh generalPurpose subagent with the lane's prompt from `LANE_PROMPTS.md`, with that file's restart preamble in front.

## Merging
Since 19:25Z the research coordinator does every merge to `main`, so two agents can never merge at once. The order is a1, then a23 (or a23b), then the f-lanes as their READY.md files appear. For each lane, the vLLM coordinator:
1. checks the gate evidence in READY.md against the baseline;
2. makes sure the branch is pushed and rebases cleanly on current `main`;
3. hands the branch and head commit to the research coordinator for a `--no-ff` merge;
4. tells the remaining lanes to rebase.

**Merge requests (sent to the owner via the Project coordinator; the research coordinator merges):**
- 22:25Z **a1**: `lane/vllm-rf-a1-rebased` @ `bcbec401`. That is a1's `39c5ee7a` rebased onto main `21688b01`, plus one coordinator commit deleting the 2 lint allowlist entries that main's `e0c7bfe9` (fold_compare) made stale. The lints are 41/41 on main on a CPU pod, and without the fix 2 fail. `lane/vllm-rf-a1` itself is untouched. **Merged 22:10Z as main `1d9c3198`** (research coordinator, `--no-ff`). At 22:13Z the rebase broadcast `20260924T2213Z-main-moved-rebase.md` went out, with a banner in each lane's STATE.md. a23b has one trivial conflict in `fold_compare.py`; f1, f24, f3 and f56 are clean. Next: a23b.
- 00:20Z **a23b**: `lane/vllm-rf-a23b` @ `9be6e462`, rebased onto main `58e4c1aa`. It rebases cleanly onto `a47a45bd`, with `integrations/vllm` and `packages/` identical. Gate (a) T0+T1 matches the same-pod base on all 158 tests. Gate (b) xdist shows no new F/E or skips (the order-dependent gc pair aside). Lints 41/41 at the exact tree. Scope: 122 files, all under `integrations/vllm`, +240/-8,607. After it merges, f3 rebases onto the W11 move (`a9abe0a0`) and every lane rebases again. T1 needs a 512 GB pod (`replay_partition`, 63-115 GB per process). a23b's agent finished at 00:14Z and both of its pods are terminated. Gate gap it found: on a store-only pod, T1 `decomp_hashes` skips on every row, because the stored fixtures lack `match_decomp.json` and the batched `match/...` trees. So gate (a)'s T1 today exercises only `replay_partition`. Candidate follow-up: stage those files in the store.
- **a23b merged as `932a4886`** (main `4bd6c54c`, seen 00:31Z). At 00:32Z the rebase broadcast `20260925T0032Z-main-moved-a23b.md` went out, with banners in f1, f24, f3 and f56. f1 and f56 are clean. f24 conflicts in `p10_size.json`. f3's D15 conflicts in `tables_dir()`, and its duplicate W11 move gets dropped.
- 02:40Z **f24** (`lane/vllm-rf-f24` @ `e818a5d4`) and **f56** (`lane/vllm-rf-f56` @ `a4b823a3`), both on main `bbbe936c`, merge requests in that order.
  - They don't conflict with each other (they share `tp/commit.py`, `p10_size.json` and `by_name_allowlist.json`).
  - With main + f24 + f56 merged on a CPU pod: lints 41/41, and `test_no_by_name_rules` plus `test_imports_resolve` pass.
  - Gates reproduced with jdiff: gate (a) T0+T1 matches a23b's same-pod base, and gate (b) shows no new F/E or skips (the gc pair and sigint flake are order or timing dependent; one skip reason is main's own `test_ship_roots` wording).
  - Not ready yet: f3 (rebasing, `bca6ab61`, READY still names pre-rebase `4fb0eb2c`) and f1 (in progress).
- 03:50Z **f3** is READY at `4c4159c5` (rebased onto `bbbe936c`; lints 41/41; gate (b) matches main on the same pod; gate (a) T0+T1 green at `4fb0eb2c` apart from one shared-cache race on `manifest_digest-r11`, which passes when rerun alone).
  - f3's branch conflicts with f24 in `p10_size.json`. So the coordinator built **`lane/vllm-rf-f3-integrated` @ `68e75c14`** (pushed): f3 + f24 + f56 + main `b84f11ea`, with the p10 conflict resolved (f24's `verdict.py` caps, f3's `padding_steps.py` 930, `commit_delta.main` 1915 as measured). Lints, by-name and imports are 45/45 on a pod.
  - Merge order: f24, f56, then f3-integrated (not `lane/vllm-rf-f3`).
  - Combined gate (b) is running as research run `r20260925-034304-3b78` on `vyv-rf-coord-gb` (`qhycj9nzntk7wx`, guard 60). Fetch it with `research fetch r20260925-034304-3b78`, then jdiff against a1's xdist base. The f3 merge request is final once that's green.
- 04:05Z **f24 merged as `24e3b391`, f56 as `baeefd21`** (research coordinator). f3-integrated merges cleanly onto `baeefd21`, and the merge result's `integrations/vllm` and `packages/verity` trees are byte-identical to the tested tree `68e75c14`.
- 04:10Z the combined gate (b) (`r20260925-034304-3b78`, preserved) is **green** against a1's xdist base: 0 new failures or skips. There are 66 F/E; one skip reason is main's `test_ship_roots` wording. **f3 merge request sent: `lane/vllm-rf-f3-integrated` @ `68e75c14`.** Pod `vyv-rf-coord-gb` terminated.
- 04:06Z f1 was told to rebase onto `baeefd21` (handoff `vllm-rf-f1/20260925T0406Z-...`): import-line conflicts in `check/sampled_replay.py` and `tp/partial_source.py`, plus `p10_size.json`.
- 04:37Z **f3 merged** (`lane/vllm-rf-f3-integrated`, main `cc7842a0`, lints 41/41). Phase 0/1 is merged except f1. At 04:40Z f1 was told to rebase `299f42d5` onto `cc7842a0`; the only conflict is the `p10_size.json` `commit_delta.main` cap.
- 06:05Z **f1 merge request sent: `lane/vllm-rf-f1` @ `8efb918e`** (on `c1891d48`; merges cleanly with main `2994bd25`; 27 files, all under `integrations/vllm`).
  - Evidence at `8efb918e`: lints 44/44, touched tests only on a1's list, gate (b) jdiff against main on the same pod exits 0.
  - Earlier heads: gate (a) T0+T1 at `e2f85a82` green; GPU rows #11, #67 and #70 with verdicts unchanged; the pod negative fails as intended.
  - Commit time is +8% dense, +30% on #70 and +49% on #67's compare (opening every read value).
- 06:05Z **Owner's overnight direction:** after f1, proceed with A4 and then the phases that follow, without waiting. Hold anything that needs an owner decision, stay under the $600 cap, keep extending the deadline in small steps, check the research coordinator's handoffs before touching the steward or guard (the vyv- guard moves to `research pods guard` during the cloud switch-over), and report only merge requests and blockers.
- 06:05Z **A4 (re-home into the §5.1 tree) launched** as this agent's background subagent. Branch `lane/vllm-rf-a4` stacked on f1's head `8efb918e` (rebase onto main after f1 merges), worktree `rf-a4`, notes `vllm-rf-a4/`.
- 06:39Z **f1 merged** (main `7fcedf47`). All of Phase 0 and A1 to A3 are in main. a4 rebases onto it itself (its prompt says to once `8efb918e` is in main).
- 06:40Z decision brief for the owner written: the Project store's `docs/vllm-open-decisions.md` (decisions 1, 3, 4, 5, 8). Budget note: the owner set $600 overnight across both campaigns. The vyv- daemon cap is 600 cumulative (spent about $323), so vLLM has about $277 until the owner says what vLLM's share is. The cap file stays unchanged until then.
- 06:39Z **f1 merged** (main `7fcedf47`). All of Phase 0 and A1 to A3 are in main; a4 rebases onto it itself.
- 06:40Z decision brief for the owner: the Project store's `docs/vllm-open-decisions.md`.
- **Owner decisions, 06:41-06:45Z:**
  - **Decision 1:** vLLM keeps its framing as the named core scheme `vllm-v1`. Proof backends implement `vllm-v1` too (the research lanes are adding it). frame-v3 stays as a second scheme, and both are benchmarked at serving and proving time. There is no planned migration.
    - C1 goes ahead in its named-scheme form, plus per-scheme throughput instrumentation of vLLM's commit path.
    - The core module is being written on `origin/cursor/vllm-commitment-scheme-f2e6` (`verity.commitments.vllm_v1`, PROTOCOL.md, vectors, CommitmentScheme, commit_cost benchmark), and a GPU committer by research lane `hash-commit`. So vLLM's C1 is the integration side: the commit path over `verity.commitments.vllm_v1`, byte-exact against its vectors, plus the instrumentation. It starts after A4 and after that core branch merges.
  - **Decisions 3, 4 and 5: approved as recommended.**
    - Principle for 3: core owns the basic Definitions and all silicon semantics. The integration cites core for those, and defines only application-specific Definitions. Apply it in C2, and flag anything on the line between the two.
    - The four duplicate ids (Bf16ToF32_v1, F32ToBf16Rn_v1, F2fpBf16_v1, HopperBF16WgmmaDot16_v1) have the same id and signature in both copies, and Programs cite only `{"fn": id}`. So dedup is digest-neutral, provided the evaluators agree. The only digest change is `AmpereBF16TcDot16` v1 to v2, which the 11 L40S rows cite through the `ada` target.
  - Start C2 and C4's IR-analysis part as soon as A4 merges.
  - **Decision 8 (06:47Z):** a wrapped `verity_vllm.LLM(...)` that mirrors `vllm.LLM`. The user passes model, revision and documented supported options; we build and pin internally; it returns vLLM's outputs plus our records; unsupported options fail loudly; no wrapping of a user-built engine. "RowSpec" leaves the public API and docs, and the internal pinned record gets a descriptive internal name. Applied in A5.
  - **Budget (06:47Z):** vLLM gets $300 of new spend tonight. CAP was raised 600 to 623 on vy-control-verity (logged; the daemon picked it up at 06:48Z). Up to 20 agents project-wide. All five decisions are settled, so run every unblocked lane.
  - C1 open items from the root: vLLM's four CUDA hashing copies against the vllm-v1 conformance vectors (PR #15) on a GPU pod, and the weights root against a live model, both byte for byte.
- **Lanes running (06:55Z), all background subagents of this agent:**
  - `a4`, bc-2caed690: re-home; budget $45.
  - `c1`, bc-9eae5bc7: vllm-v1 scheme; budget $35.
    - Phase 1 now: CUDA copies against the vectors, and the weights root live check (evidence only).
    - Phase 2 after A4 and PR #15 (`fa9c4594`, `origin/cursor/vllm-commitment-scheme-f2e6`) are both in main: commit path over `verity.commitments.vllm_v1` plus per-scheme throughput instrumentation.
  - `c4ir`, bc-fbcf78e2: boundary, partition and liveness into `verity.ir`; budget $15. Core side now, integration switch after A4.
- 08:25Z **Wave 2 started early on a4's pushed head `10996616`** (root: use idle capacity, since these lanes need a4's layout but not its merge). Shared rules: `WAVE2_BRIEF.md`. Each lane rebases with `git rebase --onto origin/main 10996616` once a4 merges.
  - `a5`, bc-95dc5f40: CLI, typed config and decision-8 `verity_vllm.LLM`; $35.
  - `c2`, bc-568d82f4: Definition library under the owner's principle; the digest-neutral dedup first, and the AmpereBF16TcDot16 v2 epoch commit last and separate; $25.
  - `b1`, bc-910bfdb6: kernels in `program/kernels/` registered with core `verity.evaluation`, and `check/replay/`; $45.
  - `b4`, bc-95aa165d: engine and hooks; $25.
  - `b2v`, bc-7d05cc29: one verdict and properties records; $30.
  - Budgets across all 8 lanes come to about $255 of the $300.
- 08:24Z **Agent cap (owner, 20 project-wide):** vLLM gets 8 including this coordinator, research 11 including its coordinator, and the survey 1.
  - b2v (lowest priority) is **paused**, signalled through its STATE.md banner, `vllm-rf-b2v/PAUSE` and a WAVE2_BRIEF line. It keeps its worktree `rf-b2v` at `10996616`, with nothing pushed. That leaves 7 lanes (a4, c1, c4ir, a5, c2, b1, b4) plus the coordinator.
  - **Queue as slots free:** first resume b2v (Task resume bc-7d05cc29; tell it to delete PAUSE, re-read STATE and continue), then the B5 splits one at a time (native_host after C1), then B3 and B2's heredoc part after A5, and C3 after B4.
- 08:32Z **Agent share is now 9 including this coordinator** (the survey agent finished), so the cap is 8 lanes plus the coordinator. b2v's pause was cancelled before it took effect: b2v never paused, the notices are removed, and it continues. Running: a4, c1, c4ir, a5, c2, b1, b4, b2v (8). The queue is unchanged: B5 splits, then B3 and B2's heredoc part after A5, and C3 after B4.
- a4 status at 08:15Z: every file move is committed and pushed (14 commits, head `10996616` at 01:10 PT). Left: head lints plus gate (b) against main on its CPU pod, gate (a) T0+T1, and the GPU smoke of #101 (its `reg` and `g1` pods are up). ETA for its merge request is about 4 AM PT. Its STATE.md lagged its commits by about an hour; commits are the liveness signal.
- **To launch when A4 merges (now mostly launched early; what remains):** B5 splits (native_host after C1). After A5: B3 and B2's heredoc part. After B4: C3. After C1 to C3: the re-baseline epoch. The original list:
  - A5 (one CLI and typed config, with the decision-8 API `verity_vllm.LLM(...)`), about $30;
  - C2 (Definition library under the owner's principle), about $20;
  - B1 (evaluator kernels and replay; `program/kernels/`), about $40;
  - B4 (engine and hooks), about $25;
  - B2's verdict part, about $25;
  - then B5 splits as money allows (native_host only after C1).
  - After A5: B3 and B2's heredoc part. After B4: C3. After C1 to C3: the re-baseline epoch (decision 4a).
  - Money: $300 of new spend tonight (cap 623).
- 06:35Z **Owner-approved naming:** `program/kernels/`, not `program/backends/`, for the evaluator implementations. Sent to a4 (STATE banner and handoff) before it moved anything, and recorded in SYNTHESIS's new decision log. The owner wants work to continue nonstop past 8:30 AM PT.
- **Held for the owner (morning list):** decision 1 (commitment framing; assessment in the Project store `internal/commitment-format-assessment.md`); decision 3 (Definition ids: C2); decision 4 (re-baseline epoch); decision 5 (upstreaming: C4, including the IR analyses); decision 8 (API scope: blocks A5, and so B3 and B2's heredoc part). The owner first chose (a), frame-v3 in production, with vLLM keeping its CUDA and passing core conformance vectors. He then asked to consider standardizing on vLLM's existing framing as a named `verity.commitments` scheme, provided proof backends don't fork per format. No plan or code change until he confirms.

## Next phases (not started)
- **A4, re-home into the 12-package tree:** after the Phase 0 lanes merge.
- **A5, one CLI and typed config:** after A4.
- **Phase 2:** B1 to B5.
- **Phase 3:** C1 to C4, behind decisions 1, 3, 4 and 5, which are still open.
