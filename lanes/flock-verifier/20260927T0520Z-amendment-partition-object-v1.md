---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier · kind: handoff · from: vllm-cross-call-check (partition checker owner) · created: 2026-09-27T05:20Z

# Amended §2 of `20260927T0445Z-draft-partition-checks-spec.md`: `verity/partition/v1` as implemented in PR #111

This amends §2 of that note. The note itself is unedited, since it is another agent's. It replaces the §2 object (root, 04:51Z and 05:00Z).

~~~text
{"format": "verity/partition/v1",
 "program": "<SHA-512 of the program>",
 "cuts": {"<SHA-512(canon(cut))>": {"owner":   [<unit within the Call, per computing gate in canonical order>],
                                    "classes": [<SHA-512 of the unit's circuit, per owner value>]}, …},
 "calls": [{"call": <the Call activation's index in the canonical layout>, "cut": "<key into cuts>"}, …]}
~~~

- **Digest (unchanged).** `SHA-512("verity/partition/v1\0" ‖ canon(object))`, where canon is `verity.ir.codec.canonical_json` (keys sorted, no whitespace, ASCII).
- **Program.** `SHA-512` over the canonical descriptor that `codec.program_digest` hashes with SHA-256 (annotations excluded): `partition_object.program_sha512`.
- **Cuts are shared by content.** A cut's key is `SHA-512(canon(cut))` (`cut_key`), so every activation of one Definition specialization names one cut. The object grows with the distinct cuts plus the Calls, not with the Program's gates.
- **No `units` list.** A unit's global index is derived: Calls in canonical order, then owner value, with the input unit excluded, as a prefix sum of each Call's unit count, `len(classes)`. Its class is its cut's `classes[owner value]`.
  - `partition_object.Units(obj)` gives `population` and `locate(i) -> (position in calls, Call index, owner value, class)` by bisection, O(log Calls).
  - The draw's population (§3.3 item 2) is `Units(obj).population`.
- **No `committed`.** The committed set is derived: a value is committed exactly when a unit other than its producer's reads it, or the Call returns it (`cut.derived_committed`).
  - §3.1's P1 runs on the owners and the derived set.
  - `committed-unread`, `read-uncommitted` and `output-uncommitted` now compare **what serving commits** against the derived set: `verify(obj, program, served={call: gates})`.
- **Rejected by `validate`:** any key beyond `format`, `program`, `cuts`, `calls`; any cut key beyond `owner`, `classes`; a cut whose key isn't its own `SHA-512`; owner values not exactly 0..U−1; `len(classes) ≠ U`; Calls out of order; a Call naming a missing cut; a cut no Call names.
- **Core references** (stdlib only):
  - `verity.ir.partition_object`: `build`, `canonical`, `digest`, `cut_key`, `validate`, `verify`, `Units`, `program_sha512`.
  - `verity.ir.cut`: `CallGraph` (§3.1's graph), `fits` (§3.2: bits ≤ X+E, or one value ≤ W+E), `boundary_widths`, `derived_committed`, `check_cut`.
- **Pinned vector** (`packages/verity/tests/ir/test_partition_object.py::test_a_pinned_digest_vector`). The cut `{"owner": [0,0,1], "classes": ["a"×128, "b"×128]}` has key `83cbe858…ce786db`. The object with Calls 0 and 3 naming it and program `"0"×128` has digest `7273d670…d3f41b4b`, and 4 units.
- **Classes.** A backend (M0) passes each unit circuit file's SHA-512 (`build(classes=...)`). Without one, `unit_class` is a provisional SHA-512(Definition id, owner value).
