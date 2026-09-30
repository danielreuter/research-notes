---
id: 20260930T2205Z-report-env-check-and-classes
campaign: verity
lane: proofs-n2-guest
kind: report
status: open
repo: danielreuter/verity
origin: proofs-n2-guest (bc-c951b059), worker of @proofs (bc-8416bc72); answers note:20260930T2144Z-handoff-from-proofs-replan-2-drop-k2048-rest
---

CHECKPOINT 3fd1af6f (22:06Z) [open] 3:07 PM PDT: re-plan 2 applied: whole-row guests withdrawn (13 stale pn2g-* scripts exit 0 at once); env check: node 2 matches node 1 (driver 580.173.02, libcudart 13.0.96, clocks locked 2100); only new class K=8192 (#1936): stage queued, gate + 2 chunks follow (<1 GPU-h); loop tmux proofs-n2-guest; note:20260930T2205Z-report-env-check-and-classes
# proofs-n2-guest: node 2's environment matches node 1's, so K=8192 is the one new class; its 3 chunks are all that's queued

## Environment check (3:00 PM PDT, read-only, outside a timed window)

| | Node 1 (`vy-nebius-1`) | Node 2 (`vy-nebius-2`) |
|---|---|---|
| Driver | 580.173.02 (`/proc/driver/nvidia/version`) | 580.173.02 (`/proc/driver/nvidia/version` and `nvidia-smi`) |
| Prover | `flock-circuit` sha256 `e484a335…` (build key `4d568a3cb558b005`, sm_120) | the same file, copied from node 1 |
| CUDA runtime it loads | `/usr/local/cuda-13.0/…/libcudart.so.13.0.96` | the same (`nvidia-smi`: CUDA 13.0) |
| SM clock | locked at 2,100 MHz (brief; `lanes/vllm-sm120-fp8-ckpt/…vy-nebius-1-ready.md`) | 2,070–2,092 MHz on all 8 GPUs under PoUW load; max 2,430 |

- **Verdict:** they match, so node 2's costs are comparable with node 1's. Every record carries this as `env_check`.
- **Driver:** the brief's "node 1: 595.91" isn't what node 1 loads. Its kernel module is 580.173.02, the same as node 2's.
  595.91.07 appears only in `vllm-sm120-fp8-ckpt` for a different pod.
- **Clocks:** `nvidia-smi -q -d CLOCK` doesn't print the lock setting itself. Node 2's readings match `kb/sm120-kernels.md`:
  locked node-wide at 2,100 / 12,481 MHz by the node's owner, 2,070–2,092 MHz under the power cap.
- **What I ran:** one `nvidia-smi` on node 2, gated on `status.txt` showing no timed window. I made no NVML call on node 1 and
  changed nothing.

## Shape classes (distinct K or tile pattern)

Llama-3.2-1B has two GEMM-coordinate shapes, and both use the default 4×4 tile and `HopperBF16WgmmaDot16_v1`:

| Class | Shape (line of `shapes.tsv`) | Covered by |
|---|---|---|
| K=2048 | `f1e4d147` (#1551): `Gemm_v2` K=2048 at N=128,256 and N=16,384 | node 1, backend-sweep-2 (b), chunks 0–7,500 |
| K=8192 | `7a1fc1a9` (#1936): `Gemm_v2` K=8192, N=2,048 (`down_proj`) | **node 2, this lane: 3 chunks** |

- **The rest of the whole-row plan is withdrawn.** That covers the AttentionHead, SiluMul, RMSNorm and Rope shapes (ranks 4–17
  of `note:20260930T2153Z-report-ranking-and-split`). They aren't K classes, so none is queued, and I'm not proposing any.
- **The 13 scripts from 2:52 PM PDT are withdrawn** (`pn2g-<idx>-{stage,r0}.sh`):
  - At 2:58 PM PDT infra held 11 of them in `fill/held-proofs-pn2g/`. If any is restored, `job.sh` exits 0 at once, because it
    carries no `PN2G_QUESTION`. On the owner's yes I'd queue `pn2g-q-*` versions instead.
  - node2-ops' restored `pn2g-1936-stage.sh` ran at 22:04Z while my STOP file was set, and exited 0 without staging.
    `pn2g-q-1936-stage.sh` stages #1936 instead.
  - Four CPU stage jobs (#12, #15, #1546, #1549) ran 1–2 min each before STOP. Their records sit in `withdrawn/` on node 2 and on
    node 1 (`/workspace/jobs/proofs-n2-guest/`), outside custody.
- **The K=2048 remainder:** none was ever queued.
- **If K=8192 doesn't fit the current circuit** (M0's note), #1936's stage or gate fails. The loop then stops that row and queues
  nothing else, and I report it (`note:20260930T2200Z-handoff-from-proofs-gemm-only-scope`).

## What runs (scripts `pn2g-q-1936-*.sh`, tools in `tools/`)

- **Question:** every script carries `# question: "what is the whole-row proving cost against K, per shape class, on sm_120? (3
  chunks per new class)"`. It is also passed as `PN2G_QUESTION`, which `verify.py` writes into each done record.
- **Stage:** a gpus=0 stage job. Node 1 never staged #1936, so it has no record.
- **Chunk 1, the gate:** 20 statements with the GPU selftest (`gpu_paths_agree` and `gpu_proofs_match_cpu`, byte for byte against the CPU
  prover). It must be verified before anything else is queued.
- **Chunks 2 and 3:** about 600 s of statements each, at the gate's measured seconds per statement (at least 100). The runner's
  30-min cap on GPU jobs rules out node 1's 2,500-statement chunks. Compare per-statement costs, not chunk totals.
- **Estimated size:** well under 1 GPU-h. No gate can run before the GPUs are idle, since Verity GPU guests start only with
  no PoUW job ready and 2 or more GPUs free.
- **Labels, custody, loop and stop:** as in `note:20260930T2153Z-report-ranking-and-split`. To stop:
  `touch /workspace/verity-guest/wholerow/STOP`.
