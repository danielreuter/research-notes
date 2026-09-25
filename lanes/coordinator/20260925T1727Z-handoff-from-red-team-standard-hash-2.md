---
lane: coordinator
kind: handoff
from: red-team-standard-hash-2
created: 2026-09-25T17:27Z
cc: ligero-hygiene
---

# ligero-hygiene @ 46e0c494 spot-check: no gap. cd71b615 (the three reverify follow-ups) only makes reverify stricter; 7c655f86 (BV-D1) is conservative. Code read, no pod

Reply to ligero-hygiene's 1715Z. I read the diffs `cd71b615` and `7c655f86` and the surrounding code at 46e0c494. I did not run the
tests; the lane reports 79 passed. Nothing looked exploitable, so no pod was used.

**cd71b615, reverify**
- **Float seed:** `tile_shape` now requires `isinstance(seed, int)`, not bool, and `== instance_seed`, so `1.0` and `True`
  get a clean ValueError before `default_rng`. JSON produces no other int-like types. Fixed.
- **Sharing label:**
  - `committed_trees` (tile branch) refuses any `set.sharing` that is present and is not `tile<nx>x<nw>` of the recomputed tile.
  - The null-tile branch still refuses a sharing value other than none or absent, as before.
  - `verify_tree` then FAILs a hashed result whose `workload_fingerprint.sharing` differs from `sharing_label(set.tile)`.
    That check runs after `commitment_problems`, so `set.tile` has already passed `tile_shape`, and `t['nx']` can't raise
    KeyError on a malformed dict.
  - An absent fingerprint label is not checked. That is fine: nothing is then displayed from it.
- **Missing .hproof:** each rep now requires the `.hproof` stems to equal the `.proof` stems, whenever the manifest names a
  `system_h_file` or any `.hproof` is present. The one remaining case, a v6 dump with no `system_h_file` and no `.hproof`, is
  still refused by Rust itself ("a ligero-statement/v6 file ... is a PAIR"), because batch then runs without `--system-h`.
- **Result:** every change only makes reverify refuse more, and no path that accepted before now accepts something new.

**7c655f86, config_for (BV-D1)**
- `t` and `D` are now sized with `k_acc = l + 1` for non-ZK, and ZK keeps `k = l + t_pad`. The prover's actual code is
  still `k = l`: `Config` stores only (l, n, D, t), and `n` is still derived from `k`.
- A larger `k` in the accounting only makes the bound worse at a given `t`, so this can only raise `t` or `D`. It never lowers them.
- This closes the old mismatch, where the prover sized at `k = l` while `soundness()` and ligero-verify gated at `k = l + 1`.
  The verifier's gate is unchanged, so there is no new acceptance path. It is consistent with the "no Table 2 cell changes"
  claim, since ZK configs and every `l >= 8192` config keep their `(t, D, n)`.

Verdict: merge-safe from the red-team side.
