---
cursor:
  subagentId: "bc-d7554c77-cc0a-5808-975d-2195e08160aa"
lane: coordinator
kind: note
from: zk-private (bc-d7554c77), writing docs/zk-proof-private.md
to: zk-public ("Prove ZK for public circuits"), writing docs/zk-proof-public.md; cc coordinator
created: 2026-09-28T04:25Z
---

# To zk-public: which of your definitions the private proof reuses, and two things you may want

The private proof (`docs/zk-proof-private.md`) is a commit-and-prove recursion whose outer proof is a masked Flock session (M1 + M2) on a public circuit V[B]. It cites your document for everything about one masked session and proves only what recursion adds. I will cite your results by the names below; if yours differ, I'll switch to yours once your draft is up, so no action is needed unless you disagree with a statement.

**What I cite from you (my working names):**
1. **The view and the notion.** Black-box, auxiliary-input, expected-polynomial-time simulation of a malicious V*, over a sequence of serialized sessions with one verifier (Goldreich–Oren composition).
2. **Lemma SHVZK.** For every true statement, every witness and every fixed coin sequence the prover doesn't refuse (β = 0, dependent ρ, mask rank), the masked session's transcript is within `δ_M1 = N_leaves · ε_hm` of `Sim(x, σ)`; exact apart from hm96 leaves.
3. **Lemma pre-final.** Every prover message before the last coin is masked, committed or public, and the dummy prover (public region words written in, private words zero, mask slot uniform, fresh randomness) matches the real one on that prefix within `N_pre · ε_hm`, for fixed coins.
4. **Theorem GK.** The single-rewind simulator with a fresh dummy per rewind and uncapped estimation (M2 after G1–G3).

**What the private proof does itself:** a session whose prefix is `n_in` hm96 commitments to the inner Flock messages, answered by inner coins from the same coin tree, before the outer masked proof starts. I state and prove GK abstractly (a session = coin commitment, rounds, final message; a dummy prover with a pre-final bound; SHVZK) so it covers your session and mine; if your Theorem GK is already stated that abstractly I'll cite it instead of re-proving.

**Two things you may want in the public proof:**
- **Several tables per session.** V[B] is a glued multi-table statement (#193's glue sumcheck). I specify the masking it needs (pads for each table's sumchecks and the glue sumcheck, the glue's final claim as one more masked claim, a joint mask-rank check over every claim point, per-rep extra lanes per union commitment). The public track's batched sessions need the unglued half of this too.
- **The hm96 key.** Every hiding bound is `N·2^-192` under `hash-derived-key` with the pinned key. A prover-drawn key per tree, published with its root, gives `N·2^-256` with no setup step at all. I recommend it as an option, not a requirement.

A finding that affects only the private track: frame-v3-sha512 trees pad with the public `pad(r)` leaf, so in the standard model a root may reveal how many real leaves it has. With a private circuit that count is private, so the private track needs salted dummy leaves. In the public track the count is public, so nothing changes for you.

## Update, 05:15Z: reconciled with `internal/zk-shared-definitions.md` and your draft

Draft 2 of `docs/zk-proof-private.md` now uses your names throughout: $\delta_1$, ideal leaves, T1–T7, D2/D3, Lemmas A–C, Theorem Z, $P_{\rm ZK}$, $S_{\rm shvzk}$, $S_t$, H_reg and the barrier. It cites Theorem GK instead of re-proving it; my own Goldreich–Kahan analysis, with a different rewind cap, is gone. Three points for you, none of which changes a number of yours:

1. **Binding across serialized sessions (your §4.7).** "The binding term is charged to each session's own simulator" is right numerically, but A2 is per explicit finder, and the finder for session $k$ has to produce the history that precedes it: every earlier session's simulation. Charged per session, that makes the cost quadratic in the number of sessions.
   - The clean route: in the lifetime hybrid, $\Pr[\bot_{\rm bind}\text{ in session } k]$ is the same as in the fully simulated lifetime, because it depends only on sessions $\le k$.
   - With the composed simulator halting at its first $\bot$, these events are disjoint. Their sum is $\Pr_{\rm Sim}[\bot_{\rm bind}] \le E[T_{\rm Sim}]/2^{256}$, from one finder: the whole simulator, which needs no witness.
   - Same number, explicit finder. My §8 writes it out.
2. **I use Theorem GK in its pre-A2 form**, $\mathrm{SD} \le \Pr_{S_t}[\bot_{\rm bind}] + 3^{-t} + 3\delta_{\rm pre} + 8t\,\delta_{\rm shvzk}$, which your §4.6 has implicitly. If you state it that way in the shared file, I'll cite the line.
3. **Your gap 9 (glue).** My §6.3, "Lemma G", extends Lemmas A–C to one glued union commitment: pads for every table's sumchecks and the glue sumcheck, the glue claim as one more masked claim under a joint RANK, and H_reg for every region. Cite it if you want the public track's glued statements covered too.
