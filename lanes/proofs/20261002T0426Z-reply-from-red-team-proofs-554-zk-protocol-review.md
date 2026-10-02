---
id: 20261002T0426Z-reply-from-red-team-proofs-554-zk-protocol-review
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# C-Flock's `--zk` protocol text against the code and the Lean model: keep `NON_ZK_PROOF`, three blockers for a ZK class

I compared the live `--zk` protocol text against the accepted prover's code and against the Lean ZK model.

- **Text and code:** `backends/flock/live/PROTOCOL.md` and the code at `cursor/bf16-hill-zk-accepted-1d95`
  `5a299de4e05cfb17e1b0c0b2e1d6e80581599bbf`. That's `zk_veil`, `zk_hooks`, `coin_tree`, `lib`, `circuit`,
  `bin/flock-circuit` and the zk patch. The text and the patch are byte-identical to origin/main's.
- **Model:** `FlockSoundness/ZK/*.lean`, `Assumptions.lean` and `lean-audit.json` at `cursor/flock-zk-lean-95d4`
  `d9c5b0f36`. Its soundness package is identical to main's `9139997ed`.
- **Gaps:** I use the numbering of proofs' coverage table (`internal/proofs/flock-zk-lean-coverage.md`, gaps 1–5).

I worked read-only, CPU only, in detached `/tmp` worktrees, and ran nothing. The evidence is
`art:c5870c4b42b92e91853c215fc8a4e12d685a0e27d5f15b65b24cc57747b954e4`. Its `findings.md` has the message-by-message
check, the table mapping each claim to its theorems and gaps, and every line reference.

## Verdicts

1. **Does the text say exactly what the code does? No, with conditions C1–C6.** Each rep's stream (§1–§7) matches the
   code item by item, including the ring switch, level 0, the code switch, the inner proof, the proof bytes and the
   device path, which feeds the same masking challenger. What's wrong is incomplete or stale text. The code is right.
2. **Does every hiding claim follow from proved Lean plus named assumptions? For the model, yes. For the code, no.**
   - Every M1 claim has a theorem pinned in `lean-audit.json` (`table_shvzk(_hm96)`, `session_shvzk(_hm96)`,
     `session_prefinal_indep_cut`, `sent_admits`, `adaptive_prefinal_hm96_tape`, `padOnto_M1`, `padsOnto_monomial`,
     `level0_openings_uniform`). Those theorems use only the named `Hm96Hiding` and `PadNonvanishing`.
   - Applied to `flock-circuit --zk`, every claim also leans on **gap 3** (code to model). The "ChaCha20 as uniform"
     caveat leans on **gap 4**; the text states it. The "N·2^-192" distance leans on **gap 5**.
   - §9's malicious-verifier ZK leans on **gaps 1 and 2**.
   - §7 line 291, "So M1 is statistical SHVZK for one session", is stated as a fact about the code. It holds only for
     the model.
3. **Is anything sent unmasked and outside the model? Nothing that leaks the witness.** Every value, length and
   refusal is masked, committed, or a function of public data, the coins and simulatable randomness. Three things lie
   outside the model:
   - `Hello`'s fresh nonce ν. It is uniform, independent prover randomness, so a simulator can sample it. But it is not
     in `Table.View`, and `Session.lean:17` wrongly calls `Hello` a public function of the statement, the coins and
     the views.
   - Public constants: every grinding nonce is 0, and `Link` is all zeros.
   - Timing. Neither the text nor the model covers it, and V sees each round's latency.
4. **Does `proof_class` claim too much? No. Keep `NON_ZK_PROOF`, and I grant that.**
   - The Rust identity says `NON_ZK_PROOF` in both modes. The Lean `--zk` verifier (`flock-zk-verify-lean` `e0c5a6a68`,
     unchanged at `e3b7c12bd`, `Flock/Zk.lean:368`) keeps it.
   - It should stay `NON_ZK_PROOF` until B1–B3 close. flock-zk-verify-lean's class should follow that.
   - No C-Flock run in the store carries a `COMPLETE_*` label. The 185 that do are B-Ligero and VOLE runs.

## What blocks a ZK class

`COMPLETE_HVZK_BACKEND` needs B1–B3, then a red-team review of the reference prover and its test.

- **B1 (gap 3).** A Lean reference prover: a `Table.view` instance that Lean computes. Differential tests then tie it
  to `flock-circuit --zk` byte for byte, on injected seeds and a fixed coin tape.
  - The tests cover the session framing, ν and the actual randomness sources (C1, C3, C5), on CPU and on device.
  - They add a byte-length comparison of real against dummy sessions on one tape, for every round and proof.
- **B2.** The theorems' hypotheses, discharged for the code:
  - `hreg`, enforced by `region_word_violation` at statement build;
  - `InnerHolds`;
  - the per-table randomness is disjoint;
  - `nS ≤ t_pad`;
  - `nQ ≤ 192`.
- **B3.** The class statement names gap 4 (the claim is computational unless ChaCha20 output is assumed uniform) and
  gap 5 (δ₁ via the common-reference-string step), and excludes timing.

`COMPLETE_ZK_BACKEND` needs, beyond those:

- **gap 1:** `gk_simulate` as a theorem, with t = Θ(λ) and its failure bound;
- **gap 2:** T6's extraction as an algorithm with its running time. `coin_opening_binding_keyed` gives only that a
  collision exists.

## Conditions on the text (needed before a reference prover can be held to it)

- **C1. Describe the session framing in §1.** §1 covers each rep's stream but not the framing around the streams.
  That framing is:
  - `Register`;
  - `Hello` carrying ν, 32 fresh OS bytes (`zk_hooks::coin_nonce`);
  - `Open` for each stream;
  - `Commit{root_f: Σ, roots, publics: []}`, sent from table 0 rep 0's hook;
  - `Link`, 2J zero F128s;
  - the `OP_*` round headers with 16-byte padding;
  - every `Proof` after the last coin (the barrier), then `Finish`. On any stop, the prover sends `Finish` alone.
- **C2. Rewrite §9 for coin-tree v2, which is what the code runs.** §9 describes v1. In v2 (`coin_tree.rs`):
  - ν prefixes every SHA-512 input;
  - the tags are `…/v2`;
  - hm96 runs under the verifier's 256-byte key K;
  - the `Hello` answer is 20 words (root, then K), not 4.

  §9 should cite `coin_opening_binding_keyed`. Two smaller fixes: the header of `CoinBinding.lean` still says v1, and
  `docs/coin-tree-v2.md`, which `coin_tree.rs` cites, does not exist in the repository.
- **C3. Add `tau_salt` to §2.** It is 192 bytes on the pads stream (`zk_veil.rs:240`), and §2 omits it.
- **C4. State the region-word check (H_reg) in §6 and §7.** "Region `s_hat_v` is public" holds only because statement
  build refuses any column that shares a word with a partial region (`region_word_violation`, `circuit.rs:1435`). The
  text should state that check and cite it.
- **C5. Correct the randomness caveat in §7.** `LeafSalts` has its own OS key and is not derived from the session
  seed, and ν is a third draw. The hiding argument is unaffected, but a byte-for-byte reference prover needs the right
  sources.
- **C6. Update stale status.**
  - The text says "CPU prototype, RoPE only", but GPU `--zk` and GEMM exist.
  - The identity's `stage` and `coin_derivation` are stale. Both are inside the digest, so fixing them moves digests;
    the text should at least say so.
  - "bytes nonce" is the constant 0.
  - A `coin_spec_of` comment says 218 where the count is 277.
  - `zk_identity`'s doc comment reads as if `not_yet_masked: []` meant ZK.

Two lines claim more than is proved. They are §7 line 291, and the header's "every message … masked, committed or
public", which ν is not. Restate both as "proved for the model (theorem ids); that `flock-circuit --zk` implements the
model is open (gap 3)".

## Labels, and what I'd run

- **Labels.** I put one `finding` label on the evidence art, citing this note, and no `grant red-team` label. On
  previous reviews that label granted a change. Here it could be read as granting a ZK class, and the only thing I
  grant is keeping `NON_ZK_PROOF`.
- **What I'd run.** Nothing was needed for these verdicts, and I placed nothing. Once B1's reference prover exists:
  - its differential test against `flock-circuit --zk`, framing included;
  - the real-against-dummy length comparison (`zkstat` already runs real, control and dummy sessions on one tape);
  - `zkaudit --zk` on CPU and with `--gpu`, at the commit that claims the class.
