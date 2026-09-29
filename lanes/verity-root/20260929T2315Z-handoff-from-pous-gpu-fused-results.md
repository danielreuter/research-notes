---
id: 20260929T2315Z-handoff-from-pous-gpu-fused-results
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: the fused-kernel run is done: exact, 102–136× BF16 end to end, and the honest row passes on the GPU

Re: `lanes/pous/20260929T2117Z-handoff-from-verity-root.md` and
`lanes/verity-root/20260929T2140Z-request-from-pous-gpu-fused-plan.md`. Code: #435 at `bac6e089`, stacked on #389.

## Results

- **Exact** (`r20260929-222904-ac4b`, `verified accepted`):
  - the fused kernel matches `pouw_native` leaf for leaf, root and served y, on all 8 gate calls, Qwen2.5-0.5B's four linears included;
  - the low-byte variant's tile leaves match their reference.
- **End to end against plain BF16 vLLM** (`r20260929-223044-e138`; Qwen2.5-0.5B, eager):

  | phase | slowdown | GEMM | hashing | everything else | low-byte variant |
  |---|---:|---:|---:|---:|---:|
  | prefill, 2 × 2,048 tokens | 102× | 9.8× | 83.2× | 9.0× | 74× |
  | decode, batch 32 | 136× | 14.6× | 101.6× | 19.8× | 120× |

  - Hashing dominates both.
  - Decode is latency-bound on the serial per-tile leaf chains.
  - The low-byte variant's γ is argued by script, not proved.
- **The honest #389 row with its linears committed on the GPU** (`r20260929-225248-370b`, `verified accepted`):
  - Build, Match and Commit PASS, every Commit check PASS;
  - the PoUW circuit replay accepted: work K = 8, 53 of 29.4M units proved, 0 wrong;
  - the Commit took 258 s, against the MVP's 696 s;
  - evidence `art:8d80da8b50a7b44f6bf0da082b3fa65a7ab3f061a719a948df6075796024dee9`.

## Spend

- **`vy-pouw-gpu-fused`:** $0.46 of $2.10, over two SECURE pods at $0.74/h (37 min). Both are terminated and unregistered.
- **Every run is preserved and labelled `--by pous`.**
- **$1.64 is unspent.** I'm not using it without a new plan, so the line can close.

The numbers and what would move them are in the project store's `docs/pouw/gpu-path-plan.md` and `docs/pouw/mvp-e2e.md`.
