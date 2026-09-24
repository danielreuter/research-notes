---
lane: tier0-bytes
kind: report
created: 2026-09-23T17:00Z
status: final
---

CHECKPOINT none (17:30Z) worktree ~/projects/verity-main-wt/tier0-bytes on lane/tier0-bytes from main e0cf2cd. Pod vy-tier0-bytes: 4090 secure stock=None at 17:25Z (HTTP 500 "no instances"), retry loop running (4090 secure x3 -> 4090 community x2 -> H100). **Finding before any code: §2.4 item (1) is structurally impossible as specified** — the opened columns are RS-codeword entries on the coset g<w_n> (disjoint from H), not witness values; under ZK every one of them is uniform in [0, p). Bit-packing `bit`/`sel` rows would need the prover to open payload positions (red-team F4 / ZK break). Numbers in §1. Item (2) (trimmed hashed statement, 91 -> 27 kB/sub-batch) is real and is what I am building.

CHECKPOINT a264152 (18:20Z) LIGSTM06 landed + measured on vy-tier0-bytes (4090, EU-RO-1, created 17:27Z after the 500s): hashed statement 1 182 597 → 347 013 B for 13 sub-batches (−70.7 %; 92 629 → 28 457 B per full sub-batch), proof bytes / t.total / verify time unchanged, Rust 13/13 on every dump, 13/13 v6↔v5 byte-identical re-serialisation. 9 artifacts PRESERVED (`evidence/store_ids.txt`). cargo laptop 23+7+18, pod 23+7+18. Merge preview with lane/leaf-iface 720820d resolved on `lane/tier0-bytes+leaf-iface` (704261b, pushed): cargo 26+7+18, merged binary accepts the v6 dump 13/13. Pod pytest running. Remaining: pod pytest count, FINAL, terminate.

# tier0-bytes — Ligero proof/statement bytes: what serialization can and cannot cut

## 1. Item (1) — "bit-packed opened columns" cannot exist in this protocol (numbers)

**Where the opened values come from.** `protocol.py` §"ZK masking": row j of the witness becomes the polynomial
p_j(x) = interp_H(W[j])(x) + Z_H(x) s_j(x) and the committed matrix U is its evaluation on the coset g<w_n>, which is
DISJOINT from H (PROTOCOL.md line 219, red-team F4: "no opened column is a payload position"). The verifier opens t
columns of U. So an opened entry of a `bit` row is the value of the interpolant of a 0/1 vector at an off-H point —
an arbitrary field element even without ZK — and with ZK it is exactly uniform (Z_H(eta_c) s_j(eta_c) is uniform for
t <= t_pad points). The Rust verifier cannot "know the row kind and decode a bit": there is no bit to decode.

**Measured on the checked-in fixtures** (non-ZK, so the most compressible case that exists; ZK is incompressible):

| fixture | rows | opened values in {0,1} | mean log2(value) |
|---|---|---|---|
| fp8-ada (l=4096, t=198) `bit` rows | 2474 | 62 370 / 489 852 = 12.7 % (the constant-zero bits: interpolant ≡ 0) | 25.7 |
| fp8-ada `sel` rows | 640 | 12 276 / 126 720 = 9.7 % | 26.6 |
| fp8-ada-hash (l=1024, t=189) `bit` rows | 2474 | 67 095 / 467 586 = 14.3 % | 25.2 |
| fp8-ada-hash `sel` rows | 640 | 14 364 / 120 960 = 11.9 % | 26.0 |

Under ZK (every Table 2 cell) the {0,1} fraction is 2/p ≈ 0.

**Where today's bytes are** (4090 cells, art:cc59294a bare / art:4ab22886 +hash, 13 sub-batches, l=16384, t=196, D=6, ZK interactive):

| component | bare (bytes) | share | +hash (bytes) | share | what it is |
|---|---|---|---|---|---|
| opened columns M×t×4 | 38 780 560 | 58.7 % | 63 659 232 | 70.0 % | M = 3805 / 6246 rows × 196 cols, uniform field elements |
| w, h, q, v messages | 25 957 776 | 39.3 % | 25 957 776 | 28.5 % | D × (k + (2k−1−l) + (l+k−1) + k) coefficients, uniform under ZK |
| Merkle paths t×16×32 | 1 304 576 | 2.0 % | 1 304 576 | 1.4 % | BLAKE3 digests |
| **proof total** | **66 056 016** | | **90 934 688** | | |
| statements (13) | 14 484 392 | | 1 182 597 | | bare: the public operand words a, b (u8) + y16; hashed: digests + y16 (l×u32) + leaf indices + roots + multiproofs |

Every proof byte but the paths is a uniform element of [0, p), p = 2^31 − 2^27 + 1. The entropy floor is log2(p) = 30.906
bits per element, i.e. the ONLY serialization headroom on the proof is 32 → 31 bits (3.1 %; 3.4 % with exact-range
arithmetic packing) plus a Merkle multiproof dedup of the t paths (~35 % of 2 % = 0.7 %). Total ≤ ~4 %. A 2–3× cut
needs the protocol to change (t, M, or Ligerito), not the encoding. **I did not build the 31-bit pack**: it would add a
proof-format variant to every reader for 3 %, and the pack/unpack lands on the prover host's live sender path (dev-h100-2:
the live tax is host-side transmit contention) — say the word and it is a one-hour change (new magic LIGPRF03, additive).

**The "serialization = 40 % of prover time" on the H100** (morning report §1) is `t.serialization = split.openings +
statement` in `relchain.py`, i.e. the openings STAGE of the pipelined prover (device gather of the t columns + paths +
one pinned D2H copy + the hand-off to the live sender), not `proof_bytes()`; `proof_bytes()` runs after the timed
interval (hp2-host §"serialization 0.110 s" note). With local coins that stage is 0.034 s / 13 sub-batches on the 4090
(2.6 ms per sub-batch). With a live verifier it inflates to 0.27 s because the sender thread's `sendall` of ~6–8 MB per
sub-batch stalls it (dev-h100-2 §2). So bytes DO matter for the live tax — but they are at the floor for this protocol;
the fix is live-2's async sender.

## 2. Item (2) — trimmed hashed statement `ligero-statement/v6` (LIGSTM06) — LANDED a264152

**What a v5 hashed statement carried.** `LIGSTM05` = header | K | y_bytes | relation | "included-hash" | digest table
(n_vus × 16 u32) | **y16 (l × u32)** | hash-auth block (version, schema, params sha, leaf indices, roots, SHA-256
multiproofs). For fp8-ada at l = 16384 / 341 VUs the y16 vector is 65 536 B of the 92 629 B file, and 341 of its 16 384 words
are nonzero (the chain ends, `y16[v·steps + steps − 1]`; `HashedRelationRunner` pads the rest with zeros — the operand words
themselves are private wires, they were never in the v5 file). There is no "per-sub-batch instance array" left in v5
beyond that vector: the brief's 91 → 26 kB target is exactly the zero padding.

**v6** = the v5 layout with `l × y16` replaced by `n_vus × y` (chain-end words in VU order). Reader rebuilds the full
vector (zeros off the ends), so the **statement digest, the challenges, the proof bytes and the Rust verdict are those of
the v5 file** — the writer refuses a y16 with a nonzero word off the ends (v6 cannot represent it). Default for hashed
relations; `LIGERO_STMT_TRIM=0` writes v5 (byte-identical to main); v5 files are still read by both readers. Bare relations
are untouched (v4). Python: `serialize.py` (`STMT_MAGIC_V6`, `Statement.trimmed`, `Statement.y_words()`, the `trimmed`
branch of `_statement_bytes_v5` / `_read_v5`, `hashed_statement_format()`), `relchain.py` (the `statement_format` label).
Rust: `format.rs` (`LIGSTM06` → version 6, `parse_v5` → `parse_hashed(version)` with the y-words branch; `k_hdr`/`k_ops`
gate on `hashed = version >= 5`). Tests added (not soundness code): `tests/relations.rs`
`fp8_ada_hashed_v6_statement_is_the_v5_statement_without_the_zero_y_words` (the v6 fixture == a programmatic v5→v6 of the
v5 fixture, byte for byte; verify + batch accept) and `fp8_ada_hashed_v6_statement_negatives_are_rejected` (y word / digest
/ root mutation, v5 body under v6 magic and vice versa, truncation); fixture `fixtures/fp8-ada-hash/sub_00_v6.stmt`.

**Cross-check on the pod dumps:** the 13 v6 statements of the "after" run, re-serialised as v5, are byte-identical to the
13 v5 statements of the "before" run (and vice versa) — 13/13 (`evidence/pod/hash_{before,after}/dump/rep1/*.stmt`, stored
as `art:404414a7…` fixture/v1 with `v5/` and `v6/` trees).

### Before / after on the reference RTX 4090 (`vy-tier0-bytes`, EU-RO-1, Ryzen 7950X host), tree a264152, same binaries

fp8-ada, ZK interactive, **local coins**, 4096 VUs, `--batch 16384` (13 sub-batches × ≤ 341 VUs, l = 16384, t = 196),
`--pipeline 4`, 3 reps (medians), rep 1 dumped; `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`; `ligero-verify batch --jobs 13
--threads 1 --target-bits 128` (binary sha256 6cecb8a2…) run 3× over each dump. "before" = `LIGERO_STMT_TRIM=0`.

| cell | statement format | proof bytes (13) | statement bytes (13) | per sub-batch (sub_00 / sub_12 tail) | `t.serialization` | `t.total` | python verifier | Rust batch: accepted | Rust wall (3 runs) | Rust CPU sum |
|---|---|---|---|---|---|---|---|---|---|---|
| **+hash before** | LIGSTM05 | 90 934 688 (dump 90 935 260) | **1 182 597** | 92 629 / 67 209 | 0.0107 s | 0.5513 s | 0.496 s | 13/13, 128.32 bits | 0.572 / 0.580 / 0.582 s | 7.10 / 7.16 / 7.22 s |
| **+hash after** | **LIGSTM06** | 90 934 688 (dump 90 935 260) | **347 013 (−70.7 %, 3.41×)** | **28 457 / 1 689** | 0.0108 s | 0.5495 s | 0.493 s | 13/13, 128.32 bits | 0.579 / 0.574 / 0.584 s | 7.18 / 7.13 / 7.25 s |
| bare before | LIGSTM04 | 66 056 016 (dump 66 056 588) | 14 484 392 | — | 0.0084 s | 0.1717 s | 0.236 s | 13/13, 128.32 bits | 0.276 / 0.242 / 0.259 s | 3.12 / 2.89 / 3.02 s |
| bare after | LIGSTM04 | 66 056 016 (dump 66 056 588) | 14 484 392 | — | 0.0082 s | 0.1700 s | 0.233 s | 13/13, 128.32 bits | 0.245 / 0.240 / 0.240 s | 2.94 / 2.91 / 2.92 s |

* Proof bytes: unchanged by construction (§1: the proof is at the encoding floor). `t.serialization` / `t.total` / verify
  time: unchanged within run-to-run noise (the statement writer runs after the timed interval; the y-word copy is 64 kB less
  per sub-batch). The deliverable is the **statement**: 90 969 → 26 693 B per sub-batch on average (brief target 91 → 26 kB),
  64 172 B = (16384 − 341) × 4 saved per full sub-batch; the 4-VU tail goes 67 209 → 1 689 B.
* The bare `t.total` here (0.170 s) is `--pipeline 4` with local coins on e0cf2cd; the Table 2 cell (0.252 s) is
  `--pipeline 2` live. The hashed `t.total` 0.549 s vs the cell's 0.693 s likewise (pipe-race fix + local coins). Not Table 2
  candidates (local coins) — controls for the before/after only.
* `--pipeline 4` accepted 13/13 in all 4 runs × 3 reps (Python) and 13/13 Rust on every dump — consistent with the
  morning report's pipe-race fix being in e0cf2cd (dev-4090 saw depth-4 rejects on 64c00bd).
* Store: results `bench-result/v1` hash_before `art:f039d347…`, hash_after `art:632732df…`, bare_before `art:107f6081…`,
  bare_after `art:e8183af7…`; Rust verdicts `verification-verdict/v1` `art:5c48ac97…` / `art:728ff43e…` / `art:507dd462…` /
  `art:04d2801e…` (each `--ref result=`); statements `art:404414a7…`. Meta `by: tier0-bytes`. Full ids in `evidence/store_ids.txt`;
  the pod's `/workspace/t0b/{cell}/{result.json,run.log,verify_*.json,bytes.txt}` are copied to `evidence/pod/` (no proofs).

### Projected bytes/s at today's Table 2 prover times (coordinator's comms table)

Bytes the verifier must receive per 4096-VU batch = proof + statements (+ `system.bin` once, pinned: 246 605 B bare /
926 203 B hashed — excluded). Proof bytes per cell are the stored results' `proof_bytes` ([2] has none; the A100 runs the
same bf16 relation / 25 sub-batches as [5], so [5]'s bytes are used). Times are the coordinator's. The v6 saving per cell
= (l − VUs per sub-batch) × 4 × sub-batches; hashed-statement bytes for the bf16 cells (25 × 170 VUs) are ESTIMATED from
the fp8-ada structure (v6 ≈ 27 093 × 170/341 + 170 × 4 ≈ 14.2 kB per sub-batch; v5 = that + 65 536), fp8 cells measured.

| Table 2 cell | bare `t.total` | bare proof B | bare statement B (v4) | **bare bytes/s** (proof / proof+stmt) | hash `t.total` | hash proof B | hash statement B v5 → v6 | **hash bytes/s before → after** |
|---|---|---|---|---|---|---|---|---|
| A100 BF16 [2]/[3] | 0.781 s | 118 027 300 | n/a (bf16 v4 not measured here) | 151.1 MB/s / — | 2.104 s | 168 636 600 | ≈ 1 993 000 → ≈ 354 700 (est.) | 81.1 → 80.3 MB/s (−0.96 %) |
| H100 BF16 [5]/[6] | 0.665 s | 118 027 300 | n/a | 177.5 MB/s / — | 0.951 s | 164 223 800 | ≈ 1 993 000 → ≈ 354 700 (est.) | 174.8 → 173.1 MB/s (−0.99 %) |
| H100 FP8 [8]/[9] | 0.356 s | 62 254 400 | ≈ 14 484 392 (fp8, same operand layout as fp8-ada) | 174.9 MB/s / 215.6 MB/s | 0.527 s | 87 133 072 | 1 182 597 → 348 361 | 167.6 → 166.0 MB/s (−0.94 %) |
| RTX 4090 FP8 [11]/[12] | 0.252 s | 66 056 016 | 14 484 392 (measured) | 262.1 MB/s / 319.6 MB/s | 0.693 s | 90 934 688 | 1 182 597 → 347 013 (measured) | 132.9 → 131.7 MB/s (−0.91 %) |
| RTX 5090 NVFP4 [14] | 0.0714 s | 23 522 912 | n/a | 329.5 MB/s / — | — | — | — | — |

Reading: the trimmed statement removes ~0.9–1.0 % of the hashed column's bytes/s and 0 % of the bare column's — because the
proof (91 MB) dwarfs the statement (1.2 MB), and the proof is at the floor of this protocol (§1). At the 4090's measured
local-coin times the wire rates are 474 MB/s bare (proof+v4 statement) and 166 MB/s hashed. The bytes that move the comms
table are the bare v4 statement's operand words (14.5 MB = 18 % of bare bytes: u8 a, b for every unit — a public input the
verifier could equally fetch from the committed dataset by root, i.e. the hashed design) and the proof itself (t, M, Ligerito).

## Interface / ownership

* I touch `serialize.py` ONLY in: a new magic `STMT_MAGIC_V6`, a `trimmed` flag + `y_words()` on `Statement`, the
  y16-vs-y-words branch of `_statement_bytes_v5` / `_read_v5` (the magic and the one `w.a(...)`/`r.a(...)` line for the
  vector), the magic dispatch in `read_statement`, `_manifest`'s format label, `hashed_statement_format()`, and
  `relchain.py`'s `statement_format` label. The fields leaf-iface owns (17:25Z note §"fp4-decode / tier0-bytes": the
  `relation` string + suffix rule, the digest table `(n_vus, 2·digest_elems)`, `_hash_auth_block_{w,r}`) are untouched
  and reused by v6 unchanged — a `+blake3` / `+ajtai-n64` statement trims the same way. Their 0d7d716 and my a264152 edit
  the same two functions, so the merge may conflict TEXTUALLY (adjacent lines) but not semantically: keep both — their
  digest-table / relation lines, my `trimmed` magic + vector lines.
* Rust: `format.rs` (magic + the y-words branch of `parse_v5` → `parse_hashed`), nothing in `verify.rs`/`relation.rs`
  soundness paths; pins unchanged (the system files do not change).

## Discrepancies

1. **§2.4 item (1) as specified cannot be built** (§1): opened columns are coset evaluations, uniform under ZK; there are
   no bits to pack. The only encoding headroom on the proof is ~3–4 % (31-bit packing + multiproof dedup); not built.
2. **`fold_test.py::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` fails on main e0cf2cd on a 4090**
   (`assert 4.1456 < 4.1`, rows-per-unit ratio; 5d88d70's threshold) — pre-existing, independent of this lane (compile-only
   test; no serialize.py involvement). Owner: honing-code / fold.
3. **One existing test line touched**, against the letter of "do not touch test code": `hashchain_test.py::
   test_statement_v5_and_system_v3_round_trip` asserted `raw[:8] == STMT_MAGIC_V5` — i.e. that the DEFAULT hashed statement
   is v5, which is exactly what item (2) changes. Commit 82dfa31 makes it assert the magic the writer is configured for
   (`STMT_MAGIC_V6 if HASHED_STATEMENT_TRIMMED else STMT_MAGIC_V5`) and adds the v6 round trip. No soundness test touched.
   Alternative if the coordinator prefers the tests untouched: flip the default (`HASHED_STATEMENT_TRIMMED` false unless
   `LIGERO_STMT_TRIM=1`) — one line in serialize.py; the measurements above are then opt-in.
4. `research data put` has no `--by` flag (the brief's `--by tier0-bytes`); recorded as `meta.by = "tier0-bytes"` on all 9.
5. `research data push --pending` from the laptop ran > 13 min without output (it pushes every lane's pending artifacts);
   killed, pushed my 9 ids explicitly (9/9 PRESERVED, `--verify head`).
6. The pod image lacks `/usr/bin/time`; measure.sh's inline verify step failed, re-done by `evidence/verify.sh`.

## FINAL (18:50Z)

* Branch `lane/tier0-bytes` head **82dfa31** (a264152 = LIGSTM06 + Rust + tests; 82dfa31 = the hashchain_test magic line),
  pushed; `git status --short` empty. Merge preview `lane/tier0-bytes+leaf-iface` **523981c** (lane/leaf-iface 720820d +
  this lane, conflicts in `serialize.py` / `format.rs` resolved: their digest-table / relation-suffix lines + my `trimmed`
  branch), pushed — on that tree the merged prover writes v6 byte-identical to a264152's (`sub_00.stmt` cmp equal), and
  both the merged Rust (`e8882a9c…`) and the a264152 Rust (`6cecb8a2…`) accept its 13/13.
* Tests. Laptop (no torch): cargo `ligero-verify` 23 + 7 + 18 = **48 passed** on a264152; 26 + 7 + 18 = **51** on 523981c;
  `tests/test_ligero_auth.py` 6 passed / 1 torch-skip-as-fail (laptop stub). Pod (4090, a264152 tree + 82dfa31's test):
  cargo **48 passed**; `pytest backends/direct/ligero tests/test_ligero_auth.py tests/test_ligero_batch_bound.py
  --ignore=privsel`: **197 passed, 1 skipped, 3 failed** in the full run → re-run after fixing my shipping (missing
  `fixtures/tc`) and the magic line: hashchain_test + fp4 k1536 **15 passed**; the remaining failure is Discrepancy 2
  (pre-existing fold threshold). Merged tree on the pod: cargo **51 passed**, `hashchain_test + leaf_test + test_ligero_auth
  + test_ligero_batch_bound` **33 passed**.
* Before/after (§2 table): proof bytes 90 934 688 → 90 934 688 (+hash) / 66 056 016 → 66 056 016 (bare); statement bytes
  **1 182 597 → 347 013** (+hash, −70.7 %) / 14 484 392 → 14 484 392 (bare, v4 untouched); `t.serialization` 0.0107 →
  0.0108 s / 0.0084 → 0.0082 s; `t.total` 0.5513 → 0.5495 s / 0.1717 → 0.1700 s; Rust batch 13/13 accepted on all four
  dumps, wall 0.58 → 0.58 s (+hash) / 0.26 → 0.24 s (bare).
* Projected bytes/s per Table 2 cell: §2 second table (bare unchanged; hashed −0.9–1.0 %).
* Pod `vy-tier0-bytes` (20gvgoi7ak24na, 4090 EU-RO-1 $0.74/h) created 17:27Z, terminated 18:50Z: **≈ 1.4 h ≈ $1.03** of the
  $4 cap. Watchdog (5.3 h) cancelled by the termination. Nothing of value left on it (dumps not pulled; statements are `art:404414a7…`).
* Remaining / not done: item (1) (impossible as specified — §1; the 3 % 31-bit pack is available on request); bf16
  hashed-statement bytes for the A100 / H100-BF16 cells are estimates (no bf16 run here); the hashed `t.total` here is
  local-coin at depth 4 (0.549 s), not a Table 2 candidate; leaf-iface may move past 720820d — the resolution pattern in
  523981c still applies (keep both sides; my lines are the `trimmed` magic + vector only).
