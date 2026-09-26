---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T21:40Z
---
# PR #88 verdict (vLLM side): APPROVE, head `f1df809f`. The red-team verdict on the scheme gates it too, as you said

Your three questions:

1. **The default path is byte-identical. No digest of record moves.** With `leaf_scheme` defaulting to `vllm-v1` (`hiding is None`):
   - `_leaf_ctx()` returns `b""`, so the step context digest `sha256(run_id/step=s + b"")` is unchanged;
   - `_salted` returns the leaves unchanged;
   - `_leaf_rule(inner, b"")` returns `inner`;
   - `_salts_of` returns `b""`, and `persistent_bytes` adds 0.
   - The only default-path difference is two telemetry keys in `RunCommitment.extra` (`"leaf_scheme": "vllm-v1", "salt_bytes": 0`). That
     dict is the committer's diagnostics bag (timings, pool sizes, errors), not a digest input.
   - Test `test_roots_bind_the_leaf_scheme_and_default_leaves_are_unchanged`.
2. **The ratchet lints pass on main `56c62af2` + #88** (39/39), and the merge is clean. The P10 allowlist change moves `native_host`'s
   `_open_levels` into `native_ranges.open_levels` (shared by both paths).
3. **Both range and point verification check the hiding layer:**
   - point (`NativeHostCommitter.verify`): the leaf is `_leaf_rule([pos_leaf(value)], opening.salt)` before the path fold, and an
     opening carrying a salt under `vllm-v1` is refused;
   - range (`verify_range` → `_range_leaves(..., ro.salts)`): each leaf goes through `_leaf_rule`. A wrong salt length gives None
     (refused), and salts under `vllm-v1` are refused;
   - tests `test_value_salt_and_path_are_bound`, `test_range_openings_carry_their_salts`,
     `test_two_commitments_of_the_same_stream_differ_and_do_not_cross_open`;
   - both paths also keep #77's guards (a 32-byte run root; `_run_root` is None over placeholder steps).

**Refused, by design:** hm96 together with the GPU chunk tree (host-hashed only), and padding steps under hm96. Both fail loudly at
construction or commit.

The core scheme (`verity.commitments.hm96`: spec, reference, vectors) is the red team's to judge, not mine.
