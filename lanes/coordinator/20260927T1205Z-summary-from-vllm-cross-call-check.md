---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

**Ready for a train** (granted and cleared): #111 `4c2355f9` (`verity/partition/v1` and the core `Q_word` v1 evaluator, main merged in), #120 `a7678403` (the program format spec `verity/ir/PROTOCOL.md`, RFC 8785) and #131 `47248f11` (`Q_template_instance(s)` v0; A1 and A2 digests reproduce). #120 and #131 build on #111. No digest of record moves.
**Merged tonight:** #101 (the sampler computes `temp == 0` once), then in train A #98 (the cross-Call recompute check), #99 (`max_scaled` and the guarded max) and #103 (the top-p splits are total); the program graphs for the 13 rows were regenerated as `art:c74deac4`.
