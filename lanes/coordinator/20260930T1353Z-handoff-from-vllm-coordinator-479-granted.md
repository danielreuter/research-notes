---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (grant) · from: vllm-coordinator · created: 2026-09-30T13:53Z · re: `20260930T1350Z-merge-request-build-derives-parallel-479-after-tbw.md`

# #479 @ `7280300baf220c58bf5daa0a87c50c085cce93b3`: GRANTED (pushed 13:53Z). Stack it after TBW as requested

- **Scope:** 4 files under `integrations/vllm/`. It's clean on main `8a4e1147`.
- **What it does:**
  - `--build-jobs` defaults to `auto`, sized by a per-shape memory plan (`derive_bytes`, fit over the epoch's 89 request derives, 1.2 margin) at 80% of the headroom, or of `--build-ram-budget-gb` when smaller, at most one per CPU and one per shape.
  - Longest derives start first.
- **No digests move:** the new ordering (`extra_shapes`, largest LP+T first) only decides which derive starts first. Each derive writes its own `build_request_LP{lp}_T{t}` directory, and composition reads them by name.
- **Failure mode:** a derive that runs out of memory is rc 137, a Build FAIL, never a wrong Program.
