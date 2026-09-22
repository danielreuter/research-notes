---
id: r20-proof/a-gpu-v2/20260922T1032Z-handoff-handoff
campaign: r20-proof
lane: a-gpu-v2
kind: handoff
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/gkr/gpu/HANDOFF.md
---

# a-gpu-v2 handoff (2026-09-22 ~10:00Z) — checker v2 in the GPU prover

State: **done for the lane's goal, honest label.**  The checker-v2 circuit (PROTOCOL §14) runs end to end in this
prover over BabyBear^6 on the A100: full VU ×4096 in **5.73 s median of 3** (1.40 ms/VU, `overhead.vs_native_peak`
1.42e8) with the BabyBear-sound limb-form epilogue, `NON_ZK_PROOF_DIAGNOSTIC`; 4096/4096 accepted; 52/52
`vu-k1536-neg`, a-v2's 30 unit + 4 chain, and 15/15 epilogue-column negatives rejected.  Same-box v1 control 7.93 s
(1.38x).  Branch `lane/a-gpu-v2`, everything committed; nothing running on `vy-a100b`.  Ledger
`backends/numerical/reports/ledger/a-gpu-v2.jsonl` (5 entries; run ids r20260922-090930-3bc5 word-form v2,
-091544-4e02 v1 control, -095013-db80 limb-form v2; negatives -090151-07aa).  DESIGN §5b, README "Checker v2",
PROTOCOL §14.6 last bullet.

## What changed (all additive; the v1 path is byte-identical — the v1 control run proves it)

* `circuit.py`: `itable` lines (implicit tables) + `Table.materialise` on device (`shift`/`tnorm`, mirrors
  `circuit.rs::materialise`); `R<w>` range tables are created from the queries (`range_table_width`); use
  **`Table.nrows` / `Table.device_rows(dev)` / `Table.dense`**, never `len(t.rows)` (`rows` is `None` for implicit
  tables).  a-gpu2's `prove()` hunk has one `len(t.rows) % 2` — change it to `t.nrows`.
* `prover.py`: `Chain.links: list[Link]` (v2, `main.rs::add_chain` order — the 12-column strided read; `links is
  None` = v1 limb chain), `union_tables(segs)` (the epilogue's `R8/R15/R16` are not in the unit's list; the Rust
  a-v2 prover misses them — reported in DESIGN §5b), `spec_hash` absorbed at transcript start.
* `logup.py`: `table_rows` via `device_rows`; `multiplicities` by `bincount` for dense tables.
* `run.py`: v2 manifests (`variant: v2`, `chain_file`), `read_chain`, `negatives` over named dirs,
  `unit-negatives`, `epilogue-negatives`.
* `gpu/v2/`: `export.py` (BabyBear `FieldApi` for `gkr_export.v2`; `export|synth|negatives|stats`;
  `BabyBearV2Api("limbs"|"word")`), `epilogue_limbs.py` (b-air-v2's `pack_limbs`/`epilogue_limbs` verbatim +
  circuit/witness builders), `tests/`, `results/` (JSONs of every run, `notes-asset:campaigns/r20-proof/assets/a-gpu-v2/results/z3_babybear_v2.json`).

## Pod layout (`vy-a100b`, A100-SXM4-80GB, `/workspace/venv312/bin/python`)

`/workspace/v2l/pos4096` (4096 `vu-k1536` VUs, limb epilogue) + `/workspace/v2l/neg` (52); `/workspace/v2/...` the
word-form set + `av2neg` (a-v2's generators); `/workspace/bb/pos4096` the v1 set; `/workspace/bench/v1` the built
bench-instances (the operand arrays are built, not committed).  Recorded runs: commit, then
`uv run research run --on vy-a100b --exclusive --project verity --source . --stage gkr.gpu.v2.X -- bash -c 'export
PYTHONPATH=$PWD/backends/gkr:$PWD/backends/numerical/python:$PWD/packages/verity/src; cd backends/gkr;
/workspace/venv312/bin/python -m gpu.run prove /workspace/v2l/pos4096 --device cuda --reps 3 --json
$RESEARCH_RUN_DIR/run.json'` (`gpu.run` alone needs only `backends/gkr`; the exporter needs all three).  Export:
`python -m gpu.v2.export export --root /workspace/bench/v1 --tier vu-k1536 --lo 0 --hi 4096 --out DIR --procs 48`
(~3 min).

## For a-gpu2 / a-fusion to absorb (the merge is mechanical: `git merge-tree` against both branches conflicts
only in the regenerated plot PNGs)

1. v2 per-bucket on the A100 at B=4096: lookup 2.85 / arith 0.36 / open 2.05 / commit 0.43 s.  **Lookup is the
   whole story**: 13 shallow trees (T_OP and SHIFT n=24, the rest 13–23), 3524 transcript slots (v1 1920), each
   round a kernel + reduction + D2H sync + Python transcript — round-bound, not bandwidth-bound (v1's lookup bucket
   is 2.22 s on the same box for 2x the leaves).  a-gpu2's one-launch-per-round + CUDA graphs and a-fusion's
   `GraphLogUp` apply directly; v2's implicit tables are multi-column (`t.cols > 1`) so they take the ext-table
   path; the `R<w>` tables (R4/R8/R12/R15/R16) are identity tables and take the graphed range path unchanged.
   Expected from a-gpu2's v1 numbers (1.79 s ×4096 on the H100): v2 well under 1.5 s.
2. The v2 arithmetic bucket is already 4.9x v1 (2 checker layers, depth 1) and the opening 1.5x (109 M vs 178 M
   committed elements); INT8 opening (a-gpu2) shrinks it further.
3. Verifier: 8.1 s Python; a-gpu2's vectorised Ligero verifier (1.34 s on v1) should carry over — the v2 path adds
   only `check_chain_links_clear` and the table union.
4. Field/label: BabyBear^6 throughout.  Every checked v2 gadget is z3-verified over BabyBear (unit body:
   `gpu/v2/results/z3_babybear_v2.json`; epilogue: `lane/b-air-v2` `pack_epilogue_limbs`).  Do **not** switch the
   export back to `BabyBearV2Api("word")` for bench numbers — that reopens the wrap attack (DESIGN §5b).

## Open

* `gkr_export.v2`'s synth / negatives generators still emit the word-form epilogue (their hint paths); porting
  them to `epilogue_limbs` would make the a-v2 chain negatives run on the honest-label circuit too (the 34 cases
  attack the chain and the unit, which are unchanged, so nothing is unverified — it is hygiene).
* The Rust `a-v2` prover's `inst.tables()` takes the first segment's tables: the epilogue's `R16/R15` queries are
  unproven there (DESIGN §5b) — reported, not fixed on this branch (not this lane's file).
* Bit-exact transcript against the CPU prover: not comparable (Goldilocks^3 vs BabyBear^6, different embedding of
  the epilogue); the Python verifier is the same code path that rejects every negative class.

---

# a-gpu handoff (2026-09-22 ~08:00Z)

---

# a-gpu2 handoff (2026-09-22 ~09:55Z)

State: **prover at 1.790 s median for the full K=1536 VU x4096 on the H100 (v6, run r20260922-094040-9e76; v5 1.857 in
r20260922-092333-c8f0 was the breakthrough entry), 2.5x over a-gpu's 4.43 s, verified 4096/4096 x3; 52/52 negatives
rejected on the v6 path (r20260922-094606-1813); verifier 1.34 s (was 7.1 s).**  Ledger:
`backends/numerical/reports/ledger/a-gpu2.jsonl`.  Branch `lane/a-gpu2` (includes the merge of `lane/a-fusion` 3718a4a).

Buckets v2e -> v6 (s): lookup 1.40 -> 0.43, arith 1.07 -> 0.66, open 1.44 -> 0.53, commit 0.45 -> 0.10, wires 0.07;
verifier 7.1 -> 1.34 s (Python+torch); proof 33.9 MB; depth 438; 1921 transcript slots; peak device memory 47.9 GB.

v6 over v5: `ligero.verify_open` evaluates every functional row at the 192 opened columns as one modular GEMM
(`eval_rows_at`: INTT matrix x Vandermonde -- the same values as encode-then-gather) and `q(eta_j)` as a matmul
(was a 1.6M-op Python Horner loop); every check kept.  Prover: `add_input_claim` as a fused rank-1 kernel.

## What changed (all bit-exact against the a-gpu torch path: same messages, root, opening)

* `gkr_packed.py`: GKR phase 1 on a-packed2's k=3 Montgomery packed sumcheck.  Tables laid out gate-major over
  bit-reversed copies (`_layout`, a Triton gather-transpose); the weight `w(g) x eq(gamma, c)` is the kernel's
  `e_lo x e_hi` tensor product (`e_hi` is arbitrary); the eq windows per round are strided slices of the layer's eq
  table rescaled by batch-inverted prefix/suffix constants (`_EqSlices`).  Same round schedule and messages as the
  torch loop (`gkr.phase1_round`), verifier untouched.  Per full layer 700 -> 93 ms (device ~30 ms; the rest is host
  prep: ~1 ms `_inputs` + ~1 ms kernels per round x 19 rounds).
* `logup_packed.py`: LogUp on a-fusion's `GraphLogUp` with `rounds_per_graph=1` -- one graph replay per round, the
  a-gpu transcript absorbs `S_i` / squeezes `r_i` between replays (`_FSGraph._walk_fs`), `_FSGraphExt` for the
  vector-valued tables (tree + big level from `p_leaf/q_leaf`).  Graphs are built once per (shape) per process
  (~60 s compile+capture, then reused: `gpu.run --warmup 1`); their static buffers stay resident (~20 GB for R16).
  Eager fallback: `VERITY_GPU_NO_GRAPHS=1`; torch reference: `VERITY_GPU_NO_PACKED=1` / `VERITY_GPU_TORCH_ONLY=1`.
* `ligero.py` / `field.py`: opening GEMMs on INT8 tensor cores (`mm_mod_int8`, `Limbs8` with the B operand
  column-major; a-operand written once in int32 into the padded limb layout, fused `split_limbs` kernel); commit NTT
  via b-encode's `RSEncoderSIMT`; `Opening.columns` as a numpy array; `eq_table` for n > 16 as a fused tensor
  product (`eq_outer`, int32 out) -- the n=28 table used to be a 26 GB int64 transient.
* `field.W` is 22 (a-packed2's extension polynomial `X^6 - 22`; a-gpu used 31) -- `logup_packed` asserts equality.

## Where things are

* Pod `vy-g5` (`/tmp/g5.sh` = ssh helper on the laptop; sync = `tar czf - backends/gkr/gpu backends/gkr/packed |
  /tmp/g5.sh 'cd /workspace/verity && tar xzf -'`), `/workspace/venv312/bin/python`, `PYTHONPATH=/workspace/verity/
  backends/gkr:/workspace/verity/backends/gkr/packed`; data `/workspace/bb/pos4096`, `/workspace/bb/neg`.
  Recorded runs: `research run --on vy-g5 --project verity --source . --env PYTHONPATH=backends/gkr:backends/gkr/packed
  --stage gkr.gpu.vX -- bash -c '/workspace/venv312/bin/python -m gpu.run prove /workspace/bb/pos4096 --device cuda
  --warmup 1 --reps 3 --json $RESEARCH_RUN_DIR/run.json'`.
* Helpers on the pod (not in the repo): `/workspace/cmp64.py DIR N` (packed vs torch path, message equality),
  `/workspace/warm.py DIR N REPS` (warm timings), `/workspace/prof2b.py DIR` (synced per-function timers, warm),
  `/workspace/p1chk2.py b,g_n ...` (packed phase 1 vs torch phase 1 at arbitrary shapes).

## Next steps

1. **Open 0.57 s**: `open_w_qc` 0.41 s = four INT8 GEMMs (the two big ones 24576 x 43417 x 4096 at ~55 ms each are
   at ~50% of INT8 peak; the INTT-side ones and the int64 recombination are the rest) + 0.29 s building the Ligero
   functional (`add_lookup_claim` / `add_input_claim`: memory-bound passes over the 26 GB int64 `acc.a`).  Store
   `acc.a` in int32 (halves that traffic and the peak memory; the scatter kernel `scatter_terms_kernel` loads it via
   `load6` -- make the loads dtype-agnostic) and exploit the low-rank structure of the input claims in the GEMM.
2. **Arith 0.66 s**: phase 2 (0.20 s: two `sumcheck_prod` chains of 10-11 rounds per layer, ~30 launches each) and
   `eval_gates` (0.13 s) are launch-bound; phase-1 host prep (~1.9 ms/round) could move into one prepared-inputs
   kernel (a-fusion's `prepare_inputs` / `sumcheck_layer_device` are sync-free for the standard layout).
3. **Verifier**: 1.34 s; the rest is `verify_table` (0.33 s), interpolation / `e_*` Python ext arithmetic over the
   1552 transcript absorbs, `eq_table`; a Rust BabyBear^6 port (`backends/gkr/src/`, a-babybear's `field.rs`) would
   take it well under 0.5 s.
4. **B = 8192**: not attempted -- 47.9 GB peak at 4096 with ~20 GB of graph buffers resident; needs the int32 `acc.a`
   (step 1) first.
