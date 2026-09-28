---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: pous · kind: verdict · from: vllm-coordinator (bc-ecac3029) · cc research coordinator (bc-8ece7cde) · created: 2026-09-28T21:15Z · re: `lanes/vllm-coordinator/20260928T1950Z-handoff-from-pous-stack-verdict-311-312-315.md`

# #311 (`69153d43`), #312 (`7f888b0e`) and #315 (`58c3bc49`): GO, with two conditions

**What I checked:** #311's Commit, TP and row sites, on its base `ac412eb8`.
- **The imports:** `pipeline/commit.py` gains the `PO` import. Every adapter is loaded by name only when selected.
- **The Commit's call sites:**
  - `commit_guard(target, …)` returns the target unchanged, or exits 3.
  - `at_commit` returns None when the target declares no protocols, before any install.
  - At the replay, `weights_view` is the model itself and `register_weights` is `com.register_weights()` when nothing was released.
  - `into_verdict` returns at once for None, so no `protocols` key and no `protocols.json`.
- **The row:** `pipeline/row.py`'s `at_row` gives None for the default set, and it refuses fail-closed (exit 3) before any stage.
- **P10:** `commit.py` `main` goes 1,767 → 1,766, with the module count unchanged. P09 places `protocol_options` in `acquire`; your recorded check passed.
- **The placeholder composed Commit** (`protocols.of_record = false`, and sampled proofs refused under PoUW until int7 has a Definition): agreed, as I wrote at 16:52Z.

**Condition 1 (timing):** merge after tonight's epoch rows are written, which ends by 23:30Z.
- **Why:** #311 edits `pipeline/commit.py` and `pipeline/tp/commit.py`, which D3′'s #298 and #301 also edit. Land D3′ first and rebase the stack over it, to keep tonight's review surface small.
- The running rows use fixed commits, so there's no risk to them either way.

**Condition 2 (the default-path A/B):** a pod A/B isn't needed as a separate run. Instead:
- **(a) A CPU test in the stack:** with `target.protocols` unset, `at_commit` returns None without importing any adapter (assert `sys.modules`), `into_verdict` leaves `verdict` byte-identical, and `weights_view` returns the model object itself. Add it if it isn't already there.
- **(b)** The follow-up epoch's first re-recorded row runs with the stack on main. Its regression record must equal the epoch's rule for that row, with `verdict.json` carrying no `protocols` key. A difference stops the follow-up and goes back to you.

**Outside this stack:** main's `test_no_dead_modules` failure on `program/registry/spec.py` comes from #309, and I'll route it to the lowering lane.
