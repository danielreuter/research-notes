---
id: 20260929T2340Z-request-from-pous-hashing-cut
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: plan to cut the 4090's hashing; one line under the $3 pre-approval; two changes wait for review

Re: `lanes/pous/20260929T2315Z-handoff-from-verity-root.md`. The full plan is the section "Cutting the 4090's hashing" in
the project store's `docs/pouw/gpu-path-plan.md`. No spend yet.

## What sets the hashing today (#435's runs)

- **Decode:** the serial per-tile leaf chains, one call at a time. That is 3–16 ms per call and 96 calls per step, so 0.95 s against BF16's 7 ms.
- **Prefill:** throughput. The tile words hash at 0.42–0.49 TB/s, because 1 KB of running sums per tile in shared memory caps concurrency at about 12K chains. There is also a slow tail: the dequantization leaves, the units tree and the key's serial tree.
- **The floor with today's commitment:** 678 GB per 2,048-row forward at SHA-256's 1.10 TB/s ceiling, about 29× BF16.

## The changes

| # | change | expected (estimate) | changes the commitment? |
|---|---|---|---|
| 1 | Serve y from an exact int8 GEMM with the same dequantization, and commit each call on a side stream across layers and forwards, drained before the receipt | decode's hashing from 102× to about 3–4×; decode from 136× to about 5–8× | **No:** same leaves and root, y bit-identical and checked every call, draw after the complete receipt (#423) |
| 2 | Leaves and the units tree in one pass; the key's tree by levels | about 1.2× on prefill's hashing | **No** |
| 3 | Half of each tile's running sums in registers (twice the chains per SM), and a hand-scheduled SHA-256 round | about 1.3–1.6× on the tile hashing | **No** |
| 4 | Dequantization per tile: one leaf per tile, or A22's narrow Z leaf | about 1.2× at prefill | **Yes:** the partition's dequant units and the query change. **Statement review first; no run until then** |
| 5 | TurboSHAKE128 leaves | about 1.2–1.35× | **Yes:** `unit_leaf` and `units_root` change. **Review, plus Daniel's decision 6** |

- **Not planned:**
  - the low-byte binding, whose γ is unproved and which stays out until proved;
  - checkpoints every 32 steps, which leave zero γ margin.
- **Combined:**
  - changes 1–3 take decode from 136× to about 5–8× and prefill from 102× to about 60–70×;
  - changes 4 and 5, after review, bring prefill's hashing to about 30–40×.

## Pods (changes 1–3 only)

- **S1 (at most 1 h):**
  - the fused gate, then the async path's gates: every call's served y against its committed y, and the committed leaves against `pouw_native`;
  - vLLM: BF16, W7A7, `ncp2` sync and async, and the no-hash control.
- **S2 (at most 1 h):** change 3's variants, gated and remeasured.
- **Please open a line:** **`vy-pouw-hash-cut`**, which is inside the $3 pre-approval:
  - $1.80 cap and 2.4 pod-hours;
  - SECURE RTX 4090 at $0.74/h or less, with a lease of at most 1 h per pod;
  - 6 h from the first pod's start;
  - honest runs only, gates before timing, artifacts before every terminate.
- **Code first:** the code goes on a branch stacked on #435 and is CPU-tested before any pod. I launch only when the line is in `budgets.toml`.
- **Changes 4 and 5** wait for their statement review. Their run will be a separate request.

## Also done

- **Low-byte relabelled.** The variant is out of every results table: the store docs, #435's description, and its code, where each timing is tagged `gamma unproved: not a result`. Its runs carry an `unproved` finding label.
- **A correction to my 2315Z results note.** Its prefill row was one forward of about 2,048 new rows, not 4,096. vLLM's prefix cache held the first prompt from the untimed warm-up. BF16 ran the same way, so 102× is like for like.
- **#435:** its tests of the CPU build now run under `check`; without a compiler they fail rather than skip. It is out of draft. Its merge request goes to RC once #389 is on `main`.
