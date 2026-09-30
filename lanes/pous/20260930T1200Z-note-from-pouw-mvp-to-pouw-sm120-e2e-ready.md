---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
lane: pous
kind: handoff
from: PoUW MVP lane (bc-dd22acf8, for the Verity root)
to: sm_120 PoUW coordinator (bc-2aa33ad8); GPU 1 (bc-18346d9c); bc-b139c29c
created: 2026-09-30T12:00Z
---

# -> bc-2aa33ad8: the PoUW MVP e2e on node 2 is ready to queue once GPU 1's kernel gates

- **What's ready.** Draft [#540](https://github.com/danielreuter/verity/pull/540) (head `c7033d67`) runs vLLM with every linear
  committed by GPU 1's sm_120 pipeline (`pearl-c-sm120-v1-h1`, from `cursor/pearl-c-sm120-h1-b44b` at `124585e5`):
  - the model is Llama-3.1-8B-Instruct in BF16 at TP 1;
  - prefill is one 8,192-token prompt and decode 32 sequences, so every linear has the panel's m;
  - the modes are bf16, fp8 (the divisor), pearlc-nohash and pearlc, each gated before timing;
  - the retained verify passes start from poisoned buffers and must repeat their timed commitments;
  - the reference verifier (`pearl_c_work`'s draws and exclusion tiles) runs after the window.
  Node 2's environment is installed (`r20260930-113242-c755`, CPU only). No GPU time has been used.
- **For you:** one timed window (`gpu-lease 8 --wait --timed`, estimated 11–13 min, capped at 19), then a CPU verify job. The job
  spec and run lines are in the research store's `docs/pouw/mvp-e2e.md` ("RTX PRO 6000"). My status file is
  `internal/pouw/rtx-pro/workers/pouw-mvp-e2e.md`.
- **What blocks it:**
  - **GPU 1's gate (the only blocker for `-h1`).** GPU 1, post the gated head and I'll merge it into #540. The window needs
    your `build.sh` ship built from that tree.
  - **`-h2`.** #532's frame-b3s kernels aren't in GPU 1's pipeline, and the two schemes conflict in `pearl_c.py` (mechanically).
    bc-b139c29c and GPU 1: once A's rows and every tree are frame-b3s in `run.py`'s steps, #540 adds `pearl-c-sm120-v1-h2`
    in one line.
