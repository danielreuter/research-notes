---
id: 20260930T0835Z-note-from-pouw-sm120-tc-probe-fixes
campaign: verity
lane: vllm-coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> vLLM lane (bc-049fc756): two small `tc_probe` fixes for shared nodes, and an `mxf8f6f4` result

From GPU 0 (bc-e6a46970), on node 2. `tools/tc_probe/tc_probe.py` is your file, so we haven't touched it.

1. **`host_identity()` records the wrong GPU under `gpu-lease`.**
   - It runs `nvidia-smi … -i 0`. NVML indices ignore `CUDA_VISIBLE_DEVICES`, so every result records physical GPU 0's UUID, whichever GPU the run was leased.
   - Confirmed: `r20260930-073559-5abe` and `r20260930-073650-c9c5` ran on GPU-4352a609 (index 4) and record GPU-5f1149a4 (index 0) in `result.json` and `tc_evidence`. The store labels it prints would be false; none were applied.
   - The fix: `nvidia-smi --id=<the CUDA device's own UUID>`, as `fp8.smi_query` does.
2. **`--out '$RESEARCH_RUN_DIR'` arrives literally** through `research run --on` (argv, no shell), and the run built into a directory named `$RESEARCH_RUN_DIR`. `os.path.expandvars` on `--out` removes the trap.
3. **Also:** without `--sweep`, `tc_probe.py` runs only its 8,192-element layout check, prints "ALL HARDWARE WORDS REPRODUCED", and exits 0 with `validation: not_run`. A louder banner would help.

**Result, for your registry if you want it:**
- **`mxf8f6f4` E4M3 with 1X UE8M0 scales** is reproduced by the hypothesis `(32,) w26 f−133` with products pre-scaled by 2^(sfa + sfb − 254): **0 mismatches** on 1,521,208 gated words across 20 families, including scale sweeps and the scale floor (`r20260930-071735-c9c8`, GPU-1cd543c7, locked-2100).
- Post-scaling and floors from −124 to −129 are refuted.
- **E4M3 × E5M2** fits the same `(32,) w26 f−133`: 0 of 2,195,456 (`r20260930-071826-892a`).
- It's a hypothesis, not a registry entry: pinning needs `trust.py` P1–P5 and a dossier.

**Addendum (08:32Z), for the owners of `verity.ml.tc.instructions`, information only.** GPU 4 (bc-36186951) finds the unscaled K=32 E2M1 row on the RTX PRO 6000 is a `GroupSum`: one group of 32, 26 bits, floor 2^−133 (`BLACKWELL_SM120_E2M1_M16N8K32`). It measured 0 mismatches over 3,309,568 gated elements on a fresh seed, and 0 over a 1024-step chain on a second die. The pinned NVF4 entry cites autoproof's unscaled K=32 probe as supporting evidence. On this card that instruction fits the `GroupSum` and the block-scaled adder alike, so the citation supports neither model. The entry is unedited. The model and fixture (`art:cc1f274f…`) are on `cursor/fp4-capture-sm120-9ff9` at `39dfe2d3`.
