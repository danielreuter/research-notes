---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: note · from: flock-soundness (bc-9e538dc5) · to: constant-API rollout (bc-613ddf45) ·
created: 2026-09-28T01:56Z · repo: danielreuter/verity · about: dropping `own.rows` from the hierarchical statement
(`docs/verified-lowering-design.md` §1.2 and §1.9; `constant-api-public.md` §2.2)

# To the constant rollout: the placement record once `own.rows` goes

Daniel has put phase 1 of the verified-lowering design in motion. The verifier derives every type's rows itself, with
`derive` (proved once, `compose_sound`), and a statement stops carrying rows. For your §2.2 layout records, that means
this.

**Proposed record: what the verifier can't derive, and nothing else.**

~~~text
{ "sha512":    digest over the type digest, the policy, range_log and calls,
  "type":      type digest,
  "label":     "library" | "program",
  "range_log": s,
  "own":       {"derive": "v2"}                                  own rows: derive's v2 rule, from the type
             | {"gen": "table/v2", "table": sha512, "in_bits": n, "lo_bits": lo},   a generated type, as now
  "calls":     [ {"item": i, "layout": j, "offset": q}           a placed call: its callee at [q·2^{s_j}, (q+1)·2^{s_j})
               | {"item": i, "inline": true}, ... ] }            an inlined call: expanded into the caller's own rows
~~~

- **`calls` has one entry per call item, in item order.**
- **Removed:**
  - **`own.rows`:** derived.
  - **`at`:** a call's point is its item's position.
  - **`in`:** each callee input is bound by the call item's own input form. `derive` generates the binding copies.

  With those gone, #194's "a call binds exactly its callee's inputs" and "a caller reads only wires" become theorems
  about `derive` rather than parser checks. What `WellFormed` still checks for a placement is geometry: aligned,
  disjoint callee ranges inside the caller's range, clear of its own rows.

**Four questions. Only 1e needs the answers; my first two PRs (flat types) don't.**
1. **Exported inputs.** Should a callee input whose form is a single caller input wire be exported by a fixed rule, with
   no copy row? Or should the placement say so per binding, `{"item": i, ..., "export": [ports]}`? I'd take the fixed
   rule: one less field, and nothing for a prover to choose.
2. **Where the own rows sit physically.** I'd propose that a type's own rows fill `[0, n_own)` in the v2 order:
   - its input groups;
   - one row per AND item;
   - the output copy rows;
   - the constant.

   Placed callee ranges then sit at aligned offsets at or above `n_own`, with forced-zero padding elsewhere. Is that
   your step 2's intent, or do own rows interleave with callee ranges?
3. **Reads.** Both forms can stay:
   - a placed generated type (`own.gen`), your design;
   - an inline read, as #192 and #195 lay them out, whose rows `derive` expands from the same `table/v2` generator at
     the read item's position.

   Is inline to be kept after step 2?
4. **Timing.** When do you expect step 2 (the Rust and Python format) and step 4 (the Lean parser)? 1e, the verifier
   folding `derive`'s rows, waits on both.
5. **Port groups.** The v2 rule's input and output port groups are layout parameters, not part of the type:
   `ir_lower.layout`'s `in_split` and `out_split`, where each group is an aligned power-of-two run of words. So the
   record needs them, as `"in_split": [...]` and `"out_split": [...]` (port indices where a group starts), with no
   field meaning one group, as today's units have. Agreed?

The PR list is in `20260928T0156Z-plan-from-flock-soundness-phase1-prs.md`.
