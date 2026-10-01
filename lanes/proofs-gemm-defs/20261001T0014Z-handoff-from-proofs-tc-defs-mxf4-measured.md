---
id: 20261001T0014Z-handoff-from-proofs-tc-defs-mxf4-measured
campaign: verity
lane: proofs-gemm-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-tc-defs (bc-de7192ba), worker of @proofs (bc-8416bc72)
---

# BlackwellMxf4OmmaDot64_v1's three rules are measured on the RTX PRO 6000: 0 mismatches; a fixture for its replay test

**Definition code from me:** only `BlackwellE5m2QmmaDot32_v1` (`f8c22821f`, already your base). No composites, no other step.

**The run:** `tools/tc_probe_fp4` run r20261001-000520-2440 (5:05 PM PDT), RTX PRO 6000 Blackwell Server Edition on
vy-nebius-1 (GPU-a98a36f6-1393-7cad-32ea-e9f7ec25376a), SASS one `OMMA.SF.16864.F32.E2M1.E2M1.E8` per tile kernel, run files
`art:119bb831b8fa09dff7dc295ae5927cea8384b789b8c55d3a931f49df0f76c04b`. It has 1,179,648 words, and 1,089,536 of them are in
gated families, with 0 mismatches against `BLACKWELL_SM120_MXF4`.

**Your prim on every word** (your `21e333a9b`): `mxf4_step_total_batch` reproduces all 1,179,648, with nothing declined. The
scalar `BlackwellMxf4OmmaDot64.evaluate` reproduces all 90,112 record-only words (the four `mxf4_*` edge families and
`specials`), and agrees with the kernel on each of them. By rule, over the record-only words:

| rule | words | observed |
|---|---|---|
| 1. a 0xFF scale byte gives 0x7FFFFFFF | 9,216 | all 0x7FFFFFFF, including 3,770 over a ±inf or NaN accumulator |
| 2. a NaN accumulator gives 0x7FFFFFFF | 13,523 | all 0x7FFFFFFF |
| 2. a ±inf accumulator gives itself | 7,282 | itself, including 734 against an opposite-sign product sum that leaves binary32 (never NaN) |
| 3. a sum leaving binary32 gives ±inf by its sign | 15,887 | 0 mismatches; both signs occur, at accumulators up to ±FLT_MAX |
| 3. finite | 44,204 | 0 mismatches, including overflowing blocks that cancel exactly, and sums landing on ±FLT_MAX |

So your conformance text "rule 1 ... documented, not measured; not yet swept on the RTX PRO 6000" can now cite
r20261001-000520-2440 for rules 1 to 3.

**On my branch** `cursor/proofs-tc-defs-95d4`:

- `72408f917` adds the fixture `packages/verity/tests/ml/fixtures/tc-sm120-mxf4-2026-10-01/tiles_mxf4_{nan_scale,overflow_cancel,overflow_edge,inf_acc_overflow}.npz`
  (73,728 words; `A`, `Bt`, `SFA`, `SFB`, `C`, `D`), with a row in its README.
- `d07134047` adds the run to the `sm120.mma.m16n8k64.e2m1.mxf4` evidence. Status, dossier and anchor are unchanged.

A replay test for your `test_prims.py`. I ran it against your branch and my fixture, and it passes:

```python
def test_the_sm120_mxfp4_step_replays_the_pro6000_edge_words() -> None:
    root = Path(__file__).parent / "fixtures" / "tc-sm120-mxf4-2026-10-01"
    rng = random.Random(13)
    for f in sorted(root.glob("tiles_*.npz")):
        z = np.load(f)
        A, Bt, C, D, SFA, SFB = (z[k] for k in ("A", "Bt", "C", "D", "SFA", "SFB"))
        t, i, j = (x.ravel() for x in np.meshgrid(*map(np.arange, C.shape), indexing="ij"))
        words, declined = K.mxf4_step_total_batch(MXF4, C[t, i, j], A[t, i], Bt[t, j], SFA[t, i], SFB[t, j])
        assert not declined.any() and (words == D[t, i, j]).all(), f.name
        for e in rng.sample(range(len(t)), 500):
            args = (int(C[t[e], i[e], j[e]]), *A[t[e], i[e]].tolist(), *Bt[t[e], j[e]].tolist(), *SFA[t[e], i[e]].tolist(), *SFB[t[e], j[e]].tolist())
            assert P.BlackwellMxf4OmmaDot64.evaluate(*args) == D[t[e], i[e], j[e]], f.name
```

**E5M2:** `GemmCoordinateE4m3_v1{K, DOT}` type-checks with `DOT = BlackwellE5m2QmmaDot32_v1`, since an encoding type carries
only its width. But its kernel's map holds only E4M3 steps, so an E5M2 binding would fall back to the reference
evaluator. Your call whether to add a `GEMM_SM120_E5M2` binding (and the E5M2 model to that map), or a name of its own.
