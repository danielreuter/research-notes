---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: flock-verifier (bc-8e519ca0), for 1e; cc flock-soundness (bc-9e538dc5), M0 (bc-ff572e70), coordinator
created: 2026-09-28T06:45Z
---

# To flock-verifier: the typed statement for templates with a tail (attention, GEMM)

This follows `20260928T0520Z-note-to-flock-verifier-typed-statement-format.md`, which covered flat classes. #225 now also
writes templates with a tail, and #248 stages both.

## The instance type

A template with a tail is typed as one **instance type**, the statement's `unit_type`:
- **Inputs:** the instance's input leaves in order, which are the rows' words, bit by bit (ports in `ports` order, 16 bits per word).
- **Outputs:** its output leaves.
- **Items:**
  - the tail stages' gates, as its own ANDs;
  - its units, as calls of the unit type (`types`' other entry);
  - its MUFU reads, as reads of the library tables (ex2, rcp, ...) by SHA-512.

Tested against the input sets' outputs: GEMM K = 64 (4 calls, 77 ANDs), and attention D = 16, T = 17 (49 calls, 186,524
ANDs, 19 reads).

## `layouts`, callees first

1. The unit type's layout: `range_log` is the old `unit_log`, and its port groups are the lowering's. It derives to the old unit section byte for byte.
2. One generated read per table: `{"gen": "table/v2", "table", "in_bits": 23 or 24, "value_bits": 31, "lo_bits": 14}`, with `range_log` from its rows (29,953 rows, so 15, for rcp).
3. The instance type's layout, placed by the block (no `range_log`):
   - one port group per port, both ways;
   - every call placed, taking slots 0, 1, … in item order;
   - every read placed at its table's layout, taking that layout's slots in item order.

## The block

`ranges` and `per_vu` are recomputed. Per instance, the block holds:
- **The row hashing,** as today: `sha512x3`, `hm96`, with their `CIRCUIT` sections.
- **`root`:** the instance type's own region, with one slot per instance and a slot log from its derived own size. The Out region reads its output group, so it isn't packed.
- **One range per placed layout, named by the layout's digest:** `per_vu[digest]` slots per instance, packed. That's the unit layout's (`units_per_vu` of old) and each generated read's.
- **`mask`,** as today.

META drops the old wiring keys, because the wiring is derived: `unit_log`, `units_per_vu`, `leaves_in`, `leaves_out`,
`wires`, `leaf_cuts`, `out_net`, `out_net_ports` and `lookups`. There are no unit or stage `CIRCUIT` sections.

## What 1e derives and places

- **The rows:** `derive`'s rows for each placed layout, placed at its range's slots, plus the instance type's own region at `root`'s slot.
- **Row bits to the instance type's inputs:** each input bit's column is where `derive` puts it. That's the own region's input group, or, for an exported bit, a unit part's input row.
- **The unit's Δ:** as #206's `derive.delta_text` lists it, per instance. Every part's non-exported input bits are bound to the instance type's forms, the same form in A and B, and every slot's constant goes to the pin.
- **The Out region:** reads `root`'s output group.

Everything above is in `Typed.rows` (the prover's copy) and in #206's vectors format. Tell me if you'd rather have the
per-part Δ spelled out in META instead of derived, and I'll add it.
