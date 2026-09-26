---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: b4, engine and hooks, from vLLM coordinator bc-ecac3029, 19:15Z

- **Merge:** `lane/vllm-rf-b4c` @ **`9689a1ef`**, `--no-ff`: b4b's `5c05ff6d`, plus main `38a8d35d`, plus
  `lane/vllm-rf-a5c` `40b9e571` (now in main).
- **One conflict on main `a1ccdecd`, which is mechanical:** `integrations/vllm/tests/lint/_imports.py`, in `LAYER`. c4ir
  (merged as `8679caa6`) deleted the three `query.boundary` / `query.partition` / `program.frontend.liveness` → `"core"`
  lines; b4 added `engine.hooks` / `engine.env` → `"core"` right beside them. **Resolution: take main's side, then add b4's
  two `engine.*` lines** (b4's docstring paragraph auto-merges). Everything else auto-merges (the p07/p10/p11
  allowlists). With that resolution, every ratchet lint runnable without pytest passes (39/39).
- **Why the gates carry:** since b4's gate base `40b9e571`, main added c4ir, gc and non-vLLM work. b4 shares only the
  allowlists and `_imports.py` with them.
- **Gates:**
  - lints 47 passed (base 45);
  - gate (b), head `r20260925-180555-f321` against base `40b9e571` `r20260925-180449-ed37` on the same pod: 0 new
    failures, skips or skip reasons, 0 deleted or renamed, 17 new tests pass;
  - gate (a) T0+T1 73/85 = a23b's (at `0f71b5b4`, pre-rebase; b4b's READY).
- **Acceptance:**
  - #101 at `9689a1ef` (`r20260925-180228-0dda`): program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`,
    commit PASS = record; non-interference 992/992 (`r20260925-184105-e73e`);
  - earlier: #70 32/32 against f1's base, and FA3 on H100 head = base (b4b).
- **What changed:** `engine/hooks.py` owns every vLLM/torch patch (each uninstallable, with a test), and `engine/env.py` is
  the one writer of vLLM env pins. All 43 P9 runtime-patch entries are gone. `construction_version` moves (code
  identity, allowed); no Program, manifest, root or verdict change.
- **Behaviour choice in the a5 merge:** P7 `pin_writes` exempts only `engine/env.py` (a5's `pipeline/cli.py` is an
  env owner for reads).
- **Found, not fixed:** after a5, `python -m verity_vllm.properties.noninterference` exits 0 silently (use
  `verity-vllm noninterference`).
- **Evidence:** `lanes/vllm-rf-b4c/READY.md`, `lanes/vllm-rf-b4c/evidence/{gate_b2,r101}/`; handoff
  `lanes/vllm-coordinator/20260925T1855Z-handoff-from-vllm-rf-b4c.md`. b4c spent about $5 of $8.
- **Next:** b1 (b1c re-gate against `40b9e571` due about 12:25 PM PT). Then one confirming gate (a) on main after
  a5/b4/b1.

