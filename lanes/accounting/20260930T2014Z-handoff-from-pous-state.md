---
id: 20260930T2014Z-handoff-from-pous-state
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f
---

# @old-accounting's state for the three successors: PoUW to compute, PoUS to memory, network timing to network

This answers `note:20260930T2000Z-handoff-from-accounting-state-for-successor` (compute) in full. It points memory and network to
their own replies. It covers what changed since the charter (`note:20260930T1740Z-handoff-from-pous-charter-pouw`, 17:35Z) and
what the charter doesn't say. Daniel's word on this handoff: it needn't be perfect. The old coordinator keeps its tacit knowledge,
so ask it on Slack, tagging @old-accounting.

| Handle | Successor | Your section |
|---|---|---|
| @compute-accounting (PoUW) | bc-e90634dd-8e87-5b7b-8ecd-97abfd87e3fa | §A below |
| @memory-accounting (PoUS) | bc-15ada664-f325-5371-a473-65d408be3cf5 | §B below: a summary. The full reply goes to `lanes/memory-accounting/` by 21:30Z |
| @network-accounting (network timing) | bc-ecea50f6-c509-5918-b17a-d2148d57728f | §C below: a summary. The full reply goes to `lanes/network-accounting/` by 21:30Z |

## The store tree (for all three)

**`art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9`** (kind `evidence/v1`, PRESERVED, 3,506 files, 193 MB).
It is a copy at about 20:05Z of the pous Project store (`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`). It holds
`notes.md`, `preferences.md`, all of `docs/` and all of `internal/`, including `internal/pouw/panel/`,
`internal/pouw/rtx-pro/server.md`, `internal/pouw/rtx-pro/workers/` and `internal/pouw/red-team/ratings.md`. To restore a file, run
`research data fetch <art> --path <member>`, for example `--path internal/pouw/rtx-pro/server.md`.

- **Left out:**
  - `private/`: the store has no `private/` directory.
  - `internal/efficient-crypto/p2-bounty-kit/challenges-private.json`: the P2 bounty's private challenges. Ask for it if you need it.
  - Store-root folders the spec didn't name: `lean/` (53 MB, including the Lean staging `lean/submissions/pouw/`), `code/`
    (31 MB), `inbox/`, `media/`, `artifacts/` (empty) and `archived.md`. Ask and I'll ship any of them the same way.
- **Red-team verdicts** in this store are under `internal/pouw/red-team/` (in the tree), not in a private path.

---

## §A. For @compute-accounting (bc-e90634dd): PoUW

### A1. Agents

This is a snapshot of the cloud-agent list at 20:05Z. RUNNING means mid-turn, and WAITING means waiting on its own background
work. IDLE agents sleep until someone messages them, and the two sub-coordinators wake their own IDLE workers.

**RUNNING or WAITING (8 PoUW agents):**

| Agent | Current task | Expected finish | Hands back what, to whom | After it |
|---|---|---|---|---|
| **bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d**, RTX PRO sub-coordinator (WAITING) | Runs node-2 GPU work and the panel for its workers (listed below). Its open items: (1) queue #593's whole-node CUDA-graph decode window ("window 6"), then the CPU verify of about 35 min; (2) **the freeze-list sign-off to `lanes/cluster-build/`** (§A4); (3) the rc=4 failures of GPU 1's forms jobs on die 5 (`GPU-0c776bca`, node2-ops' 19:20Z alert) and GPU 4's real `RECHECK VERIFY FAILED` in `fp4-recheck2-verify-d3b846cf.sh`; (4) queue the corrected 70B keyed-transform evals; (5) switch the FP8 panel lines to the packed-cast basis (v1 0.519%, v2 0.371%) once GPU 1 confirms the binary; (6) keep ≥ 8 GPU-h of useful fill queued (node2-ops' ask, relayed 19:31Z) | Standing | Panel rows, timed windows and worker results → you | Keep |
| **bc-824e54a2-2192-5eb8-8334-4f9105631b51**, new-crypto sub-coordinator (WAITING) | The PoUW Lean store. It is rebuilding the FP4 base-split fix on the post-M4 store (worker bc-ae19a858) for review. RowSeed (M3) waits on its statement review and on Daniel: is its per-row draw condition a named assumption? v2-hot (M2b) is held on the first-atoms grant | M3 and the FP4 fix need their reviews first. M2b needs a v2-hot route to be rated | Lean pins and store merges → you. Merges go through the research coordinator's train | Keep |
| bc-ccd30e80-9a35-5547-b43c-64054af776ee, served-gap profile (#593, #596) | #593's CUDA-graph decode is verified untimed and waits on window 6. #596 (`-h2` on the served graph path) is verified and waits on Daniel's `-h2` answer | Window 6 is in bc-2aa33ad8's queue | Decode rows (expected about 2.0–2.2×, from 3.94×) → bc-2aa33ad8's panel and you | Queued: **fix 12** (both arms under CUDA graphs: stock FP8 in vLLM's cudagraph mode, Pearl-C's whole step captured), then **fix 8** (hashing's per-call host work) |
| bc-dd22acf8-7690-5123-ab90-d129950f4f91, the MVP (#540, #585) | Window 5 is verified as panel attempt 103: prefill 1.718×, decode 4.145× eager FP8. The quality gap is the scheme's intended noise at its predicted size | Window 6 is #593's. Window 7 adds the hashing forms `s,one` (estimates: prefill about 1.55×, decode about 1.7×). It first needs GPU 1's gate under `s,one`, then the served-tree changes | Windows and verifies → bc-2aa33ad8 | Queued: window 7 |
| bc-3006c44a-5462-55f5-9ce2-722e3ecca818, cheap binding | v2-hot's first atoms. The derived charge from atom 4 is the interim: B conditional, γ 0.689% packed. The uncredit-atom-0 route is withdrawn. Under the audit's new row-dependent floors, the assessor (20:00Z) finds every GPU 3 block below the floor, so v2-hot may hold at 0.371% with no charge | Waits on GPU 3's CPU check | γ and the route → the assessor, bc-b58c6093 and you | Held until GPU 3 reports: the per-word draw scoping and the full-catalogue Δ recompute |
| bc-d9842080-f8c7-54a2-84bb-ba0a4b680482, FP4-tile model and catalogue audit | Its audit found the copied catalogue missing Smirnov's ⟨3,3,6;40⟩. It is producing the full floor staircase W*(L, M) over 4,180 schemes, the free-family shape list and the catalogue hash, then rerunning v1's closure on them. The assessor says v1's 9.2% margin stands | This turn | Floors and the hash → the assessor, bc-3006c44a, bc-b58c6093 and GPU 3 | Then v2-hot's Δ and the assessor's conditions get restated |
| bc-a8466279-735b-5800-a6cf-19e3b12b2cf6, Pearl-C4 domain rules (#534, #556) | B-OVF (`a097a30e`) and V-EX (`a1b72fd0`) are on #556. The assessor's 20:00Z ruling on the c_L pin was sent to it: pin c_L at the catalogue minimum, at the lower-bound add count (0.661 / 0.579 / 0.507 / 0.408 at 8k / 16k / 32k / 64k³), as a pinned table. No rating moves | This turn | #556 commits → GPU 5 (bc-71c6ab78), who ports them to #580 | Then the panel's small-n flag (n ≤ 1,024) lifts |
| bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4, hashing | **The forms grid is complete (20:07Z):** all 13 panel shapes from 283 chunks of GPU 1's fill (`art:b7790414e6c880a800dcb66818b459d05eb060498f0cceba1999ea94e81ba8d3`, `internal/pouw/rtx-pro/hashing-forms-by-shape.md`). `s,one/split` wins everywhere, from −2.9% to −16.1% at prefill, and within 2% of the best at decode. **This supersedes the coordinator's "2 of about 18 shapes picked"** | Done bar the served tree taking the forms | The picks → bc-dd22acf8 and bc-ccd30e80 | Stop after window 7 unless you give it the `w` epilogue (v2 and v2-hot, per shape) |

**RTX PRO workers** (bc-2aa33ad8's, one status file each under `internal/pouw/rtx-pro/workers/`). All were IDLE at 20:05Z except GPU 7:

- GPU 0, bc-e6a46970-b6ef-5738-af64-182b143075d4: FP8 capture. Its second capture fill (16 jobs) was queued at 18:45Z.
  node2-ops flagged its `fp8chain-die*` jobs for holding GPUs idle in CPU phases (0.72 GPU-h); the fix was relayed.
- GPU 1, bc-18346d9c-4bfb-56af-ad79-0d17e73bb44b: the Pearl-C sm_120 kernel. It owes the binary check that the packed cast is
  what runs, and the arm gate under `PEARLC_A_FORMS=s,one` (window 7's first item). Its forms jobs exited rc=4 on die 5.
- GPU 2, bc-7442ca43-9389-5653-ae57-2cbf499a9569: hashing. The self-recording pilot is done (attempts 67 and 68).
- **GPU 3, bc-0f3f8a2f-3024-5bae-bda9-8e3836b9cb92: the FP8 attacker, running the v2-hot row-count check on CPU under the new
  floors.** This is the result v2-hot waits on. Clause (b) held at 19:05Z (0 of 2,376 cases).
- GPU 4, bc-36186951-83fc-53b6-87de-fa584ddf9ff9: FP4 capture, done. Its recheck verify failed for real (19:12Z), and nobody has
  explained it yet.
- GPU 5, bc-71c6ab78-d098-5f45-8c08-337ac2c83084: Pearl-C4 verifier #580, at `14d6f1bb` (the 16k row is attempt 21, verified).
  It is porting B-OVF and V-EX from #556.
- GPU 7, bc-dbc19788-573d-5ba4-b3b2-d6551c1c60ef (RUNNING): FP4 attacker; its keyed-rotated NVFP4 census was queued at 18:38Z.
- Harness, bc-0de2d624-783f-5e35-9b57-19c1627bd2f2 (#491); helper, bc-6da61042-1b56-5e51-964f-9ae86e909da4 (#588); mainloops,
  bc-fb55a759-0d1c-55f4-a2da-04aadde30be9 (#543, #570; idle since 15:29Z).

**New-crypto workers** (bc-824e54a2's): bc-ae19a858 (the FP4 base-split fix on the post-M4 store), bc-5382063c (the RowSeed
fragment argument, option (a)), and bc-5a715b19 and bc-3cdbf3c1 (M4, done).

**IDLE PoUW agents that need a nudge, not a stop:**

- bc-d7d4b0d1, the assessor (last active 19:56Z). Its open items are the ε₈ ruling, the int8-Strassen replay, the derived charge's
  conditions (Δ for window lengths 22–256, and GPU 3 at starts 4–5), and its verdict once GPU 3 reports.
- bc-b58c6093, TT_OUT restatements. It restates v2-hot's row once the floors land.
- bc-69c09d42, the assumptions table. It is current only to 18:45Z, so it needs the catalogue audit, the v2-hot route, B-OVF and
  the c_L pin.
- bc-6289d8b0, keyed transforms. The corrected 70B evals are queued through bc-2aa33ad8. A 70B-class registration must fold γ.
- bc-f5bf55c8, FP4 specialization. Version 3 of its 70B census runs after the MVP's windows.
- bc-876ca543, price twins. It waits on the grants.
- bc-8412d697, approved weights. Its work is done, pending Daniel.
- bc-9914c188, #449. A small test-shim PR follows the merge.
- bc-f4e8ae34, the vLLM API. #567 merges first, then `main` goes into #573, #576, #578 and #585.
- bc-22298e90, the Lean red team. It wakes when a set is staged.

**Retire now:**

- bc-efe47341 (node-2 ops): stopped at 18:57Z and handed to node2-ops (bc-c0738ef6), with no timers.
- bc-c3ade0aa (one-cluster design): handed to infra; cluster-build (bc-c2e4c12a) runs the shadow and the switch.
- bc-1a23b70c (kernel tooling): done bar #590. Hand #590 to the harness owner, bc-0de2d624.
- bc-e4a2abca (the H100 capture): withdrawn. Its #453 can close.
- bc-b395c87c (the forming-glue red team): done.

bc-26712550 (the console panels) moves to @console, and Daniel drives bc-838f9732 (Slack) himself.

Not ours, as far as I can tell: bc-2a5f14cf ("Pearl-C chain onto main") and bc-35ab914e ("vLLM GPU/CPU pipeline split", stale
since 14:30Z). bc-274e414a, bc-ea6ebbd6 and bc-df404df0 were started by the new subcoordinators.

### A2. PRs

- **Merge requested and waiting on the research coordinator** (still runs trains, per Daniel's 19:12Z ruling 6):
  - #449, then #548, then #534. #449's check passed at `5f6a31c7` (`note:20260930T1352Z-handoff-from-pous-449-check-passed-ready-to-merge`),
    and #548's head moved to `6064845f` (14:28Z).
  - #491 (the harness) and #567 (the linear API, the only one not in draft). #567 unblocks the stack #573 → #576 → #578 → #585.
  - #577 (the kernel skill, docs only; #595 rewrites it, stacked on it).
  - None of them has merged, and I found no train in `lanes/coordinator/` since 14:28Z. `main` has moved to `b1c77be0`, so each
    needs a fresh recorded `check` of its merged tree.
- **Next to request, once green:**
  - #556 (then #580, which carries its fix into the verifier);
  - #590 (the runner publishes its records);
  - #593, then #596 (#596 only if Daniel says yes to `-h2`);
  - #572 (the `-h2` switch in the sm_120 pipeline).
- **Closeable:**
  - #453 (its H100 run was withdrawn).
  - #542 (Pearl-C4 v4 was rejected; it is kept only for replay, so close it or leave it as history).
  - The `-h2` and `-h3` hashing drafts #510, #537, #541, #544, #547, #549 and #555 are measurement branches that #572 and #591
    carry forward. Ask bc-b139c29c before closing any of them.
- **Red-team verdicts outstanding** (all in `internal/pouw/red-team/ratings.md`, in the tree):
  - v2-hot's TT_OUT grant (`no-aligned-exact-region/sm120-unpromoted-hot`) is held. The derived charge is B conditional (19:28Z).
    No-charge at 0.371% waits on GPU 3's check.
  - The FP4 grant waits on the red team's GO on the rebuilt base-split fix, the R1-as-charge ruling and the assessor.
  - The ε₈ ruling (`fp8-merge-rate/sm120`) is pending.
- **Other lanes' PRs:** #586 (cluster-build's foundation) wants a recorded check from the research coordinator, and #592
  (Slack) has infra's merge request (19:34Z).

### A3. Daniel's decisions

None of the three standing decisions has an answer from Daniel that the coordinator knows of.

| Decision | Where it's written | Recommendation now |
|---|---|---|
| **Beacon:** drand quicknet | `notes.md` "Morning decisions"; `docs/pouw/assumptions.md` summary (`beacon-unpredictability` C) and its beacon table; charter §"Open decisions" 1 | Unchanged: drand quicknet. It is still the C on every line |
| **Per-row seeds:** `-h3` or `-h2` | The same three places; `docs/pouw/hashing-accounting.md`; `docs/pouw/assumptions.md` row `tt-out/pearl-c-sm120-rowseed` (B) | Narrowed. At 19:58Z the coordinator asked Daniel for **`-h2` on the served path**: yes, rated A, with prefill 1.68× → 1.62×. #596 waits on him, and I found no file copy of the ask. `-h3` (P2) stays open behind M3's review and the named-assumption question |
| **Registered weights:** keyed rotation or a curated list | `docs/pouw/approved-weights.md`; `docs/pouw/assumptions.md` (the recommendation for Daniel, near its line 170) | Unchanged: rotation for FP8 now, and for Pearl-C4 once #580 enforces the fix, with the curated list as the fallback. V/O rotation plus head interleave waits on the corrected 70B evals, then goes to Daniel |

**The decode headline rule** is the coordinator's (19:58Z), not Daniel's. Both arms will run under CUDA graphs (fix 12), with the
eager row beside them. Until then, the kernel-time ratio is published next to the eager row: 27.7 / 7.65 = 3.6× under `-h1`.

**"Morning questions"** (`docs/project-context.md`): none has an answer recorded in the store.
- **Still open:**
  - P2 deployment's two questions (for memory);
  - the POUS MVP's three: refuse D > 5 or scale k, who the colleague is, and where the Notion page lives (for memory);
  - the PoUW MVP Notion page's home and access;
  - the research-notes registry: full kill reasons or titles only.
- **Overtaken:** the FP8-lane questions (the lead moved to Pearl-C on sm_120), the GPU account and the GPU freeze (node 2 is on
  root's Nebius budget), and the Theorem 1 and correction items, which were informational and have been told.

### A4. Promises owed

- **The freeze-list sign-off: not in `lanes/cluster-build/`** as of 20:10Z, since nothing there mentions the freeze. It is owed by
  bc-2aa33ad8 to cluster-build (bc-c2e4c12a) before the node-2 switch. It was asked for at 18:59Z and 19:31Z (see
  `note:20260930T1915Z-handoff-from-infra-rulings-one-pool-for-pouw`). If bc-2aa33ad8 objects, the objection goes there too.
- **For kueue-fold (bc-d5ffe46d): the list of untimed PoUW jobs for node-1 overflow**
  (`note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`). Unanswered. The limits are ≤ 20 GB, preemptible
  with 5 s grace, and no timing; name each job and the paths it reads in `lanes/kueue-fold/`. It is bc-2aa33ad8's list to
  give; good candidates are the verifies, censuses, coverage and recheck jobs.
- **For node2-ops:** ≥ 8 GPU-h of useful fill queued, `filler=` labels, and CPU fill on cores 96–127. Relayed to bc-2aa33ad8 at
  19:31Z; bc-2aa33ad8 owes the queue.
- **For Daniel:**
  - A v2-hot answer once GPU 3 reports: either no charge at 0.371%, or the derived charge at 0.689% as the fallback. He was
    told it's held.
  - The keyed-transform adoption question once the 70B evals land.
  - The decode headline under CUDA graphs (window 6, then fix 12).
  - The morning deliverables stand (Daniel, 04:51Z): slowdown plots, the rated assumptions table and the proofs. The table
    needs its post-18:45Z update.
- **For infra:** POUS's 19:08Z yes on node-2 spare CPU and RAM and on node-2 metrics in node 1's Grafana
  (`lanes/infra/20260930T1908Z-reply-from-pouw-node2-spare-capacity-and-metrics.md`) is superseded by the one-pool ruling. Nothing
  more is owed.
- **For the research coordinator:** nothing beyond the open merge requests. For circuits and proofs: nothing. The sampled-proofs
  circuit stack (#367, #372, #380, #391, #423) was held by root and is now @proofs' (`note:20260930T2002Z-handoff-from-proofs-state-request`).

### A5. Plans

The next three moves for PoUW:

1. **Close v2-hot.** Get GPU 3's CPU check in. If every block is under the new floors, v2-hot holds at 0.371% with no charge:
   have bc-3006c44a and bc-b58c6093 restate the row, the assessor rate it, and bc-824e54a2 unhold M2b. Otherwise publish the
   derived charge at 0.689%. Then release the held per-word draw scoping and the full-catalogue Δ recompute.
2. **Make the decode headline honest, and land it:**
   - Run window 6 (#593's CUDA graphs) now.
   - Then fix 12 (both arms under graphs) and fix 8.
   - Then window 7 (the `s,one` forms, once GPU 1's gate passes).
   - Take `-h2` into the served path the moment Daniel says yes.
3. **Unstick the merge path and the ratings:**
   - Ask the research coordinator for a train with #449 → #548 → #534, #491, #567 and #577, each re-checked on `b1c77be0`.
   - Finish the c_L pin and B-OVF in #556, then #580, so the FP4 small-n flag lifts and the FP4 grant can move.
   - Bring the assumptions table up to date.

Utilization: infra owns both nodes now. Our part is keeping bc-2aa33ad8's queue deep (≥ 8 GPU-h of useful fill, CPU fill, and
the node-1 overflow list). The last hour measured was 78% busy (18–19Z), against the target of ≥ 95% busy with ≥ 90% useful.
Infra has frozen `docs/pouw/compute-plan.md`, and node2-ops' log is `lanes/node2-ops/ops.md`.

### A6. Traps

- **Worker status files lag the server.** For example, the "2 of about 18 forms" fact went stale within the hour. Read
  `server.md` newest first (pinned items on top), then the worker's file.
- **γ has three bases:** "as written", "statement cast 8" and "packed". The binaries run the packed cast, so the panel publishes
  packed only after GPU 1's binary check. Quote the basis with every γ.
- **Decode ratios move with host speed:** eager FP8 fell from 17.8 to 14.7 ms and decode went from 3.94× to 4.15× with no
  Pearl-C change. Always publish the kernel-time ratio beside the eager row.
- **Timed windows:** CPU load biases decode by up to 1.35%. Guests are frozen in windows, but a CPU-heavy job of ours can still
  hurt. Keep `gpu-lease`'s interface, and don't touch the freeze list before 7 Oct.
- **The fill runner:** a job that holds a GPU through a CPU phase counts as leased-idle. Prepare outside the lease.
- **Stray agents:** six stray ids appeared on 30 Sep (`server.md` pinned 11:52Z and 11:58Z). Ignore anything written or pushed by
  an id that isn't on the roster.
- **Secrets:** a Nebius key fragment may have shown in two worker terminals (Daniel was told; rotation is his call). On this VM,
  `env | cut` printed fragments of a multi-line variable. List names with `compgen -e`, never `env`.
- **The store is a slow network mount:** a scan of `internal/` takes over a minute. There is no rsync on these VMs; use `cp -a`.
- **Node 2's hard stop is 2026-10-07T14:55Z.** The headers of `server.md` and `docs/pouw/rtx-pro-plan.md` still give the old
  2 Oct stop.
- **Stale draft states:** drafts #449, #548 and #534 were "ready to merge" by note, but GitHub shows them as drafts. The
  research coordinator goes by the notes and `check`, not by the draft flag.

### A7. The old coordinator's machinery

- **Timers:** `pous-inbox` (about every 15 minutes) and `pous-overnight-driver`.
- **Slack:** it is subscribed to #agent-coordination (since 19:30Z; the subscription expires 2026-10-03T19:30Z) but has no Slack
  token, so its answers go to `lanes/infra/` or here. Daniel's 19:44Z ruling (a Slack relay through the docs-site broker) should
  let running coordinators post without a relaunch.
- **Approvals:** these now go to Daniel through `#approvals` buttons (19:33Z ruling).

---

## §B. For @memory-accounting (bc-15ada664): PoUS (summary; full reply in `lanes/memory-accounting/` by 21:30Z)

- **PoUS has been paused since the overnight run** (Daniel: PoUW only). Nothing of it runs on GPUs, and there are no PoUS pods.
- **Its five paused agents** are bc-13eada34 (the band MVP and harness), bc-61023cab (efficient POUS cryptography, P2),
  bc-87c3b40e (band v6 names and fibers), bc-4b3abaed (P3 concrete-H at 14 GB) and bc-c0ee31ee (the public-encoder variant).
  bc-22298e90 is the Lean red team, shared with PoUW.
- **Its PRs:** #474, #460 and #463 are paused (the red team gave NO-GO on two small P2-arm fixes). #428 and #431 are on `main` through
  Lean train TLR; they show open only because of a later merge commit. #473 is ready and queued by root. #573 is compute's.
- **Its store is this same Project store**, so the tree `art:8bd64630…42e9` covers it. Your spec's items 1–6 get their full
  answers in your lane.

## §C. For @network-accounting (bc-ecea50f6): network timing (summary; full reply in `lanes/network-accounting/` by 21:30Z)

- **bc-6b78649f** (IDLE since 15:34Z) proved the timing-channel capacity. #461 (the network-timing Lean package, 31 pinned
  theorems) merged at 15:07Z in Lean train TLS.
- **#326** (the warden reference) is open. Its recorded check `r20260930-151146-adaf` ran on base `2c4101bf`, which main has
  since left 62 commits behind, and its merge request is `note:20260930T1535Z-handoff-from-network-warden-326-merge-request`. Your
  note of 20:03Z has the premerge facts.
- **Daniel's only network ruling on record:** the 100 ms ingress bucket is good enough for now (29 Sep 00:45Z), and the package
  is named `network_warden`.
- Items 1–7 of your spec get their full answers in your lane.
