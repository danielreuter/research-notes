---
lane: vllm-rf-b1c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T19:55Z
---
# REOPENED: main gained a second "one challenge module". Merge main and reconcile before your merge request

`1fd7e9dc` no longer merges into main (`7da00370`; b4 is in). Main now has PR #29's commit `948a9c7e` ("one challenge
module on verity.randomness", Daniel's decisions 25–27). It adds `verity_vllm/commit/challenge.py` (`LEGACY = True`,
`stratum_picks`, `replay_key`, `challenge_positions`, `identity_picker`; vectors in
`tests/commit/challenge_legacy_vectors.json`, tests in `tests/commit/test_challenge.py`), and it edits
`check/replay/sampled_replay.py`, which you delete. Conflicts: that modify/delete, `tests/lint/test_p03_one_evaluator.py`,
`allowlists/p03_one_evaluator.json`, and `tests/lint/_imports.py`.

**Coordinator's call:** there is one challenge module, and it's `commit/challenge.py`, the owner-decided one on
`verity.randomness`.
1. `git merge origin/main`.
2. Port `948a9c7e`'s `sampled_replay.py` hunks into your split modules: `sample()` takes `key=` and draws through
   `CH.stratum_picks`; the challenge-seed derivation goes through `commit.challenge`.
3. Move your `check/replay/challenge.py` derivations (`root_seed`, `challenge_seed`, `kernel_check_seed`,
   `reference_rows_seed`, `case_seed`, `generator`, `stream`) into `commit/challenge.py` under `LEGACY`, **byte-identical**.
   Both `tests/check/test_challenge_seeds.py` (your pins) and `challenge_legacy_vectors.json` must pass unchanged.
   Delete `check/replay/challenge.py`, point the importers at `commit.challenge`, and make P03's RNG owner set only
   `commit/challenge.py`. If moving everything is more than about an hour, keep a thin
   `check/replay/challenge.py` that only re-exports from `commit.challenge` (no generator of its own), and say so.
4. `_imports.py`: take main's side, then re-add any `LAYER` lines of yours.
5. Re-gate: lints and gate (b), head against base = main `7da00370` (or later) on one cpu pod (`vyv-rf-b1c-cpu`), plus
   **#101 on an L40S** (the sampled-replay picks, strata and by_family digests equal to the record: 1374 picked of 46558,
   seed `8853214064722388274`). Use the no-waiting rule while the gates run.
6. Then send a new merge-ready handoff. Budget: $6 more (b1c is at about $4.2 of $10). This is still the 4 PM goal; it will
   likely land a little after.
