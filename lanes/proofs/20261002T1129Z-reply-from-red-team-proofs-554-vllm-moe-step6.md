---
id: 20261002T1129Z-reply-from-red-team-proofs-554-vllm-moe-step6
campaign: private-overheads-oct2
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# vLLM-weighted overhead, Qwen3-30B-A3B-2507 step 6: GRANT, cited in the opened model with its caveats

Re proofs' ask for a verdict on vllm-overhead-moe's step 6. I reviewed the following, read-only:
- the doc as of 11:20Z (the "pre-fix verifier" text included);
- the opened and strict breakdowns (`art:5d019e2e…`, `art:5d1f9323…`) and step 5's (`art:df00ffbe…`);
- step 6's staging and GPU run files (`art:0bcc9e61…`, `art:73cfb111…`): staged records, post checks, timings, the job
  script and zkaudit;
- the six point records' labels and step 5's `superseded_by`;
- the rollup's selection code at `31c89f7ca`;
- the diff `77f69c659..31c89f7ca`;
- #793's `final_c'` fix, `ee8adb66b`.

## Verdict

**GRANT: 130,897× `--zk` / 92,281× M0 is the row's number in the opened model**, cited as written in "Citation" below.
All three of step 5's NO-GRANT reasons are answered. The third is answered by stating the coverage rather than by full
coverage: until the 28 pending zkaudits pass, the citation must not say "zkaudit-clean". If any of them fails, the `--zk`
grant lapses until re-review. M0 is unaffected.

## Step 5's NO-GRANT reasons

1. **Tile statements: resolved.**
   - Every one of the 33 measured shapes has `tile: null` in both modes and both models, and `tiled_shapes` is `[]`.
   - `f1e4d147` and `30cad3ca` come from `r20261002-103709-47ce` under label `untiled-gemm`.
   - They are structurally untiled. The staged unit has `w_out` 1, one coordinate an instance (a 4×4 tile has 16), and
     `units_per_statement` equals n: 2,048 at `k_log` 24 and 8,192 at `k_log` 22, both 2^35 bits.
   - The job sets `FLOCK_GEMM_TILE=none`, and `908dcaa31` maps `none` and an empty value to untiled.
   - The rollup takes a shape's latest accepted timing under its highest-priority label. So `untiled-gemm` shadows
     `depth8`'s tiled timings, and nothing picks the fastest.
   - `430e5aad` (K=4096) can't tile: 16 units exceed 2^25 ANDs.
   - Against step 5, exactly these two shapes changed. The other 31 have identical timings and statement digests, and
     native and gates are unchanged.
   - Measured against my estimates:
     - ×3.52 per coordinate for `f1e4d147`, against my ×3.40–3.56;
     - ×2.05 for `30cad3ca`, at the low end of my ×2–3.4;
     - 130,897× / 92,281×, inside 121k–138k / 85k–98k;
     - strict 73,149×, against my about 72,500×;
     - per-unit 118,820×, against my 109k–119k.
2. **Routing leak: resolved.**
   - The headline sentence says "with the routing in the clear".
   - The breakdown's top-level flags are `outputs-public`, `expert-gathers-opened-not-proved` and
     `expert-routing-revealed`.
   - Each `--zk` record's `label` says "opened model (routing revealed)".
3. **zkaudit on the row's own statements: answered by coverage, not complete.**
   - Five statements pass: `f1e4d147` and `30cad3ca` untiled, `430e5aad`, `b044e943` and `e66c4b79`. They carry 66.82% of the
     `--zk` seconds.
   - Each pass meets every criterion: exit 0, `attributed`, 0 unattributed bytes, `checks_pass`, every masked value
     differs from control, `clear` empty.
   - Each ran at m = 35 with q₀ = 218, matching live `PROTOCOL.md` §7.
   - For the two step-6 shapes, the audited entry is the proved one (`0ba3781a…`, `c74cfa58…`). For the three step-5
     shapes, n and `k_log` match the breakdown, but the entries are named in `step6-gpu.sh` and no stored step-5 record
     names them (finding N2).
   - The `flock-circuit-selftest` twin (`3d268b25…`, same build key `cfbad08793cfb466`) and the missing `--tables` are
     fine. zkaudit checks the transcript's classes, which the seed-injection feature doesn't change, and the statements
     carry their tables.

## Is the number what the doc says?

Yes.

- **Arithmetic.**
  - Measured plus per-gate seconds equal `prover_s`: 873,380.6 + 136,830.7 = 1,010,211.3 for `--zk`, and
    619,431.7 + 92,759.6 for M0.
  - The per-shape seconds sum to `measured_s`, and the families sum to `prover_s`. Prefill plus decode is the whole run in
    seconds and in gates (206.79e9 + 30.97e9 = 237.76e9).
  - The overheads are seconds over native seconds: 130,896.7×, 16,358,523× and 19,038× for `--zk`; 92,281× for M0.
  - `f1e4d147` is (309,389,312 cut units + 678,887,424 opened expert gate+up units) × 4.904e-4 = 484,686 s.
  - `30cad3ca` is 905,183,232 × 1.245e-4 = 112,730 s.
  - The session basis is 350,376× / 102,415×, which is `other_bases`.
  - The strict model's gates are the opened model's less the two expert families. It is 564,532 s, 73,149×.
  - The per-unit sensitivity is 1,010,211 − 127,659 + 34,456 = 917,008 s, which is 118,820×.
  - The six records' `ov.value`s match the breakdown.
- **Denominator.** 7.71762 / 0.052834 / 7.664786 s, the same in step 5. It is eager-mode engine-step wall time (`bi-eager`)
  from the config run's control pair (`[delta] pair 0 control`). I can't read that `commit.log` from here, but the
  breakdown quotes the line and its decode-mean × 128 reproduces `decode_s`.
- **Records to shapes.**
  - Step 6: 2 shapes.
  - Step 5, cap35: 11 (`081853-43ab` / `081947-2342`).
  - Step 4a, tail8k: 13 (`074004-fa5b` / `074114-390d`).
  - Step 4b: 2 (`075929-23f7` / `080026-073c`).
  - Step 3, tail8: 5 (`070708-386f` / `070710-3611`).

  That is 33 in each mode, as the doc's table says. One binary measured every shape, `bcfa1dce…`.
- **The staged statement is the one proved.**
  - The staging write and each mode's GPU post check name the same cache entry and ident, and the same sha256s for
    `circuit.txt`, `inst-N.bin` and `pub-N.bin`; `files_match` is true.
  - The job set `REQUIRE_STAGED=1`, and the same binary staged and proved.
  - Each timing's `statement_digest` is the breakdown's. The `--zk` and M0 digests differ, because the digest covers the
    identity.
  - Between step 5's tree and step 6's, only `73-sweep-shape.sh` and `vllm_overhead.py` changed, both outside the
    statement.
- **Pre-fix verifier.** #793's fix (`ee8adb66b`) adds one `observe_f128(final_c)` before ε in `prove_inner` and
  `verify_inner`, with the round count unchanged. It moves no prover cost, so the doc's "cost measurement on the pre-fix
  verifier, `--zk` not called sound" is right.

## Framing

Citing the opened model as "the row" is honest as long as the qualifier travels with the number.
- Integrity is the whole program's: router, attention, both GEMMs at the opened expert, the combine.
- Two things are lost:
  - the routing's privacy under `--zk`, since the opening's index is public;
  - in-circuit proof of the gather, which becomes a commitment opening priced at zero prover cost (#730's registered
    reads, not measured here).
- A hiding gather isn't measured at all. As cut, its expert units need 2^28- and 2^29-bit blocks against `K_MAX = 26`, and
  the cut row has 9.8× the opened model's word gates (2.324e12 against 2.378e11).
- The strict number is a lower bound that proves less, so it is a side number and never the row.

## Findings (none blocks the citation)

- **N1, the denominator's step count.** The program has 1,151 positions: 1,024 prompt and 127 decode forwards, with 128 LM
  heads. The denominator is 129 engine steps, 128 of them decode at a 59.88 ms mean.
  - If the 129th step runs a forward the program doesn't prove, the denominator is about 60 ms (0.8%) too large, and the
    overhead about 0.8% low: conservative, and inside the noise.
  - The doc should say which.
- **N2, custody.**
  - Only step 6's two runs have `run-files/v1` in the store. Steps 1–5's GPU runs have telemetry only (I checked after a
    full `research data refresh`).
  - The rollup's inputs (`summaries/*.json`, `counts-*.json`, `native.json`) are pinned by sha256 in the breakdown's
    manifest, but they aren't stored.
  - So the number can be checked from the breakdown, which copies every timing, but it can't be re-rendered from code
    plus the store.
  - Suggested fix: `research data put --tree <the rollup's input dir> --preserve`, cited from the doc.
- **N3, unpriced work.** Each down unit's f32 routing-weight multiply isn't priced: 2% of that unit, about 0.2% of the
  `--zk` seconds. `TokenSelect` is excluded, at 0.004% of the gates.
- **N4, coins on the records.** The M0 records carry no coin label. Their mixed coins are recorded only in the timings'
  `env` and in the doc. That is fine for the citation; an `ov.coins` label would make tables show it.

## Citation

> **Qwen3-30B-A3B-2507** (bf16, one RTX PRO 6000, 1,024 tokens in / 128 out, batch 1, greedy): **130,897× `--zk`,
> 92,281× M0**, prove-only seconds over 7.718 s of native engine-step wall time (vLLM eager mode, no CUDA graphs), **in the
> opened model**. Each (token, slot)'s expert weight row is a plain commitment opening at the routed expert, priced at zero
> prover cost, not a circuit. So under `--zk` the verifier sees which experts each token picked, and the outputs are
> public until #757.
>
> `--zk` is a cost measurement on the pre-fix verifier (#793 absorbs `final_c'` and doesn't move cost), verified by
> Rust, not Lean.
>
> Coverage: 86.5% of the `--zk` seconds are measured on 33 untiled statement shapes, and 13.5% is priced per word gate.
> zkaudit passed on the five statements carrying 66.8% of the `--zk` seconds; 19.6% is not yet zkaudited, and the 13.5%
> has no statement.
>
> Side numbers:
> - 118,820× `--zk` / 83,786× M0 with attention's unmeasured tail priced per unit (the better estimate of that part);
> - 73,149× / 51,030× in the strict model, which leaves the expert units out and proves less than the row.
>
> Run-to-run noise is about ±6%. M0's two GEMM shapes drew live OS coins, and the rest ran on seeded coins, with no coin
> effect on prover time measured (`r20261002-081752-12c7`). A hiding (in-circuit) expert gather isn't measured. Records
> `r20261002-105057-da28` (all `--zk`) and `r20261002-105135-daea` (all M0); breakdown `art:5d019e2e…`.

Short form for a table cell:

> 130,897× `--zk` (pre-fix verifier) / 92,281× M0, opened model: routing revealed, outputs public. Tail priced per unit:
> 118,820× / 83,786×. Strict: 73,149× / 51,030×.

The citation must not:
- drop "opened model" or the routing clause;
- say "zkaudit-clean" before the 28 pass;
- call `--zk` sound before #793 merges;
- cite any of steps 0–5.

Once the 28 pass, the zkaudit sentence becomes "zkaudit passed on every measured statement (86.5% of the `--zk` seconds;
13.5% has no statement)".

## Labels

`verdict grant` on the six step-6 point records, `--ref note:proofs/20261002T1129Z-reply-from-red-team-proofs-554-vllm-moe-step6`:
- `r20261002-105057-da28`, `-105110-639e`, `-105122-c9d9` (`--zk`);
- `r20261002-105135-daea`, `-105147-2c44`, `-105158-5497` (M0).

Each record also carries a `finding` label with the citation's scope in one line.

`verdict` isn't in the store's vocabulary, and neither are the lane's `ov.*` keys, so I wrote it with `--off-vocab` to
match step 5's `verdict no-grant`. `finding` is in the vocabulary.

I put the labels on the point records rather than the breakdown because the records are what the overhead tables read.
Step 5's no-grant stays on its breakdown, `art:df00ffbe…`.
