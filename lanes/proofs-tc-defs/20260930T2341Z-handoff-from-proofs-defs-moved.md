---
id: 20260930T2341Z-handoff-from-proofs-defs-moved
campaign: verity
lane: proofs-tc-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# 4:41 PM PDT: the GemmCoordinate Definitions moved to a new worker (deadline 5:40 PM); you keep the probes, so don't write Definitions

Daniel's reset makes FP8 and FP4 `GemmCoordinate` Definitions, green on circuit-check, due by **5:40 PM PDT**. A dedicated
worker (lane `proofs-gemm-defs`, branch `cursor/proofs-gemm-defs-95d4`, based on your branch `cursor/proofs-tc-defs-95d4`
@ `f8c22821`) writes them. It uses the ids `Sm120E4m3MmaDot32_v1`, `Sm120Nvf4MmaDot64_v1`, `Sm120Mxf4MmaDot64_v1` and
`GemmCoordinate{E4m3,Nvf4,Mxf4}_v1`, or reuses any existing ids; see `lanes/proofs-gemm-defs/NAMES.md`.

- **Don't** write step primitives or GemmCoordinate composites yourself, so the two branches don't conflict.
- **Keep:** anchoring E5M2 on a PRO 6000, the total (NaN/Inf) semantics probes, and the MXFP4 NaN-scale probe. Push your
  branch so the Definitions worker can merge your probe results.
- If you already wrote Definition code, push it now and say so in a note in `lanes/proofs-gemm-defs/`.
