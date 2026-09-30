---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
id: 20260930T2020Z-handoff-from-coordinator-state
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (the research coordinator, bc-8ece7cde), to proofs (bc-8416bc72)
---

# @old-circuits-and-proofs → @proofs: state at 20:20Z, Sep 30

Answers `lanes/coordinator/20260930T2002Z-handoff-from-proofs-state-request`. I keep running the merge trains until the Job queue has run one full train; everything else in the proof charter is yours.

## 1. Workers I run

Only four agents are mine: the ones I launched today. The charter's other workers are root's lanes, or report to their own coordinators (vLLM, POUS, infra). I don't run them, so I can't report on them.

| Id | Lane | Doing now | State |
|---|---|---|---|
| bc-62b7c7a1 | `backend-sweep-2` | Llama-3.2-1B sm_120 shapes as dispatcher ready files on M0's #554 build; then (a) the 460 sampled units per passing vLLM deployment and (b) whole-row proving for K = 2,048 (≈14 GPU-h; stop at 5% agreement with the extrapolation), both approved by root 19:04Z | running |
| bc-5be66fb3 | `assumption-sweeps` | first 8-die invariance pass done (all identical); waits for red-team-vllm-semantics' next job list | idle, finished its task |
| bc-70706bc3 | `node1-dispatcher` | the agent has finished; its loop `dispatch.py` keeps running in tmux `node1-dispatch` on node 1, as `research` | loop live, agent idle |
| bc-8a7dff1c | `flock-v4-design` | handed M0 attempts A and B; M0 found both duplicates of its v3 #14 and #16 | finished; hand back or stop |

I'd move `flock-v4-design` into your theory work or stop it. The other three are infra's or yours now.

## 2. Open PRs in the proof remit

| PR | Head | Grants | Blocks | Train |
|---|---|---|---|---|
| #250 (MUFU/`div.full` to core) | `19cf12bc` | vLLM grant (18:14Z). Red-team grant carried forward by root from `da4261e5` by blob identity: `backends/flock/` is unchanged, `tail_pieces.py` is blob `dd70e064` in both (`lanes/coordinator/20260930T1902Z-note-…-grant-carried`) | check passed with `lean-agreement` (`r20260930-193729-72ba`), but its attempt failed to publish (custody manifest meta 559 KB > 256 KB, listing 3,332 undeclared agreement files). Re-publishing now; the gate needs the attempt | TCP, next to land |
| #367, #372, #380, #391 | — | — | carry `hold`; stay open as drafts; closing them waits for Daniel | none |

Landed today in the proof remit: #452, #490, #500, #511 (TLO); #513, #514, #521, #526 (TLP); #519 (TLQ); #428, #431 (TLR); #461 with network_warden's lean-deps pin (TLS); #560 (TLT); #228 (TCN).

## 3. Trains

- **`main`:** `b1c77be0` (TVR, #594, pushed 19:42Z).
- **Stack:** TCP = `b1c77be0` + #250, check `r20260930-193729-72ba`, all steps passed, expected merge `73eee493`. It lands once its attempt is in the store.
- **Queue after it:** #557 (back with the vLLM coordinator: its TP2 MoE manifests need re-pinning); #592 (Slack skill + CLI; no grant at `b5e3df46`); POUS #449 + #548 then #534, and #433 then #471 (all waiting on vLLM grants; #449 has no merge request; #534 needs retargeting to `main`).
- **Machinery:** node 1 slots a, b and c (`check-{a,b,c}.lock`, CPUs 32–63, 64–95, 8–31), each with its own per-test cache. Each train stacks on the tip of the one ahead, so #509 lands it without a re-check. `/tmp/launchv.sh` on my VM, recipe in `lanes/train-speedup/20260930T0625Z-handoff-from-coordinator-launch-recipe`.

## 4. Promises owed

- Land #250 (TCP) once its attempt publishes.
- Cut #592 once it's granted.
- Cut #557 once the vLLM coordinator re-pins it.
- The POUS trains in §3, once granted.
- Tell the train-speedup lane when node 1's slots can share one per-test cache again (after their race fix).

## 5. Plans and the Daniel items

These docs are in verity-root's store. I can't write to your Project store (`bc-7f347b4b…` isn't one I can access), so the decision points are summarized here.

- **GEMM-hash levers** (`gemm-hash-cost-plan.md`): these rows need Daniel.
  - 4: BLAKE3 rows (636 → 306 per byte). Needs the row scheme, hm96, every root and the post-quantum margin.
  - 5: hash once per statement or session. A new mechanism of 5b's class, which was ruled out on Sep 28.
  - 6: a C matrix in the relation. Needs the proof relation.
  - 7: smaller items (≤1.05×); hm96 is already agreed.

  Row 1's CPU reference is draft #328.
- **Lean organization** (`lean-organization.md` §7, decisions for Daniel):
  - the definition moves;
  - retiring the old `#print axioms` lists (the three PRs it waited on have landed);
  - POUS's code home;
  - a nightly `--fresh` machine;
  - build caching for `check`;
  - computed status.

  Core-only proofs now live in `packages/verity/lean` (decided Sep 30; first was #490).
- **ZK:**
  - `zk-proof-public.md`: a complete paper proof, granted by the red team with three conditions, all closed. The adaptivity step and coin-commitment binding are proved in Lean (#227, #239, #245). Several tables per session is #306.
  - `zk-proof-private.md`: draft 4 for Daniel. What is public: $N$ and $k$ exactly, other sizes only to their power of two.
- **Closing #367, #372, #380, #391:** waits for Daniel.

## 6. Pods and spend

- **RunPod:** none of mine. All check pods are terminated, and nothing is running under `vy-coord-` (line $325/day, expires 2026-10-06T00:00Z).
- **Node 1:** my checks run on node 1's three slots; its deadline is 2026-10-07T15:00Z.
- **Spend ledger:** $460.44, a label only. The budgets guard enforces the lines, with the RunPod balance floored at $25.
