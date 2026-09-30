---
id: 20260930T1133Z-handoff-from-vllm-coverage-defs-topp-maxgates-table
campaign: overnight-sep30
lane: vllm-coverage-defs
kind: handoff
status: ready
repo: danielreuter/verity
origin: vy-nebius-1
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

# Top-p / Gumbel on large vocabularies: option 3 (raised MAX_GATES)

This follows the coordinator's 10:20Z decision. The `_v3` split is dropped; no PR comes from it.

## Evidence runs (vy-nebius-1, CPU direct, `CUDA_VISIBLE_DEVICES=`, tree `cursor/coverage-v0-2622` @ f508d19b)

| run | row | n used | result | wall | peak RSS (largest process) |
|---|---|---:|---|---:|---:|
| r20260930-105616-f995 | llama32-1b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager | 103,000,000 | build PASS, word check complete (8067 identities), manifest 76c6ef274a1108a0 | 29:06 | 61.84 GiB |
| r20260930-105616-204f | llama32-1b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__stoch-t0.8-p1__bi-eager | 103,000,000 | build PASS, word check complete (8067 identities), manifest a27629197861f058 | 29:52 | 61.91 GiB |

- The measured need at V=128256, S=32 is 102.38M gates.
- Peak RSS is the `/usr/bin/time -v` maximum resident set size.
- The two runs ran concurrently in one cgroup, which peaked at 140.4 GiB. The per-process sum in resources.jsonl double-counts shared pages (262 and 293 GiB), so ignore it.
- Both runs are labelled `ov.ws build`, `ov.metric peak-rss`, `ov.value`, `ov.unit GiB`, `ov.config <row slug>`, `ov.line topp-maxgates`, `ov.attempt 0`, `ov.phase prefill`, and `ov.note`, all `--by vllm-coverage-defs --off-vocab`.
- The labels are in the host's local store only. `research data push --pending` has not been run, because it would also upload other lanes' pending labels; push them with the next batch.

## Formula: n per cached vocabulary (S=32, about 10% over the measured `_v2` gates)

Expected RSS assumes 648.6 B/gate, measured from the Llama top-p run (61.84 GiB / 102.38M gates). That run's peak was dominated by the sampler word check. Size the host at the n column.

| V | `_v2` gates (measured) | `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=` | expected RSS at need | RSS bound at n |
|---:|---:|---:|---:|---:|
| 32,000 | 27.01M | 30000000 | 16.3 GiB | 18.1 GiB |
| 49,152 | 39.97M | 44000000 | 24.1 GiB | 26.6 GiB |
| 50,304 | 40.84M | 45000000 | 24.7 GiB | 27.2 GiB |
| 128,256 | 102.38M | 113000000 | 61.8 GiB | 68.3 GiB |
| 151,936 | 122.93M | 136000000 | 74.3 GiB | 82.1 GiB |
| 256,000 | 204.34M | 225000000 | 123.4 GiB | 135.9 GiB |

- Rows at or below V=27,995 (S=32) are under the default 24M and need no override.
- The same n covers the Gumbel row (top_p=1).
- The gate count scales with S. For another S, re-measure it rather than reusing this table.
- Wall time is about 30 min per Build at 128k on CPU.
- Per the coordinator, the cell `ov.note` must read: `sampler Call one unit (MAX_GATES raised to <n>); not provable in practice`.
- No digest moves: the override changes only the admission limit, not the Definition or the record.
