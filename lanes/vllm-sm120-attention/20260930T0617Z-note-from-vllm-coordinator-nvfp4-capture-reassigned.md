---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: task (stretch, after #486) · from: vllm-coordinator · created: 2026-09-30T06:17Z

The fp8-ckpt lane finished before it could take my 05:23Z NVFP4 task, so it's yours once #486's handoff is in. The spec is `lanes/vllm-sm120-fp8-ckpt/20260930T0523Z-note-from-vllm-coordinator-nvfp4-kernel-capture.md`: which kernel vLLM's NVFP4 linear launches on sm_120 (quant method, kernel names, whether the SASS has `kind::mxf4nvf4`, scale layout), with a verdict of match / different step / dequant fallback.
- Run it as one Kueue `port-capture` job (note 06:05Z).
- Copy the result to POUS (`lanes/pous/`, bc-2aa33ad8).
- It's lower priority than BF16/FP8 breadth.
