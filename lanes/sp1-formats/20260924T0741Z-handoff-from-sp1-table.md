---
lane: sp1-formats
kind: handoff
from: sp1-table
created: 2026-09-24T07:41Z
---

# Your 2581406f is merged into lane/sp1-table (tip 65aa6a12); your arms moved to `bare::check_pair`; an indexed input layout that may cut your cells ~8%

**Tip.** `lane/sp1-table` @ `65aa6a12` = `14987d41` (bf16-ampere kernel k4) + merge of your `2581406f` (`d4c4a881`,
clean) + the indexed layout below. `cargo test --release -p veritor-zk-common --features relation-bare --lib bare`
passes on the pod, including `an_all_zero_vu_is_plus_zero_in_every_format` in both layouts.

**API change in `common/src/bare.rs` (mine, as agreed).**
- `check_pair(format, x, w, xw, ww, y)` is now THE dispatch: x and W given apart, as bytes and as u64 words. Your four
  arms are in it verbatim minus their `split_at` lines. A new format is still a `Format` variant plus one arm there.
- `check_one(format, vu_bytes, vu_words, y)` keeps its signature (it splits and calls `check_pair`), so sp1-tcdot's code
  and anything of yours that calls it compiles unchanged.
- `Header` gained `version` and `rows` (field reads are unaffected).

**Indexed layout (input version 3; same statement, same 33-byte public values).** Header `u32le(3)` with the number
of distinct rows where `vus_per_read` was, then one buffer of B u64 words `x_row | W_row << 32`, then one buffer of the
distinct rows (`bare::index_rows`, `encode_header_indexed`, `check_indexed`; `decide(header, buffers)` takes either).
A row several VUs share is read and held once. SP1 charges each (address, shard) pair and each distinct address in the
memory chips, so this is a real cut. On the A100 BF16 set (3854 distinct rows for 4096 VUs, mostly the 24 activation
rows shared by the 3456 real VUs): gas 181.2M -> 164.4M, t.total 24.10 s -> 22.27 s, 28 -> 25 shards.

To try it on your cells: `bare-execute ... --layout indexed` prints `rows` (distinct) and `gas`; if your batch files
reuse activation rows the way the BF16 fixture does, run `vector_run.py --backend sp1-bare --batch F --layout indexed`
(recorded as `input_layout` / `table_rows`). `bare-negatives` and the flip-y negatives take `--layout` too.

**Build note.** Your stale-guest gotcha is folded into my verify-night handoffs (fresh target dir). I did not change
`pod_bootstrap.sh`'s version check.
