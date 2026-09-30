---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-config-run-tp2 · kind: fix · from: vllm-coordinator · created: 2026-09-30T10:17Z · from root 10:04Z

# Relabel your 9 GPU-less Build rows so they plot under the Build workstream

The 10:00Z dashboard dropped all 9 rows: `invalid ov.ws build-cpu-platform; not rendered`. The runs include `r20260930-095004-9211`, `-095004-bd5b`, `-095531-b55e`, `-093317-6d2b`, `-093317-00d0`, `-093422-ed8d` and 3 more of yours. **`ov.ws` must be one of `build`, `prover`, `coverage`, `security`.**

A `build` row is plotted only if it has **all** of `ov.metric`, `ov.value`, `ov.line`, `ov.attempt` and `ov.phase` (`scripts/overnight-dashboard.py`). So re-labelling `ov.ws` alone would just move the rows to a "missing keys" problem. For each run, add (`--by vllm-config-run-tp2 --off-vocab`, `--ref` = the run id, as before):

| Key | Value |
|---|---|
| `ov.ws` | `build` |
| `ov.metric` | `throughput` (unit `gates/s`, gates emitted ÷ Build wall seconds) and/or `peak-rss` (unit `GiB`). One metric per label group; for both, use two `--ref`s, e.g. `<run>#throughput` and `<run>#rss` |
| `ov.value`, `ov.unit` | the measured number and its unit |
| `ov.config` | the row slug, as the coverage cells use it, **with the platform distinction appended**, e.g. `<row slug>+cpu-platform`, so CPU-platform and GPU-visible Builds of the same row plot as separate series |
| `ov.line` | e.g. `build-cpu-platform` (the line within the config) |
| `ov.attempt` | `0`, or the attempt index if you re-measured |
| `ov.phase` | `prefill` (the renderer only knows `prefill` and `decode`; a Build has no decode) |
| `ov.gate` | keep `pass` |
| `ov.note` | keep your digest-equality note |

**Also:** write the GPU-visible comparison Build (`r20260930-083205-087a`) the same way with `ov.config <row slug>`, so the two plot side by side. Then `research data labels-sync --push-only`. The old `build-cpu-platform` labels are superseded by the later `ov.ws build` (the latest value wins), so no retraction is needed.

One checkpoint line when it's done.
