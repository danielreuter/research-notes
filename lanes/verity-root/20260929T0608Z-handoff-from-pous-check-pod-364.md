---
id: 20260929T0608Z-handoff-from-pous-check-pod-364
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: request a CPU pod for #364's recorded check; #372 stacked on #362

**Request.** Approve one CPU pod, `vy-pous-check364`, for the recorded check of [#364](https://github.com/danielreuter/verity/pull/364), the PoUW sampled-proofs circuit.
- **Terms:** the same as #312/#315's check pod. At least 64 GB RAM, about 16 vCPUs, about 100 GB disk, no GPU. Cap $1.50, pod maximum 2 h, dead-man timer as the first command, your fleet guard on the prefix. No launch under a $95 balance, and no relaunch.
- **The run:** `uv run python tools/check/check.py --record --on <pod>` at #364's head, now `df4a2496`. Lean deps come from the mirrors `check-pod.sh` already uses. #364 changes nothing under `backends/flock/` and no Lean file, so `lean-agreement` is skipped by name.
- **Timing:** we'll launch only after our red team's build review of #364 comes back (in progress). A GO WITH FIXES would move the head, and we don't want to run the check twice. The head we run will be the one in the launch note.
- **Already passing, unrecorded, at `df4a2496`:** `repository` (17 passed, 1 skipped), `verity-pouw` (88), `verity-circuit-check` (21), `verity-pouw-benchmarks` (7), `verity-flock` (341 passed, 10 skipped), and `circuit-check --all` (1,092 targets, no new failures; the one known failure, `ScaledMmFp8Block_v1`'s recompute, predates #364).

**Also: [#372](https://github.com/danielreuter/verity/pull/372) (draft)** is #364's plan on your law `work`, stacked on #362 with #364 merged in.
- **Strata:** one per template, which is how #362's verifier derives them. #364 on its own had two, which #362 would refuse.
- **Work table:** it emits #362's `--work-table` and law object, and turns a verifier-issued draw into a plan by adding the closures.
- **Agreement:** on five small calls, `flock-verify draw --work K` derived exactly the plan's law object, and the plan accepted every draw it issued.
- **K:** 27,713 is now a code constant, recomputed exactly. The 70B window draws 27,715 tiles once the per-stratum ceilings are applied, for 147.0–150.2 T.
- **Check:** #372's own check needs `lean-agreement`, because it carries #362's `backends/flock` changes. It runs when #362 is ready.
