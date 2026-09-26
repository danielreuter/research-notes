---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T18:20Z

# Restart: one queue, every GEMM cell re-run once, total and on separate machines

**Why:** Daniel's new standing rule (2026-09-26) is that circuits are total by default. They must match the hardware on
every bit pattern, NaN and infinity included. A finite-only circuit is allowed only as an explicit, named choice, and only
if total would cost more than 10×.
- The pure-block GEMM unit (`verity_flock/unit.py`, the 7,100-AND census unit) asserts finite operands.
- The total `tc_dot16` (8,623 ANDs, about 1.21× the work) already exists in `verity_flock/fp.py`; the IR lowering uses it.

**The queue (9 cells):**
- The five co-resident L40S cells: art:4e3f5048, aea553ae, 86780ca6, 4a319a65 and 89dab836.
- #101's two L40S GEMM cells: art:73a9e9f3 (K 2048) and #101's K 8192 cell.
- The two ChunkTail cells: #57 K 2304 and #39 K 8960. They build on PR #75, now on main.

**Steps:**
1. **Code first, no pods:** wire the total `tc_dot16` into the GemmCoordinate pure-block unit under a new statement name,
   with `domain="total"` in the fingerprint. Selftests and negatives must include NaN and infinity operands. Hand it to
   red-team-flock for a short review before any cell runs.
2. **Placement:** plan through `bench.cell` (PR #74's machine-identity check). Only a prover and verifier on separate
   machines, reached over a routed path, count.
3. **One-hour placement limit:** if no same-datacenter L40S pair with a separate verifier turns up within about an hour
   of starting the search, stop and write me the options rather than polling all day:
   - a cross-datacenter verifier, with the measured RTT recorded in the interaction record (red-team-flock's ruling allows
     it);
   - or another route, such as another GPU model.
4. **After each cell registers:** label the old cell `superseded_by` the new one. Handoffs go to verify-flock-pure and
   red-team-flock as before. Register each cell once, with `--lane`.

**Spend:** a $25 cap for the whole queue. My estimate is about $10–15: 9 cells at about 1.2× the old work on L40S pairs,
plus build and setup. Terminate pods between batches.

**GitHub token:** push via bundles if it has still expired. Leave the bundle in `research-notes/bundles/` and tell me, and
I'll push it.
