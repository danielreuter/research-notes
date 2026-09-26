---
cursor:
  subagentId: "bc-231b1a72-2c21-58bc-b207-c9ee2ac71772"
lane: coordinator
kind: handoff
from: sp1-evaluator (bc-231b1a72)
created: 2026-09-26T07:05Z
---

# sp1-evaluator: SiLU·mul on SP1 and a sampled #101 cover, done. Merge request (PR #58) and non-producer verify request

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request

- **PR:** [PR #58](https://github.com/danielreuter/verity/pull/58), `lane/sp1-evaluator` into `main`, tip `0a652c36`. It holds two commits on top of main `1b818427` (#52 merged), and merges cleanly.
- **Commit `13405f08`:** `verity.proofs.elem_bf16` promotes `veritor.elem-bf16@1`.
  - The digest `06172374…` equals `GateSet::resolve`'s.
  - The SiLU table is regenerated from the registered float64 formula. It must hash to the guest's `elem_silu_table.bin` (`bd9cb7bd…`), otherwise it raises. Making it match meant decoding −0 as +0, as the IR does.
  - The gates equal the IR primitives on 300,000 random pairs.
  - It's registered in `family_gate_set` and `SUPPORTED_FAMILIES`.
- **Commit `0a652c36`:** `ir_call` gains the elem-bf16 family (`SiluMul_v1`), and `benchmarks/ir_call/sp1_cover.py` is the chunked cover driver.
- **Tests:** the proofs, SP1, boundary and protocols suites pass (346), including the new `test_elem_bf16_is_the_guests`.
- **Unchanged:** no Rust, ELF, verifying key or semantics change.

## Results

All runs used the approved guest (ELF `cef2b78a`, vk `0x007d9347`, reproduced on each pod) with compressed proofs and `authentication=included`. Every chunk was accepted, and every run's three negatives were rejected by both the guest and the Python reference. Each run carries 17 labels by `sp1-evaluator` (`sweep=101-sampled-cover`), with a `note --ref` to its prepare run.

- **Snapshot:** `sp1-101-sampled-cover-20260926`, `art:33c34aa2d278742998fb304504558af3276628a8b531b0b860b8d6f509562fd6`, PRESERVED. Its members are the 7 cover results and the 7 prepare results.
- **Summary JSON:** `note:` `lanes/sp1-evaluator/evidence/101-sampled-cover-summary.json`, next to `cover_summary.py`, which computes it.

The draw is #101's `replay_partition.sample`: 1,374 VUs.

| Template | Proven | Drawn | Cover run (result) | Prepare run | Compressed t.total | Per instance | Proofs | Soundness (union bound) |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| RMSNormFusedCuda_v2 N=2048 | 256 rows | 256 VUs | r20260926-034955-d892 (`art:7946731a`) | r..032831-2477 | 638 s | 2.49 s | 8 | 2^-89.7 |
| RMSNormTriton_v1 N=2048 | 8 rows | 8 VUs | r20260926-033603-f9db (`art:9db5ba4b`) | r..032430-e0b5 | 22.7 s | 2.84 s | 1 | 2^-94.7 |
| SiluMul_v1 I=8192 | 128 rows | 128 VUs | r20260926-033832-8524 (`art:a8306205`) | r..032451-e97c | 276 s | 2.16 s | 4 | 2^-91.1 |
| SiluMul_v1, rows 128–255 (completes the 256-row set) | 128 rows | — | r20260926-060409-6ac5 (`art:60fb1d0d`) | r..035254-c31a | 203 s | 1.59 s | 4 | 2^-91.1 |
| RoPE_v1 D=64 | 1,024 heads | 256 VUs = 5,120 heads | r20260926-034726-3955 (`art:1797cc4e`) | r..032809-5920 | 53.7 s | 52 ms | 1 | 2^-93.5 |
| GEMM K=2048 | 6,272 coords | 391 VUs = 3,650,304 coords | r20260926-061318-2f7f (`art:fdbb9812`) | r..032430-2152 | 1,358 s | 0.217 s | 25 | 2^-88.4 |
| GEMM K=8192 | 1,920 coords | 128 VUs = 262,144 coords | r20260926-040909-ffa5 (`art:cba6c36f`) | r..032430-df49 | 2,161 s | 1.13 s | 30 | 2^-88.2 |

**Totals:** 4,509 s of compressed proving and 73 proofs of 1.27 MB each.

**Soundness:** the column is SP1's 100 bits per STARK proof, union-bounded over an estimated count of proofs. That count is two per core shard, with core shards estimated as cycles / 4.73M, to cover the recursion tree.
- This corrects my 02:50Z handoff, which gave compressed proofs as 2^-100.
- All of it is below the tables' 2^-128.

### Work-weighted overhead and share of the draw covered

The native hardware is L40S and the prover is a 4090.

| Basis | Work-weighted overhead | Share of the supported draw's native work | Share of the whole draw's |
| --- | ---: | ---: | ---: |
| GEMM at BF16 tensor peak (362 TFLOPS, the Table 2 convention); the others at 864 GB/s HBM traffic | 3.2e8× | 20.4% | 3.2% |
| Every template memory-bound (a GEMM coordinate reads its 2K-byte weight row, i.e. batch-1 decode) | 5.6e7× | 0.36% | 0.35% |

**Per-template overhead** (first basis): GEMM 1.9e10–2.5e10×, RMSNorm 1.0e8–2.0e8×, RoPE 1.2e8×, SiLU·mul 3.8e7×. These are compressed-proof times that include per-chunk fixed costs. At the core batch rates in my 02:50Z handoff, each is about 2× lower.

**Excluded from the cover:**
- **Attention_v3, 192 VUs:** an estimated 366 µs of native work, the largest share of the draw on the first basis.
- **GumbelTopPTokenSelect_v1, 7 VUs.**
- **Why:** no existing guest family evaluates either.
- **Embedding_v1, 8 VUs:** a commitment opening, not a subcircuit.

**Why coverage is partial where it is:**
- **GEMM:** the export holds 32 coordinates of each sampled row, from 196 and 60 VUs, while the protocol draws whole rows.
- **RoPE:** the export holds 4 heads per VU.
- **RMSNorm, Triton and SiLU·mul:** covered at the draw's full size.

### GEMM and `relation-bare`

Not used. `bare::K = 1536` is a compile-time constant that the guest checks against the header, and #101's GEMMs are K=2048 and K=8192.

**To cover the draw's GEMM VUs:**
1. Export the drawn VUs whole, with all N output coordinates. That is the vllm-vu-export lane's exporter, with `gemm_coords_per_row` set to all.
2. Then either:
   - **the checker guest, as now:** authentication included, about 0.22 s (K=2048) and 1.13 s (K=8192) per coordinate, compressed, so about $190; or
   - **a `relation-bare` build with K taken from the header:** a new ELF and vk that needs approval, with authentication excluded, at about 33k cycles per K=1536 VU scaled with K, so about $6.

## Non-producer verify request

For each cover run, and each chunk `chunkNNN` of it:
1. **Get the object.** Download the prepare run's `objects/chunkNNN.json.gz`, from its run files or `research data fetch <prepare result art>`. Recompute `h_O = object_digest(obj)` yourself, and the statement bytes with `verity.proofs.lowering.statement_bytes_v3(obj)`.
2. **Check the statement.** Its sha256 must equal both `meta.json`'s `chunks[i].statement_sha256` and the statement inside `bundle.tgz`.
3. **Check the proof.** Take the proof from the cover run's `run_files` at `proofs/chunkNNN-compressed.bin`. Run `veritor-zk-host verify --proof <p> --statement <statement.bin>` from your own build of `backends/sp1`; its `info` must be ELF `cef2b78a…`, vk `0x007d9347…`.
4. **Accept** only if all of these hold:
   - the proof verifies;
   - the vk is the APPROVED one;
   - the build is not a diagnostic one;
   - `statement_match` is true;
   - the public values are exactly `h_O || sha256(statement) || 01`.

That's 73 compressed proofs, each verifying in about 0.07 s after about 15 s of key setup. The three negatives per run were checked in the executor only; their objects are `objects/neg-*.json.gz`. My 02:50Z spike runs are still waiting for the same check.

## Incidents, pods and spend

- **Reaped pod:** the steward's reaper terminated the first pod, `am0dh7td6pwiv8`, at 05:44Z as idle. The queue driving the pod ran on this agent's VM, which stopped while my turn was ended.
  - **Data:** nothing was lost. The K=8192 run had finished and was preserved.
  - **Recovery:** I relaunched the last two runs on `pai4lo7hpqo7ug`, from inside the turn.
- **Pods:** both are terminated, the second drained with all 11 attempts preserved.
- **Spend:** about $1.67 plus $0.75, so about $2.40 of $25.
