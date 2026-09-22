---
id: r20-proof/a-verifier-2/20260922T1054Z-finding-f1-triage
campaign: r20-proof
lane: a-verifier-2
kind: finding
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/gkr/gpu/F1_TRIAGE.md
---

# F1 triage: the committed Triton-kernel path vs the torch path (a-verifier-2, 2026-09-22)

**Verdict: not reproducible on a clean card.  The committed `main` kernel path (48897d1, `backends/gkr/gpu` at
86f064d) produces proofs that are byte-identical to the torch-reference path and that the Rust verifier accepts at
B = 2 (synth), 64 and 512 on vy-sp1 (RTX 4090, sm_89, `~/.triton/cache` wiped first).  A per-level diff harness
finds zero differing entries in any intermediate of any of the 5 lookup tables.  So the vy-g5 rejection reported in
`note:r20-proof/a-verifier/20260922T0942Z-report-a-verifier-discrepancies` (F1) is hypothesis (b) -- an environment fault on that pod
(stale `~/.triton/cache` serving a wrong binary to the old tree, or its torch/triton versions / sm_90 codegen), not a
latent bug in `_fast_phase1` / `_fast_combine_level` / `_fast_scatter` (a).  The a-gpu 4.43 s / "4096/4096 accepted"
row still needs re-recording from a committed tree with a proof file the Rust verifier accepts; it has not been
reproduced from any commit on vy-g5.**

## Evidence (run `r20260922-100739-bc57`, vy-sp1; exports built in the run-1 attempts `r20260922-094836-64d2` .. `-095933-ca30`)

Environment: RTX 4090 24 GB, driver 580.159.04, torch 2.6.0+cu124, triton 3.2.0, cupy 14.2.0 (lane venv
`/workspace/venv-av2`).  `~/.triton/cache` had 16 entries before the run and was deleted; 52 entries were compiled
fresh during the run.  Instances: `pos4096` (the bench-instances v1 export, `vu-k1536`), `synth2` (`--synth 2`).

| instance | path | prover s (rep 1 / warm) | Python verifier | Rust verifier (16T) | proof bytes |
|---|---|---|---|---|---|
| synth B=2 | kernel | 401.3 (compile) / 6.29 | accepted | accepted, 0.069 s | 433 660 |
| synth B=2 | torch  | 8.31 | accepted | accepted, 0.066 s | 433 660 (byte-identical to kernel) |
| pos4096 B=64 | kernel | 29.0 / 7.28 | accepted | accepted, 0.129 s | 1 000 060 |
| pos4096 B=64 | torch  | 12.3 | accepted | accepted, 0.132 s | 1 000 060 (byte-identical) |
| pos4096 B=512 | kernel | 12.35 / 11.28 | accepted | accepted, 0.506 s | 4 673 980 |
| pos4096 B=512 | torch  | 31.6 | accepted | accepted, 0.510 s | 4 673 980 (byte-identical) |

(`cmp` on the six `proof_*.bin` files: the kernel and torch proofs are identical bytes at every size, so the two paths
agree on every committed value, every LogUp message and every opening, not just on acceptance.  B = 4096 was not
run on the 24 GB card in the triage hour; B = 512 peaked at 11.1 GB, so B = 1024-2048 is likely feasible there.)

Diff harness `python -m gpu.f1_diff DIR [--vus N]` (`backends/gkr/gpu/f1_diff.py`): builds the instance once,
derives the same transcript challenges, then for every lookup table runs the level-0 leaf build and every
`combine_level` / `fold` / `ext_mul` / `logup_round` step through BOTH the Triton kernels and the torch references on
the same inputs, and reports the first mismatching tensor.  Results (`diff_64.json`, `diff_synth2.json`):
`differing_entries: 0` for every tensor of POW, ALIGN, LEAD, NORM, R16 at B = 64 (POW n = 14, ALIGN n = 17, R16
n = 22, m.max = 261) and at synth B = 2; the kernel-chain root `(p, q)` equals the torch root for every table;
`ALL MATCH`.

The kernels under suspicion are the same code in both trees: `git diff c4d472a main -- backends/gkr/gpu/kernels.py`
only *adds* `eq_outer_kernel`, `rank1_add_kernel`, `split_limbs_kernel` (a-gpu2); `phase1_round`, `combine_level`,
`scatter_terms`, `fold`, `logup_round`, `ext_mul` are byte-identical, and `logup.py::_combine_level` / `build_leaves`
call them the same way.  So the triage on `main` covers the c4d472a kernels; `main`'s prover is the a-gpu2 merge
(2e1ef3f: packed LogUp/GKR phase 1, CUDA graphs, INT8 opening), which is therefore also Rust-verified here at
B = 2 / 64 / 512 from a committed tree (the a-gpu2 merge message left that open).

## What this rules out and what it does not

- Rules out a deterministic kernel bug in the committed level-0 build / tree combine for these table sizes and
  multiplicity ranges on sm_89: the numerators and denominators agree entry-for-entry at every level.
- Rules out a proof-serialisation fault: byte-identical proofs.
- Does not exercise B = 4096 (memory) or sm_90.  A race that only manifests at H100 occupancy / tile configs is
  not excluded by this run, but the vy-g5 failure was deterministic at B = 2 as well (`note:r20-proof/a-verifier/20260922T0942Z-report-a-verifier-discrepancies`,
  F1: synth B = 2, 64 and 4096 all rejected at `LogUp POW level 0: final check`), and B = 2 passes here with the
  same code -- a deterministic failure at B = 2 on one card and a bit-exact pass on another points at the binaries
  the card ran, not at the arithmetic.

## Recommended follow-up (a-gpu2 / whoever owns vy-g5)

1. `rm -rf ~/.triton/cache` on vy-g5, re-run `python -m gpu.run prove /workspace/bb/pos4096 --device cuda --vus 64
   --proof-out proof.bin` from a committed tree and verify with `verity-gkr-verify verify`.  If it passes, F1 was the
   cache; record the tree sha and the cache state in the ledger note.
2. If it still fails on the H100 after a cache wipe, run `python -m gpu.f1_diff /workspace/bb/pos4096 --vus 64` there:
   it names the first divergent tensor (kernel, level, `differing_entries`, first index) and is the reproducer to
   hand over.
3. Re-record the a-gpu B = 4096 row with `--proof-out` and the Rust verifier's acceptance JSON attached.

Reproduce this triage: `backends/gkr/verifier/scripts/f1_run2.sh` (run on vy-sp1 via
`research run --on vy-sp1 --project verity --source . --stage a-verifier-2.f1.run2 --send scripts/f1_run2.sh`).
