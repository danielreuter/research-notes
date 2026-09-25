---
lane: coordinator
kind: handoff
from: ligero-hygiene
created: 2026-09-25T17:15Z
---

# Merge-ready: lane/ligero-hygiene @ 46e0c494 (BV-D1 fixed in config_for; live_test green; 3 tile follow-ups; conformance negatives all PASS)

- **Tip** `46e0c494` on main `239c0e28`. Report: `lanes/ligero-hygiene/20260925T1627Z-report-ligero-hygiene.md`.
- **Tests at the tip** (VM, CPU): `cargo test --release` (ligero-verify, unchanged by this lane) 69 passed; `pytest hashauth_test
  reverify_test steps_pin_test live_test` 79 passed, 0 failed, 0 skipped with LIGERO_VERIFY set. Conformance
  `test_committed_operand_negatives_rejected[dummy|poseidon2|sha256]` all PASS on an idle cpu3c pod (r20260925-164906-1069,
  art:020560e11fdb6de173a1ce65b5cc72680bc2fbfae2fa00385112d3890b3ab912): 69 s / 111 s / 901 s. sha256 is 47 full proofs
  at 41,918 rows/unit: give it a timeout of 3600 s or more.
- **Behaviour change (prover parameters):** `protocol.config_for` now sizes `t` / `D` at `k = l + 1` for non-ZK, the `k` that
  `soundness()` and ligero-verify gate on (BV-D1, now resolved). Small-l non-ZK configs gain a column or two (l = 256 at 2^-128:
  t 189 -> 190); ZK and every l >= 8192 config keep their parameters, so no Table 2 cell changes. That is what fixed
  `live_test::test_shared_pair_every_coin_from_the_verifier[None]`; the test's target was not touched.
- **Behaviour change (reverify accepts less):** a float `set.tile` seed, a `set.sharing` or result-fingerprint `sharing` label
  that is not the recomputed tile's, and a pair sub-batch without its `.hproof` now FAIL with a reason. This changes what a
  verifier accepts, so the brief's red-team spot-check applies (reverify.py `tile_shape`, `committed_trees`,
  `commitment_problems`, `verify_tree`).
- **kb fact** for whoever owns the ligero kb doc: the sha256 conformance negatives take ~15 min on 4 idle vCPUs (NTT and
  boolean witness rows dominate); 1800 s is too short on a loaded host.
- Pod vy-ligero-hygiene (hb8gfpinlwovt7, cpu3c 4 vCPU) terminated 17:11Z, about 26 min, under $0.10.
