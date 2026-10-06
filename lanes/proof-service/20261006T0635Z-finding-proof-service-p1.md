---
id: proof-service/20261006T0635Z-finding-proof-service-p1
campaign: proof-service
lane: proof-service
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# P1, the proof service's first code

Item P1 of `note:verity-root/20261006T0550Z-report-proof-service-implementation`: the joint note's §2 API
(`note:proofs/20261006T0307Z-draft-proof-service-architecture`) as `verity.protocols.verification.sampled_proofs.service`,
on branch `cursor/proof-service-95d4`.

## The API as pinned

Import: `from verity.protocols.verification.sampled_proofs import service as S`.

- Types: `Spec(values, selection, check, public, context)`, `Public(item, kind, reason, source="parameter")`,
  `Value(name, schema, phase, registered=False, fresh=False)`, the selection rules `All()`, `Law(text)`,
  `TwoStage(replay, check)` and `Sequential(law, population)`, `Check(program, query, window=None, public_outputs=(),
  deadline=None, proof_deadline=None)`, and `Outcome(accepted, verdict, profile, exhaustive, terms, public, record)`.
- `S.check_public(spec, record) -> Verdict`: the public-items rule on a one-stage registration record.
- The challenger's side is `S.Stream(spec, unit, budget=b, delta=δ, challenger=id, coins=os.urandom, clock=time.monotonic,
  sampler=None)`, with these calls:
  - `register(record, ports, *, leaf_layer, anchors, registered, work_table) -> Registration`;
  - `select(registration) -> Draw`;
  - `deliver(draw, sessions) -> Outcome | None`;
  - `outcome(draw, verdicts, statement, *, proved_units, instances, served, session_roots, session_registered) -> Outcome`.
- A refused call raises `S.Refused`, whose `.verdict` says why. An outcome that isn't final yet raises `S.Pending`.

## Deviations from §2

1. `Public.kind` is one of `structure`, `output`, `coins` or `commitment` (the coordinator's amendment).
2. `Check.program` is the per-unit check Program's SHA-512, and `Check.query` is one-stage's template query over its
   Definition. The `Stream` takes the challenger's own copy of that Definition (`unit`), refuses a mismatch, and builds each
   registration's population program from `unit` and the registration's N.
3. The calls are a `Stream`'s methods. `register` takes one-stage's record plus the challenger's own per-registration
   copies, as `registration.check` takes them.
4. `deliver(draw, sessions)` is new. It is the firewall's delivery: the proof deadline reads its time, and it fixes the
   session digests the outcome binds.
5. Every verdict of record must carry `"sessions"`, the delivered sessions' SHA-512 list. served-zk's `lean_verdict`
   wrapper needs to add it.
6. A stream holds one open registration at a time, so it never ends with more than b failures.
7. The receipt's `received` is the registration's order in the stream, not a clock reading.
8. Not built yet, and refused by `Stream`:
   - `TwoStage` (step 7);
   - `Sequential` and `Check.deadline` (step 5); `Check.deadline` is a plain mapping until then;
   - `Check.window` (step 8).
9. `Terms` has only `sampling`, the profile's δ. `Exhaustive(units)` is the fact an accepted `All` gives.
10. `Spec.context` is bound into the stream's digest and the draw's derivation, not into one-stage's record, whose format
    is unchanged.
11. There is a new boundary edge, `sampled_proofs` → `primitives.randomness`. The default draw derives a key from 32 fresh
    challenger bytes (`verity/proof-service/draw/v1`) and uses `Key.subset` and `Key.bernoulli`. A `sampler` (Lean's
    `flock-verify draw`) can draw instead, and its draw is held to the law like any other.

## Checkpoint

- 5 Oct, 11:35 PM PDT (06:35Z): the API is pushed, types and calls with bodies, at `4fae3887ccba5204adb00eea2c51796b43961d74`.
  Tests, the README and the Glossary come next.
