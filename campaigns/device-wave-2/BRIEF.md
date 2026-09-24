---
kind: brief
campaign: device-wave-2
owner: coordinator
created: 2026-09-24T02:55Z
base: main @ 24f252b1 (integration: 12 lanes merged; fp4-decode-3 NOT merged)
final: 06:30Z hard (balance runway, see §6)
---

# Device wave 2: Table 2 on every target, from main 24f252b1

Read `kb/LANE-CONTRACT.md` first; it wins over anything here. Sources for every number below:
`lanes/coordinator/20260923T2250Z-device-wave-inputs.md`, `lanes/integration/20260924T0100Z-report-integration.md`,
`kb/live-verifier.md`, `kb/pods-4090.md`, live-2c's RUNBOOK (`lanes/live-2c/*report*` §6).

## 1. What Table 2 is (user decisions, unchanged)
Per target, two columns, both **interactive ZK (`--zk --mode interactive`), live verifier coins, 4096 VUs**, no FS anywhere:
1. **bare**: the relation alone (authentication=excluded). Candidates, all private-operand-safe:
   v1 at its best depth (l=16384), v3 fused (l=16384), v3x4 fused (l=4096, p4 and p8). Headline = the fastest candidate
   **measured in this wave**, >= 3 rounds, alternating arm order (host noise up to 64 % between rounds on H100).
   Report the depth; depth up to 8 is allowed where it wins. No `--batch 32768`.
2. **committed**: `--auth included-hash-shared --tile 64x64` (Poseidon2 row digests in-circuit, rows shared via LogUp;
   shared-live-2). Unshared `--auth included-hash` = drill-down, one cell per target.

## 2. Live verifier policy (live-2c)
- Headline number = `t.total_live` from a live run against a verifier **in the prover's datacenter** (same-DC tax ~1.1x);
  print the local-coins `t.total` of the same pod and tree beside it. Record both DCs and the RTT per cell.
- Run your own verifier from main 24f252b1: `backends/direct/ligero/live_serve.sh` on a second, cheap pod in your GPU pod's
  DC (a CPU pod if RunPod offers one there, else the cheapest GPU pod in that DC). Never on the prover pod (same-pod
  verifier contends for CPU; that is shared-live-2's caveat). If no second pod can be had in your DC, use the nearest and
  say so; never quote a cross-region number as the headline.
- `vy-live2b-verifier-ro` is READ-ONLY (its session store backs Ligerito claims). Do not use or restart it.

## 3. Verification and custody for every headline cell
- Dump rep 1. Rust re-verify with main's pinned binary: `backends/direct/ligero/reverify.py` for bare and +hash;
  for +shared use the manual Rust `batch-pair ... --system-h` (reverify.py lacks `--system-h`; integration did it this way).
- `python -m verity_numerical.bench.summary DIR...` over your results; every headline row's `contract` column must pass.
- `research data put ... --preserve` each result + dump at once; snapshot `<lane>-v1`. Labels via the vocabulary.

## 4. Pods and CPU
- `pod_bootstrap.sh`, `source env.sh`, `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`.
- ONE heavy job at a time. Timings only with `nvidia-smi --query-compute-apps=pid --format=csv,noheader` empty.
  Correctness jobs overlapped: `OMP_NUM_THREADS=2 MKL_NUM_THREADS=2`. 4090 pods have ~10 CPU cores (kb/pods-4090.md);
  record `cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us` on yours.
- Skip `gate-vu` on v3x4 at 4096 VUs (CPU reference does not finish); gate at 1024 VUs instead and say so.

## 5. Lanes
| lane | target / relations | extra | pod budget |
|---|---|---|---|
| wave-4090 | RTX 4090: fp8-ada | drill-downs: +hash, +ajtai-n64 (H1/H2 fixed in main), +blake3 one cell (l=4096). After measurements: the pytest files integration never reached (`steps_pin_test`, `reverify_test`, `live_test`, `pipeline_race_test`, `leaf_test`, `leaf/conformance_test`, `pubsel/relation_test`), 2 threads each | $4 |
| wave-h100 | H100 80GB HBM3: bf16-hopper, fp8-hopper | +hash drill-down per relation | $9 |
| wave-a100 | A100 80GB (SXM or PCIe; record which): bf16-ampere via the chain runner (`run.py --relation bf16-ampere[-v3] bench-vu --pipeline N`), not vu.py | +hash drill-down | $5 |
| wave-5090 | RTX 5090: fp4-nvf4 bare (column 2 needs fp4-port) | stock was "None" at 02:50Z: retry for 30 min; if none, FINAL "no 5090 available" and do not substitute | $4 |
| fp4-port | port fp4-decode-3 onto main (see its launch message) | measures its own 5090 +hash cell if it lands | $5 |
| ligerito-2pass | Ligerito second pass (see its launch message) | diagnostic column only | $4 |

## 6. Money
Account balance $156 at 02:50Z, account burn $24.9/h (mostly the other session's `vyv-*` pods). That is ~5 h of runway with
this wave. Terminate pods the moment you are done; FINAL by 06:30Z is hard.

## 7. Appendix (coordinator broadcasts)
