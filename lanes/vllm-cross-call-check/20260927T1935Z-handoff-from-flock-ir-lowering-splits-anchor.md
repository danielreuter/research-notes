---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: vllm-cross-call-check · kind: handoff · from: flock-ir-lowering (bc-9916bbb1) · to: vllm-cross-call-check (bc-f7aadce6), cc the vLLM coordinator (bc-ecac3029) · created: 2026-09-27T19:35Z · re: the ground-truth audit's §6.2 fix 9 (anchor `splits`), routed to workstream 1

# Anchoring `splits`: a per-step constant on single-request programs, and `SplitsForSMS(n_live)` on a workload program

**Done on my side:** #125's keep word now follows #169 (each lane takes its own half's stop). It is merged with #169's branch, checked on #169's constructed rows, and on `main` `e40fa730`.

**The problem.** `splits` is the one prover-supplied input of #101's program with no anchor in the circuit. On `main` the Build makes it a request-owned input by design (`pipeline/build.py` `sampler_geometry`, ruling M-0169 / M-0571 (3)): S_t = `SplitsFor_v1`(|live(t)|, num_SMs) depends on how many requests are live at step t, which one request's program can't know. The Match checks it (GM-01 G6), and so does the Commit's linkage (`check/replay/linkage.py`). The circuit never does.

**Proposal:**
1. **One request (all 13 served rows).** Only #101 is stochastic, and it has one request. Its |live(t)| = 1 at every sampling event by construction (a request that stops has no later event), so S_t = `SplitsFor_v1`(1, 142) = 32.
   - Emit it as a per-step `Const32[S]`, as the fold already does for temperature, top-p and the Philox positions.
   - This is exact by construction, not by the assumption M-0169 ruled out (every request runs to its cap), because nothing else is live.
2. **Several requests (none served yet).** Derive S_t in the circuit with the registry's `SplitsForSMS<SMS>_v1(n_live)`. `n_live` is built from every request's activity values (`LStepLive` / `LIsActive`, `lifted.py`). That needs a workload-level (lifted) program, not per-request ones.

**What it changes. Yes, it's a statement change:**
- #101's program digest moves (`ccc21347…` no longer names it);
- the Commit's prescribed inputs lose `splits`;
- the linkage's splits check and the Match's G6 become implied by the circuit, for proposal 1.

Proposal 2 is a larger change: a workload program in place of per-request programs.

**What it does to the size.** With `splits` a constant, the export lowers only the chosen pipeline (the walker propagates the constant). The keep word drops from 1.45 × 10¹¹ to about 2.4 × 10¹⁰ ANDs per step, about −3.9 × 10¹² on #101 (−2.5%).

**Asks:**
- Is proposal 1 yours to land (the fold / Build), or the vLLM coordinator's call?
- Does M-0169 need a new ruling for the single-request case?

My lowering needs nothing further: it lowers whatever the program gives, constant or input.
