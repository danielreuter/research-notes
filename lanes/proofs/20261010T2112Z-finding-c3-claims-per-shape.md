---
id: proofs/20261010T2112Z-finding-c3-claims-per-shape
campaign: flock
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: F4 design agent (bc-74de88e1), lean's F5 question (Slack 1791664363) and top's per-shape region ruling (1791665463), on art:5200015a… at b795ecbde, for the proofs coordinator bc-8416bc72
---

# Candidate 3: claims per sampled inner session, per pinned shape (2:12 PM PT, 10 Oct)

**Blocker first:** V\* refuses one pinned shape at its real count, llama32-1b/b1/i256's (B 256, bound 2^29). Its
`GumbelTopPTokenSelect_v1{V=128256}` entry has 7 regions, so claims 16, and padding gives the shape's other two entries the
same count. At claims 16, the last residual alone (residual 20 of 21, the batched T) needs 172 sha512x3 slots, against
`MAX_SLOTS` 160 (it reads 19 regions, under `MAX_REGIONS` 64). So `rec_residuals.parts` and `VStar.parts` throw, and
`Menu.Staged` fails. The other 82 shapes stage.

**For lean, as is:** No: `claims = 2` holds for no pinned shape. (1) The 2 in `proofs_rows`' `V.terms(nu, ell, B, 2, T,
inst)` is the reps (`vstar_c3.terms(nu, ell, slots, reps, T, instances)`). `proofs_rows` carries no inner claims count.
(2) A sampled slot session's inner statement is `RecVStar.innerTags`, `verity/flock-circuit+plain-leaves`. That tag
inherits `hiddenOutputs := true` from `circuitF5df3bbc` (through `b3727bd9`, `cec3e347` and `circuit`; `withPlainLeaves` and
`withCoins` change only the leaf scheme and identity). So `Stmt.setupTables` takes `Stmt.setupHidden`, not `setupH`. Its
regions are `HmOut.regions`, one `digest p` region per row: each input port's row, then one row per output port, since no
menu unit sets `out_row_ports`. `HmIn.regions` adds nothing, because `innerOf` passes no public inputs. There is no out
region. So a session's regions are its unit's input ports plus its output ports, and `Menu.inner s = ⟨inner_m, k_log, 2 +
2·regions⟩`, with regions the largest over the shape's entries. Candidate 3's slot circuit is built per bucket from that
bucket's own unit types, so a shape's entries do not share one circuit by construction. On art:5200015a…, the 90 entries
form 83 shapes: 77 have one entry, and of the 6 with several, 4 already agree. The other 2 take padding:
llama32-1b/b1/i256's (256, 2^29), whose entries have 4, 7 and 2 regions (padded to 7), and mistral-7b/b8/i1024's (256,
2^29), with 5 and 4 (padded to 5). Per shape, regions are 2, 3, 4 or 5 (claims 6, 8, 10 or 12) for 82 shapes, and 7
(claims 16) for one. (3) V\* stages every shape at claims ≤ 14 except llama32-1b/b1/i256's (256, 2^29). Padding gives that
shape's three entries (the attention pieces, Gumbel and the SiluMul tail) Gumbel's 6 inputs + 1 output = 7 regions, claims
16. There, the batched-T residual alone needs 172 sha512x3 slots, against `MAX_SLOTS` 160 (19 regions, under `MAX_REGIONS`
64). So `rec_residuals.parts` and `VStar.parts` refuse it, and `Menu.Staged` fails. `setupH`'s count (inputs + 1) gives 7
too, so this does not depend on the statement form. It clears only if the parts limit grows to at least 172 slots in both
`rec_residuals` and `VStar.Parts`, or the batched-T residual is split (circuits' call). Gumbel's 6 input rows cannot be
packed today, since the prover packs output rows only. V\*'s corrected rows: `proofs_rows` omits the inner reps' own
algebra. Adding it, 2 reps × products(Shape(inner_m, k_log, claims)) × ≈2,439 rows a product, puts 0.30% to 0.71% on a
staged shape's total rows, and the claims beyond 2 alone are 0.13% to 0.43%.

**Which it is (the 21:00Z ask):**
- Padding applies, on 2 shapes, both B 256, bound 2^29, both mixing cap pieces and the tail:
  - llama32-1b/b1/i256, entries #7, #8 and #9 (4, 7, 2 → 7, claims 16, refused);
  - mistral-7b/b8/i1024, entries #6 and #8 (5, 4 → 5, claims 12, stages).
- 4 multi-entry shapes agree without padding:
  - gemma2-2b's (64, 20.9M), the two RoPE entries, 3 regions;
  - llama32-1b/b1/i4096's (256, 2^29), 4;
  - qwen3-4b-fp8's (256, 2^29), 4;
  - qwen3-4b's (256, 2^29), 4.
- The other 77 shapes have one entry each. Within an entry, every unit type has the same (inputs, outputs) maximum, so a
  bucket needs no padding.
- The 20:56Z block's `setupH` reading is off for the regions. `setupH`'s count is inputs + 1; the hidden count is inputs +
  outputs. They agree for one-output units (every shape except the 13 at 5 regions that hold a two-output unit, and the
  router's). The F1 gate's claims 8 / regions 3 fits either reading. The table uses the hidden count.
- 33 distinct (inner_m, k_log, claims) triples over the 22 sessions.

**Per shape** (art:5200015a…, the code at b795ecbde):
- "Of total" is against `proofs_rows`' `total_rows` (art:2b16d554's `proofs-rows/buckets.json`, the same inventory),
  taking the shape's largest entry.
- The merged shapes' base is at the shape's `inner_m`.
- "Claims > 2 alone" is the rep algebra at the shape's claims minus at 2.

| model | B | bound | entries (part, class) | inner m, k_log | regions per entry → shape | claims | V* `parts` | rep algebra rows (M), of total | claims > 2 alone |
|---|---|---|---|---|---|---|---|---|---|
| gemma2-2b/b8/i1024 | 1024 | 33.8M | #0 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| gemma2-2b/b8/i1024 | 1024 | 38M | #1 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| gemma2-2b/b8/i1024 | 1024 | 152M | #2 (body; registered 2^19) | 35, 25 | 3 → 3 | 8 | stages | 14.4 (0.41%) | 0.21% |
| gemma2-2b/b8/i1024 | 16 | 37M | #3 (rare; rare) | 27, 23 | 3 → 3 | 8 | stages | 13.7 (0.42%) | 0.23% |
| gemma2-2b/b8/i1024 | 64 | 20.9M | #4, 5 (rare; rare) | 28, 22 | 3 / 3 → 3 | 8 | stages | 13.9 (0.60%) | 0.32% |
| gemma2-2b/b8/i1024 | 4 | 273M | #6 (tail; tail) | 29, 27 | 2 → 2 | 6 | stages | 11.5 (0.30%) | 0.13% |
| llama32-1b/b1/i256 | 256 | 5.21M | #0 (body; registered 2^18) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.53%) | 0.29% |
| llama32-1b/b1/i256 | 1024 | 33.8M | #1 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| llama32-1b/b1/i256 | 1024 | 135M | #2 (body; registered 2^19) | 35, 25 | 3 → 3 | 8 | stages | 14.4 (0.41%) | 0.21% |
| llama32-1b/b1/i256 | 64 | 269M | #3 (body; registered 2^19) | 32, 26 | 4 → 4 | 10 | stages | 16.5 (0.55%) | 0.33% |
| llama32-1b/b1/i256 | 16 | 270M | #4 (body; registered 2^19) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.63%) | 0.38% |
| llama32-1b/b1/i256 | 64 | 268M | #5 (rare; rare) | 32, 26 | 5 → 5 | 12 | stages | 19.0 (0.52%) | 0.34% |
| llama32-1b/b1/i256 | 16 | 243M | #6 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.39%) | 0.21% |
| llama32-1b/b1/i256 | 256 | 2^29 | #7, 8, 9 (body, tail; cap pieces) | 35, 27 | 4 / 7 / 2 → 7 (**padded**) | 16 | **refused** | 24.4 (0.69%) | 0.50% |
| llama32-1b/b1/i4096 | 256 | 5.21M | #0 (body; registered 2^18) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.53%) | 0.29% |
| llama32-1b/b1/i4096 | 1024 | 33.8M | #1 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| llama32-1b/b1/i4096 | 1024 | 135M | #2 (body; registered 2^19) | 35, 25 | 3 → 3 | 8 | stages | 14.4 (0.41%) | 0.21% |
| llama32-1b/b1/i4096 | 16 | 269M | #3 (body; registered 2^19) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.63%) | 0.38% |
| llama32-1b/b1/i4096 | 4 | 270M | #4 (body; registered 2^19) | 28, 26 | 4 → 4 | 10 | stages | 16.4 (0.71%) | 0.43% |
| llama32-1b/b1/i4096 | 64 | 268M | #5 (rare; rare) | 32, 26 | 5 → 5 | 12 | stages | 19.0 (0.52%) | 0.34% |
| llama32-1b/b1/i4096 | 16 | 243M | #6 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.39%) | 0.21% |
| llama32-1b/b1/i4096 | 256 | 2^29 | #7, 9 (body, tail; cap pieces) | 35, 27 | 4 / 4 → 4 | 10 | stages | 16.9 (0.45%) | 0.27% |
| llama32-1b/b1/i4096 | 4 | 137M | #8 (tail; tail) | 28, 26 | 2 → 2 | 6 | stages | 11.4 (0.32%) | 0.14% |
| mistral-7b/b8/i1024 | 256 | 10.4M | #0 (body; registered 2^18) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.53%) | 0.29% |
| mistral-7b/b8/i1024 | 1024 | 67.6M | #1 (body; registered 2^19) | 34, 24 | 3 → 3 | 8 | stages | 14.2 (0.42%) | 0.22% |
| mistral-7b/b8/i1024 | 256 | 236M | #2 (body; registered 2^19) | 34, 26 | 3 → 3 | 8 | stages | 14.2 (0.42%) | 0.22% |
| mistral-7b/b8/i1024 | 64 | 268M | #3 (body; registered 2^19) | 32, 26 | 4 → 4 | 10 | stages | 16.5 (0.55%) | 0.33% |
| mistral-7b/b8/i1024 | 16 | 270M | #4 (body; registered 2^19) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.63%) | 0.38% |
| mistral-7b/b8/i1024 | 16 | 487M | #5 (rare; rare) | 31, 27 | 3 → 3 | 8 | stages | 13.9 (0.37%) | 0.20% |
| mistral-7b/b8/i1024 | 256 | 2^29 | #6, 8 (body, tail; cap pieces) | 35, 27 | 5 / 4 → 5 (**padded**) | 12 | stages | 19.4 (0.42%) | 0.27% |
| mistral-7b/b8/i1024 | 4 | 34.9M | #7 (tail; tail) | 26, 24 | 2 → 2 | 6 | stages | 10.9 (0.36%) | 0.17% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 256 | 23.3M | #0 (body; generic 2^25) | 32, 24 | 5 → 5 | 12 | stages | 19.0 (0.48%) | 0.32% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 256 | 46.4M | #1 (body; generic 2^26) | 33, 25 | 4 → 4 | 10 | stages | 16.8 (0.40%) | 0.24% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 16 | 65M | #2 (body; generic 2^26) | 27, 23 | 3 → 3 | 8 | stages | 13.7 (0.42%) | 0.23% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 64 | 10.4M | #3 (body; registered 2^18) | 28, 22 | 3 → 3 | 8 | stages | 13.9 (0.60%) | 0.32% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 1024 | 33.8M | #4 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 64 | 268M | #5 (body; registered 2^19) | 32, 26 | 4 → 4 | 10 | stages | 16.5 (0.55%) | 0.33% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 16 | 268M | #6 (rare; rare) | 30, 26 | 5 → 5 | 12 | stages | 19.0 (0.58%) | 0.38% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 16 | 243M | #7 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.39%) | 0.21% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 16 | 2^28 | #8 (body; cap pieces) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.39%) | 0.23% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 4 | 53.6M | #9 (tail; tail) | 26, 24 | 2 → 2 | 6 | stages | 10.9 (0.35%) | 0.16% |
| olmoe-1b-7b/b32/i1024/mixed-arrivals | 256 | 2^28 | #10 (tail; cap pieces) | 34, 26 | 4 → 4 | 10 | stages | 16.7 (0.50%) | 0.30% |
| olmoe-1b-7b/b32/i1024 | 256 | 23.3M | #0 (body; generic 2^25) | 32, 24 | 5 → 5 | 12 | stages | 19.0 (0.48%) | 0.32% |
| olmoe-1b-7b/b32/i1024 | 256 | 46.4M | #1 (body; generic 2^26) | 33, 25 | 4 → 4 | 10 | stages | 16.8 (0.40%) | 0.24% |
| olmoe-1b-7b/b32/i1024 | 16 | 65M | #2 (body; generic 2^26) | 27, 23 | 3 → 3 | 8 | stages | 13.7 (0.42%) | 0.23% |
| olmoe-1b-7b/b32/i1024 | 64 | 10.4M | #3 (body; registered 2^18) | 28, 22 | 3 → 3 | 8 | stages | 13.9 (0.60%) | 0.32% |
| olmoe-1b-7b/b32/i1024 | 1024 | 33.8M | #4 (body; registered 2^19) | 33, 23 | 3 → 3 | 8 | stages | 14.3 (0.45%) | 0.24% |
| olmoe-1b-7b/b32/i1024 | 64 | 268M | #5 (body; registered 2^19) | 32, 26 | 4 → 4 | 10 | stages | 16.5 (0.55%) | 0.33% |
| olmoe-1b-7b/b32/i1024 | 16 | 268M | #6 (rare; rare) | 30, 26 | 5 → 5 | 12 | stages | 19.0 (0.58%) | 0.38% |
| olmoe-1b-7b/b32/i1024 | 16 | 243M | #7 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.39%) | 0.21% |
| olmoe-1b-7b/b32/i1024 | 16 | 2^28 | #8 (body; cap pieces) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.39%) | 0.23% |
| olmoe-1b-7b/b32/i1024 | 4 | 53.6M | #9 (tail; tail) | 26, 24 | 2 → 2 | 6 | stages | 10.9 (0.35%) | 0.16% |
| olmoe-1b-7b/b32/i1024 | 256 | 2^28 | #10 (tail; cap pieces) | 34, 26 | 4 → 4 | 10 | stages | 16.7 (0.50%) | 0.30% |
| qwen25-15b/b1/i4096 | 64 | 10.4M | #0 (body; registered 2^18) | 28, 22 | 3 → 3 | 8 | stages | 13.9 (0.60%) | 0.32% |
| qwen25-15b/b1/i4096 | 1024 | 25.3M | #1 (body; registered 2^19) | 32, 22 | 3 → 3 | 8 | stages | 14.0 (0.47%) | 0.25% |
| qwen25-15b/b1/i4096 | 1024 | 148M | #2 (body; registered 2^19) | 35, 25 | 3 → 3 | 8 | stages | 14.4 (0.41%) | 0.21% |
| qwen25-15b/b1/i4096 | 16 | 268M | #3 (body; registered 2^19) | 30, 26 | 4 → 4 | 10 | stages | 16.5 (0.63%) | 0.38% |
| qwen25-15b/b1/i4096 | 4 | 270M | #4 (body; registered 2^19) | 28, 26 | 4 → 4 | 10 | stages | 16.4 (0.71%) | 0.43% |
| qwen25-15b/b1/i4096 | 16 | 29.5M | #5 (rare; rare) | 27, 23 | 3 → 3 | 8 | stages | 13.7 (0.44%) | 0.24% |
| qwen25-15b/b1/i4096 | 16 | 184M | #6 (rare; rare) | 29, 25 | 3 → 3 | 8 | stages | 14.0 (0.37%) | 0.20% |
| qwen25-15b/b1/i4096 | 16 | 201M | #7 (rare; rare) | 29, 25 | 5 → 5 | 12 | stages | 19.0 (0.50%) | 0.33% |
| qwen25-15b/b1/i4096 | 64 | 2^29 | #8 (body; cap pieces) | 33, 27 | 4 → 4 | 10 | stages | 16.9 (0.54%) | 0.32% |
| qwen25-15b/b1/i4096 | 4 | 162M | #9 (tail; tail) | 28, 26 | 2 → 2 | 6 | stages | 11.4 (0.31%) | 0.13% |
| qwen25-15b/b1/i4096 | 256 | 2^29 | #10 (tail; cap pieces) | 35, 27 | 4 → 4 | 10 | stages | 16.9 (0.45%) | 0.27% |
| qwen3-4b-fp8/b8/i1024 | 256 | 25.5M | #0 (body; generic 2^25) | 30, 22 | 5 → 5 | 12 | stages | 19.0 (0.51%) | 0.34% |
| qwen3-4b-fp8/b8/i1024 | 256 | 40.9M | #1 (body; generic 2^26) | 31, 23 | 5 → 5 | 12 | stages | 18.8 (0.48%) | 0.32% |
| qwen3-4b-fp8/b8/i1024 | 256 | 42.5M | #2 (body; generic 2^26) | 31, 23 | 3 → 3 | 8 | stages | 13.8 (0.35%) | 0.19% |
| qwen3-4b-fp8/b8/i1024 | 64 | 97.2M | #3 (body; generic 2^27) | 30, 24 | 5 → 5 | 12 | stages | 19.0 (0.49%) | 0.33% |
| qwen3-4b-fp8/b8/i1024 | 256 | 10.4M | #4 (body; registered 2^18) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.53%) | 0.29% |
| qwen3-4b-fp8/b8/i1024 | 256 | 15.3M | #5 (body; registered 2^22) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.43%) | 0.23% |
| qwen3-4b-fp8/b8/i1024 | 16 | 306M | #6 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.34%) | 0.18% |
| qwen3-4b-fp8/b8/i1024 | 16 | 359M | #7 (rare; rare) | 30, 26 | 5 → 5 | 12 | stages | 19.0 (0.46%) | 0.30% |
| qwen3-4b-fp8/b8/i1024 | 256 | 2^29 | #8, 10 (body, tail; cap pieces) | 35, 27 | 4 / 4 → 4 | 10 | stages | 16.9 (0.45%) | 0.27% |
| qwen3-4b-fp8/b8/i1024 | 4 | 162M | #9 (tail; tail) | 28, 26 | 2 → 2 | 6 | stages | 11.4 (0.31%) | 0.13% |
| qwen3-4b/b8/i1024 | 256 | 42.5M | #0 (body; generic 2^26) | 31, 23 | 3 → 3 | 8 | stages | 13.8 (0.33%) | 0.18% |
| qwen3-4b/b8/i1024 | 64 | 67.9M | #1 (body; generic 2^27) | 30, 24 | 3 → 3 | 8 | stages | 14.0 (0.38%) | 0.20% |
| qwen3-4b/b8/i1024 | 64 | 161M | #2 (body; generic 2^28) | 31, 25 | 3 → 3 | 8 | stages | 13.9 (0.33%) | 0.18% |
| qwen3-4b/b8/i1024 | 256 | 10.4M | #3 (body; registered 2^18) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.53%) | 0.29% |
| qwen3-4b/b8/i1024 | 256 | 15.3M | #4 (body; registered 2^22) | 30, 22 | 3 → 3 | 8 | stages | 14.0 (0.43%) | 0.23% |
| qwen3-4b/b8/i1024 | 16 | 306M | #5 (rare; rare) | 30, 26 | 3 → 3 | 8 | stages | 14.0 (0.34%) | 0.18% |
| qwen3-4b/b8/i1024 | 16 | 359M | #6 (rare; rare) | 30, 26 | 5 → 5 | 12 | stages | 19.0 (0.46%) | 0.30% |
| qwen3-4b/b8/i1024 | 256 | 2^29 | #7, 9 (body, tail; cap pieces) | 35, 27 | 4 / 4 → 4 | 10 | stages | 16.9 (0.45%) | 0.27% |
| qwen3-4b/b8/i1024 | 4 | 162M | #8 (tail; tail) | 28, 26 | 2 → 2 | 6 | stages | 11.4 (0.31%) | 0.13% |

**Caveats:**
- A cap-pieces entry's ports are its subcircuit's (`templates.subcircuit`). A piece's own cut ports could add rows; that
  needs circuits to check.
- `out_row_ports` is set only for PoUW's segmented or v2 output runs (`circuit.py:635`), so here there is one output row
  per port.
- ≈2,439 rows a product is rec-reprice's estimate (10,440,705 / 4,281). The product counts are exact
  (`rec_algebra.structure` at b795ecbde): 1,410 at Shape(35, 27, 2), 2,946 at claims 8, 4,994 at claims 16.
- Hiding: the reason the regions are per shape also applies to V\*'s other statement parameters (nu, ell, T,
  instances), which `proofs_rows` prices per bucket. For the corrected rows I took the largest entry's rows, not a padded
  statement. compute-accounting would price the padded statement.
- The scripts (`/tmp/b795shape.py`, `/tmp/b795res.py`, `/tmp/b795ports2.py`) are local scratch.
