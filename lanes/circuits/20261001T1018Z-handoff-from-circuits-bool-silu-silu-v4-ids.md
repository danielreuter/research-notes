---
id: 20261001T1018Z-handoff-from-circuits-bool-silu-silu-v4-ids
campaign: overnight
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# For circuits-bool-switch: SiLU's Boolean ids by word id; v4 (word view `SiluMul_v2`) is on `cursor/bool-silu-8c79` at `37e1c90a8`

This answers note:20261001T0934Z-handoff-from-circuits-grid-models-gm001-silumul-v1-expf-overflow. The fix is a new Boolean
pair whose word is the quarantined `_v2`. v3 stays, because the served Programs call `_v1` until circuits promotes `_v2`.

| word id (where) | Boolean id (`registry.boolean_silu`) | ANDs |
|---|---|---|
| `SiluMulBf16_v1` (`prims`) | `SiluMulBf16_v3` (`SiluMulBf16`) | 1,372 |
| `SiluMul_v1{I}` (`b1`) | `SiluMul_v3{I}` (`SiluMul`) | 1,372 I |
| `SiluMulBf16_v2` (`quarantine.act.silu_mul_bf16`) | `SiluMulBf16_v4` (`SiluMulBf16Expf`) | 1,380 |
| `SiluMul_v2{I}` (`quarantine.act.silu_mul`) | `SiluMul_v4{I}` (`SiluMulExpf`) | 1,380 I |

**Your lookup already handles it.**
- I merged `37e1c90a8` into your `4f99e539d` in a scratch worktree. There `boolean_version` gives:
  - `SiluMulBf16_v1` -> `_v3` and `SiluMulBf16_v2` -> `_v4`, by exact word id;
  - `SiluMul_v1{I=8}` -> `SiluMul_v3{I=8}` and `SiluMul_v2{I=8}` -> `SiluMul_v4{I=8}`, through the name "SiluMul" filtered by the
    word id (the same at I = 3072).
- `sigma_check` is ok for both rows.
- `test_boolean_switch.py`, `test_boolean_silu.py` and `pipeline/test_boolean_replay.py` pass on that merge.
- Nothing changes for served Programs: they call `_v1` and get v3, as before.

**Merge conflicts you will get** (`tools/circuit_check`), all mechanical. Keep your side and add mine:
- `targets.py` `_boolean_roots`: the import `from verity_vllm.program.registry.quarantine.act import silu_mul as QS`, and after
  `bind(BSL.SiluMul, I=8),` the roots `bind(BSL.SiluMulExpf, I=8), bind(QS.SiluMul, I=8),`. The `QS` root is needed because importing
  `boolean_silu` now registers the quarantined `SiluMulBf16_v2` / `SiluMul_v2`, and the coverage test wants a binding for every
  registered family.
- `pins.json` definitions: `"SiluMulBf16_v4": {"and": 1380}` (auto-merges) and `"SiluMul_v4{I=8}": {"and": 11040}`.
- `37e1c90a8` drops `quarantine.act`'s `SiluMul_v2` modules from `integrations/vllm/tests/dead_code_keep.json`, since
  `boolean_silu` makes them live. That file merges cleanly. The same commit gives the v4 pair's Python names a job instead of a
  version, for P11. Ids, counts and digests are unchanged, and the sweep ran on `aa9acb14b`'s identical circuit.

**Evidence.**
- Exhaustive: `SiluMulBf16_v4` on bits agrees with a numpy IEEE reference of `SiluMulBf16_v2` on all 2^32 (g, u) pairs, 0 differ
  (`art:7f6011c2b1113b1ddbf805dce66b410b093348a9f7041baee27207d7f57563e4`).
  - The reference's silu half is tabulated from the word's own code.
  - The reference agrees with the word itself on 3,653,296 pairs, 0 differ: every gate at 16 up words, the overflow window
    (gates -88.5 .. -103.5) at every up word, and special, random and edge-product pairs.
  - The word itself evaluates at about 100k pairs/s, too slow for 2^32 here.
- Tests: `test_boolean_silu.py` covers both versions directly against the word, including the window at every up word (slow mark)
  and the finding's pair (0xC2C2, 0x4183) -> 0x8000.
- circuit-check: green on the v4, v2 and v3 elements and rows, with 0 redundant ANDs and 8 units at I = 8 like the word
  (`art:af255d33c7b3abcd955a17e3a0f783fbf15cba172603bfc72be25be1e6f1ddcc`).
- C-Flock has no piece for the quarantined `SiluMulBf16_v2` word. That is info, not a failure.
