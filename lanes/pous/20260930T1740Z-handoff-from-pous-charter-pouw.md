---
cursor:
  subagentId: "bc-27b53f62-e217-5187-8bc2-6e76e43f7085"
id: 20260930T1740Z-handoff-from-pous-charter-pouw
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: pous
---

# Charter: the pouw coordinator (PoUW on the RTX PRO 6000)

For the pouw subcoordinator in Daniel's one-Project structure (`note:20260930T1725Z-handoff-from-pous-coordinator-project-restructure`).
State as of 30 Sep 17:35Z. Bare paths are in the pous Project store, `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`;
`note:` ids are research-notes; `#n` is danielreuter/verity. Infra (node-2 ops, the one-cluster design, the live console) is
handed off separately: `note:20260930T1740Z-handoff-from-pous-charter-infra`.

## Goal

- **PoUW on the RTX PRO 6000 (sm_120), FP8 and NVFP4, on vy-nebius-2.** γ ≤ 1% under named, red-team-rated assumptions is firm,
  and each protocol is Lean-proved under them. Then hillclimb slowdown toward 1×; 5× is only the pass line. The headline is at
  8,192³ with prefill (m = n = k = 8,192) and decode (m = 32) reported separately. A new protocol version is its own line.
  Daniel's objectives: `docs/project-context.md` § "Overnight objectives (Daniel, 30 Sep 04:51Z)".
- **PoUS is paused** (the same objectives). Its lanes are idle and nothing of it runs on GPUs.

## Headline (17:30Z)

- **Panel:** `docs/pouw/panel.md`, rendered from `internal/pouw/panel/` (`attempts.jsonl`, `lines.json`, `panel.py`).
- **FP8 (Pearl-C sm_120):**
  - γ as the kernel runs: v1 0.779%, v2 0.647%. Chain-only it's 1.226% and 1.121%, and both drop under 1% once GPU 1's kernel
    reaches the measured 8.72 wide-store cast.
  - v1's wall-time γ is 0.74–1.34%. GPU 0's rewrite-mix probe decides it: v1 fits 1% if the mix runs at least 1.042× slower.
  - The best slowdowns are still estimates: v1-h1 1.79× prefill and 3.8× decode, v2-h1 1.75× and 3.74×.
- **FP4 (Pearl-C4, NVFP4 only):** γ 0.717%. It has been unflagged at C since 16:55Z, when the verifier began enforcing
  F1′ + F2 + R1 and attempt 21 became a verified row (`internal/pouw/rtx-pro/server.md`, 16:55Z).
- **Hashing:** on GPU 1's real call, `-h3` costs 1.21× prefill and 1.25× decode, against `-h2`'s 1.22× and 1.38×
  (`docs/pouw/hashing-accounting.md`).
- **MVP end to end:** Llama-3.1-8B in vLLM on Pearl-C v1-h1, verified. It runs 1.71× prefill and 3.94× decode over stock FP8.
  WikiText-2 perplexity is +1.43% over BF16, against FP8's +0.62% (`docs/pouw/mvp-e2e.md`).
- **Assumptions:** no line's weakest rating is D. FP8's weakest is the unnamed beacon and FP4's is the new fix, both C. MXFP4 is
  a D contrast line only (`docs/pouw/assumptions.md`).
- **Proofs:** M1 and M2a are merged, so every FP8 in-loop headline cites a merged theorem. M3 (RowSeed) and M4 (the FP4 scale
  decode) are in review. M2b (v2-hot) is held on its first-atoms grant (`docs/pouw/security-proofs.md`).
- **GPUs:** 38% busy 16–17Z. The limit is GPU work the lanes have written, not capacity (`docs/pouw/compute-plan.md`).

## Open decisions for Daniel

1. **Name a beacon.** drand quicknet is recommended; the missing beacon is why every line is rated C.
2. **Per-row seeds (`-h3`).** Cheaper decode at no γ cost, but it loses the debit cap as a second defense
   (`docs/pouw/hashing-accounting.md` §5.4; `note:20260930T1208Z-note-from-hash-cut-change3-to-daniel-decision-h3-vs-h2`).
3. **Registered weights: keyed rotation or a curated list.** The recommendation is rotation for FP8 now, and for Pearl-C4 once
   F1′ lands (`docs/pouw/approved-weights.md`).
4. **Not ripe yet:** V/O rotation plus head interleave (`docs/pouw/keyed-transforms.md`), once the 7B and 70B perplexity evals
   and the assessor's rating are in.

The older questions are in `docs/project-context.md` § "Morning questions for Daniel"; the sources don't say which are still open.

## Agents

Status at 17:30Z: RUNNING means mid-turn, IDLE means waiting to be resumed. The coordinator today is pous,
bc-b729c175-2ef6-418e-98fe-10896709028b (RUNNING); it has proposed becoming the pouw coordinator.

| Agent | Status | Owns |
|---|---|---|
| **bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d** | RUNNING | **Sub-coordinator, RTX PRO:** the panel, node-2 GPU work and the workers below. Channel `internal/pouw/rtx-pro/server.md`; roster `internal/pouw/rtx-pro/workers/` |
| **bc-824e54a2-2192-5eb8-8334-4f9105631b51** | RUNNING | **Sub-coordinator, new crypto:** the PoUW Lean store and milestones M1–M4 (`docs/pouw/security-proofs.md`, `docs/pouw/new-crypto.md`) |
| bc-e6a46970-b6ef-5738-af64-182b143075d4 | IDLE | GPU 0: FP8 capture, the rewrite-mix probe |
| bc-18346d9c-4bfb-56af-ad79-0d17e73bb44b | RUNNING | GPU 1: the Pearl-C sm_120 kernel (casts, hashing folds, v2-hot) |
| bc-7442ca43-9389-5653-ae57-2cbf499a9569 | RUNNING | GPU 2: hashing, and the one-day self-recording pilot |
| bc-0f3f8a2f-3024-5bae-bda9-8e3836b9cb92 | IDLE | GPU 3: FP8 attacker, v2-hot width floors |
| bc-36186951-83fc-53b6-87de-fa584ddf9ff9 | IDLE | GPU 4: FP4 capture, scale-decode vectors |
| bc-71c6ab78-d098-5f45-8c08-337ac2c83084 | RUNNING | GPU 5: Pearl-C4 design and verifier (#580) |
| bc-dbc19788-573d-5ba4-b3b2-d6551c1c60ef | IDLE | GPU 7: FP4 attacker |
| bc-0de2d624-783f-5e35-9b57-19c1627bd2f2 | RUNNING | The bench harness (#491) |
| bc-6da61042-1b56-5e51-964f-9ae86e909da4 | RUNNING | Harness helper (#588) |
| bc-fb55a759-0d1c-55f4-a2da-04aadde30be9 | IDLE | Plain FP8 and NVFP4 mainloops (#543, #570) |
| bc-69c09d42-976d-5e37-80f2-df43613020ed | IDLE | The assumptions table |
| bc-d7d4b0d1-1778-5220-abe0-789e3131dcab | RUNNING | Independent assessor (`internal/pouw/red-team/ratings.md`) |
| bc-3006c44a-5462-55f5-9ce2-722e3ecca818 | RUNNING | Cheap binding and γ theory (`docs/pouw/cheap-binding.md`) |
| bc-b58c6093-e25d-5e1f-817b-9b7725e0e696 | IDLE | TT_OUT restatements for sm_120, v2-hot |
| bc-a8466279-735b-5800-a6cf-19e3b12b2cf6 | RUNNING | Pearl-C4 domain rules (#534, #556) |
| bc-f5bf55c8-213d-5f31-8906-0b78916ecf5b | RUNNING | FP4 specialization, the Pearl-C4 censuses |
| bc-d9842080-f8c7-54a2-84bb-ba0a4b680482 | IDLE | Matmul bounds in the FP4-tile model |
| bc-876ca543-9636-59e7-ad99-0052e8cf3702 | IDLE | In-loop price twins in Lean |
| bc-22298e90-fd61-5062-a836-0b7a423cab8a | IDLE | Red team of the Lean statements |
| bc-8412d697-8e5a-51be-834a-b61a695bcc03 | IDLE | Approved (registered) weights |
| bc-6289d8b0-ad21-5f64-a446-d97206e680b2 | RUNNING | Keyed transforms; evals queued on node 2 |
| bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4 | IDLE | Hashing accounting, `-h2`/`-h3` (#475, #510, #532, #533, #537, #541, #544, #547, #549, #555, #572) |
| bc-9914c188-7567-565e-b25c-2b7015229ada | IDLE | Pearl-C kernel #449 |
| bc-dd22acf8-7690-5123-ab90-d129950f4f91 | RUNNING | MVP end to end (#540, #564) |
| bc-ccd30e80-9a35-5547-b43c-64054af776ee | RUNNING | Profiling the served MVP's slowdown gap |
| bc-f4e8ae34-77e8-5027-8012-e7892b96e318 | IDLE | The vLLM linear-site API and its migrations (#567, #573, #576, #578, #585) |
| bc-1a23b70c-8ce6-52de-9b80-c005acb94607 | IDLE | Kernel tooling and self-recording (#583, merged into #491) |
| bc-75d1b678-7ce5-5b01-a155-7dde36338030, bc-23d60f13-d4e8-52e4-8b06-ad4faa5c9924 | IDLE | The PoUW sampled-proofs circuit and vLLM protocol options, held by root (probably circuit or proof now) |

- **Handed to infra:** bc-efe47341, bc-c3ade0aa and bc-26712550 (see the infra handoff).
- **Paused PoUS lanes:** bc-13eada34-51d3-5b54-b330-070221ddc934, bc-61023cab-6d53-50c4-8e35-f47f38053ebc,
  bc-87c3b40e-c587-528c-8dfa-da14013b576e, bc-4b3abaed-5e3a-5a9d-823a-3ec326d9fbd7 and bc-c0ee31ee-703e-5bc7-bf7b-3d9af5beba8a.
- **Not PoUW, all IDLE, for the top-level to place:**
  - network timing: bc-6b78649f-a717-5744-b3d4-04b44e9386f3;
  - resource ontology: bc-e79791ab-ed15-5e19-93ab-a18898c932e9;
  - spot-check Lean: bc-e7e2bf3a-f0d8-5b5a-9714-9de87eb030a8;
  - Lean organization: bc-79934c4e-4f8e-5b94-b30b-9474fbcc01f7;
  - research-notes structure: bc-51d80f1e-a453-50ad-81ea-731440def4fc;
  - colleague handoff: bc-d3651a9e-a523-5007-9802-be1d431fdb73;
  - deployment audit: bc-f9184c6e-8fb2-5894-9934-da3d0b6bc6f8;
  - README review: bc-63c7f09e-c3a4-577c-90f0-cc091a1dd93b.

## Open PRs

Triage: `docs/pr-triage-pous.md`. All merges go through the research coordinator (`lanes/coordinator/`).

- **Merge requested:** [#449](https://github.com/danielreuter/verity/pull/449) (first in the train, then #548 and #534), [#491](https://github.com/danielreuter/verity/pull/491), [#567](https://github.com/danielreuter/verity/pull/567) and [#577](https://github.com/danielreuter/verity/pull/577).
- **Harness and bench:** [#588](https://github.com/danielreuter/verity/pull/588), [#436](https://github.com/danielreuter/verity/pull/436), [#332](https://github.com/danielreuter/verity/pull/332), [#451](https://github.com/danielreuter/verity/pull/451), [#505](https://github.com/danielreuter/verity/pull/505), [#506](https://github.com/danielreuter/verity/pull/506), [#507](https://github.com/danielreuter/verity/pull/507).
- **FP8 kernels and hashing:** [#510](https://github.com/danielreuter/verity/pull/510), [#529](https://github.com/danielreuter/verity/pull/529), [#532](https://github.com/danielreuter/verity/pull/532), [#533](https://github.com/danielreuter/verity/pull/533), [#537](https://github.com/danielreuter/verity/pull/537), [#541](https://github.com/danielreuter/verity/pull/541), [#543](https://github.com/danielreuter/verity/pull/543), [#544](https://github.com/danielreuter/verity/pull/544), [#547](https://github.com/danielreuter/verity/pull/547), [#549](https://github.com/danielreuter/verity/pull/549), [#555](https://github.com/danielreuter/verity/pull/555), [#570](https://github.com/danielreuter/verity/pull/570), [#572](https://github.com/danielreuter/verity/pull/572).
- **FP4 (Pearl-C4):** [#548](https://github.com/danielreuter/verity/pull/548), [#534](https://github.com/danielreuter/verity/pull/534), [#556](https://github.com/danielreuter/verity/pull/556), [#580](https://github.com/danielreuter/verity/pull/580), [#525](https://github.com/danielreuter/verity/pull/525), [#530](https://github.com/danielreuter/verity/pull/530), [#542](https://github.com/danielreuter/verity/pull/542), [#545](https://github.com/danielreuter/verity/pull/545).
- **MVP and vLLM:** [#540](https://github.com/danielreuter/verity/pull/540), [#564](https://github.com/danielreuter/verity/pull/564), [#573](https://github.com/danielreuter/verity/pull/573), [#576](https://github.com/danielreuter/verity/pull/576), [#578](https://github.com/danielreuter/verity/pull/578), [#585](https://github.com/danielreuter/verity/pull/585), [#389](https://github.com/danielreuter/verity/pull/389), [#433](https://github.com/danielreuter/verity/pull/433), [#435](https://github.com/danielreuter/verity/pull/435), [#462](https://github.com/danielreuter/verity/pull/462), [#471](https://github.com/danielreuter/verity/pull/471).
- **Held (the sampled-proofs circuit):** [#423](https://github.com/danielreuter/verity/pull/423), [#367](https://github.com/danielreuter/verity/pull/367), [#372](https://github.com/danielreuter/verity/pull/372), [#380](https://github.com/danielreuter/verity/pull/380), [#391](https://github.com/danielreuter/verity/pull/391).
- **Fallbacks and the older 4090/H100 work:** [#295](https://github.com/danielreuter/verity/pull/295) (NCP-FP8), [#464](https://github.com/danielreuter/verity/pull/464), [#468](https://github.com/danielreuter/verity/pull/468), [#475](https://github.com/danielreuter/verity/pull/475), [#453](https://github.com/danielreuter/verity/pull/453) (withdrawn run).

## Standing rules and preferences

- No `gh` write operations. Never push Verity's `main`: merges go only through the research coordinator.
- No access changes without Daniel's explicit yes. No live-node change without a written cutover plan brought to Daniel.
- Never print secrets: key fragments were exposed twice today.
- Message Daniel only for decisions, blockers or milestones.
- Research velocity over process: SSH is fine for interactive work.
- Agents are proactive and leave the repo better than they found it.
- Also in force:
  - `preferences.md`: balance the agent mix to the compute; vLLM goes through one interface.
  - `docs/project-context.md`: γ ≤ 1% is firm, and no security-changing choice is made without Daniel; worker models are
    xhigh, not max; no LaTeX in Markdown; notes to the research coordinator or Verity root are named `-handoff-`.
  - `docs/pouw/compute-plan.md` § "How node 2 is shared": GPU work goes through `gpu-lease` or the fill queue, and timed
    windows use `gpu-lease 8 --wait --timed` with `--no-sampler` (`server.md`, 17:27Z).

## Where state lives

- **Status:** `notes.md`. **Decisions:** `docs/project-context.md`. **Preferences:** `preferences.md`.
- **Deliverables:** `docs/pouw/`. **Panel data:** `internal/pouw/panel/`. From #491 and #583, the evidence store's
  `kernel-attempt/v1` records join the panel after GPU 2's pilot.
- **Workers:** `internal/pouw/rtx-pro/server.md` (newest first, pinned items on top) and `internal/pouw/rtx-pro/workers/`.
- **Ratings:** `internal/pouw/red-team/ratings.md`. **Lean staging:** `lean/submissions/pouw/`.
- **Research-notes:** `lanes/pous/` (inbound), `lanes/coordinator/` (merge requests), `lanes/verity-root/`, `lanes/nebius-infra/`.
- **Runs:** `r2026…` ids in the evidence store. **Node 2:** `/workspace/pouw/`, and the live page `/workspace/pouw/infra/status.md`.
- **Stale:** the headers of `internal/pouw/rtx-pro/server.md` and `docs/pouw/rtx-pro-plan.md` still give the old 2 Oct stop.
  Node 2 stops itself at 2026-10-07T14:55Z.
