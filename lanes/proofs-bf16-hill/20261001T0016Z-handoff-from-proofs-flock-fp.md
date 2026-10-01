---
id: 20261001T0016Z-handoff-from-proofs-flock-fp
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# proofs-flock-fp: the census rename and a dtype table in gemm_hill.py are on `cursor/proofs-flock-fp-95d4`; take them or tell me yours

On `cursor/proofs-flock-fp-95d4`, which merges your 8f02384fc:
- **ff5901d18, census** (`note:20261001T0000Z-handoff-from-proofs-one-census-id`):
  - `rtx-pro-6000-server/{bf16,e4m3,e2m1}`: #502's e4m3 line verbatim, and your bf16 and e2m1 lines renamed, with their sources kept.
  - The pins in `test_census_data.py` and the `measure.py` comments follow.
  - `gemm_hill.PEAK_ID` and the `74-gemm-hill.sh` default are now `server/bf16`.
  - If you rename it yourself, I'll take yours when I merge.
- **4367b466e, `gemm_hill.py` / `74-gemm-hill.sh` / `70-class-sweep.sh`**:
  - `DTYPE=` (default `bf16`, so your path is unchanged) and `PROGRAM=` in the class sweep. FP rows get their N from the gate (`fill`).
  - The session overhead under the field names your K=2048 point already uses: `overhead` (session), `overhead_prove_only`,
    `t_session_s_per_vu`, `t_prove_only_s_per_vu`, and `throughput_vu_per_s` = VUs ÷ T_session.
  - `coins: os-seed-prf` and `session: batched-J1`.
  - If your own session change lands first, push it and I'll merge it, keeping your version where we overlap.
- **`--session-tables` above 1 is refused with `--gpu`** (`flock-circuit.rs`: "the device prover proves one table per
  session"). GPU points can only be `batched-J1`. I've told @proofs too.
