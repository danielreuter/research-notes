---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the public-circuit ZK proof (bc-b483c71e) · 2026-09-28 05:20Z · re: `docs/zk-proof-public.md`
§2.8 row 9 and §7 gap 4

# The GPU `--zk` path: inside §2.8, with one change of row 9 and one refusal detail

**Short version.** The port is [PR #229](https://github.com/danielreuter/verity/pull/229) (branch `cursor/flock-zk-gpu-5659`,
draft). It is built to meet gap 4 as you state it: the same randomness layout and the same transcript. For equal seeds and
coins it must give byte-identical proofs and transcripts to the CPU prover, and a selftest case checks that
(`gpu_proofs_match_cpu`). Nothing in $P_{\rm ZK}$ changes. No multi-table sessions are added, so the barrier rule doesn't come
up yet. **It hasn't run on a GPU yet**: it compiles for sm_89, and I'll send the equality result when the first pod has run it.

## What changes in §2.8

- **Row 9.** "`--zk` is CPU only" becomes: a GPU path exists and is held to the CPU prover's bytes by a differential test
  (the GPU prover against the CPU prover, not yet a Lean reference). Gap 4 then closes through gap 3, as you wrote.
- **Row 10.** The masking now sits on #193, which is on #192. Your row already covers the rebase given H_reg.
  - #193's multi-table glue statement (`verity/flock-tables`, your gap 9) isn't touched: `--zk` stays the single-table
    `verity/flock-circuit`.
  - On the merged base, CPU `selftest --zk` passes 31/31 on RoPE, with circuit `d2dafe7efdde`, #192's pin.

## Randomness (§2.2): the same draws, from the same streams

- **Drawn on the host, as on the CPU:**
  - `ProverRng` streams 1 (mask slot), 6 ($R_i$), 7 ($\mu_l$), and 4 and 5 (pads, inner proof, $y_\tau$);
  - `level0_zk` and `Pads::draw` run unchanged, before the rep's proof.
- **Uploaded to the device:**
  - the mask slot, as host slots of the device witness ($z = a = b$ on the slot, since its circuit is the identity);
  - $\mu$ and $R$, as flat arrays.
- **hm96 salts:** the device expands ChaCha20 under the same `LeafSalts` key.
  - Tree 0 is level 0.
  - Every later tree takes `next_id()` in the same order as on the CPU: the rep's pads tree first (on the host), then level
    1 onward as the device builds them.

## The prover's messages (§2.4): the same calls

- **Lines 1–14.** The device frames each round as upstream's prover does. The host then makes that round again through the
  same `zk_veil::Masking` challenger (`flock_live::replay_round`):
  - each frame's kind picks the call: scalar or slice observe, label, bytes, then the squeeze;
  - so `Masking` sees exactly the CPU prover's calls: the pads root after `flock-zerocheck-v0`, the pad order and RANK at
    `flock-pcs-open-batch-v0`.
- **Line 15.**
  - Level 0's codeword is `commit_zk`'s. Every lane $\mathrm{Enc}(P_l + (X_L + \kappa)\mu_l)$ goes through the full
    transform, since the padding's upper half isn't zero; a CPU check confirms it equals `commit_zk`.
  - The lane phase's step runs between the last lane fold and the code switch: $e$, then $\rho$ as two squeezes with the
    independence refusal, then the blind with $T'$, then $\bar y$. It is `backends/flock/cuda/ligerito_zk.cuh`.
  - The enforced sum isn't computed on the device. Upstream's presplit introduce only asserts it, and the GPU ladder takes
    the message straight from the blinded table.
- **Line 16 and §2.5.** These are `zk_finish`, the same function the CPU prover now calls: the masking, the replay, the
  constraints, the inner proof and the `bincode` of the proof.

## One refusal detail (§2.6, row 4): the same view, different timing

- **How the device treats a refused coin:** it calls `abort()`, since M0's live hook can't unwind. So a round that fails on
  the host is latched instead:
  - the failure can be RANK (inside `Masking`), an invalid coin opening (`coin_tree::Checked`) or `LIVE-REFUSED`;
  - that round's squeeze isn't sent, since the panic comes before it, just as on the CPU;
  - no later round reaches the verifier;
  - the device finishes its computation locally and nothing more is sent;
  - `session` then raises the same `PROVER-STOPPED` / `LIVE-REFUSED` and sends `Finish`.
- **So $V^*$'s view is the CPU prover's.** Only the time until `Finish` differs, which is outside the model (gap 11).
- **The dependent-$\rho$ refusal** happens on the device itself, which returns before its next round.

## Appendix A, for the GPU path

| pseudocode | GPU code (PR #229) |
|---|---|
| §2.3 lines 4–8 | `wit` (mask slot, stream 1, uploaded as host slots: `mask_host`), `level0_zk`, `fc_commit_l0_zk` (`backends/flock/cuda/prove_circuit.cuh`) |
| §2.4 lines 1–14 | M0's device prover, each round through `replay_round` into `zk_masking`'s `Masking` (`flock-circuit.rs`, `gpu.rs::Rounds`) |
| line 15 | `run_ligerito_f256` with `LigZk` (`ligerito_zk.cuh`, installed by `cuda_circuit_patch.py`) |
| line 16, §2.5 | `zk_finish` (shared with the CPU prover) |

The region-words gap (your gap 2) is noted. It's verifier-side, and I'm not blocking on it.
