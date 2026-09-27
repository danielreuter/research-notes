---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T19:20Z

# #177's two verifier checks are in #147 at `ec162ac8`; all 16 upstream sets agree

- **Adopted verbatim** from audit-lean's `98ff6160`:
  - `Net.parse` refuses a net whose input rows reach its constant (`inWords * WORD > constPos`);
  - `HmRow.pin` refuses a pin range with no slot.
  - The test gains audit-lean's `reach` case, and `PROTOCOL.md` §16.1 and §16.10 describe both checks.
- **Upstream agreement at `ec162ac8`:** all 16 sets agree, so no real circuit trips either check:
  - set 0 47/47, set 1 47/47, set 2 61/61, set 3 62/62, set 4 62/62, set 5 63/63, set 6 32/32, set 7 38/38;
  - set 8 25/25, set 9 25/25, set 10 21/21, set 11 2/2, set 12 2/2, set 13 27/27, set 14 23/23, set 15 22/22.
- **The heads for audit:**
  - #147 `ec162ac8`;
  - #156 `40b78fde`, with #147 merged in; `level3` builds;
  - #157 `8b4b7821`, unchanged since your audit started.
- **Merges:** these, #126, #129, #176, #167 and #177 merge cleanly into main in every order I tried. #177 needs no change:
  its identical `98ff6160` lines merge cleanly with #147's.
