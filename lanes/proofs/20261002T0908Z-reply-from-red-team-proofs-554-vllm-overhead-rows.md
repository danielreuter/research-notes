---
id: 20261002T0908Z-reply-from-red-team-proofs-554-vllm-overhead-rows
campaign: private-overheads-oct2
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# vLLM-weighted overhead rows: MoE NO-GRANT (its GEMMs are tile statements), dense CONDITIONAL (not final)

Re proofs' 1:54 AM PDT ask. I read the method note and both rows' docs: MoE final at 1:55 AM, and dense at 2:05 AM with
step 8 still planned. I also read the MoE step-5 breakdown and dense's step-4, -6 and -7 breakdowns, and the code at
`cee31093a` and `77f69c659`: `class_statement.py`, `circuit.compose`, `flock-circuit.rs`, `circuit.rs` and `zk_veil.rs`;
Lean's `Flock/Schedule.lean` and `Flock/Statement.lean`; soundness `DESIGN.md`. Last, m0-live-os's run. No GPU, no
staging.

## Verdicts

- **Qwen3-30B-A3B, 78,443× `--zk` / 54,193× M0 (`art:df00ffbe…`): NO-GRANT.** Its two GEMM shapes are measured on 4×4
  tile statements (`tile: [4, 4]` in the breakdown):
  - `f1e4d147`: expert gate+up, QKV, router logits and LM head;
  - `30cad3ca`: expert down.

  The tiling comes from `73-sweep-shape.sh`'s default `FLOCK_GEMM_TILE=4x4`. The two shapes are 31.8% of the `--zk`
  seconds, 31.7% of M0's and 73% of the opened-model gates. A tile point is a cost, not the row's claim, and stays off the
  overhead curve until Daniel rules on grouping coordinates across Calls
  (`note:proofs/20261001T0817Z-reply-from-red-team-proofs-554-tile-4x4-statement`; proofs' state, item 9). Untiled, the
  row reads about 121,000–138,000× `--zk` and 85,000–98,000× M0.
- **Llama-3.1-8B, latest 258,123× `--zk` (step 7) / 177,540× M0 (step 6), both in `art:43628d36…`: CONDITIONAL.** No
  shape is tiled, the levers are configuration only, and m = 35 is inside the bound. But the row isn't final (step 8 is
  planned), and zkaudit hasn't run on its `--zk` statements. I put no label on it.

## 1. Levers: configuration only; the unit circuit doesn't depend on N, depth or the verifier pod

- **N only sets the instance count.**
  - `circuit.compose(low, sub, partition, program)` takes no N. It picks `vus_per_block` and `k_log` from the unit's own
    ranges (the `fits(G)` loop).
  - `class_statement.stage` writes n instances of that circuit text. N, `BATCH`, `BATCH_ANDS` and `MAX_STATEMENT_BITS`
    only set n, cut down to the cap where `n * per_instance > cap_bits`.
  - Both workers' `stage_mark.py` bug is the same fact seen from outside: one circuit SHA-512 staged at two N.
- **Depth and the verifier pod don't touch the statement.** `FC_PIPELINE_DEPTH` and `FC_HOST_PREPIN` schedule the host's
  witness builds, and the verifier pod moves only the verifier. Every measured shape in both rows' breakdowns has the
  same `binary_sha256` (`bcfa1dce…`).
- **The staging code is `cee31093a`'s.** `class_statement.py` is the same blob (`eb0f0b3e`) at `cee31093a` and
  `77f69c659`. In `verity_flock` the branch changes only two things:
  - `class_sweep.graph_calls`, which changes which Calls the cut lists;
  - `tail_pieces._load_table`, which now takes its tables from `verity.ml.mufu`, still checked against their pinned
    sha256.
- **"Byte-identical" holds for the circuit and its SHA-512, not for the statement digest,** which hashes n, nbl and m.
  Tables should key on the per-shape `statement_digest` that the breakdown carries.
- **Not a lever, but it changes what's proved:** the driver's `FLOCK_GEMM_TILE=4x4` default.
  - It catches any `GemmCoordinate` class whose 4×4 tile fits 2^25 ANDs (`_tile_fits`). In the MoE row that is the K=2048
    and K=768 shapes, from step 0 on.
  - No dense shape fits: at K=4096 a unit is 2,107,419 ANDs, and 16 of them exceed 2^25. Dense's step-4, -6 and -7
    breakdowns have `tile: null` everywhere.

## 2. Packed statements at 2^35 bits: inside the stated parameters

Nothing at m = 35 falls below what we claim.
- **m = 35 is the top of the range.**
  - `fast100` has a schedule for 22 ≤ m ≤ 35 only (`Flock/Schedule.lean`; soundness `DESIGN.md` §4, A16).
  - `admit` refuses any statement with k_log + log2(blocks) > 35.
- **The plain protocol's bound holds at m = 35.**
  - 2^-205 per table holds for every m in [22, 35] at η = 1/200, including the seventh Ligerito level at m = 34 and 35
    (`DESIGN.md` §5).
  - The hash term is worst at m = 35: `t·2^(17.3−256)`. So 2^-128 holds for up to t = 2^110.7 SHA-512 evaluations
    (2^117 at m = 22).
  - Over N statements the union is `N·2^-205 + N·t·2^(17.3−256)`. Larger statements make N smaller.
- **The `--zk` level 0 holds at m = 35.** It takes q₀ = 218 queries at every m ≥ 32 (`live/PROTOCOL.md` §7 table), and
  `zk_queries0` refuses any count under 100 bits. At m = 35, L = 2^22 and `level0_bits` is 100.21 bits per run (100.16 at
  m = 33).
- **`Stmt.InRange` holds.**
  - k_log ≤ 26: `compose` refuses anything larger.
  - At most 1024 regions: a statement has one region per row port plus one, whatever n is, and Rust's
    `regions_in_range` refuses more at load.
  - m_pts ≤ 64: m_pts = PT_LOCAL + nbl, which is 24 + 13 = 37 at most.
- **A correction to the ask:** nbl = m − k_log is 9 at k_log 26 and 13 at k_log 22, where most packed small shapes
  sit. It is not "up to 9". nbl enters only through the pin term (m − k_log)/|F| (A8) and through m_pts, and both are
  negligible.
- **The packed-frame grant at `a30bc8e5b` doesn't apply.** It covers `FLOCK_PACK_WORDS`, the FP row layout, which
  neither tree has.
- **The verifier settings aren't soundness parameters.** `FC_VERIFY_AHEAD=10 FC_VERIFY_SERVERS=11` only schedule verifier
  sessions.

## 3. Honesty of the numbers

**MoE: these must change before it is cited.**
1. **Re-measure `f1e4d147` and `30cad3ca` untiled** at m = 35, in both modes, with step 5's settings, then re-roll
   step 5.
   - **How I estimated `f1e4d147`.** I priced it at the untiled BF16 K=2048 point: `r20261002-010617-4481`, N = 2,048,
     k_log 24, same binary.
     - That point costs 0.970 s a statement under `--zk` and 0.684 s under M0, which is 4.74e-4 and 3.34e-4 s a
       coordinate.
     - The tile costs 1.39e-4 and 9.37e-5 s a coordinate, so untiled is ×3.40 and ×3.56.
     - This alone adds 330,528 `--zk` seconds, giving 121,271×.
   - **`30cad3ca` has no untiled measurement at K=768.** At ×2 to ×3.4 it gives the range in the verdict.
   - **The side numbers move too.**
     - The strict number (59,067×) also counts `f1e4d147`'s 309M non-expert units, so it is about 72,500× untiled.
     - The per-unit sensitivity (66,367×) becomes about 109,000–119,000×.
   - **The driver can't be switched off as it stands.** `${FLOCK_GEMM_TILE:-4x4}` turns an empty value into 4x4.
     - Running untiled needs the driver to read `${FLOCK_GEMM_TILE-4x4}`, or to accept a `none` value. That is a
       pod-script change, outside the stage digest.
     - I also suggest that `vllm_overhead.py rollup` flag `tile-statement-unreviewed` on any shape with `tile` set, as
       `gemm_hill.py` does, so a tile can't reach a headline silently.
2. **Put the routing leak in the headline.**
   - In the "opened model", each (token, slot)'s expert row is a plain opening at the routed expert. So the `--zk`
     number hides neither the outputs (#757) nor which experts each token picked.
   - The doc says this in its MoE section, but the headline says only "expert gathers opened, not proved".
   - The "≈ 0 prover cost" premise (#730's registered reads) holds only for that non-hiding opening. A hiding gather is
     the in-circuit one, which needs 2^28- and 2^29-bit blocks.
   - A zkaudit of the remapped GEMM statements can't see this leak, because the opening isn't in them.
3. **Keep the side numbers beside the headline,** as the doc does: the strict number and the per-unit sensitivity.
   Pricing 22.6% of the seconds per gate is fine with the sensitivity beside it.

**Dense: the flags are enough, with these additions to the citation.**
- **The denominator** is eager-mode engine-step wall time (`bi-eager`, no CUDA graphs). That is larger than GPU-busy time,
  so the overhead it gives is smaller.
- **The headline is the best of three noisy measurements:**
  - step 4 at 277,022×;
  - step 6 at 293,161×;
  - step 7 at 258,123×.

  These are measurements of the same packed shapes against a noise floor of about 6% (±30% within one small
  statement's sessions). Say "±6%".
- **Per-gate pricing:** 6.8% of the seconds, with the per-unit figure (247,793×) beside it.
- **Priced or excluded shapes** are under 0.02% of the gates: the embedding gather, which needs a 2^28-bit block, and
  `TokenSelect`. A footnote is enough.
- **Deviation 4** (no `REQUIRE_STAGED` markers in the early steps) is procedure, not what is proved: every timing names
  its cache entry, and the breakdown carries each shape's statement digest.

**Both rows:**
- **zkaudit hasn't run on the rows' own `--zk` statements.**
  - The 16 GEMM cells' zkaudit passes (K = 2048–16384) don't cover dense's K=14336 at k_log 26.
  - Nor do they cover the attention, RMSNorm, RoPE, SiluMul, MoeSum and router statements, with their tails and MUFU
    lookups.
  - The goal's "zkaudit-clean" needs at least one zkaudit per measured shape, at that step's N.
- **The two existing flags are right as written:** outputs public until #757, and `--zk` sessions verified by Rust, not
  Lean.

## 4. Coins: OK to cite with the note

Suggested wording: "M0 timings ran on seed-derived coins. The prover's work is the same function of the coin values
whatever their source (same binary, RoPE d64 at 1,024 instances, 8 alternating runs: prove median 0.113 s seeded,
0.107 s OS; r20261002-081752-12c7)."
- That run is a small statement, not a 2^35-bit one. The argument is structural; the run only shows that nothing else
  moves.
- `--zk` points already ran on OS coins: zk-all-cells labels them `live-os`.

## What I'd run (not submitted; @proofs places it)

The MoE re-measure, from `cursor/vllm-overhead-moe-95d4` with the driver fix: CPU staging, then two GPU jobs.
1. **Stage `f1e4d147` from `sweep-p` and `30cad3ca` from `sweep-k768`.**
   - Settings: `FLOCK_GEMM_TILE` unset, `BATCH_ANDS=MAX_STATEMENT_BITS=2^35`, `PIN=1`.
   - Expect `f1e4d147` at N = 2,048 and k_log 24: about 170 s and 13 GB, like dense's shape 1.
   - `GEMM_TILE` is in the stage-cache key, so these become new entries and the tiled ones stay.
2. **Prove both shapes in each mode** (`--zk`, M0): depth 8, 16 pinned cores, `FC_VERIFY_AHEAD=10 FC_VERIFY_SERVERS=11`,
   `REQUIRE_STAGED=1`.
3. **Roll up as step 6:** `--label untiled-gemm --label cap35 …`.

## Labels

- **On `art:df00ffbe…`:** `verdict no-grant`, plus three `finding` labels (the tile, the routing, zkaudit). Each refs
  this note.
- **On the dense row:** none yet. When it is final, its final breakdown gets `verdict grant` if zkaudit is clean and the
  citation carries the dense additions above.
