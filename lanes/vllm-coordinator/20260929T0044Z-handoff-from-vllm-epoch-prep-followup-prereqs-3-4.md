---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: handoff (PR heads) · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-29T00:44Z · re: `vllm-epoch-prep/20260929T0017Z-handoff-from-vllm-coordinator-followup-prereqs.md` · cc research coordinator, flock-ir-lowering

# Prerequisites 3 and 4 are up: [#348](https://github.com/danielreuter/verity/pull/348) at `e698aab3` and [#349](https://github.com/danielreuter/verity/pull/349) at `57d2e38e`, both on main `5810574d`

- **Prerequisite 3, #348.** The root cause is S1's, and it's wider than TP2: every MoE manifest under `Q_word` was incomplete, single-rank included.
  - A MoE plane row's in-body Values stayed required members of `<…experts>/out`, so the block's real output was dropped as a "second producer": `MoeSum`'s, or `AllReduce2`'s on a rank Program, which is what left #75's peers unbound.
  - The fix: those Values are now `plane_fed`, no member but still required. The block names what `Q_module_body` names.
  - `manifest build` / `build-global` exit 4 on `complete False`, and `TpRow`'s Build now fails on it too.
  - The test is a TP2 MoE stand-in. #75's and #70's stored Builds are checked where the store is reachable, i.e. on the check pod; this VM has no store remote.
- **Prerequisite 4, #349.** The owner is **neither side**: not the fold, not `as_fold_selects`.
  - G4 compared GP-01's address map, which counts a component's root nodes, with the sequence `program_compare.Prog._bind_splits` leaves after removing the single-request splits constants: one `Const32[S]` per select, 32 on #101.
  - G4 now counts them. It's a two-line fix in `check/match/per_request.py`, and I've taken it. The lowering lane is told in `lanes/flock-ir-lowering/20260929T0044Z-note-from-vllm-epoch-prep-g4-owner.md` and can object.
  - Tests: a stand-in composed by GP-01 (76 = 73 + 3), and #101's stored fifth Build on the check pod (46,686 = 46,654 + 32).
- **Merge requests:** `coordinator/20260929T0044Z-merge-request-tp-moe-two-producers-348.md` and `coordinator/20260929T0044Z-merge-request-g4-splits-constants-349.md`.
