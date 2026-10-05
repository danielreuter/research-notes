---
id: proofs/20261005T1614Z-finding-flock-security-defs
campaign: flock
lane: proofs
kind: finding
status: done
repo: danielreuter/verity
origin: bc-e3b551b5-6835-5a58-ba91-31ab8894f651 (flock-security-defs, for the proofs coordinator bc-8416bc72)
---

# C-Flock's trusted text on Mathlib: the Goldreich–Kahan closure, `Game` on `Verity.Game`, and the closure test

**Question.** Can C-Flock's Goldreich–Kahan simulator, extractor and model build on Mathlib alone, and can C-Flock's `Game`
become core's `Verity.Game`, without weakening any guarantee? And can a test keep trusted text off ArkLib, VCVio and CompPoly
from here on?

**Scope.** Items 2–4 of the brief, narrowed by the coordinator at 19:07Z. Item 1, extracting C-Flock's spec and with it
the ArkLib cuts, is out of scope; the Lean layout move made the two ArkLib cuts it needed (15f0987a0).

**Branch.** `cursor/flock-gk-game-f651` at e70aceb44, on `cursor/lean-layout-move-c3b2` at 77b8d66bc
([#1225](https://github.com/danielreuter/verity/pull/1225)). It supersedes the earlier `cursor/flock-security-defs-95d4`
plan (steps 1–6 on the pre-move layout), which is dropped.

## Answer: yes, for items 2–4

- **Item 2.** Every `ZK/GK` module that declares a definition (`Rand`, `Extract`, `Sim` and the new `Model`) reaches no
  proof-only library through its imports.
  - At 77b8d66bc, only Theorem GK's model was tainted: it sat in `GK/Theorem.lean`, which imports `ZK.Masking`.
  - The model now lives in `GK/Model.lean`. Its reads group digest is unchanged (c93e1e93…).
- **Item 3.** C-Flock's `Game` and its operations are core's definitions, exported under the old names, and every lemma
  keeps its name.
  - Audit r20261005-202739-215a certifies that the 186 guarantees reading them say the same thing under the old names:
    181 under old names, and 5 printed differently with the same type hash.
  - Three definitions print as "changed": `interleave`, `interleaveWith` and `batchLock`. Each is proven to be the same
    term with a different, identical matcher, because Lean reuses a `match_N` only within a module.
  - The evidence: probe r20261005-214506-6f75 reproduces the old record's digests from the old modules, built verbatim and
    separately; r20261005-212921-9a05 does the same for `batchLock`.
- **Item 4.** `tests/test_lean_packages.py` fails on any trusted module (a guarantee's reads, or a named assumption) that
  reaches a proof-only library, outside `ARKLIB_PENDING`.

  | | trusted modules | reaching a proof-only library |
  |---|---|---|
  | 77b8d66bc | 525 | 191 |
  | e70aceb44 | 523 | 190 (all in `ARKLIB_PENDING`, waiting on item 1) |

## Evidence

- art:076c4db87e94ea9112098c38d75ccb0e696996e4fe3689fe9bda23adde9e6e5f: the audit run.
  - Security: PASS.
  - Proofs: the four failures the move's own audit of 77b8d66bc also has (r20261005-180406-63e4).
- art:40726cb02998e748c3b5386e519253e047ba0fa26f69e95b4883cb065e0e1aa0: every changed record, before and after, for the
  named statement reviewer.
- art:2a78bd645cc9546d13ae76c548a5d9101bdcda59a1761fdc52c2fda2578356ec: the faithful matcher probe.
- art:7647eb92b1ba32733acc8bdc53ee4d5479f06c0a4379c9a2ea05ac2e1027428e: the scratch comparison.
- art:d08da1c65da8301099b50495e7eb519811c3923bf0fe61a48110a703eac2f0cc: the probe and comparison scripts.

## Findings for other lanes

- **Lean infra / the move.** The Proofs package's kernel replay ran out of memory past 95 GiB in a 96 GiB cgroup
  (r20261005-194325-4f55, art:ed2be9d2a133aa61d559b7688b306d66eef81e3de07d20fc75770cecbab20887).
- **Steward.** Node 1 has no `build` slot pool, so `lean_changed.py --records` refuses there.

## Open

- **Restack.** The move's head will be `cursor/lean-layout-move-2-c3b2`, which reverts 77b8d66bc. At 24a857af4, the five
  code commits cherry-pick cleanly and the lock delta overlaps nothing there. Waiting on B4's update
  (r20261005-211634-5b38), then:
  1. Rerun the `--moved` audit and take this branch's records.
  2. Rerun the tests.
- **Review.** A named statement reviewer has to sign off on the changed records.
