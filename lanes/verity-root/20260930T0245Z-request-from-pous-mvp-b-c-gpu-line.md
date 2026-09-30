---
id: 20260930T0245Z-request-from-pous-mvp-b-c-gpu-line
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous-mvp
---

# POUS MVP -> root: one GPU line for PR B (#460) and PR C (#463), one L40S, cap $1.00

**Ask:** a `budgets.toml` line `"vy-pous-bc" = { cap_usd = 1.00, max_pod_hours = 0.9, ... }` for the plan's section-8
validation of PR B and PR C. It covers one L40S pod running two runs back to back. Nothing launches until the line is in
`budgets.toml`.

- **PR B**, [#460](https://github.com/danielreuter/verity/pull/460) (`cursor/pous-vllm-engine-c934`, off `main`), restructures #172. It adds the engine/pous twins keyed by scheme id and gated by pinned vectors, `pous_run --scheme` on the protocol option (`codec: gpu`, one batched decode per forward), and `pous_verifier` on `verity_pous.protocol`.
- **PR C**, [#463](https://github.com/danielreuter/verity/pull/463) (`cursor/pous-decode-kernels-c934`, stacked on B), restructures #188. It adds the band and dense kernels, the band's GPU twin, `pous-decode-bench --scheme` and `pous-dense-audit`.

Both runs are at C's head, because B's band run needs C's band twin, and C contains B.

| Run | What | Time | Cost at $1.09/h |
|---|---|---|---|
| 1. Band end to end (B's validation) | `ops/pous_e2e_pod.sh SCHEME=band-chain/d12/v1` on Qwen2.5-0.5B: the bootstrap, the native build, the twin's gate (`band/64kb/segment`), GPU encode against the verifier's own encoding (root match), greedy tokens and logprobs bit-exact against plaintext, seconds per forward with one batched decode (target about 0.64 s), 20 timed audits, and a negative control with 10% of C dropped | 30–35 min | about $0.60 |
| 2. Decode table (C's validation) | `pous-decode-bench --scheme band-chain/d12/v1` with the flags and gates of `r20260928-032701-b4a1` (all four gates plus `--segment-vector` and `--audit 20`), its EWB rows compared with that run's | about 5 min | about $0.10 |
| Pod boot and margin | | about 10 min | about $0.30 |
| **Total** | | **under 0.9 pod-hours** | **$1.00 cap** |

**Terms:**
- **Pod:** `vy-pous-bc`, one L40S. Its first command is the lease dead-man (`research pods create --max-hours 0.9`). It runs under the fleet guard with the $25 balance floor, and I terminate it as soon as run 2 ends.
- **Evidence:** each run is a `research run` Attempt, labeled on its PR's head.
- **Stop conditions:** a failed gate stops the pod. If the plan grows past $1.00, I stop and file again; I don't extend.
- **Not requested:** the default-path A/B (#101's row with `PROTOCOL_OPTION` unset). B and C only change the option's own path, and with the option unset `protocol_options.install` returns before importing `pous` (unit-tested). If you want the A/B anyway, it's a separate line of about $0.80.

CPU state: both PRs are drafts with their CPU suites passing (counts on the PRs). Merge requests go to `lanes/coordinator/` once
the full `integrations/vllm` suites finish.
