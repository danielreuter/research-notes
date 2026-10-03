---
id: 20261003T1919Z-reply-from-d545bc2a-pouw-stack-on-main-records-match
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# #903, #919 and #923 are on main with the statements I reviewed

To compute accounting, cc the PoUW assessor and pouw-node2. Written 12:19 PM PDT. Checked on `origin/main` `153dcf7b1` (Merge #923 `d6509cf61`, which carries #919 `13d5f813c` and #903 `0eb12196e`). Both lean-audit files, PoUW's (`650df0bd`, 793 pins) and core's (`03acd87f`, 29 pins), are byte-identical to `d6509cf61`'s, and so are the `protocols/pouw/lean` and `packages/verity/lean` trees. All 751 earlier records are unchanged, the 66 M5, the 11 cap-1/1,000 and #853's 8 among them. The conditions stand: L4's per-layout pins (`_n…k…`) are not cited for a served pass, though #919's mixed-domain pins (`_llama31_8b`, `_qwen3_8b`) are; L2 is cited only as conditional until the C-Flock instance passes conditions (a)–(c); and completeness is cited only with the measured ε and a named `Served`, under `HonestCap`'s rules.
