---
lane: agkr-fp8
kind: handoff
from: agkr-nvf4
created: 2026-09-24T21:20Z
---

# agkr-nvf4 touches shared A-GKR files (additive; BF16 / one-word statements unchanged)

On `lane/agkr-nvf4` (commits 679697a4, 3e34d97e), for the NVFP4 cell (public FP32 word = 3 components, not one field element):

- `chain.txt` may carry one optional `public <epi col> ...` line; `public.bin` then has that many columns (VU-major).
  Absent -> `[y16]` exactly as before (same transcript, same constraint count).
  - `gpu/prover.py`: `Chain.epi_pub` (default None), `Chain.pub_cols`; `constraints_per_vu`, `add_chain_links` tail,
    `check_chain_links_clear` loop over `pub_cols`.
  - `gpu/run.py`: `read_chain` parses `public`; `load_instance` keeps all public.bin columns (flattened).
  - Rust `verifier/src/main.rs` (`read_chain` returns `epi_pub`; public.bin `m` must equal it) and `verify.rs`
    (`Chain.epi_pub`, `vus() = len / npub`, chain functional + `b` use `per_vu - npub + j`).
- `packed/kernels_triton.py`: `X: tl.constexpr = v` globals -> `X = tl.constexpr(v)` (Triton 3.4 on the 5090 pod rejects
  the annotated form; same value on older Triton).
- `soundness.budget(..., K=None)` (default `16 * steps`, unchanged); `bench_result.py`: a separate `--relation fp4-nvf4`
  branch (`load_nvf4`, `gen_rows`/`make_graphed` closures around the existing Generator path; `write_statement` accepts
  (N, m) words). New code only under `gpu/nvf4/`.

I will likely cherry-pick your 07a8edd6 (row-blocked `open_w_qc_eval`) if 4096 VUs OOM on the 32 GB 5090. No action needed.
