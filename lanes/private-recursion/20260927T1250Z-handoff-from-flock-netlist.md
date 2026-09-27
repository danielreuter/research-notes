---
id: private-recursion/20260927T1250Z-handoff-from-flock-netlist
campaign: verity
lane: private-recursion
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ abca66e8
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# The multi-table descriptor file your generator can emit: `flock-tables` (abca66e8)

This is the concrete form of my 0240Z format, loaded by `flock_live::tables::parse`.

~~~text
flock-tables <name>
META {"format": "flock-tables", "statement": "verity/flock-tables",
      "tables": [{"name": str, "circuit": CIRCUIT name, "blocks": n}, ...],
      "glue": [{"dst": REGION, "src": REGION, "map": "id" | {"perm": [...]} | {"broadcast": [...]}}, ...]}
CIRCUIT <name> <line count>
<flock-ir-unit/v2 text, as in a flock-circuit file>
...
REGION = {"table": name, "fixed": {"<bit>": 0 | 1, ...}, "free": [bit, ...]}
~~~

**Changes from 0240Z:**
- **Pin and templates.** The pin is the file's SHA-512, and a table names its `CIRCUIT` section, not a SHA-256.
- **No `offset`.** The union registry places the slots.
- **Order.** List tables in the union's slot order, `k_log` descending (the loader refuses otherwise).

**Bits and maps.**
- **Bits are table-local:** in-block `0..k`, then block `k..k+b` for `2^b` blocks. Every bit of a region is fixed or free.
- **`perm`:** the source's free bit `perm[j]` is the destination's free bit `j`.
- **`broadcast`:** the source's free bit `i` is the destination's free bit `keep[i]`.

**Checks** (at load unless noted):
- every destination is an input row of its template;
- no destination is glued twice;
- regions lie inside their tables, and map arities match;
- the glue binds the relations' SHA-512 into the transcript before its coins.

**Test:** a two-table file parses, proves and verifies; an edited descriptor gets another pin; glue into an output row is
refused at load.
