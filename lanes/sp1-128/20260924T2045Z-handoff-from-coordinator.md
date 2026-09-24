---
lane: sp1-128
kind: handoff
from: coordinator
created: 2026-09-24T20:45Z
---

# Re 2040Z: option 2 (A100 BF16 only, honest D2 row, <= $5); option 3 goes to Daniel; stop the other four rows

Good finding, and the right call not to register a run under target + log2(shards) accounting.

- Do option 2: one source-built 6.6.0 GPU server + a host with `sp1-primitives` patched to the same constant, A100 BF16 only,
  labelled "SP1, FRI query count raised to a 134-bit target (otherwise unmodified)". The envelope holds `security.target` -134
  (the design constant), achieved = the additive per-shard sum + log2(shards) (about -95.5), and every per-term figure in
  `security.parameters`. Table 2 must exclude it on achieved: check the render says so. Cap $5. Hand the registered result to
  me for non-producer verification as the launch message says.
- Do not start the H100 / 4090 / 5090 rows: the same field-bound terms apply there.
- Write the finding into `kb/sp1-prover.md` (soundcalc table, reproduce line, "cannot reach 2^-128 without protocol changes:
  grinding in every commit round, zerocheck and jagged reduction, or a larger extension field") and make D1's SP1 rows say so.
  If D1 needs a drilldown.py change to state it, make it on your branch (drilldown.py is not frozen; tables.py is).
- The ~1-bit optimism in the existing SP1 records (per-shard -100 recorded vs -99.0 additive): do not rewrite existing
  records. Put the corrected accounting in the kb doc and in your new envelope; I have it on the backlog for the emitters.
- Option 3 (an SP1 variant with added grinding / a larger field) is a protocol change: I am asking Daniel. Not in this lane.
- After option 2 lands: FINAL. Pods terminated.
