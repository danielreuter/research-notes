---
id: 20260926T1740Z-report-flock-netlist
campaign: boolean-escape-hatch
lane: flock-netlist
kind: report
status: open
repo: danielreuter/verity
origin: cursor/flock-netlist-m0-4d6a
branch: cursor/flock-netlist-m0-4d6a
---

CHECKPOINT e231d583 (18:05Z) [open] GPU path works on RTX 4090 dev pod: device witness + multi-range fold, GPU selftests all-pass RoPE (k_log 20) and SiLU (k_log 26, private BLAKE3 parent tree) r20260926-175514-5b86; verifier-tail refusal + negative (Daniel's rule) landed; now timing r20260926-180450-ecfa; L40S hunter running (no stock); next RMSNorm tail in circuit (MUFU lookup slots)
CHECKPOINT 9fd167e1 (17:40Z) [open] started M0: verity/flock-netlist/v1 CPU statement landed (RoPE 19/19 CPU selftest cases incl relabelled netlist, SiLU in-circuit parent tree); next GPU device witness + multi-range fold; branch cursor/flock-netlist-m0-4d6a; agent bc-ff572e70
# flock-netlist: M0 `verity/flock-netlist/v1` (NON_ZK, ZK-ready)

Spec: Project store `docs/boolean-prover-scoping.md` (M0 row, M0 acceptance, section 4). Agent bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a.

## Design (as built)

- One or more whole VUs per block; every glue inside a block is a copy constraint (Δ); no prover-supplied value, no glue claim.
- Slot types per block: BLAKE3 compressions (chunk runs per port; for a multi-chunk port its parent tree, root first), the
  template's units, a reserved mask slot (free cells, A = B = I), forced-zero padding apart from it.
- Public: frame-v3 roots, the row digests (serving leaves; unsalted until Daniel's call), declared outputs, the pinned layout.
  Chaining values, chunk values, every word between slots: private.
- The pinned composite netlist (`flock-netlist/v1`, sha256 = pin) is the meaning: META (ports, ranges, compression roles, leaf
  and output maps, pinned padding-instance values, leaf-commitment scheme) + each slot type's `flock-ir-unit/v2` netlist. The
  verifier derives Δ, regions and values from it and its own public file (no rows).
- Code: `backends/flock/python/verity_flock/netlist.py`, `backends/flock/live/src/{netlist,zk_hooks}.rs`, `bin/flock-netlist.rs`.

## Standing rule (Daniel, 18:01Z): the verifier evaluates no part of the computation

Tightens scoping §4.1 (no exception for functions of public data). Built into the statement: `Composite::parse` refuses a `CUT`
line in any NET and META keys `tail`/`cut`/`cut_words`/`public_ports`/`public`/`native`; negative `verifier_evaluated_tail_refused`
(both forms refused at parse). The verifier no longer evaluates the unit netlist on zero inputs to check the pinned padding
outputs (the circuit forces them; a wrong pinned value only makes the statement unsatisfiable). It still hashes a zero row to
check the pinned padding digest (the commitment scheme's own function) and recomputes the frame-v3 roots.

Sampling under the rule (not in M0 acceptance; estimate, not lowered): per vocabulary lane, Gumbel noise =
Philox4x32-10 (~15k ANDs/lane amortised) + libdevice `logf(-log1pf(-u))` (~24 fma + 5 mul + 3 add + add.rz + 3 cvt ≈ 125k
ANDs at the fp piece costs 4,498 / 2,406 / 823) ≈ 140k ANDs/lane vs 5,099 today (27x); V = 128,256 → ~1.8e10 ANDs/row;
#101's 32 rows → ~5.8e11 ANDs (+0.37% of #101's 1.57e14; ~+580 L40S-s at 1 G AND/s ≈ +1.1% of ~51k s). Top-p keep word
(MUFU EX2/RCP over whole-row reductions) in circuit: the scoping's x2 on sampling (another ~0.65 G ANDs/row) plus EX2/RCP
lookup slots (~40k ANDs each). Sampling carries become private Δ glue between consecutive lane units (free).

## Checkpoint results (18:25Z)

- CPU selftests: RoPE 20/20, SiLU (in-circuit BLAKE3 parent tree) all pass (local).
- GPU (RTX 4090 dev, then L40S): selftests all-pass RoPE k_log 20 and SiLU k_log 26 (runs r20260926-175514-5b86,
  r20260926-180609-0360); device witness = BLAKE3 kernel + new bit-sliced level-ordered unit kernel; multi-range fold.
- 4090 loopback timing (r20260926-180450-ecfa): SiLU 32 rows (707M ANDs, m=31, both reps) e2e 0.218 s = 3.2 G AND/s;
  device witness units 17 ms, compressions 4.5 ms per rep.
- Tail pieces: RsqrtApprox (954 ANDs), MufuSqrtFtz (148), DivFullRcp (5,657) exact vs the IR primitives on ~4k words (19
  NaN-payload-only differences in DivFullRcp from fp's canonical NaN, the lowering's existing policy). Lookup slot (lookup.rs):
  fast witness = its rows' evaluation (unit test). RMSNorm tails: fused 2 stages (27.7k + 0.2k ANDs) + 1 rsq lookup; Triton
  3 stages (8.5k + 3.3k + 5.0k) + sqrt + rcp lookups (DivFullRcp of the constant N folded).
