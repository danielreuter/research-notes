20260930T0240Z open: started (agent bc-f23795f4-fb08-523a-a894-44ef03ab3ebd). CPU survey of FP8 checkpoints first; no pod until the vy-sm120- line is confirmed here.
20260930T0244Z open: budget line confirmed; hub survey of FP8 releases for the 17 representable models under way.
20260930T0249Z open: survey done (only Qwen3-4B/Qwen3-30B-A3B have official block-FP8); writing a data-free block-128 recipe for the rest.
20260930T0309Z open: recipe verity-fp8-block128/v1 (data-free, amax/448 per 128x128 block, RNE e4m3, deterministic container) written; QWEN05 made on VM in 6s, verified by the reference safetensors parser, accepted by quant_refusal. Downloads under way; next: pins for 13 models + tests.
