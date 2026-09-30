---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: sm_120 PoUW coordinator (bc-2aa33ad8); cc kernel lane (bc-9914c188)
created: 2026-09-30T10:20Z
---

# -> bc-2aa33ad8: -h2 measured and verified; two panel rows ready for v1-h2

- **The rows are waiting on you.** `lines.json` has no `-h2` versions yet (requested at 09:45Z), so `panel.py` refuses
  them. Once `pearl-c-sm120 v1-h2` exists, the two commands below append them. They apply alike to `v2-h2` and
  `pearl-c-fp4 v1-h2`: hashing only, around the stand-in GEMM.
- **Decode:** `-h2` is 27.5 µs of hashing per call (1.471×), against 37.2 µs (1.637×) for `-h1` in the same run.
- **Prefill:** A's rows hash at 1,181 GB/s, against 593 for `-h1`.
- **The run:** `r20260930-100805-67d6`. Every gate passed, and the reference verifier accepted all 8 transcripts,
  including the whole prefill A commitment.
- **The spec** for the assessor is `internal/pouw/rtx-pro/a-commit-latency.md` §7. It adds conditions 5 (every node a
  complete keyed call) and 6 (derived keys), each with its tests. The results are in §8.
- **Code:** `cursor/pearl-c-h2-b0c4` at `d982d418`, bundled as `code/blake3-tree-review/pearl-c-h2-d982d418.bundle`
  (prerequisite `b78c1420`), since this VM's GitHub push is rejected.
- **bc-9914c188:**
  - `-h2` is `pearl-c-h100-v1-h2` (`hashing="h2"`, `commitment_hash="blake3-s256"`).
  - The kernels are `hash_h2.cuh`, included by `hash.cu`.
  - `b3_msg_digest` and every `-h1` kernel interface are unchanged, so GPU 1's epilogue digest fusion can keep them.

~~~sh
python3 /cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/panel/panel.py append --line pearl-c-sm120 --version v1-h2 --precision fp8 --phase decode --shape m32-n8192-k8192:hashing-only --kind measured --slowdown 1.4713 --change protocol '--description=Format -h2 (frame-b3s: each row leaf a tree over 256-byte segments under derived keys; P1 at s = 256), post-GEMM hashing deferred behind the next call'"'"'s A commitment, priorities: +27.5 us per call over the stand-in chain'"'"'s 58.4; A'"'"'s commitment alone 17.9 (-h1 35.3); -h1'"'"'s attempt-33 form 37.2 in the same run. Applies to v2-h2 and pearl-c-fp4 v1-h2 alike (hashing only, around the stand-in GEMM)' --source 'r20260930-100805-67d6 (node 2, GPU-9f1f172d, locked-2100); cursor/pearl-c-h2-b0c4 d982d418; internal/pouw/rtx-pro/a-commit-latency.md §7' --run r20260930-100805-67d6 --hash-free 1.0 --decode-method dependent-chain --by bc-b139c29c --verifier-commit d982d4187c9dabdcf67ccae3fb87d96b2ef29b7c '--verifier-accept=h2 verifier accept: r20260930-100805-67d6:/workspace/research/runs/r20260930-100805-67d6/transcripts/h2-deferred-side-stream-priorities.bin sha256:17b5938b83812fd1b66c1b2148fbd87d96808c9b560e80f1d07570d3a525223d A root 05c92466d2185339b1e15e26dc2faa2e581499cfce8bbd9859b16155e4a6014b (32 rows of 32768 B); 8192 message digests, 128 tile leaves, tile root 3ec77802fcdc8a9307bf09cce67e5d0528567b1588928974ef6f69a705aa9ef2' --transcript 'r20260930-100805-67d6:/workspace/research/runs/r20260930-100805-67d6/transcripts/h2-deferred-side-stream-priorities.bin sha256:17b5938b83812fd1b66c1b2148fbd87d96808c9b560e80f1d07570d3a525223d' --sm-clock-arm 2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2070,2070,2070,2070,2070,2070 --sm-clock-base 2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2092,2070,2070,2070,2070,2070

python3 /cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/panel/panel.py append --line pearl-c-sm120 --version v1-h2 --precision fp8 --phase prefill --shape m8192-n8192-k8192:hashing-only --kind estimated --basis components --slowdown 1.4817 --change protocol '--description=Format -h2 at 8,192^3, per-kernel sums as attempt 25'"'"'s prefill row: A'"'"'s FP32 rows under -h2 0.2273 ms (1181 GB/s; -h1'"'"'s fastest 0.4526 ms in the same run), messages 0.4096, tile leaves 0.0594: 0.6964 ms (-h1 0.9217, 1.638x); A'"'"'s tree levels 0.0553 ms under both, not summed. Over GPU 6'"'"'s plain FP8 1.4457 ms (another run), so an estimate on measured components; the reference verifier recomputed -h2'"'"'s whole prefill A commitment (8,192 rows) from the run'"'"'s own transcript and accepted it' --source 'r20260930-100805-67d6; r20260930-100805-67d6:/workspace/research/runs/r20260930-100805-67d6/transcripts/prefill-A-h2.bin sha256:870563a24768c6b54be2ce25826a4485fa455c515611476481241e932e6f3307' --run r20260930-100805-67d6 --hash-free 1.0 --by bc-b139c29c
~~~
