---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Request from the docs site: words per read on the Program graph's edges

**To:** coordinator, for vllm-vu-export. **From:** the docs-site worker. **Written:** Sat Sep 26, 9:50 AM PT. Daniel approved asking.

## Why

The Program visualizer now has a Widths toggle that labels each edge with the size of the value it carries. Inside a Definition body the sizes are exact, because they come from the codec refs.

Between Calls, `program.json`'s `edges` give only `reads`, the count of (consumer Call, producer Call, port) triples, with no width. The site currently labels an edge with the producer Call's whole return. That overstates it wherever the reader takes only part:
- a fused norm returns its normed row and its residual (8 KB), but each reader takes one of the two (4 KB);
- `qkv_proj` returns 6 KB, but RoPE q, RoPE k and attention's v each read a slice.

## What would fix it

For each group edge in `program.json`, add the words (and word width) the consumer reads from the producer:
- per read, or summed across the edge's reads so the site can divide;
- the consumer port it lands on, if that's cheap, so the site can name ports by the Definition's parameter names rather than by annotation.

The site would then label an edge with bits per Call (words per read × reads per Call), and could show the KV-cache reads as the wide edges they are.
