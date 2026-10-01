---
id: 20261001T1200Z-handoff-from-proofs-flock-fp-packed-frame
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-flock-fp (bc-15199603-ae1e-5aa0-9da4-6be8dedb83e6)
---

# The packed frame on CPU: four FP4 or two E4M3 elements per u16 leaf; same ANDs, 2–4× fewer row blocks, n up to 4× at m = 35

to: proofs and red-team-proofs-554 (review after Q3c and the `Q_word` v2 PR). From proofs-flock-fp, on proofs' 2:50 AM PDT
work item 1. No GPU point was run; none is queued.

- **Branch and head:** `cursor/proofs-flock-fp-95d4` at `238988415` (on `b45e8b187`, `deca19e50`), pushed. `FLOCK_PACK_WORDS=1`
  (`70-class-sweep.sh`, `74-gemm-hill.sh`) packs every input word narrower than 16 bits into the current u16 leaf, low bits
  first, a word never across two leaves. The default layout is untouched: `FLOCK_PACK_WORDS` unset gives the old circuits and
  statements byte for byte (NVF4 K=2048's control `r20261001-112044-98fe` is red-team's `902fe8f5a2429661` /
  `5022d5110c0d7443`; NVF4 K=128 N=16 is `94eba2199b73925e`).
- **What changed in code:** `class_statement.py` only lays out the unit's input words and stages them (`_slots`, packed
  `class_lowering`/`pack`/`stage`; the unit is named `-packed`, its shim's form carries `/packed`, the record says
  `packed: true`, the stage cache keys it apart, a tile refuses it). The unit's gates are the default layout's; only its input
  wiring moves. Rust: `flock-circuit statement` prints the statement the verifier builds from its public file and its digest,
  nothing proved (`b45e8b187`; no prove, serve or verify path changes). `gemm_hill.py` flags any packed point
  `packed-statement-unreviewed`.
- **Checks:** circuit-check is green on the three word Definitions the packed units lower
  (`GemmCoordinate{Nvf4,Mxf4}_v1{K=128}`, `GemmCoordinateE4m3_v1{K=64}`: 0 failures, the one known warning each,
  `redundant-gates/boolean`, 2080 over the 3). `test_class_statement.py` passes (3 tests, 26 s): each packed row is the
  tensor's packed bytes (FP4 `bytes(a | b << 4 for a, b in zip(x[::2], x[1::2]))`, FP8 and scales `bytes(x)`, then zeros to
  the block), and the packed unit equals the IR evaluator on circuit-check's vectors for all three. On CPU at K=128 N=16, the
  packed statements prove and verify (LIVE `accepted`, NVF4 2.8 s, MXF4 20.5 s, E4M3 1.5 s) and the selftests pass in full
  (38, 41 and 41 cases).
- **Evidence:** `art:ca2cc01bd51a2ab9a525540c908e111d7720a60f688a078ace009b9307a0ffcd` (circuit-check catalog, K=128 stage
  records plain and packed, LIVE runs, selftests, pytest log). Stage-only runs on node 1 (`--stage-only`, `STATEMENT_DIGEST=1`,
  tree `proofs-flock-fp-pack` at `238988415`, m = 35), one at a time on a free provers slice: listed in the table.
- **Open:** no packed GPU point until the research owner's yes and this review; the K=16384 rows land after 12:55Z (one stage at
  a time, ending by 14:35Z). Prover time per packed statement is the first GPU question once allowed: FP4's statements carry
  2× (MXF4 K=8192: 4×) the instances for 2–4× fewer row blocks each.

## Per cell, at m = 35: default → packed

The unit's ANDs are the same in both layouts at every cell. Unit rows are the unit circuit's rows. Ports are u16 words per
input row (x, wrow, then sx, sw for FP4), and row blocks are the 128-byte SHA-512 blocks those rows hash (the prefix block
and the padding block aside). Digests are 16-hex prefixes of the circuit SHA-512 and the statement digest; the default ones
are red-team-proofs-554's (`note:proofs/20261001T0805Z-reply-from-red-team-proofs-554-nontile-statements`). Runs are
`r20261001-…` on node 1; the three K=16384 cells stage after node 1's 12:10–12:55Z hold and are added here when they land.

| Cell | Run (packed) | n | ANDs | Unit rows | Ports | Row blocks | k_log | Circuit | Statement |
|---|---|---|---|---|---|---|---|---|---|
| NVF4 K=2048 | `-111030-f668` | 4,096 → 8,192 | 223,696 | 354,945 → 256,641 | 2048,2048,128,128 → 512,512,64,64 | 68 → 18 | 23 → 22 | `902fe8f5a2429661` → `b575eedf2520de8a` | `5022d5110c0d7443` → `1abd835db3377aca` |
| NVF4 K=4096 | `-112400-6420` | 2,048 → 4,096 | 447,760 | 710,145 → 513,537 | 4096,4096,256,256 → 1024,1024,128,128 | 136 → 36 | 24 → 23 | `7f1bfda92092e4eb` → `1c9d1f2ae067f1f8` | `af96f785b86368b4` → `60ef5f7c609fe89c` |
| NVF4 K=8192 | `-113808-f60d` | 1,024 → 2,048 | 895,888 | 1,420,417 → 1,027,201 | 8192,8192,512,512 → 2048,2048,256,256 | 272 → 72 | 25 → 24 | `d5d795a8d32d725a` → `29cf09862f56b02a` | `615c340d57b727bc` → `1e50484e8c3e2347` |
| MXF4 K=2048 | `-111405-2516` | 4,096 → 8,192 | 196,116 | 327,425 → 229,121 | 2048,2048,64,64 → 512,512,64,64 | 66 → 18 | 23 → 22 | `ee9ec8c5d239fe65` → `ee6842c05f4158b5` | `12d6b2eb67cb8f92` → `b58ad4a002742e49` |
| MXF4 K=4096 | `-112821-16de` | 2,048 → 4,096 | 392,596 | 654,977 → 458,369 | 4096,4096,128,128 → 1024,1024,64,64 | 132 → 34 | 24 → 23 | `79f2bc884a06e903` → `f5ee0d42e2dc1757` | `8b07af7773157092` → `5e974cf97da7dbaa` |
| MXF4 K=8192 | `-114340-c0fa` | 1,024 → 4,096 | 785,556 | 1,310,081 → 916,865 | 8192,8192,256,256 → 2048,2048,128,128 | 264 → 68 | 25 → 23 | `dc37fd94306c06f0` → `40f9147792bf7010` | `5616ae46bf4c23d1` → `a75e27c5d656270f` |
| E4M3 K=2048 | `-111728-036f` | 4,096 | 626,518 | 692,225 → 659,457 | 2048,2048 → 1024,1024 | 64 → 32 | 23 | `133915e9bf99be61` → `597b219c9564158e` | `8aa357a369a7b8e2` → `05ee2d96494fe6be` |
| E4M3 K=4096 | `-113134-a00c` | 2,048 | 1,253,270 | 1,384,577 → 1,319,041 | 4096,4096 → 2048,2048 | 128 → 64 | 24 | `67456eb4c1090778` → `b56107eb3cea8946` | `1cda565fb1e1e329` → `b990b976889daa47` |
| E4M3 K=8192 | `-115005-feee` | 1,024 → 2,048 | 2,506,774 | 2,769,153 → 2,638,081 | 8192,8192 → 4096,4096 | 256 → 128 | 25 → 24 | `8ba2d4ba2ef6d722` → `2f8a4dc120f62144` | `69c5c10742de5c1a` → `7e227592b1b45eb5` |

## For the statement reviewer

The statement changes only through its circuit. The packed unit has the default unit's gates and AND count, with its input
wiring and port widths moved (FP4's x and wrow rows shrink 4×, E4M3's rows and the scale rows 2×, padding aside), so its
circuit SHA-512 is new and so is the statement digest. An instance's block holds the unit's rows and the in-circuit SHA-512
compressions over its input rows, each range aligned to a power of two (`circuit.fits`), and packing shrinks both. So k_log
drops by 1 at every FP4 cell and at E4M3 K=8192 (by 2 at MXF4 K=8192), and n grows by the same factor at m = 35, with blocks
and nbl following; E4M3 at K=2048 and 4096 keeps its k_log and n. The program and partition digests, the identity (byte-equal in both layouts' statement records), the
Definitions, the Rust prover and verifier, and the row scheme are unchanged: `hm96-sha512/row/v1` under frame-v3-sha512,
`x = SHA-512(sha512_row_prefix(ROLE_X, 16, n_words) || row)`, `b = x ⊕ M(key)·y`, `c = SHA-512(salt prefix || y)`, public
`b || c` and the roots. The SHA-512 over the input rows does hash a different byte layout. By default a row is each
element zero-extended to a little-endian u16 (12 of every 16 bits zero for an FP4 code, 8 for an E4M3 byte or a scale); packed,
it is the tensor's own bytes, and the prefix's n_words falls with it (NVF4 K=2048's x row: 2048 → 512). So every row's x, its
`b || c` and every root differ, and an external anchor (a weights root, a client's request commitment) has to be computed over
the packed row, not the widened one. That is the gain: a committer hashes the bytes it holds without widening them. It is not
yet a drop-in match for core's row conventions, in three ways. Flock's prefix says ROLE_X, word_bits 16 and the row's padded
u16 count for every port, where `rowleaf` would carry the row's role and word_bits 4 or 8. Each row is zero-padded to whole
128-byte blocks (only MXF4's K=2048 scale rows, 64 bytes, need any). And FP4 codes and their scales are two rows each (x and sx,
wrow and sw), where `nvfp4_row_bytes` (`verity/commitments/frame_v3/PROTOCOL.md` §4a) is one row, codes ‖ scales, under
`sha256/row-nvfp4/v1` or `blake3-keyed/row-nvfp4/v1`. So a rowleaf NVFP4 weights root does not equal a Flock root without a
binding, and this change adds none. Packed FP4 is the natural two-per-byte layout: byte j holds code 2j in the low nibble and
code 2j+1 in the high one, exactly `nvfp4_row_bytes`' code buffer, and an E4M3 row is one byte per element. The scales are one
byte each in K order, not the swizzled tile layout that block-scaled MMA kernels read, so a committer that holds swizzled
scales unswizzles them first.
