---
lane: red-team-flock-2
kind: handoff
from: flock-ir-sampling (bc-0ba89fde-5332-53f9-b622-f1264386f8cb)
created: 2026-09-26T09:22Z
---

# flock-ir-sampling: review request for verity/flock-ir-sampling/v1 (GumbelTopPTokenSelect_v1, vLLM #101's sampling) at PR #65 @ af0bd416, and its cells: L40S art:a330c568, H100 art:26b5f7d8

This is the sampling half of overnight goal 2. PR #65 is branch `cursor/flock-ir-sampling-f8cb`; flock-ir-lowering's tip f4cd5d4e (v3) is merged in with no Rust conflict. IR6 is implemented at this statement version. The part to scrutinise is the native tail: the whole-row values are the verifier's own computations on public words (last section).

**Where the statement lives.** `backends/flock/live/src/ir_sampling.rs` and `bin/flock-ir-sampling.rs` are `ir_frame.rs` and `bin/flock-ir-frame.rs` at c53d9148 (the v2 you granted) plus exactly the sampling changes. `git diff c53d9148:backends/flock/live/src/ir_frame.rs backends/flock/live/src/ir_sampling.rs` is the delta to review; the module also carries its own copy of c53d9148's cut map with native words. The two cells ran at f70c6c77, where the same code sat inside `flock-ir-frame`. For the same file, the current `flock-ir-sampling` gives the same statement digest (9c4688f8…), Σ and public sha256 as the f70c6c77 binary: checked on a V=1280 file, before and after the merge.

**The decomposition.** Module `verity_flock/ir_sampling.py`, template module `templates/gumbel_top_p_token_select.py`.
- **Unit: one per vocabulary lane**, V = 128,256 per row, all identical. It is lowered gate by gate from the IR composites with flock-ir-lowering's walker (`ir_lower.lower_gates`, with a pieces map):
  - `TemperatureLane(x, temp, rcp, skip)`, giving `scaled`.
  - `TopPMaskStep`'s select, `SelectF32(BitAtx{V}(keep, i), scaled, -inf)`. The BitAt gate takes the lane's `kbit` port: lane v reads bit v of the keep word.
  - `GumbelSelectStep((best, best_i, i), masked, key, noisy)`. Its `GumbelNoiseLane(key, i)` gate takes the lane's `g` port.
  - Lane 0 (`i == 0`) takes the scan's init `(y_0, 0, 1)` in place of the step: `y_0` is the step's own y, and the Definition's init is `SelectF32(noisy, F32AddFtz(logits[0], noise(key, 0)), logits[0])`. `first = NOT(OR(i))`.
  - Size: 5,099 ANDs in 6,273 rows. The netlist does not depend on V; without its CUT line it is pinned at `bc18d1459f87c205977ee8c3739c19e5da93a036ae7dadbef62cba75d9e8aeaa`.
- **Pieces** (in ir_sampling.py; fp.py is unchanged). They follow numpy float32 on x86-64, NaN payloads included: b's NaN quieted when b is a NaN, else a's, else 0xFFC00000 for an invalid operation.
  - `F32Mul`, `F32AddFtz` (ftz → add → ftz), `F32GtStrict` (NaN false, ±0 equal).
  - `DivFullScaleA`: `|b| > 2^126` means 0x7E800000 < mag ≤ 0x7F800000; `|b| < 2^-126` means mag < 0x00800000; a NaN b returns a raw.
  - `SelectF32` / `SelectI32` and `I32Add`.
  - These differ from `fp.f32_mul` / `fp.f32_add`, which canonicalise NaN. The carry words can hold y_0's NaN payload.
- **Cut words per instance**, `7 + 6V` u32 words, every port 32 bits:
  - the row scalars `temp, rcp = DivFullRcp(temp), skip = temp ∈ {0, 1}, noisy = temp ≠ 0`, then the initial carry `(0, 0, 0)`;
  - per lane: `kbit, g, scaled, best, best_i, i+1`.
  - Lane v reads the 4 scalars, its kbit and g, and lane v−1's carry (the initial carry for lane 0). It writes `scaled` and its carry.
  - The per-lane ports are listed explicitly in the pinned CUT line, with `"tail": []` and `"native": "verity/flock-ir-sampling/v1"`.
- **Ports:**
  - The logits row is a private frame-v3 row: `blake3-keyed/row/v2` under the x key, hashed in the proof exactly as in v2. It is 256,512 bytes, so its last chunk has 8 blocks; runs are of nb = 4, 128 lanes per block, k_log 21.
  - The five scalar operands (top_p, seed, pos, temp, splits) are public ports. Their frame-v3 row digests (keyed BLAKE3 of their 32-bit words, a u64 as two) are computed natively.
  - The token is a `u64` word leaf taken from lane V−1's `best_i` (`out_cut`).

**The delta over v2.** A `flock-ir-sampling/v1` file gets its own TAG, Σ tag and rep domains, and the binary refuses any other file.
- Short last chunk: `Layout::blocks_in(c)` sets the flags, the chunk's CHUNK_END at its own last block, the honest run input and the C4 fold.
- `check_roots` recomputes the public ports' and the token's roots.
- `CutMap.native` holds when the CUT line names this statement. `flock-ir-block` refuses such a netlist.
- The regions are Params, CvIn, Cv, CutIn and CutOut. There is no Out region (no returned words).
- `check_sampling_words` checks the 7 row words natively in Rust: temp equals the public in4 word, rcp is `DivFullRcp` on your pinned rcp table, plus skip, noisy and the zero init.
- **IR6** (`check_sampling_blocks`): Rust derives the layout's meaning from the plan's scalars.
  - Runs are (instance, chunk, run) in order, G per block; each run's 32·nb lanes fill its component's unit slots in order; unit k is wired to byte 2(k mod upc) of run slot k/upc. The header must equal this.
  - The row key is pinned to `blake3_row_key(ROLE_X)` and the public ports to (top_p, seed, pos, temp, splits).
  - The token is pinned to the last lane's third cut output.
- `serve` of a sampling file needs `--native-checked <public sha256>`.

**The native tail: what the verifier computes, and what that implies.**
- Before any session, `verity_flock.ir_sampling.check_native` recomputes every lane's `kbit` (the `TopPMaskWordx{V}` reference `topp_split.topp_keep_row` on the file's public `scaled` words, top_p and splits) and `g` (`sampling_rows.noise_row`, the registered twin of `GumbelNoiseLane`, from the public seed and pos). `ir_bench` runs it and passes the file's public sha256 to `serve`.
- The top-p split pipeline runs the measured MUFU EX2/RCP tables over whole-row reductions: five rounds of pivots, tree sums in the kernel's order, tie counts. No circuit here lowers it. So the **tempered row is public** (V f32 words), and with it the logits row is effectively revealed: T = 0.8 makes `x·1.25` exact. The statement is NON_ZK_PROOF.
- What the proof adds beyond a native recomputation: the frame-v3 binding of the committed logits row to the public tempered row, and the lane arithmetic (temperature, mask select, noisy add, strict first-max chain) in the proof. The top-p pipeline and the noise are verifier-native, and the census may want to count that as partial coverage.
- The native noise is `O(V)` Philox plus two libdevice logs a lane. It could go in the circuit (~50–90k ANDs a lane) only if the lane unit stayed under 2^16 rows, or as a separate public-IO unit table. That is not built.

**Evidence.**
- Captured #101 (`art:ea781b02`, 32 rows): all 4,104,192 lanes through the lane netlist give 0 unit-word mismatches and 0 unsatisfied lanes; `check_native` is clean; the tokens equal the set's. The full IR evaluator (`GumbelTopPTokenSelect_v1{128256}`, `TemperatureScale`, `TopPMask`, `GumbelNoiseLane`) on 8 rows gives 0 mismatches (`lanes/flock-ir-sampling/evidence/20260926T0835Z-captured-101-exactness.json`).
- Synthetic `art:ccc8afba` (bench-spine, 32 rows): the same, with the IR evaluator on 6 rows (`…T0852Z-synthetic-101-exactness.json`).
- `backends/flock/tests/test_ir_sampling.py` (17 tests):
  - the pieces against the IR primitives, on specials and NaN pairs;
  - the lane against the IR composites walked gate by gate with the primitives' evaluators, on 4,000 adversarial lanes;
  - a row's words against the full IR evaluator at V = 1056 (last chunk 1 block) and V = 1280 (8 blocks): token, tempered row, masked row, keep bits, noise, every carry against a replay of the scan;
  - staged units;
  - negatives: a forged native kbit or g word (refused by `check_native` and `serve_args`), a forged unit word, a mutated netlist, a flipped witness bit.
- Selftests:
  - CPU 20/20 at the tip, on V = 1280 with a short last chunk, including the three IR6 load tampers;
  - L40S GPU all-pass at b7cbb4d5, run r20260926-084023-82c0, the same statement code without the IR6 load checks. L40S GPU and CPU selftests all-pass at the tip (af0bd416, the `flock-ir-sampling` binary on the merged tree), run r20260926-091906-6381.
- **Cells** (`bench.cell`, 33-ir-cell.sh; each verifier staged its own files and ran `check_native`; both `check`s are clean and the interaction rule passes):

| cell | prover / verifier | plateau | e2e | rows/s | RTT | witness / arithmetic | art |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L40S (#101's served GPU), captured #101 art:ea781b02 | Kansas City L40S r20260926-084507-3ae9 / Dallas L40S r20260926-084457-7a06 | 8 rows, 1 proof, m 34 | 16.0 s | 0.500 | 11.2 ms | 10.9 s / 3.6 s | art:a330c568 |
| H100 (optional), same set | EUR-IS-3 H100 r20260926-085143-1253 / EUR-IS-3 H100 r20260926-085104-58db | 8 rows, 1 proof, m 34 | 14.9 s | 0.537 | 0.18 ms | 13.7 s / 0.4 s | art:26b5f7d8 |

  The L40S verifier is in another datacenter: no CPU or GPU pod was free in the prover's. The proof is 1.18 MB, with 286 rounds. The verifier takes 9.1 s (L40S) and 3.2 s (H100) of wall time. The prover is bound by the host witness.

**Please check:**
1. The lane's fidelity to the three composites, lane 0's init and the NaN payloads.
2. The chain: every carry word is produced once and read once, and the token is lane V−1's `best_i`.
3. The short-chunk flags and fold.
4. The public ports and token roots.
5. IR6 as implemented.
6. Whether the native tail is acceptable as stated, or a condition.

A red-team label goes on the cells once you decide.
