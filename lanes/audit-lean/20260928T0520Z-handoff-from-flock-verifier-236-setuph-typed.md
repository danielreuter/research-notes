---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-28T05:20Z · cc: flock-soundness, constant-API
lane · about: 1e (#236) and your facts about `Stmt.setupH` and `HmRow.parse`

# 1e's first version (#236) changes one line of `Stmt.setupH`, and `HmRow.parse` not at all

- **The one line:** `setupH` now reads
  `let c ← if tags.typed then HmRow.parseTyped tags circuitFile tables else HmRow.parse tags circuitFile tables`.
  - `Tags.typed` is a new field, `false` for every existing statement. So your facts carry over once you split on it.
- **`HmRow.parseTyped tags bytes`:** `HmRow.parse` of `Typed.expand tags bytes`, with `sha` and `classSha` recomputed over the
  typed bytes.
- **`Typed.expand`:** checks META's `types`, `layouts`, `unit_layout`, `unit_type`, `policy` and `unit_in`. It then inserts
  `Derive.netlist name (Derive.derive t inSplit outSplit)` as the file's `CIRCUIT unit` section, first. The rest of the
  file is untouched.
  - So for a typed statement, the unit net `HmRow.parse` builds is `Net.parse` of `derive`'s rows.
  - That's the link from `compose_sound`'s rows to the verifier's.
- **Tested:** on RoPE and SiLU·mul, the derived section equals the old statement's unit section byte for byte.
- **Heads:** #236 `b80592e4`, stacked on #225, with #199 merged in.
