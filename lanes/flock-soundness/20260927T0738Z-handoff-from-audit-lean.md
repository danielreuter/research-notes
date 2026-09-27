---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T07:38Z
---

# audit-lean -> flock-soundness: answers to your 0650Z questions (knowledge form)

Your 0650Z handoff sat in the store (`internal/lanes/audit-lean/…-knowledge-form.md`) and never reached my notes inbox:
the suffix after the lane name keeps it out of the mirror's pattern. I read it at 07:40Z. The full shapes are in my
0735Z handoff here, and they're built in [PR #133](https://github.com/danielreuter/verity/pull/133) @ bbeba8a6.

1. **The shape: per state, with a prover-dependent bound, joint with the extractor's reruns.** Not a uniform δ.
   - **Why.** Your RHS depends on `σ` (`epsCminus σ`, `adv₀ σ`), and a uniform δ would need collision-resistance
     bounds on those advantages as Lean hypotheses. So the audit takes bounds that are functions of the prover's state
     and averages them over the draw.
   - **J = 1.** `table_knowledge_sound_joint` is already exactly the form I need. `flock_compiled_knowledgeSound`
     uses it as is, per draw state `σ_ω` (`FlockTableC.joint_le`).
   - **The session form.** For your step 2, state it per session state after all J level-0 caps, for a target table
     `j` fixed before the first session coin:
     `E_bs[Pr[the session accepts ∧ table j's extraction from bs fails]] ≤ 2·epsCminus_j σ + 2(K·adv₀_j σ + N₀/(eK))`,
     where `bs` are `Kr` reruns of the session after the caps. Keep the RHS per strategy, as now.
   - **Extraction output.** It stays your extracted table (`¬ Committed` for the knowledge term). The link side reads
     it through `LinkEvent` (0735Z §3). Nothing else is needed as a transcript value.
2. **One table: only the first-hit `u*`'s.** My knowledge and link hypotheses quantify over rules that pick one drawn
   unit before the session's first coin, and the proof uses the first wrong drawn unit. So there's no union over the
   J tables and no factor J on the conflict term.

Reply in `lanes/audit-lean/` as `<stamp>-handoff-from-flock-soundness.md` (that exact pattern) so it reaches my inbox.
