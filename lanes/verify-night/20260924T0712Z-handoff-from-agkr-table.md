# A-GKR A100 BF16: verify art:21d253bd (the faster 1.74 s result; proofs byte-identical to art:03e21c7f)

From lane agkr-table, 07:12Z. Follow-up to `20260924T0644Z-handoff-from-agkr-table.md` (you verified art:03e21c7f at
07:00Z, thank you). The Table 2 predicate's only rejection reason for the new result is `not independently verified`.

**Result**
- bench-result/v1 `art:21d253bd2b9ab59f6ab6ad2689dc4d1bb89b7137c0f225c6101fbed9b080bda2` (attempt r20260924-065721-3ac3,
  PRESERVED; source lane/agkr-table @ be2d8af4); run-files `art:1fbd535f889e23ba797373c6b5ff1b5074dc8d758f8cface0d3f0caf27c52042`.
- t.total median 1.736 s (reps 1.754 / 1.717 / 1.736) vs 2.775 s for art:03e21c7f. The prover changes are in the
  opening (q by evaluation instead of a GEMM) and the witness generator (a CUDA graph) -- the proof bytes are
  unchanged: `proofs/rep{0,1,2}.bin` sha256 `f2c058519710faaa2cabae0fa8557ddfd82e7e48c1adf930e7f809623074729c`, the same
  as art:83324658's. `statement/` is built the same way (same Params files, public.bin = frozen y[0:4096]).

**Verifier**: unchanged since 53bd441b (`backends/gkr/verifier`; your binary sha256 ee899383c03cfac3 is the right one).

**Command** (per rep; `DIR` = `research data fetch art:1fbd535f --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exactly what you recorded for art:03e21c7f -- exit 0, accepted, vus 4096, units 393216, steps 96,
slots 3524, msgs 11843, bytes_read 21213880, ligero_rows 26644, committed_elements 109132728; ~3-4 s at 15 threads.

Further results from this lane today should also carry these proof bytes (the next change moves the Fiat-Shamir sponge
of the LogUp rounds onto the GPU; the transcript is the same by construction and I check the bytes before recording).
I will append their art ids here rather than open new handoffs.

**Appended 07:47Z** -- bench-result/v1 `art:f47f8006711b79348e8bc605fbbdf5495c117752036473b4a82dda0c48388d3a` (attempt
r20260924-071929-6745, PRESERVED; source lane/agkr-table @ bab91f23, the LogUp sponge on the device); run-files
`art:8db49ca05e52e5a42367e367e500991ae635e414ce6085ba73971eccb2bfe59e`. t.total median 1.424 s (reps 1.428 / 1.421 /
1.424). `proofs/rep{0,1,2}.bin` sha256 `f2c058519710faaa2cabae0fa8557ddfd82e7e48c1adf930e7f809623074729c` (unchanged);
same command with `DIR` = `research data fetch art:8db49ca0 --to DIR`, same expected output.
