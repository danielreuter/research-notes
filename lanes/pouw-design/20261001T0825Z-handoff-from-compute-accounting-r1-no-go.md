---
id: 20261001T0825Z-handoff-from-compute-accounting-r1-no-go
campaign: verity
lane: pouw-design
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c5d0d68e: the red team's NO-GO on R1. Run the CPU census of the chain start before any GPU benchmark

From compute accounting, 1:25 AM PDT. The verdict is `note:20261001T0822Z-reply-from-d545bc2a-new-designs-r1-no-go`; the full
review is in the Project store at `private/pouw/red-team-lean/new-designs-r1-review.md`.

**The blockers:**
1. **R1's unpromoted chain from +0 is plain v2's chain,** which the assessor rated D. Charged for the chain start it's at least
   0.946% at 8,192³ (1.18–1.46% with v2's measured charge), and about double at k = 4,096.
2. **The keyed rotation doesn't reach `o_proj`'s or `down_proj`'s inputs.** That's about 35% of Llama-3.1-8B's linear MACs, and
   a crafted model can feed exact relations there.

**Also open:**
- freshness across audit windows;
- ε_f's downstream corruption;
- row 8's first clause, which is a verifier check, not an assumption;
- duplicate detection on the chain's input codes, including scaled and negated copies;
- R2's per-call versus per-epoch rotation.

**In order:**
1. **No GPU benchmark of R1 yet.** Run a CPU census, bit-exact, of the exact regions from +0 on rotated, model-reachable rows,
   separately for `o_proj` and `down_proj`. If the chain start costs 1–4 points, R1 is out whatever its cost.
2. **Re-rate row 9** honestly, without Pearl-C's B ratings, which rest on salted, noised operands.
3. **Answer the review's 7 conditions.** Repair R2, or propose a candidate that covers `o_proj` and `down_proj`.
4. **Update `docs/pouw/new-designs.md` in place,** then ask for a re-review in one line in `lanes/accounting`.

The two questions for Daniel are on my morning list already: the input model (R1 lets the prover choose the tokens), and
whether model approval carries security weight.
