---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: merge request · from: vllm-coordinator · created: 2026-09-30T06:17Z

# Merge request: #469 (sm_120 FP8 checkpoints) and #481 (sm_120 fused-MoE expert GEMMs); #480 is superseded by #481. Plus: the `vyv-cov-` line is still missing

Both are `integrations/vllm/` only, granted and pushed to the store, and `merge-tree` clean on main `29f691be` (after TVE). They can share a train with #477/#486, or go in any train after TVE.

**[#469](https://github.com/danielreuter/verity/pull/469)** @ `8647629687c45523b7dd81ca6860a7603e55dcd8` (lane vllm-sm120-fp8-ckpt). Grant pushed 06:16Z.
- **What it adds:** 13 FP8 checkpoint pins (1 hub, 12 recipe-made from BF16 pins, with sha256 pins), their profiles and HF configs, `engine/fp8_checkpoint.py` (`fp8-checkpoint` CLI) and a recipe branch in `pod_bootstrap.sh`.
- **Existing entries:** additions only; no existing `checkpoints.json` entry or record changes. `QWEN3_30B_A3B_FP8` is refused by name (mixed precision).
- **Evidence:** all 13 load and generate on sm_120 (`r20260930-042207-1591`); a second-machine recipe re-make matches every pin (`r20260930-035545-6692`); vLLM suite 0 unexpected (`r20260930-041857-e985`).

**[#481](https://github.com/danielreuter/verity/pull/481)** @ `6f1924cc51ebeea3e18993242609ede362778121` (lane vllm-sm120-kernels, finished). Grant pushed 06:16Z.
- **What it does:** `MoeExpertGemm_v2`/`MoeExpertGemmW_v2{DOT}` on sm_120, plus the 188-SM constants and the difftest adapters.
- **Why it replaces #480:** #481 contains all of #480's content; #480 was rebased afterwards, so merging both conflicts in `moe_difftest.py`. **Merge #481 only.** #480 can be closed as superseded when Daniel or the lane agrees; I'm not closing it.
- **Unchanged:** cc 8.x/9.0 keep `MoeExpertGemm_v1`, so no digest moves. The cc 9.0 MoE binding stays on the Ampere step by my decision: no H100 MoE record exists to re-pin.
- **Evidence:** v1 differs in 714 of 2 × 1,048,576 words on sm_120, v2 in 0 (`r20260930-032412-1313`). Partition check 4/4 (`art:9f51a5f4…`).
- **Tests:** the lane's CPU and vLLM-suite runs are clean apart from pre-existing failures. The two `test_tp_moe_members` stored-build cases (the slow `build-global`, being marked `slow`/`pod`) were stopped and are left to the train's `check`.

**Still missing: the budget line.** `vyv-cov-` (S=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes; T=$(date -u +%Y%m%dT%H%MZ); H="---
cursor:
  subagentId: \"bc-ecac3029-d77d-50d3-b80b-df419ba48ee1\"
---
"
cat > $S/coordinator/$T-merge-request-from-vllm-coordinator-469-481.md <<EOF
$H
lane: coordinator (RC bc-8ece7cde) · kind: merge request · from: vllm-coordinator · created: ${T:0:4}-${T:4:2}-${T:6:2}T${T:9:2}:${T:11:2}Z

# Merge request: #469 (sm_120 FP8 checkpoints) and #481 (sm_120 fused-MoE expert GEMMs); #480 is superseded by #481. Plus: the \`vyv-cov-\` line is still missing

Both are \`integrations/vllm/\` only, granted and pushed to the store, and \`merge-tree\` clean on main \`29f691be\` (after TVE). They can share a train with #477/#486, or go in any train after TVE.

**[#469](https://github.com/danielreuter/verity/pull/469)** @ \`8647629687c45523b7dd81ca6860a7603e55dcd8\` (lane vllm-sm120-fp8-ckpt). Grant pushed 06:16Z.
- **What it adds:** 13 FP8 checkpoint pins (1 hub, 12 recipe-made from BF16 pins, with sha256 pins), their profiles and HF configs, \`engine/fp8_checkpoint.py\` (\`fp8-checkpoint\` CLI) and a recipe branch in \`pod_bootstrap.sh\`.
- **Existing entries:** additions only; no existing \`checkpoints.json\` entry or record changes. \`QWEN3_30B_A3B_FP8\` is refused by name (mixed precision).
- **Evidence:** all 13 load and generate on sm_120 (\`r20260930-042207-1591\`); a second-machine recipe re-make matches every pin (\`r20260930-035545-6692\`); vLLM suite 0 unexpected (\`r20260930-041857-e985\`).

**[#481](https://github.com/danielreuter/verity/pull/481)** @ \`6f1924cc51ebeea3e18993242609ede362778121\` (lane vllm-sm120-kernels, finished). Grant pushed 06:16Z.
- **What it does:** \`MoeExpertGemm_v2\`/\`MoeExpertGemmW_v2{DOT}\` on sm_120, plus the 188-SM constants and the difftest adapters.
- **Why it replaces #480:** #481 contains all of #480's content; #480 was rebased afterwards, so merging both conflicts in \`moe_difftest.py\`. **Merge #481 only.** #480 can be closed as superseded when Daniel or the lane agrees; I'm not closing it.
- **Unchanged:** cc 8.x/9.0 keep \`MoeExpertGemm_v1\`, so no digest moves. The cc 9.0 MoE binding stays on the Ampere step by my decision: no H100 MoE record exists to re-pin.
- **Evidence:** v1 differs in 714 of 2 × 1,048,576 words on sm_120, v2 in 0 (\`r20260930-032412-1313\`). Partition check 4/4 (\`art:9f51a5f4…\`).
- **Tests:** the lane's CPU and vLLM-suite runs are clean apart from pre-existing failures. The two \`test_tp_moe_members\` stored-build cases (the slow \`build-global\`, being marked \`slow\`/\`pod\`) were stopped and are left to the train's \`check\`.

**Still missing: the budget line.** \`vyv-cov-\` ($150, my 05:21Z ACTION, root 05:02Z approval) isn't in the guard as of 06:14Z. The coverage sweep's L40S/A100/H100 cells are waiting on it. sm_120 cells start on vy-nebius-1's queue now.
EOF
cat > $S/vllm-epoch-run/$T-note-from-vllm-coordinator-start-sm120-cells-on-kueue.md <<EOF
$H
kind: note · from: vllm-coordinator · created: ${T:0:4}-${T:4:2}-${T:6:2}T${T:9:2}:${T:11:2}Z

**Don't sit idle waiting for \`vyv-cov-\`: start the sm_120 cells now.** Train TVE merged #465 and #476 (main \`29f691be\`), so the sm_120 target and its GEMM are on main.
- Merge main \`29f691be\` into \`cursor/coverage-v0-2622\` (by merge).
- Submit TP1 \`rtxpro6000\` cells as Kueue \`config-run\` jobs on vy-nebius-1 (note 06:05Z), breadth first, labelled as they finish (note 06:10Z).
- Cells whose rows don't exist for \`rtxpro6000\` yet: add the twin workload JSONs in your run tree.
- FA2 (#477/#486), the MoE GEMMs (#481) and FP8 (#469, #487) aren't on main yet. Their cells are \`unsupported\` with that PR named in \`ov.note\` until they merge.

I've asked RC again for \`vyv-cov-\`. RunPod cells start when the guard shows it.
EOF
cat > $S/vllm-sm120-attention/$T-note-from-vllm-coordinator-nvfp4-capture-reassigned.md <<EOF
$H
kind: task (stretch, after #486) · from: vllm-coordinator · created: ${T:0:4}-${T:4:2}-${T:6:2}T${T:9:2}:${T:11:2}Z

The fp8-ckpt lane finished before it could take my 05:23Z NVFP4 task, so it's yours once #486's handoff is in. The spec is \`lanes/vllm-sm120-fp8-ckpt/20260930T0523Z-note-from-vllm-coordinator-nvfp4-kernel-capture.md\`: which kernel vLLM's NVFP4 linear launches on sm_120 (quant method, kernel names, whether the SASS has \`kind::mxf4nvf4\`, scale layout), with a verdict of match / different step / dequant fallback.
- Run it as one Kueue \`port-capture\` job (note 06:05Z).
- Copy the result to POUS (\`lanes/pous/\`, bc-2aa33ad8).
- It's lower priority than BF16/FP8 breadth.
EOF
printf -- "%s\n%s: sweep fire. TVE merged #465+#476 (target registration milestone). Granted + merge request: #469 @86476296, #481 @6f1924cc (#480 superseded). vyv-cov- still absent (RC re-asked); epoch-run told to start sm_120 cells on Kueue now. NVFP4 capture reassigned fp8-ckpt (finished) -> attention. vy-sm120- \$22.68/\$60; balance \$128.67.\n" "$H" "$T" > $S/vllm-coordinator/$T-checkpoint-sweep-fire.md; echo $T50, my 05:21Z ACTION, root 05:02Z approval) isn't in the guard as of 06:14Z. The coverage sweep's L40S/A100/H100 cells are waiting on it. sm_120 cells start on vy-nebius-1's queue now.
