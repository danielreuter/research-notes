---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: draft · created: 2026-09-27T00:30Z · status: estimate sent to root; no pods until approved

# Plan: the `max_scaled` tap (follow-up for vllm-rf-normtap)

**The value.** Every attention block computes `max_scaled = F32MulFtz(m_use, scale_log2)`, and each of the block's exp2
units reads it: `p[c] = MufuEx2Ftz(F32FmaSubFtz(s[c], scale_log2, max_scaled))`, in `AttnBlock_v3` (FA2), `AttnBlock_v2`
(FA3) and `AttnBlockSoftcap_v1`. The no-recompute cut therefore commits it once per (head, key block, query row) whenever
the block has more than one visible key, and that includes the first block.

The stream doesn't carry it: ROW word 2 is the kernel's visit index (`vt_step`). Once #95's guarded max takes word 3, it
is attention's only uncommitted boundary value (normtap, 23:29Z).

## Design: a seventh stream class, `MS`, appended after FIN, under the same opt-in flag

- **Why not a wider ROW entry.** `StreamLayout` places S, P, RP, ROW, O and FIN in that order, and ROW has 8 words per
  (slab, row, block) (`hidden_stream.py` `offsets`, `word_index`, `unrank`). A ninth ROW word changes ROW's stride and
  shifts O and FIN, and it touches every reader of those offsets: thread-leaf mode, `unrank`, the replay regenerator and
  the IR twin.
- **The new class instead:**
  - `MS`, one f32 word per (slab, row, block), at `off_ms = off_fin + HB*M*4`;
  - a new source bit, `SRC_BITS["MS"] = 64`;
  - allocated and written only when the flag is on (the same `CommitConfig` flag as #95's guarded max).
- **With the flag off:** `CLASSES` and the source mask are as today, the total is unchanged, and the layout digest and
  every stream byte are identical. When the flag is off, `MS` contributes nothing to `offsets` or `total_words`.
- **Kernels:** in `rowstat` (`verity_tap.h` for FA2, softcap instantiation included, and `verity_tap_fa3.h` for FA3), one
  guarded store of the `max_scaled` value the kernel computed, the same register the exp2 FMA consumes, so it isn't
  recomputed. The first block is included, and single-visible-key blocks are stored too (the verifier ignores them). This
  is the same pattern as the guarded-max store.
- **IR, query and verify:**
  - `word_index("MS", slab, row, block=...)`;
  - `derived_rows.attn_block` maps the cut's `F32MulFtz_v1` class to `MS`;
  - `committed_today` / `_STREAM["F32MulFtz_v1"]`: "ROW step" becomes the MS plane under the flag, and not committed
    without it;
  - manifest verify reads `MS` when the flag is set.

## Acceptance (the same bar as the guarded max)

1. **Default byte-identical:** with the flag off, #101's stream, roots and manifest are unchanged (`368283ad…`), and the
   layout digest is unchanged.
2. **Kernel exactness:** every `MS` word equals the IR's `F32MulFtz` gate, on FA2 (L40S, softcap included) and FA3
   (H100); the outputs equal the untapped build's; no word is left unwritten (two fills).
3. **#101 with the flag on:** strict `--word-check` passes, and 242,688 committed `max_scaled` words equal the checker's
   count.
4. **Partition checker:** 0 recomputed gates.
5. **Gate (b)** in a git clone, head and base on the same pod.

## The corrected tap list (from #92's program graphs, `art:f0c33059…`, the `F32MulFtz_v1` "ROW step" entries)

These words move from "Committed today (FA stream)" to "New taps". Bytes are per token of the row, as in
`docs/fine-query-plan.md`.

| Row | `max_scaled` (FA2/FA3 kernel) | New taps, B/token | Committed today (FA stream), B/token |
| ---: | ---: | ---: | ---: |
| 4 | 3,272 B (4.63 M words) | **5,718** (was 2,446) | 873,421 (was 876,693) |
| 11 | 37,864 B (43.61 M words) | **73,828** (was 35,964) | 11,870,177 (was 11,908,041) |
| 23 | 5,529 B (24.32 M words) | **9,162** (was 3,633) | 1,433,075 (was 1,438,604) |
| 39 | 49,025 B (56.46 M words) | **96,955** (was 47,930) | 7,838,166 (was 7,887,191) |
| 57 | 5,122 B (5.31 M words, softcap) | **9,426** (was 4,304) | 764,044 (was 769,166) |
| 60 | 27,534 B (25.87 M words) | **51,302** (was 23,768) | 4,137,491 (was 4,165,025) |
| 67 | 5,455 B (13.55 M words) | **18,484** (was 13,029) | 802,113 (was 807,568) |
| 68 | 5,387 B (13.58 M words) | **18,348** (was 12,961) | 791,203 (was 796,590) |
| 70 | 3,330 B (3.48 M words) | **14,740** (was 11,410) | 499,127 (was 502,457) |
| 73 | 15,585 B (14.41 M words, FA3) | **32,657** (was 17,072) | 4,270,441 (was 4,286,026) |
| 74 | 15,958 B (16.10 M words, FA3) | **33,400** (was 17,442) | 4,378,809 (was 4,394,767) |
| 75 | 28,886 B (8.38 M words) | **109,863** (was 80,977) | 4,440,693 (was 4,469,579) |
| 101 | 3,382 B (0.24 M words) | **4,870** (was 1,488) | 742,019 (was 745,401) |

The total is 230.0 M words over the 13 rows. On every row it is slightly more than the guarded max, because it includes
the first block. It roughly doubles the attention part of the new-tap bytes, and it is under 1% of the FA stream the rows
already commit.

## Spend estimate (new pods; nothing starts before root approves)

| Step | Pod | Hours | Cost |
| --- | --- | ---: | ---: |
| FA2 build with MS, kernel exactness (softcap included), #101 flag off and on | L40S, about $1.09/h | about 3 | about $3.3 |
| FA3 build with MS, kernel exactness | H100, about $3.49/h | about 1.25 | about $4.4 |
| Gate (b), head and base on the same pod | CPU 16 vCPU, about $1.04/h, or the L40S | about 0.6 | about $0.6 |
| **Expected / cap** | | | **about $8 / $10** |

- **Against the day cap:**
  - Spend at 00:15Z: $728.08.
  - The running tap plan's worst case is $721.91 + $23 in caps, plus my #92 gate pod (about $0.6), so about $745.5.
  - The `max_scaled` cap on top of that is $10, giving about $755.5, under the $760 stop.
  - Expected: about $750.
- **Deadline:** the work runs past 02:30Z, so it needs one ≤4 h guard step while the pods run.
- **Code:** the kernel, layout and IR changes are on CPU, and the pods run only after they build locally.
