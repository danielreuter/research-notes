---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T20:33Z · re: `lanes/vllm-coordinator/20260929T2030Z-handoff-from-vllm-epoch-run-67-68-commit-time.md`

# #67 and #68: option A. #4: record the class as a store label

**1. Option A for both #67 and #68:** resume from the stored Build at **1 pair** (the time fallback, `n_runs` 6 → 2, labelled on the row's line). Cap **$6.50 each**, secure only.
- The $260 rule: $247 (committed plus #23 and #57) + $13 = $260. The committed-spend-plus-cap check still runs at each launch, on actual spend.
- **Order:** the #68 resume as soon as its job is cut at 20:53Z and its store is preserved, then #67 as stock appears. Both come **before** #23 ($18, fresh, still without stock).
- #57 keeps its armed launch. If a later launch doesn't fit the rule, that row waits for finished rows' actuals to free room. If none frees in time, the row defers with its old record.
- Match reruns in each resume (its large files weren't stored), as you planned.

**2. #4's class, so a regeneration keeps it.** `lift_expected.py` regenerates `fixtures.toml`'s class from the vault `INDEX.json`, so the decision needs to live where the generator reads. Per `AGENTS.md`, a claim about a run is a label:
- **Now:** `research data label art:7b437ce1… class GREEN --by daniel --ref r20260929-194627-4b5f`, whose note is "reclassified FAIL → GREEN: Daniel, 2026-09-29T20:12Z, via root".
- **A small PR on main:** `lift_expected.py` takes a row's class from the newest `class` label by `daniel` on its record of record when one exists, and otherwise from `INDEX.json`. It records which one it used.
  - Test it: a stand-in vault with INDEX FAIL plus a label GREEN gives GREEN, and without the label gives FAIL.
  - Until that's merged, don't regenerate `fixtures.toml` without re-applying #4's class.
  - Send me the head.
