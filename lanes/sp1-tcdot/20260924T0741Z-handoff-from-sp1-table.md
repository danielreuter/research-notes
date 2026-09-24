---
lane: sp1-tcdot
kind: handoff
from: sp1-table
created: 2026-09-24T07:41Z
---

# lane/sp1-table @ 65aa6a12: kernel k4 behind `bare::check_one` (your fallback gets it for free), sp1-formats merged, optional indexed input layout

**What you call is unchanged.** `bare::check_one(format, vu_bytes, vu_words, y)`, `check_words`, `parse_header`,
`encode_header`, `encode_chunk`, `decide`, `statement_*`, `public_values` keep their signatures. The format dispatch is
now `bare::check_pair(format, x, w, xw, ww, y)` (x and W apart); `check_one` splits and calls it. `Header` gained two
fields, `version` and `rows`, which a field read does not notice.

**Faster software path.** `bare::check_vu` (bf16-ampere) is kernel k4: 156.4M cycles for the 4096 VUs, from 218.1M
(gas 181.1M, from 236.8M). A VU your routing hint sends wholly to software runs it through `check_one`.

**sp1-formats merged.** Their four format arms (`2581406f`) are in (`d4c4a881`); the format modules are gated under
`relation-bare` / test, so the sound guest's ELF is unchanged.

**Indexed layout (optional; input version 3).** A header with version 3 carries the number of distinct rows where
`vus_per_read` was, followed by a u64 per VU (`x_row | W_row << 32`) and one table of distinct rows. Stock A100 BF16
B=4096: t.total 24.10 s -> 22.27 s (25 shards, from 28). Your guest's v2 loop rejects a v3 header (its
`vus_per_read` is 0), so nothing breaks. Using it would need a v3 branch in your guest and your block layout for
chip-routed VUs.

**Registered stock numbers to compare against.** k4 `art:c7ca70a0` (24.10 s) and k4 + indexed `art:1d6aa0c3`
(22.27 s), both B=4096 x 3 reps on the A100.
