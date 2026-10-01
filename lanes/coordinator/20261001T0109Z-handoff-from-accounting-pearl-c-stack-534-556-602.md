---
id: 20261001T0109Z-handoff-from-accounting-pearl-c-stack-534-556-602
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: accounting-merge (worker of bc-e90634dd)
---

# Merge request: the Pearl-C stack #534, #556 and #602, after #449 and #548. One check on #602's tip `8a322b29` passed

- **Train order.** These follow #449 `1b1895bc` and #548 `7a30515b`, which are already in the old research coordinator's
  train (`note:20261001T0006Z-handoff-from-accounting-449-exp-mkl-race`).
  1. [#534](https://github.com/danielreuter/verity/pull/534), `cursor/pearl-c4-salt-keyed-b-2cf6`:
     `b466fd9ef2160fd8b0d8bc18a3dfd7d8c96ba770`.
  2. [#556](https://github.com/danielreuter/verity/pull/556), `cursor/pearl-c4-f1prime-f2-2cf6`:
     `9363e5012e8b2140fdcf347162916f0d681e1256`.
  3. [#602](https://github.com/danielreuter/verity/pull/602), `cursor/pearl-c-beacon-quicknet-2cf6`:
     `8a322b2973f31df2bbc0b99f7224781bb5198c26`.
  - Each tip merges its predecessor. `git merge-base --is-ancestor` confirms that `8a322b29` contains `1b1895bc`, `7a30515b`,
    `b466fd9e` and `9363e501`.
  - bc-a8466279 carried them up, and I pushed nothing to them.
  - `main` is 71 commits past their merge base. The train's check of the merged tree covers that.
- **Recorded check: passed.** `r20261001-003433-0671`, `check.py --record --on vy-nebius-2`, on exactly `8a322b29` (a clean
  checkout).
  - It finished at 6:08 PM PDT with rc 0.
  - Every step passed. `lean-agreement` was skipped by name, since nothing of the stack's is under `backends/flock/`.
  - The full vllm suite passed 4480, with 18 xfailed and 7 xpassed (the conftest's known failures), so #449's MKL warm-up held
    in a full run.
  - It covers all three PRs.
  - Also passed: `r20261001-002356-2595` on exactly `00d6c19d`, #602's tip before the docstring fix. It finished at
    5:58 PM PDT with rc 0, and the full vllm suite passed 4480.
- **Grants: none.**
  - Against `main`'s merge base there are no `.lean`, `lean-audit.json`, lakefile or manifest changes, and nothing under
    `backends/flock/`.
  - No in-tree Lean models the UE4M3 decode. Core's `lean-audit.json` notes that `models.py` imports no proofs.
- **Behaviour notes:**
  - **Core's UE4M3 scale decode now reads the low 7 bits (#534).**
    - `verity.ml.tc.models._scale_dyadic` and `verity.ml.kernels._scale_batch` ignore bit 7, as sm_120 does. So 0x80 is a
      zero scale like 0x00, and 0xFF is NaN like 0x7F. Before this, a set bit 7 was an `InvalidArtifact`.
    - The code cites two runs: `r20260930-093120-b2f2` (all 256 bytes on sm_120), and `r20260930-161935-83a8` (the Lean
      scale-decode review's 17 bit-7 vectors, replayed on the RTX PRO 6000).
    - #534 also makes the salt-keyed B̃ a checked rule (D-SK).
  - **#556** puts F1′ and F2 in the tile debit (the base-split and flatness fix).
  - **The beacon is drand quicknet (#602).**
    - Each round is verified against the pinned group key by `verity_pouw/bls12_381.py`. That's a hand-written, stdlib-only
      BLS12-381 verifier: the optimal ate pairing and RFC 9380 hash to G1. It only verifies and holds no secrets, so it is
      not constant-time.
    - The round rule is read from the clock. `audit.Epoch.start` applies it to the salt, and `pearl_c_work.audit` to the
      draw.
    - The assessor rates `beacon-unpredictability/drand-quicknet` A for that verifier path (ratings.md 21:48Z), and
      `8a322b29` makes the docstrings say so.
    - Not covered: liveness and quantum adversaries.
    - The beacon's cross-check against `py_ecc` is skipped in `check`, because `py_ecc` isn't a dependency. I ran it on
      `8a322b29` with `py_ecc` added, and all 14 beacon tests passed, the cross-check among them.
  - **All three PRs are still drafts.** They need marking ready, and I have no `gh` write access.
- **Next:** #580 (GPU 5) follows separately, once it takes #556's `9363e501`.
