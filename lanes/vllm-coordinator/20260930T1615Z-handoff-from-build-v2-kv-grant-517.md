---
id: 20260930T1615Z-handoff-from-build-v2-kv-grant-517
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: done
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# Grant request: `vllm-coordinator` on #517 at `872be036` (Build plan change 3, key/value references shared as a prefix)

#517 is marked ready in the merge queue and waits only for your role, because it touches `integrations/vllm/`.

- **[#517](https://github.com/danielreuter/verity/pull/517)** at **`872be0366352512bbdbf5a942ed6cc0adcb8bb54`**, with `main` `6a815cc7` (train TVJ) merged in.
- **What changes in the integration:**
  - The attention rule cuts each layer's key/value sequences from one `PartLog` (`rules/common.py` `kv_logs`,
    `vllm_bindings/attention.py`, `rules/profile.py`), where it used to `concat` `t` rows per call.
  - Replay, the correspondence emitter (`emit.py`) and the composition (`workload.py`) each do the shared prefix once.
  - `derive.py` and `observe/fold/fold.py` now share one torch-free replayer, `program/replay.py`; the fold's verbatim copy is gone.
  - P10 caps are lowered: `derive.py` 1012 → 1009, `fold.py` 1318 → 1287.
- **Core:** `verity.ir` `refs.py` (`PartLog`, `prefix_runs`, `Concat.slice` bisect), `codec.py` and `liveness.py`. No format change.
- **Digest-neutral.** On vy-nebius-1 every row is byte-identical to `main` in same-time A/Bs: workload, manifest, component and
  correspondence digests, and gates.
  - Rows: llama32-1b and mistral-7b prefill, and llama32-1b B8 I1024 O128.
  - Runs: `r20260930-133041-d53d` (`main`) against `r20260930-133103-9fef` (tip), and `r20260930-092548-94d4`.
  - Build line `build-v2` attempts 0–2 are labelled, and every `ov.gate=pass`.
  - Speed: prefill Builds take 0.62–0.75× of `main`'s wall time and 0.57–0.68× of its peak RSS. The 1k row takes 0.66× wall and
    0.54× RSS.
- **Suites on this head:**
  - lint: 43 passed;
  - `tests/{program,observe,correspondence}` plus the import, dead-module and by-name checks, without slow tests: 1,716 passed,
    71 skipped, 3 xfailed, 1 xpassed;
  - core `ir`, `evaluation` and boundaries: 306 passed.
  - Slow tests are left to `check`.
- **Merging `main`:** it conflicted twice in `attention.py`, where `main`'s `FA2_MASKED_FROM` and `**extra` sit next to my
  `klog.cut(P)` / `vlog.cut(P)`. Both resolutions keep both sides.

`research data label pr:517@872be0366352512bbdbf5a942ed6cc0adcb8bb54 grant vllm-coordinator --by vllm-coordinator`
