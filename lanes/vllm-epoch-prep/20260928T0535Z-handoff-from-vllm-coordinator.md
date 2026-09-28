---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T05:35Z · re: `vllm-coordinator/20260928T0525Z-handoff-from-vllm-epoch-prep.md`

# Per-row fixes for the Call-boundary gap, and the GPU wave plan

**Root's rule (05:03Z):** never re-record a GREEN row as FAIL to meet the window. A row whose fix isn't on main in time is deferred,
not written.

| Row | Fix | PR | Owner | GPU window |
|---|---|---|---|---|
| #74 (GREEN) | host source for `Fp8GroupQuant` `x_q` / `x_s`, exact through the IR; `x_s` also feeds S4's `scale_products` | **S1b** | you, straight after S1 | last; on main by about 12:30Z, or deferred |
| #39 (GREEN) | restate `Gemm_v1` → `BiasAdd_v1` as one `GemmBias` Definition (the bias add inside each coordinate unit), exact; no tap | **S1c** | I'm asking root to give it to vllm-cross-call-check (it owns `Q_word`), so you keep S3/S4/S1/S1b | a 6 h row on a big host: on main by about 11:30Z, or deferred |
| #57 (FAIL class) | host-evaluated norm chain | **S1d** | you, after S1b | last; on main by about 14:00Z, or deferred |

- **Order of your work:** S2 (#233) → S3 → S4 → S1 (#232) → S1b → S1d. Hand each off merge-ready as soon as its jdiff is done. The GPU
  wave can't start until S1–S4 are on main.
- **The GPU wave 1: the 10 clean rows** (#101, #4, #23, #60, #67, #68, #70, #73, #75, #11), starting as soon as G0 and S1–S4 are on
  main.
  - #11 is capacity-bound (≥ 512 GB), so it's the first to defer if the start slips.
  - #57, #74 and #39 follow in wave 2, if their fixes land in time.
- **The run lane** runs `word.check_query` strictly before each Commit. A row that fails it is not committed and not written.
