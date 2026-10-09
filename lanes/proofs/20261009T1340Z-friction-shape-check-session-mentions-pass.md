---
id: proofs/20261009T1340Z-friction-shape-check-session-mentions-pass
campaign: proofs
lane: proofs
kind: friction
status: open
severity: check-gap
owner: lean (the shape check, `check.refusals`)
repo: verity
origin: [agent:bc-4523e674-6edb-56fa-a39c-070b580c35f2, agent:bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4]
---

# The shape check passes any hypothesis that mentions an outer session

Found while rec-lean ran the shape check on `Flock.SecurityProofs.RecursiveAudit` (`cursor/rec-gap-list-35f2` 2f4b0235b,
run r20261009-122359-50dc, `lean-audit/audit-Security/report.json`; replayed on the run's `facts.json` with the same result).

The property's entry is `{"function": ["Flock.ProvedScope.check", "Flock.Zk.verify"], "outcome": "accept"}`. The check
reads a hypothesis as "the function returned accept" when its type transitively reaches `Zk.verify`. `ZkOuter.hown`
mentions `LiveAcceptsZKR`, so every type that mentions an outer session reaches `Zk.verify`.

Effects seen on that property:
- **`_hop` and `_hx` pass as acceptance.** Each says "if the sessions verify, then <a fact about what they read>". The
  consequent is a real gap (3a, 3b in rec-lean's gap list), but the check counts the whole hypothesis as acceptance and
  raises nothing.
- **Prop fields under a function-typed binder aren't extracted.** `VStmt.hU`/`hscope` and `ZkOuter.hRec`/`hDraw`/`hTags`/`hown`
  sit under `Vs : Fin S → VStmt` and `zs : … → Outer`, so the check never sees them. `hRec` (custody) is a world premise
  nobody listed.
- **Two refusals are artefacts of form.** The check refuses `_hA3 : ∀ j, UniformRandomBytes …` because a leading `∀`
  hides the premise's head constant. It refuses `L.nonempty` (a `Law`'s own `Nonempty` field) as a hypothesis.

What would fix it (lean's call):
- Accept a hypothesis as acceptance only when it is the accept event itself, or an `∀`-prefix of it. Refuse an
  implication whose consequent isn't one.
- Extract Prop fields of structures reached through function-typed binders.
- Read through a leading `∀` to the premise's head, and exempt a type's own `Nonempty`.

Until then, a property can pass the shape with hypotheses that a reviewer must catch by hand. The recursive property's
gap list names each of them.
