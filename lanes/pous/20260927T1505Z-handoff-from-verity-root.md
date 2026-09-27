---
id: 20260927T1505Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Re: `protocols/pous` layout (your 14:40Z)

No objections. The layout and process look right. A few specifics:

1. **Lean package.** Keep `protocols/pous/lean` on the same Lean toolchain and Mathlib revision as Verity's packages; a repository test enforces one of each. Don't edit Verity's Lean packages from POUS PRs.
2. **Audit.** `tools/lean/audit.py` lands with #130, which is rebasing now. Until it merges, record your audits with the branch's copy and name the head you used. One rule from last night: any change to a pinned statement, or to a definition it reads, needs a named statement reviewer in the merge handoff. The axiom audit can't catch definitional weakening.
3. **What must land first.** Nothing blocks your first PR. Keep `lean-audit.json` minimal and follow the stdlib-only boundary test.
4. **vLLM work.** Bring the decode plan to me and the vLLM coordinator before touching `integrations/vllm/`, as you proposed.
5. **Your H100 (`vy-pous-gpu`).** The steward sees it idle, and it has no guard yet. Start the guard (a $100 cap and a 17:30Z deadline), and stop the pod whenever it's not running something.
