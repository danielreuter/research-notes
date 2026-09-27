# vllm-rf-recompute: READY

Both recomputes that the no-recompute checks found are removed as opt-in constructions. With the selectors off, every digest of record is unchanged.

| fix | PR | head | selector | checker with the selector on | gate (b) vs `3040ac1f` |
|---|---|---|---|---|---|
| #74 FP8 block scale products | #106 (approved 04:55Z) | `df13126f` | `fp8.SHARED_SCALE` (Definition map) | `Q_word_v1` + #98 member check: 4 violations / 113.6 G recomputed gates -> 0 / 0; +894.8 M committed words | jdiff rc 0 (8 new pass) |
| #57 Gemma weight + 1 | #109 | `39e3b24c` | `TargetProfile.weight_only_calls = "once"` | `cross_call`: 44,520 Calls / 102.6 M gates -> 0; `Q_word` 0 violations both ways | 0 new failures, 4 new pass, 1 designed skip (passes with #98, `r20260927-050958-682d`) |

- **Handoffs:** `$STORE/internal/lanes/vllm-coordinator/20260927T0445Z-handoff-from-vllm-rf-recompute-fp8.md` and
  `…/20260927T0520Z-handoff-from-vllm-rf-recompute-gemma.md`.
- **Gate (b) runs,** all preserved:
  - base `r20260927-035144-299a`;
  - FP8 `r20260927-035231-167a`;
  - Gemma `r20260927-044046-03f9`;
  - superseded `r20260927-035257-150f` and `r20260927-043810-c5cf`;
  - #98-patched check `r20260927-050958-682d`.
- **Evidence:** `evidence/` (scripts, checker outputs, definition digests) and `evidence/gate-b/` (jdiffs, the #98 query patch).
- **Serving:** both committed values are host-computed in the IR's semantics, NaN payloads included:
  - FP8 products, from the committed `x_s` and block scales;
  - Gemma `w + 1`, at load.

  The `0x7FFFFFFF` mapping is needed only if a kernel tap (FP8) or a runtime-tensor collector (Gemma) ever supplies them instead.
- **Switch points for the re-baseline** are listed in both PRs.
- **Found, not fixed:** GP-01 hoisting of weight-only Calls (8 per-request copies per norm on #57), and the Match fold issuing weight-only instances per step.
- **Pods:** `vyv-rf-recompute-cpu` ran 03:50Z to 05:12Z, was terminated and unregistered, and cost about $0.88. The lane made no other spend.
