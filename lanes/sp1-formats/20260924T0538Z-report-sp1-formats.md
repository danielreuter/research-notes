---
lane: sp1-formats
kind: report
created: 2026-09-24T05:38Z
status: final
---

CHECKPOINT none (16:01Z) [final] Closed by coordinator 16:02Z: work was complete at 07:46Z (transcript: four SP1-stock format cells registered at 3510cfcf, handed to verify-night, all sp1-formats pods terminated, tip 2b0cc33a); the lane ended its turn without writing FINAL.
CHECKPOINT none (07:45Z) [open] tip 2b0cc33a (merged sp1-table 65aa6a12; tests 85 pass). Cells @3510cfcf stand: indexed layout gives nothing (all 4 sets 4096+4096 distinct rows). All sp1f pods terminated.
CHECKPOINT 3510cfcf (07:43Z) [open] All 4 B=4096 cells re-proved + registered @3510cfcf (vk 0x00a42aa3): fp8-ada art:8d9df3a2 23.53s, fp4-nvf4 art:a8886e22 7.43s, fp8-hopper art:70e5bd29 20.74s, bf16-hopper art:76d13bb0 24.09s; handoffs verify-night + sp1-table 0742Z; all sp1f pods terminated.
CHECKPOINT 3510cfcf (07:27Z) [open] hill-climb 3510cfcf (elf 48bb5913): cycles/VU fp8-ada 39.4k (was 50.7k), fp8-hopper 37.2k (45.9k), fp4-nvf4 17.9k (34.4k), bf16-hopper 41.5k; oracle 4096/4096 x4 + negatives pass. Re-running all 4 cells at 3510cfcf (5090, H100 up; 4090 next).
CHECKPOINT 2581406f (07:07Z) [open] All 4 B=4096 cells registered @2581406f: fp8-ada art:0a8697da 25.93s, fp4-nvf4 art:f3072b13 14.17s, fp8-hopper art:30a1f28a 23.22s, bf16-hopper art:ef2d91ce 24.22s; instances art:4a6f7602. Next: verify-night + sp1-table handoffs, then hill-climb.
CHECKPOINT 2581406f (07:04Z) [open] tip 2581406f (elf 504423b7). Registered B=4096 cells: fp8-ada art:0a8697da (t 25.93s), fp4-nvf4 5090 art:f3072b13 (14.17s), fp8-hopper art:30a1f28a (23.22s); instances art:4a6f7602. bf16-hopper proving on H100. Inbox: 3 read (b5e1ed5f merged; guardian kills noted).
CHECKPOINT eb0a77a4 (05:43Z) [open] eb0a77a4: native oracle 4096/4096 y bit-exact on fp8-ada, fp8-hopper, bf16-hopper, fp4-nvf4 (negatives refused); handoff to sp1-table on arm shape; next: SP1 execute cycles via scratch harness on vy-sp1f-4090
CHECKPOINT d0d5ab7a (05:38Z) [open] started 05:25Z; d0d5ab7a: Rust arithmetic for bf16-hopper/fp8-hopper/fp8-ada/fp4-nvf4 (unit tests pass), native oracle + instance generator; 4090 pod vy-sp1f-4090 bootstrapping; next: generate frozen sets on pod, oracle 4096/4096

## Results (07:42Z): the four B=4096 cells at 3510cfcf (hill-climb; these supersede the 2581406f cells below)

Same flow as below, from host `9b36a54e…` built at 3510cfcf on vy-sp1f-5090 and copied to the H100 and a new 4090. The
guest ELF is `48bb5913…` and the vk is `0x00a42aa3…a599`. Statement bytes are identical to the 2581406f cells. The native
oracle at 3510cfcf again gives 4096/4096 on all four sets with every negative rejected. Each cell rejected 3/3 flip-y
negatives, and every envelope conforms. Handed to verify-night at `20260924T0742Z`. All pods are terminated.

| row | run | bench-result | run-files | y 4096/4096 | cycles/VU | cycles | shards | t.total | proof B | verify | overhead vs peak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RTX 4090 FP8 fp8-ada | r20260924-073604-222f | art:8d9df3a2 | art:8f3a4cfc | yes | 39,097 | 160.1M | 36 | 23.53 s | 54.1 MB | 2.59 s | 6.18e8 (330.3 TF) |
| RTX 5090 NVFP4 fp4-nvf4 | r20260924-072715-1793 | art:a8886e22 | art:5bd375d2 | yes | 17,623 | 72.2M | 14 | 7.43 s | 21.2 MB | 0.62 s | 9.90e8 (1676 TF) |
| H100 FP8 fp8-hopper | r20260924-072723-6a27 | art:70e5bd29 | art:4d63c357 | yes | 36,905 | 151.2M | 24 | 20.74 s | 36.7 MB | 1.20 s | 3.26e9 (1979 TF) |
| H100 BF16 bf16-hopper | r20260924-073110-41cb | art:76d13bb0 | art:0cabdd77 | yes | 41,475 | 169.9M | 30 | 24.09 s | 45.6 MB | 1.63 s | 1.89e9 (989 TF) |

- bf16-hopper's kernel is unchanged since 2581406f. Its cell was re-proved only so that all four rows share one vk.
- fp8-ada ran on a different 4090 host (EPYC 7763, load about 29) from the 2581406f cell (EPYC 9354). Its cycles fell
  23%, but t.total fell only 9%, so part of the gap may be the host CPU.
- The t.total cuts (fp4-nvf4 −48%, fp8-hopper −11%, fp8-ada −9%) track the shard count more than the cycle count.
- Tip `2b0cc33a` merges sp1-table's `65aa6a12` (dispatch in `check_pair`, indexed layout). Common tests pass (85).
  sp1-table's indexed layout gives these rows nothing: each of the four sets has 4096 distinct x rows and 4096 distinct
  W rows, so nothing is shared. No cell was re-proved from the merge.

## Results (07:16Z): the four B=4096 cells at 2581406f

All four come from the same host binary (`veritor-zk-host-cuda-relation-bare`, sha256 `6d9bb305…`), built on vy-sp1f-4090
by `evidence/pod-scripts/build_bare.sh` and copied pod to pod to the 5090 and the H100. The guest ELF is `504423b7…`
and the vk is `0x00a8ed87…565a`. Each cell is `research run … vector_run.py --backend sp1-bare --batch <fmt>.bin --reps 3`,
median of 3. Every cell's envelope conforms. Its Table 2 reasons are only SP1's 100-bit target (achieved about −95
after the union bound) and "not independently verified", which is handed to verify-night (`20260924T0712Z`).

| row | run | bench-result | run-files | y 4096/4096 | cycles/VU | cycles | shards | t.total | proof B | verify | overhead vs peak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RTX 4090 FP8 fp8-ada | r20260924-064859-e3ba | art:0a8697da | art:2c9abdc5 | yes | 50,704 | 207.7M | 42 | 25.93 s | 63.1 MB | 2.43 s | 6.81e8 (330.3 TF) |
| RTX 5090 NVFP4 fp4-nvf4 | r20260924-065225-185b | art:f3072b13 | art:bede8807 | yes | 34,438 | 141.1M | 25 | 14.17 s | 37.9 MB | 1.14 s | 1.89e9 (1676 TF) |
| H100 FP8 fp8-hopper | r20260924-065901-3794 | art:30a1f28a | art:328ed64d | yes | 45,880 | 187.9M | 28 | 23.22 s | 42.7 MB | 1.40 s | 3.65e9 (1979 TF) |
| H100 BF16 bf16-hopper | r20260924-070246-361e | art:ef2d91ce | art:114f46e9 | yes | 41,475 | 169.9M | 30 | 24.22 s | 45.6 MB | 1.49 s | 1.90e9 (989 TF) |

- Instances: `art:4a6f7602` holds the four sp1-format-instances/v1 files, generated on the pod by
  `verity_sp1.format_instances` from the canonical Ligero recipes, with each recipe digest checked against the contract.
- "y 4096/4096" rests on two checks. The native oracle (`examples/format_oracle.rs`, run on the pod) matches every y
  bit-exactly, and rejects perturbed-y and off-domain rows. And the guest's verdict at B=4096 is accept, with 3/3
  flip-y negatives rejected per cell.
- The 5090 (sm_120) is supported by SP1 6.4.0's CUDA `sp1-gpu-server`. No substitution was needed.
- The H100 host CPU was shared (load around 18). The H100 cells prove at about the 4090's cycles/s, so their t.total is
  probably CPU-bound in SP1's pipeline.
- Handoffs out: sp1-table 06:35Z (stale embedded guest), sp1-table 07:16Z (tip with the arms), verify-night 07:12Z.
- Inbox, all acted on: sp1-table 06:20Z (merged `b5e1ed5f`; arms done), coordinator 06:28Z and 06:42Z (guardian kills of
  my laptop-side launcher; later launches detached on the pod or short).
