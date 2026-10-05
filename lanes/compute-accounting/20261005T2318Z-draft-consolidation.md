---
id: 20261005T2318Z-draft-consolidation
campaign: pouw
lane: compute-accounting
kind: draft
status: draft
repo: danielreuter/verity
origin: b87eeef64
---

# PoUW consolidation: what to merge, fix and delete

Read at `b87eeef64` (`cursor/lean-layout-move-2-c3b2`, committed Oct 5 22:36Z). Scope:

- `verity/protocols/accounting/work/pouw/`: 31.4k lines, including 9.0k lines of JSON vectors.
- `benchmarks/pouw/`: 56.4k lines, of which 17.1k are tests and 13.9k are `harness/`.
- PoUW's Lean: `verity/Security/Definitions/Pouw/` (22.1k lines) and `verity/Security/Proofs/Pouw/` (54.7k lines).

This note builds on `note:20261004T2101Z-report-pouw-survey-inventory` (kernels, duplicated CUDA and loaders, about 10.1k deletable lines) and `note:20261004T2247Z-draft-move-map-answers` (where each piece goes in the move). It does not repeat their tables.

## The short version

PoUW carries every scheme we ever tried as live code. That's 9 names in the core registry, 3 more that only vLLM knows, the H100 line, forming v0, MXFP4 and the h3 hash format. Each new scheme was added beside the old ones with a default argument that keeps the old one working. The result is three things:

- `PearlC` silently defaults to the H100 device, forming v0 and hash h0.
- One module (`pearl_kw`, Pearl's published FP8 scheme) is also the floating-point library that 37 other files import.
- The Pearl-C circuit (`pc8`) is built by reaching into the Pearl-C4 circuit's private helpers.

Since your 4:06 PM PDT ruling that only a sampled ZK proof over C-Flock verifies a computation, most of that breadth has no claim depending on it.

The biggest single problem is not size, though. **The commitment the served kernel writes differs from the one the ZK statement opens.** The served kernel uses -h2, BLAKE3 trees. The circuit's rows are hm96-sha512 (`row-seg/v1`), and its tile digest is the h0 TurboSHAKE128 leaf (`circuit/leaves.py`, `PearlTileDigest`). Until those are one format, a sampled proof does not speak about what vLLM served.

## 1. Duplication, and which copy survives

**Three scheme registries.**

- `schemes/__init__.py` `SCHEMES` has 9 names.
- `circuit/__init__.py` `SCHEMES` has `ncp-v2` and `ncp-v2-shift24`.
- `integrations/vllm/.../pouw_pearl_c_device.py:108` `SCHEMES` builds its three names by constructing `PearlC(...)` directly: `pearl-c-sm120-v1-h1`, `pearl-c-sm120-unpromoted-v1-h1` and `pearl-c-sm120-v1-h2`. None of these is in the core registry, so `schemes.get` cannot resolve any scheme vLLM actually serves. The core registry's only sm120 entry is `pearl-c-sm120-v1`, on h0, and nothing serves it.
- `pouw.py:99` in vLLM takes the union of all three registries.

The survivor is `schemes.SCHEMES`, holding every name anyone serves or proves. vLLM's `scheme_of` (line 155) becomes a call to `schemes.get`.

**Two device records.**

- `schemes/pearl_c_device.Device` (`H100`, `SM120`, `SM120_UNPROMOTED`) is the survivor.
- `pearl_kw.Device` (lines 82–102: H100, B200, ADA) describes the GPUs of Pearl's published FP8 scheme. It should be renamed to say so, or deleted with the B200 code if you retire `pearl-fp8-v4`'s device variants.

**FP8, BF16 and FP32 conversions, three to four times over.**

- `pearl_kw.py` lines 108–222 implement them on Python floats: `f32_bits`, `f32_of_bits`, `bf16_to_f32`, `f32_to_bf16`, `fp8_to_f32`, `f32_to_fp8`, and `bf16_mul`/`div`/`fma`/`max`/`min`/`clamp_sym`.
- `catalog/verity_catalog/silicon/cast.py` and `fp32.py` are the bit-level, integer twins that the Lean model mirrors: `bf16_to_f32_word`, `f32_to_bf16_rn_word`, `f32_to_e4m3_sat_word`, `e4m3_to_f32_word`, `f32_to_e2m1_sat_word`, and `add`/`mul`/`fma`/`div`/`sqrt`.
- `pearl_c4.e2m1` (float midpoints) duplicates `cast.f32_to_e2m1_sat_word`.
- `benchmarks/pouw/pearl_c4/twin.py` (`e2m1`, `ue4m3`, `ue8m0_up`) and `harness/derive.py` (`e2m1_rne`) are numpy copies.

The catalog's bit-level words survive. `pearl_kw` keeps only Pearl's spec: line sampling, the device-dot replay, rows, the noise and the census. The numpy twins stay only where a benchmark needs vectorised speed, and each is tested against the catalog.

**Parallel circuit scaffolding.**

- `circuit/pc8.py` (543 lines) and `circuit/pc4.py` (597 lines) define the same functions, one copy per format: `_row_a_body`, `_row_b_body`, `_tile_body`, `_tile_hidden_body`, `line_ea`/`eb`, `basis_fa`/`fb`, `gram_g`, `DERIVATIONS`, `PORTS`, `SEEDS`, `Shape`, `_weight_units`, `_call_units`, `_check_body`, `_check_hidden_body`, `query`, `units` and `unit_cut`.
- `pc8` imports `pc4`'s private `_Emit`, `RowK` and `Unit`, plus `pearl_c._basis` and `pearl_kw.sample_line`.
- `circuit/rowk.py` (496 lines) is written twice inside one file: `_head8`/`_head4`, `_seg8`/`_seg4`, `_tail8a`/`_tail4a`, `pieces8`/`4`, `rows8`/`4`, `check8`/`4`, `root8`/`4` and `unit_templates8`/`4`.

The survivor is a shared `circuit/tile.py`, holding the emitter, `RowK`, `Unit` and the query and cut helpers, with `pc8` the only importer that lives in `verity/`. Top's 23:40Z Oct 4 call moves `pc4`'s part to `experimental/`. Once that's done, `pc8` must not import from `experimental/`, so the shared pieces have to move first.

**Benchmark copies.** The survey note counts about 2.5k lines of CUDA hashing duplicated across `pouw_hash/` and `pearl_c/hash*.cuh`, seven ctypes kernel loaders (about 4.4k lines), and six SASS/flush-to-zero gates. The survivors:

- `pearl_c/hash*.cuh`, which the sm120 kernel includes (`pearl_c_sm120.cu:17` includes `../pearl_c/hash_h2.cuh`);
- `harness/sass_gate.py` as the one gate;
- one loader in the kernel package (item 4 of the table).

**Price and γ mirrors.** `harness/price_twins.json` (4,117 lines) restates 272 Lean names. `pearl_c_work.DRAW_WREF` (line 220) is one hand-entered constant keyed by `(device, prices, cap)`. The Lean survives. The twins should be generated from `lean-audit.json` and checked, not hand-kept.

## 2. Awkward or fragile APIs, and the better form

**`PearlC.__init__(k_min=1024, tile=(64,64), forming="v0", device=H100, hashing="h0", prices=None)`.**

- Every default names a superseded choice, so a caller who forgets an argument gets the H100 v0 h0 scheme with no error. This happens in `benchmarks/pouw/pearl_c/fixture.py`, whose `C.PearlC()` calls at lines 236 and 260 take every default.
- The module functions repeat the trap: `chain`, `peel`, `gram`, `peel_factors_a`/`_b` and `form_v1` all default to `device=H100`, and `message_digest` and `leaf` default to `hashing="h0"`. `pearl_c_debit.debit_units` defaults to `device=H100`.
- Better form: construct schemes only through `schemes.get(name, **instance)`, and give `PearlC` no defaults for `forming`, `device` or `hashing`. The device should be a `Device`, and the hashing a `HashFormat` from `serving.HASH_FORMATS` rather than a string.
- There are about 60 call sites in roughly 25 files (Appendix A). Most are tests, which already pass every argument.

**v0 branches inside the v1 scheme.**

- `PearlC.__init__`, `_forming`, `credit_of`, `_side`, `admissible` and `useful` each branch on `forming == "v0"`.
- `_side` reaches into Pearl's spec for v0 (`P.parse_row`, `P.open_row`, `P.exact_norms`, `P.noisy_quantize(P.H100, …)`).
- `LABELS` are still `pearl-c/v0/seed-*` under v1. That is harmless, but changing it moves vectors, so leave it.
- Retiring v0 deletes those branches and Pearl-C's whole dependence on `pearl_kw`'s row code.

**`audit.commitment_hash(scheme)` is `getattr(scheme, "commitment_hash", "sha256")`.** A scheme that forgets the attribute is silently audited with SHA-256 trees. It should be a required attribute of `PoUWScheme` (`protocol.py`). NCP and Pearl's FP8 scheme would declare `"sha256"` explicitly.

**`serving.py` (313 lines) mixes four concerns:**

- the hash formats (`HashFormat`, `HASH_FORMATS`);
- the scheme-name grammar (`SchemeId`, `pearl-c-{device}-{forming}[-{hashing}][@{prices}]`);
- vLLM's step schedules (`Schedule`, `SCHEDULES`, `PassCommitment`, `StepIO`);
- the kernel-variant gate records (`KernelVariant`, `ShapeRule`, `GateRecord`, `variant_refusals`).

The first two are protocol, and belong with `schemes/`. The last two are serving and benchmark bookkeeping, and belong in the kernel package or `benchmarks/pouw/harness`. Importers are listed in Appendix B.

**vLLM loads the production kernel from a benchmark directory by path.**

- `pouw_pearl_c_device.Kernel.load(directory, cubin)` calls `_load`s on `run.py` and `fixture.py` inside `benchmarks/pouw/pearl_c_sm120/`.
- That `fixture.py` in turn uses `benchmarks/pouw/pearl_c/twin.py` and `fixture.py` (the H100 directory).
- `pearl_c_vllm/window.sh` `cmp`s the shipped tree's `run.py` against it.
- Your 4:19 ruling puts kernels in a top-level `kernels/`. The better form is a `kernels/pearl_c_sm120/` package that vLLM imports by name. It holds `run.py`, the fixture, the twin, the `.cu`/`.cuh` files and `fake_cuda.c`/`fake_tma.c`, with no path loading.

**`audit.Verifier` replays and calls the result verification.** `check_tile` recomputes the checked values and compares digests, then `audit` returns a `WorkProfile` with `scheme.certificate`. Under the 4:06 ruling that is a replay, a diagnostic. The code and `PROTOCOL.md` should say so. Alternatively, the profile could come only from the sampled-proofs path (`circuit` plus `verity.protocols.verification.sampled_proofs`). That is a semantics question, so it appears under rulings.

**Small items:**

- `pearl_c_debit.forming_elements` (line 161) is a stub that returns 0, pending a per-tile rule. Every debit that reads it undercounts forming work. Either land the rule or make the function raise.
- `ncp.checked_unbiased` (line 192) is "retired as NCP's checked values, kept for comparison". Only tests use it.

## 3. Dead code, with the evidence

Git dates are unreliable here: the layout move's import rewrites touched 91 benchmark files in October. The evidence below comes from two places:

- the store catalog's last recorded run whose argv names the script (`~/.research/store/catalog.sqlite`, 10,134 attempts);
- the kernel panel's `attempts.jsonl` (245 rows, Sep 30 06:34Z to Oct 1 06:47Z, sm120 and fp4 lines only). The panel ends before the served and exhaustion work, so a missing panel reference proves nothing after Oct 1.

| Code | Lines | Last recorded run | Panel | Who still imports it |
|---|---|---|---|---|
| `benchmarks/pouw/pearl_c/` (H100 kernel) | 6,924 | `verify_h1` and `h1_bench` Sep 30 | no | sm120 needs `hash.cuh`, `hash_h2.cuh`, `fake_cuda.c`, `twin.py` and `fixture.py`; the rest (`pearl_c.cu`, `h1_*`, `bench*`, `run.*`, `ship.sh`, `decode_served`, `simt_twin`, `h2_rows_stats_probe`, `verify_h1`) is H100-only |
| `pouw_hash/` | 2,483 | none recorded | no | `pouw_hash/check.py` imports `pearl_kw`; superseded by `pearl_c/hash*.cuh` |
| `nvfp4_sm120/` | 1,918 | none recorded | fp4 lines | keep `nvf4_plain.cu` and `mainloop_nvf4.cuh`; the benches are one-offs |
| top-level NCP, 4090 and B200 scripts: `pearl_calibration`, `route_u_bench`, `check_route_u_sass`, `gemm_bench`, `ncp2_gpu_bench`, `vllm_bench`, `gamma.py`, `pearl_b200_setup.sh` | about 1,580 | Sep 28–29; `gamma.py` never | no | `e2e_audit.py` (Sep 28) stays, because the pouw-e2e lane uses it |
| `pearl_c4/` scripts `f1_fast`, `real.py`, `real_table`, `form_bench`, `arm_smoke` | part of 3,640 | none recorded | fp4 lines name `build.sh` only | test-only importers |
| `pearl_c_vllm/` `fast_tile`, `served_table`, `panel_rows` | part of 3,737 | none recorded | `panel_rows.py` once | `served_debit`, `e2e`, `verify_run` and `forming_domain` are live (Oct 3–4) |
| `schemes/pearl_c_u.py` and `tests/vectors/pearl_c_u.json` | 211 + 3,199 | CPU-only; its docstring says "No kernel has run yet" (H100) | no | `pearl_c_device`, its own tests, `pearl_c/twin.py` |
| h3 (`HASH_FORMATS["h3"]`, row seeds plus `row_cap`) | about 40 | never implemented (`PearlC` refuses h3) | `-h3` panel rows Sep 30 | `serving.py`, `test_serving.py`, two refusal tests, `harness/ledger.py:178` |
| MXFP4 in `pearl_c4.py`, unregistered | part of 1,301 | approach `pearl-c4-mxfp4` is killed | yes (fp4) | `pearl_c4` tests |
| `ncp.checked_unbiased` | about 5 | n/a | n/a | tests |

The approaches registry (`APPROACHES.md`, Oct 4 21:08Z) confirms these. `pearl-c-h100-v0`, `pearl-c-hash-h0` and `pearl-c-hash-h1` are superseded. `pearl-c-h100-v1`, `pearl-c-sm120-unpromoted`, `pearl-c-sm120-v2-hot` and `pearl-c4-nvfp4` are parked. `pearl-c4-mxfp4` is killed. So are three nvfp4-sm120 variants, the hash-rows tree, tickets and the 60% window. The circuit lanes (`circuit-pc8`, `circuit-row-k`, `circuit-hidden-tile`, `circuit-registered-rows`) are marked parked, but that predates 4:06. `pc8` is now the only route to a verdict and should be live.

## 4. Changes, ranked by value against risk

"Moves a pin?" names what changes:

- **Vector:** a JSON file under `tests/vectors/`.
- **Digest:** a Program digest in `test_circuit_row_lean.py` (`DIGESTS8`, `DIGESTS4`, `DEPLOYED`), `test_circuit_whole_lean.py` (`DIGESTS`) or `test_circuit_pc8.py:497` (`WHOLE`). `circuit_check`'s `pins.json` pins only AND counts.
- **Lean:** a pinned guarantee in `verity/Security/lean-audit.json`. PoUW holds 800 of its 1,747 pins.

| # | Change | Value | Risk | Owner | Moves a pin? |
|---|---|---|---|---|---|
| 1 | One scheme registry: register the three served names in `schemes.SCHEMES`; vLLM's `SCHEMES` and `scheme_of` and `circuit.SCHEMES` read it; remove the H100/v0/h0 defaults from `PearlC` and the module functions | High: `schemes.get` resolves what is served, and a forgotten argument fails instead of silently becoming H100 | Low: names unchanged; about 60 call sites, mostly tests | PoUW, with circuits (`integrations/vllm`) | No |
| 2 | Retire superseded schemes: `pearl-c-h100-v0`/`-v1`/`-v1-h1`/`-v1-h2`, forming v0, the H100 device, `pearl_c_u`, h3, MXFP4, `pearl_kw`'s B200/ADA device variants | High: deletes the v0 branches, `pearl_c_u` (3.4k lines with vectors) and most of the H100 benchmark directory | Low for code; the pins are the cost | PoUW; Lean for the pins | **Vector** (H100 and v0 cases leave `pearl_c.json`; `pearl_c_u.json` goes; MXFP4 cases leave `pearl_c4.json`). **Digest** (h100 entries leave `DIGESTS8`). **Lean** (about 9 H100 and 10 UOnly pins, plus whatever reads `pearl_c_u`) |
| 3 | Make the served commitment and the ZK statement one format: the kernel's rows and tile leaves are what `circuit/leaves.py` opens | Highest for the claim; without it a sampled proof does not cover served work | High: changes the served kernel, its gates and a timed window, and touches C-Flock's row hashing | PoUW, with circuits and proofs (`backends/flock`) | **Vector**, **Digest** and **Lean**, all of them |
| 4 | The kernel as a package: `kernels/pearl_c_sm120/` holding what vLLM path-loads today, including the four files it needs from `pearl_c/` | High: production stops depending on a benchmark directory, and `pearl_c/` can then go | Medium: `window.sh`'s shipped-tree `cmp`, ship scripts and SASS gates need re-pointing; one served smoke run | PoUW, with circuits | No |
| 5 | Split `pearl_kw`: its floating-point helpers go to `verity_catalog.silicon.cast`/`fp32` (bit-level), and `pearl_kw` keeps Pearl's spec | Medium-high: 37 importers stop depending on Pearl's published scheme for arithmetic | Low: the vectors guard bit-exactness; the float-to-word interface needs a thin shim | PoUW, with core (catalog) | No, if bit-exact; `pearl_kw.json` is the guard |
| 6 | Shared `circuit/tile.py`: `pc8` stops importing `pc4`'s privates; `rowk`'s 8/4 pairs become one builder over a format record | Medium: unblocks top's move of `pc4` to experimental; about 600 lines fewer | Medium: every Program digest must stay equal, which the tests check | PoUW (`circuit-check` report required) | Must not; **Digest** is the guard, and any moved digest needs the Lean re-read |
| 7 | Delete benchmark one-offs (section 3 table) and fold the seven loaders and six gates into the kernel package and `harness/sass_gate.py` | Medium: about 8–10k lines | Low; check the store for runs after Oct 4 before deleting | PoUW | No, except `price_twins.json` H100 rows, which follow change 2 |
| 8 | Prune the Lean lock to the guarantees cited (#1156: `EndToEnd`, `WorkWeightedSampling`, the sm120 cap-1000 γ, NCP `Theorem1`, `GammaFromTTNCP_U_v1`), keeping the read pins | Medium: 800 pins become about 5 plus reads; stops each experiment adding pins | Low code risk; it is a statement of what we cite | Lean | **Lean** (removals only) |
| 9 | Move generated vectors out of `Definitions/Pouw` (`H1TVectors` 2,892, `Fp4Vectors` 2,063, `Sm120Vectors` 1,903, `EncVectors` 1,770, others; about 11.9k lines) to a non-trusted test layer | Medium: the trusted text shrinks by half | Low | Lean | Records move under `--moved` with no statement change |
| 10 | `PoUWScheme.commitment_hash` required, not `getattr(..., "sha256")` | Low-medium: removes a silent default from the audit | Low | PoUW | No |
| 11 | Split `serving.py`: hash formats and the name grammar to `schemes/`; schedules and gate records to the kernel package | Low-medium | Low: Appendix B importers | PoUW, with circuits | No |
| 12 | `price_twins.json` and `DRAW_WREF` generated from `lean-audit.json` and checked | Low-medium | Low | PoUW | No |
| 13 | `forming_elements` raises until its rule lands; delete `ncp.checked_unbiased` | Low | Low | PoUW | No |

Order:

- Changes 1, 5, 6, 10 and 13 move no pin and can land now, in that order.
- Change 2 waits for your ruling, and then it shrinks changes 4, 6 and 7.
- Change 3 is the one that matters for the claim. It needs its own plan, because it moves every kind of pin.

## 5. What needs your ruling

1. **Retire the H100 line.** That means `pearl-c-h100-v0`, `-v1`, `-v1-h1` and `-v1-h2`, forming v0, the H100 device record, `pearl_c_u`, and `pearl-fp8-v4`'s B200/ADA variants. "14 PRs closed (H100 line, -h1 stack)" suggests yes, but deleting the code moves vectors and Lean pins. My recommendation: retire, keeping `pearl-fp8-v4` on its published device only.
2. **v1 or v2-hot on sm120.** vLLM serves `pearl-c-sm120-unpromoted-v1-h1` (`SM120_UNPROMOTED`, whose docstring says "no scheme is registered") beside the promoted `-v1-h1` and `-v1-h2`. You left v1 against v2-hot open. The 100 Sm120v2 Lean pins and the unpromoted device hang on it.
3. **Which hash formats stay.** I recommend one served format, -h2. That means dropping -h1 from serving and dropping h3 (never implemented). It also means deciding whether the H-1T Lean vectors (`h1t_vectors.py`, `H1TVectors`; the approach is live but has no Python scheme) stay.
4. **One commitment for served work and the ZK statement** (change 3). It follows your "one canonical I/O format" (15:42Z Oct 4) and the `row-seg/v1` retirement card (default retire, deadline Oct 5 16:00Z, outcome not found). Which format wins (hm96-sha512 rows, or the kernel's BLAKE3 trees) is a cost-against-trust choice for proofs and circuits. I recommend asking proofs for C-Flock's cost of each before ruling.
5. **What `audit.Verifier`'s profile means.** Under 4:06, a replay is a diagnostic, but `Verifier.audit` emits a `WorkProfile` with the scheme's certificate. Either relabel it as a replay profile, or make the sampled-proofs path the only source of a profile. I recommend the latter, once `pc8` is wired end to end.
6. **Pearl-C4's status and MXFP4.** MXFP4 is killed in the registry but still sits in `pearl_c4.py`. `pearl-c-nvfp4-v0` is registered while its approach is parked, with 65 Fp4 Lean pins. Top's call already moves `pc4` to `experimental/`. Does the scheme go with it?
7. **The lock size** (change 8), if #1156 has not already settled it.

## Appendix A: callers of `PearlC(` (counts per file)

- `verity/protocols/accounting/work/pouw/tests/`: `test_pouw_pearl_c` 17, `test_pouw_pearl_c_sm120` 9, `test_pouw_pearl_c_work` 5, `test_circuit_rowk` 2, `test_cap_lean` 2. One each in `test_pouw_pearl_c_u`, `test_pouw_pearl_c_debit`, `test_circuit_pc8`, `pouw_regions_vectors`, `pearl_c_vectors` and `pearl_c_u_vectors`.
- `schemes/__init__.py` 1.
- `benchmarks/pouw/`: `pearl_c/fixture.py` 6 (lines 236 and 260 take every default), `pearl_c_sm120/fixture.py` 4, `pearl_c/twin.py` 2. One each in `pearl_c_sm120/verify.py`, `pearl_c_sm120/pearlc_arm.py` and `exhaustion/window.py`.
- Benchmark tests: `test_pearl_c_vllm` 2. One each in `test_price_twins_accounting`, `test_pearl_c_sm120`, `test_pearl_c_hash_host` and `test_pearl_c_bench`.
- `integrations/vllm/verity_vllm/protocol_options/pouw_pearl_c_device.py` 2: line 108 builds `SCHEMES`, and `scheme_of` builds the scheme from `serving.SchemeId`.

## Appendix B: importers

**`schemes/pearl_kw` (37 files).**

- benchmarks: `e2e_audit`, `gamma`, `gemm_bench`, `pearl_c4/{f1_fast,real,twin}`, `pearl_c/{fixture,twin}`, `pearl_c_sm120/{fixture,pearlc_arm}`, `pearl_c_vllm/{fast_tile,forming_domain}`, `pouw_hash/check`;
- benchmark tests: `test_pearl_c_{bench,hash_host,kernel,sm120,vllm}`;
- vLLM: `protocol_options/pouw_pearl_c_screen.py`;
- circuit: `circuit/pc8.py`;
- schemes: `__init__`, `pearl_c4`, `pearl_c_debit`, `pearl_c`, `pearl_c_work`;
- PoUW tests: `pearl_c_vectors`, `pearl_vectors`, `test_circuit_{pc4,pc8,rowk}`, `test_pouw_{pearl_c4,pearl_c_debit,pearl_c,pearl_c_sm120,pearl_c_work,pearl_kw}`.

Most-used names outside `pearl_kw`: `f32_of_bits` 79, `f32_bits` 67, `Reject` 28, `fp8_to_f32` 22, `f32_to_bf16` 20, `sample_line` 17, `f32_to_fp8` 15, `NOISE_NORM` 11, `SIGMA_MIN` 9, `parse_row` 9, `_line_key` 9, `Built` 9, `open_row` 8, `H100` 8, `TILE` 7.

**`pouw.serving` (13 files).**

- `schemes/pearl_c.py` (`HASH_FORMATS`) and `tests/test_serving.py`;
- vLLM: `protocol_options/pouw.py` (`SCHEDULES`), `protocol_options/pouw_pearl_c_device.py` (`SchemeId`, `Schedule`, `SCHEDULES`, `HASH_FORMATS`) and `tests/protocol_options/test_pouw_pearl_c_whole.py`;
- benchmarks: `harness/{ledger,chain,price_twins,arm}.py` (`KernelVariant`, `GateRecord`, `SchemeId`), `pearl_c_vllm/e2e.py`, and `tests/{test_pearl_c_vllm,test_ledger,test_harness}.py`.

**`pouw_pearl_c_device` (vLLM).**

- vLLM: `protocol_options/{pouw,pouw_pearl_c_graphs,pouw_pearl_c_host,pouw_pearl_c_screen,pouw_pearl_c_whole}.py` and `tests/protocol_options/{test_pouw,test_pouw_pearl_c_whole}.py`;
- benchmarks: `pearl_c/decode_served.py`, `pearl_c_vllm/{e2e,verify_run,panel_rows,served_debit,profile_decode}.py`, `tests/test_pearl_c_vllm.py`;
- PoUW: `serving.py` and `tests/test_serving.py` (by name).

**PoUW from outside PoUW, benchmarks and vLLM.**

- `backends/flock/tests/test_pouw_rows.py` (`circuit.leaves`, `pc4`, `pc8`);
- `backends/flock/tests/test_randomness_spec.py`;
- `tools/circuit_check/src/circuit_check/targets.py:269` (`ncp2`, `pc4`, `pc8`, `rowk`, plus `boolean`);
- `tools/move/layout_map.toml`.

Other vLLM importers: `check/replay/pouw_circuit.py`, `program/registry/pouw_rows.py`, `pipeline`, `frontend/rules/vllm_bindings`, `tools/migrate`, and `protocol_options/{pouw_circuit,pouw_device}.py`.

**Users of h3:** `serving.py`, `tests/test_serving.py`, `tests/test_pouw_pearl_c.py:532` (refusal), `benchmarks/pouw/tests/test_pearl_c_vllm.py:1289` (refusal), `benchmarks/pouw/tests/test_ledger.py`, `harness/ledger.py:178`, and a comment at `pearl_c/hash.cuh:299`.

## Appendix C: PoUW's 800 Lean pins

By namespace: PearlC 401, Dimension 154, TileBound 63, NCP 42, Fp8Atom 41, SecurityProofs 33, Sanity 31, Proofs 21, Barrier 10, AlignedExact 4.

Within PearlC, by family (counted from the names, so approximate): Sm120v2 100, Sampled 71, Fp4 65, Rev1 52, Cap1000 21, RowSeed 15, ChainCap 13, Unpromoted 13, UOnly 10, H100 9, Complete 3, Hidden 2, other 27.

The families that change 2 and rulings 2, 3 and 6 would remove are H100, UOnly, Sm120v2, Unpromoted, Fp4 and ChainCap: about 210 pins before the lock reduction.
