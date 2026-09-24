---
id: r23-hash-compose/hash-compose/20260923T1030Z-report-hash-compose
campaign: r23-hash-compose
lane: hash-compose
kind: report
status: closed
repo: verity-main-wt/hash-compose@bdcd412 (branch lane/hash-compose, 3 commits on main a55b3fc; merged by the coordinator as main 64c00bd)
origin: https://github.com/danielreuter/verity.git
pods: vy-hash-compose (RTX 4090, runpod vyz9u60733egnm, $0.74/h, 09:40Z-10:38Z, terminated; no 5090 rented)
---

CHECKPOINT bdcd412 (10:55Z, FINAL; unchanged since the 10:30Z checkpoint — already merged as main 64c00bd) — MERGEABLE: `bf16-ampere` (the Table 2 A100 cell) has its `--auth included-hash` column: composed on the generic
chain runner over the SAME frozen `bench-instances/v1` VUs as the bare cell (§1), GPU-gated 2048 honest VUs + 86 negatives (§2), Rust-pinned with a
fixture and two new tests, a real 25-sub-batch GPU dump `batch ACCEPT … system pinned (bf16-ampere+hash)` (§3), the bare vu.py path byte-identical
(§4), measured at l = 8192 / 16384 on the 4090 with the same-pod bare reference (§5; 1.724 s vs 0.678 s per 4096 VUs at l=16384).  Three additive
commits on `main a55b3fc` (`810a117` relation + frozen-set loader, `3fb87ad` Rust pin + fixture + tests, `bdcd412` store-tool `--root`); `git
merge-tree` against the current `main 538801e` is conflict-free; nothing renamed.  fp4-nvf4: NOT composed — design + cost worked out (§6), it is a
~6-8 h item (a new in-circuit decode layer for the 141 verifier-side pins, a 24-bit-lane sponge packing to stay at 2 permutations/unit, a component
chain end in the v5 statement on both sides, a 5090 gate); nothing speculative is on the branch, and no 5090 was rented.

Tests at bdcd412 — laptop: `pytest packages/verity tests` 468 passed / 6 skipped, `pytest tools/research backends/numerical/python` 162 passed /
1 skipped, `cargo test --release` green incl. the two new bf16-ampere hashed tests.  Pod (`/workspace/src` = the rsynced lane tree; bdcd412 differs from 3fb87ad only in `fp8/tool.py`'s
`--root` parsing, shipped to every `research run` via `--source .`): `pytest backends/direct/ligero -k 'not test_differential_v1_v3'` **166 passed, 1 skipped, 4 deselected** (evidence/pod_pytest_1020Z.log); the 4 deselected `privsel
test_differential_v1_v3[*-v3]` fail identically on the untouched `main a55b3fc` tree on the same pod (same log) — merge-val's finding, not this lane's.
`git status --short` empty.

# Lane hash-compose — the `--auth included-hash` column for the remaining Table 2 targets (2026-09-23)

## 1. What was composed and how (bf16-ampere)

Problem (hash-relation §8 item 4): the Table 2 A100 cell `bf16-ampere` is the legacy runner `vu.py`/`unit.py` over the frozen `bench-instances/v1`
set (`vu-k1536`, 4096 VUs, manifest sha256 `059103cf…eeea`), not a `relations.py` relation, so `hashchain.compose` / `HashedRelationRunner` did not
reach it.  Route taken (the one the brief preferred): register a generic-runner relation **with the same name `bf16-ampere`** in `relations.py`
whose unit is exactly vu.py's — `compile_unit(REAL)` (`REAL = Params.from_model(AMPERE_BF16_M16N8K16)` in `unit.py`; m=3516, L=347, Q=3387,
96 pins, y16 word chain end) — and whose instances are the frozen `bench-instances/v1` `vu-k1536` set itself, so bare and committed columns prove
the same 4096 VUs (both columns' `result.json` record `instances = {dataset bench-instances/v1, tier vu-k1536, range [0, 4096], manifest_sha256 059103cf…}`):

* `relations.py`: `Relation.frozen_tier: str | None` (new optional field, default None — no other relation changes).  `BF16_AMPERE_RELATION =
  Relation(name="bf16-ampere", …, frozen_tier="vu-k1536", instance_seed=0 (unused))`, compile/hints/public vectors are the shared bf16 helpers used by
  `bf16-hopper`.  `RELATIONS["bf16-ampere"]` is new; `bf16-ampere-v2` (relmin-lookup's synthetic-instance registration) is untouched.
* `relchain.py`: `frozen_instances(rel, n, root)` reads `<root>/<tier>.{x,w,y}.u16` + `.index.json` the way `vu.py` does (recycling if n exceeds the
  set; every gate/bench here stayed inside the 4096), `instances()` dispatches on `rel.frozen_tier`, `instances_digest()` returns the frozen manifest's
  sha256 for such relations (so `result.json` `instances` = `{'dataset': 'bench-instances/v1', 'tier': 'vu-k1536', 'manifest_sha256': '059103cf…'}`,
  the same fingerprint the bare column records).  `gate_hashed` / `bench_vu_rel` pass `--root` through.
* `run.py`: `bf16-ampere` added to `--relation` choices (help text says it is the generic chain runner for the A100 cell; `--relation bf16` is still the
  legacy vu.py path).  `fp8/tool.py` (`bench_vu_fp8` store tool): `--root` parsed and dropped (not a key param; it is a pod path).
* `hashchain_test.py`: `bf16-ampere` in `CENSUS` — `rows_base` taken from `compile_unit(REAL, chain=True).m` = 3516 (asserted equal to vu.py's
  REAL system), +608 private-operand rows, +1720 hash rows → hashed system m=5861, L=364, Q=5747, 17 pins, 727 hints (`hint 727, bit 2534, prod 1909,
  sel 610, inv 64, pin 17`), format `ligero-system/v3`, statement v5 (`authentication: included-hash, x rows + W columns + y words under the a/b/y roots`).

Hashed system digests (pod `system.bin` == laptop torch-free recompute, byte for byte):
`sys_id 673461ab446d96869a0ab32d1291667f4af4ba86cdf5fb6479fefaa50dbb8ed4`, `table_digest 3ba12207d9f221dcb2a471044cabb314cc3e05e4512a27559080f431aa7210c9`.

## 2. Gate (GPU, 4090) — evidence/gate_bf16ampere_hashed_2048.log

`python -m backends.direct.ligero.run --relation bf16-ampere gate-vu --vus 2048 --batch 16384 --auth included-hash --root /workspace/bench-instances/v1
--device cuda --target -128` → `bf16-ampere hashed gate: 13 honest sub-batches (170 VUs each, [0,2048)), 86 negatives, 0 failures`.  The 86 negatives are
`relchain.hashed_negatives` (wrong digest / wrong row / wrong index / broken capacity link / every `hash.*` hint row ±δ, e.g. `hash.a[3].b0 (hint) +2 in
column 138: REJECTED linear constraints failed`) plus the relation's own negative families.  The earlier smoke gate (evidence/gate_bf16ampere_smoke.log,
1 honest sub-batch, 34 negatives, 0 failures) was the CPU dry run of the same families.

## 3. Rust (`backends/ligero-verify`) — commit 3fb87ad

* `src/relation.rs`: `BF16_AMPERE.hashed_sys_id / hashed_table_digest` = the digests above (all other relations' pins unchanged; the docstring no longer
  lists bf16-ampere among the non-composed relations; `names_are_distinct_and_digests_unique` now asserts the bf16-ampere hashed pin is 64 hex chars).
* `fixtures/bf16-ampere-hash/` (system.bin 904 KB, manifest.json, sub_00.{stmt,proof,coins}; 5.3 MB like `fp8-ada-hash`): a CPU-deterministic pod dump
  (`bench-vu --zk --mode interactive --auth included-hash --device cpu`, frozen `vu-k1536` VUs 0..10, v5 statement).
* `tests/relations.rs`: `bf16_ampere_hashed_v5_proof_is_accepted_and_the_hashed_system_is_pinned` (ACCEPT, `system_pinned=true`, `pinned_relation
  "bf16-ampere+hash"`, python agreement) and `bf16_ampere_hashed_negatives_and_system_mismatches_are_rejected` (x digest / W digest / y word / W index swap /
  x root flipped and an out-of-range leaf claim in the statement, a truncated multiproof block, the bare pinned bf16-ampere system offered for the
  hashed statement (pin refusal, and row count 5861 vs 3516 with `--allow-any-system`) and the bare v2 statement against the hashed system, a proof
  byte flipped → all REJECT).
* Real pod dump accepted by the release binary: `ligero-verify batch --dir /workspace/fx/bf16-ampere-hash/rep1 --system …/system.bin --target-bits 128`
  → `batch ACCEPT … union bound 2^-128.05; system pinned (bf16-ampere+hash); python agreement 1/1` (evidence/bitexact_bare_bf16.log, 09:55:14).  The
  GPU measurement dump r20260923-095623-ecdf (25 sub-batches x 170 VUs, l=16384, §5): `ligero-verify batch --dir proofs/rep1 --system proofs/system.bin
  --target-bits 128` → **`25 proofs: 25 accepted, 0 rejected; batch ACCEPT (union bound 2^-128.05 <= 2^-128); system pinned (bf16-ampere+hash); python
  agreement 25/25`**, verify sum 35.1 s CPU / wall 2.92 s at 13 jobs (evidence/rust_batch_gpu_dump_l16k.txt); the run's own `validation: passed`.

## 4. Bare path byte-identity (`authentication=excluded`) — evidence/bitexact_bare_bf16.log

Same CPU-deterministic `--relation bf16 bench-vu --zk --mode interactive --batch 4096 --vus 10 --device cpu` (vu.py, `bench-instances/v1` VUs 0..10)
from `/workspace/src-main` (main a55b3fc) and `/workspace/src` (lane tree): `IDENTICAL system.bin`, `IDENTICAL rep1/sub_00.stmt`, `IDENTICAL
rep1/sub_00.proof`; the lane-tree dump verifies in Rust with the existing pin (`system pinned (bf16-ampere)`, sys_id `44cb05b9…89cb`, table
`c147cc4c…3a95`, ligero-system/v1, m=3516, L=347, Q=3387, 96 pins — unchanged).  Bare GPU gate on the lane tree at the full 2048 VUs (`--relation bf16 gate-vu --vus 2048 --batch 16384`, evidence/gate_bare_bf16_2048.log): every
honest sub-batch accepted, `negatives: 52/52 rejected`, `mutations: 252/252 rejected` (2m24s).  And the bare vu.py `research run`s of §5 (l=16384 and
8192) verify in Rust with the existing pin: `system pinned (bf16-ampere)`, 25/25 and 49/49 accepted.

## 5. Measurements (4090; the A100 numbers are Wave 2's) — `research run`, tool `bench_vu_fp8`, campaign r23-hash-compose

| run | relation / column | l | sub-batches | prover t.total (s, 4096 VUs, median of 3) | of which hints_host | verifier (s) | ms/VU | transcript MB | peak dev GB | soundness bits | validation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260923-100248-4034 | bf16 (vu.py) **bare**, int-ZK | 16384 | 25 | **0.678** | 0.134 | 0.693 | 0.166 | 122.4 | 3.0 | — | passed |
| r20260923-095623-ecdf | bf16-ampere **included-hash**, int-ZK | 16384 | 25 | **1.724** (+154 %) | 0.370 | 1.258 | 0.421 | 168.6 | 10.7 | 128.05 | passed, Rust 25/25 |
| r20260923-100319-3e25 | bf16-ampere included-hash, int-ZK | 8192 | 49 | 2.229 | 0.485 | 1.684 | 0.544 | 285.6 | 5.4 | 128.20 | passed |
| r20260923-100414-301a | bf16-ampere included-hash, int-ZK | 32768 | 13 | **OOM** on the 24 GB 4090 (20.45 GB in use + 5.76 GB requested at the encode step) | | | | | >26 | | failed |
| r20260923-102124-5062 | bf16 (vu.py) bare, int-ZK | 8192 | 49 | 1.049 | 0.266 | 1.237 | 0.256 | 193.7 | 1.5 | — | passed, Rust 49/49 |
| r20260923-101935-ab9f | bf16-ampere included-hash, **non-ZK** interactive | 16384 | 25 | 1.584 | 0.287 | 1.266 | 0.387 | 156.7 | 10.7 | 128.25 | passed, Rust 25/25 |
| r20260923-102029-f7a8 | bf16-ampere included-hash, **Fiat-Shamir ZK** | 16384 | 25 | 1.813 | 0.376 | 1.540 | 0.443 | 232.9 | 10.7 | 128.04 | passed, Rust 25/25 |

Operating point on the 4090: **l = 16384** (0.421 ms/VU vs 0.544 at l = 8192; l = 32768 does not fit 24 GB).  For the A100 lane: the hashed column's peak
device memory scales ~linearly in l (5.4 → 10.7 GB), so l = 32768 (13 sub-batches of 341 VUs) needs ~27 GB — it should fit an A100-40GB and certainly
an A100-80GB and is the value to try first there (ms/VU kept improving with l); fall back to 16384.  Committed/bare ratio at l=16384 on this pod: prover
2.54x (2.12x at l=8192), verifier 1.8x, transcript 1.38x, memory 3.5x.  Both columns ran the sequential schedule (vu.py has no `--pipeline`; the hashed
runner forces depth 0 — `relchain.py:855`, hash-relation's open item), so the ratio is apples to apples.  "Rust N/N" = `ligero-verify batch --dir
proofs/rep1 --system proofs/system.bin --target-bits 128` on the pod's dump of rep 1 (evidence/rust_batch_gpu_dump_l16k.txt, rust_batch_gpu_dumps_modes.txt):
every sub-batch accepted, `system pinned (bf16-ampere+hash)` resp. `(bf16-ampere)`, python agreement N/N.  Store: all six completed runs pulled (evidence/data_pull.txt), labelled (evidence/labels.txt;
`--by hash-compose --ref <run>`, `authentication= hash= sharing= note=`), `research data push --pending` (48/48 after the first three; the second push and the snapshot `hash-compose-v1`: §9).
NOTE for the coordinator: the laptop disk is at **1.8 GiB free** after these pulls (was 4.6 before the lane) — pull nothing more before freeing space.

Per-rep detail r20260923-095623-ecdf (evidence/run_amp-hash-int-zk-l16k.log): warm-up 5.90 s; rep1 prover 3.765 + hints 0.628 (first ragged layout
compiles), rep2 1.354 + 0.370, rep3 1.333 + 0.291; verifier 1.24–1.32 s; pass wall 5.4–8.3 s.  Labels: `authentication=included-hash
hash=poseidon2-babybear-w24 sharing=none`, `--by hash-compose`.  For scale: hash-relation's bf16-hopper committed int-ZK on its 4090 was 1.88 s
(r20260923-081632-0fb3, §3 of its note; base 3292 rows vs Ampere's 3516, same +608/+1720 hashed rows; main a55b3fc predates its `9d7d93d`
hint-assembly speedup), so 1.72 s is the expected neighbourhood.  Mode spread of the committed column at l=16384: non-ZK interactive 1.584 s <
ZK interactive 1.724 s < Fiat-Shamir ZK 1.813 s (FS verifier 1.54 s, transcript 233 MB).

## 6. fp4-nvf4 — NOT composed; the design and its cost (nothing speculative on the branch)

Why it is not a 2-hour item.  `hashchain.compose` privatises a relation whose public operands are *decode triples* `(s, m, e)` of fixed-width
words: it turns those pins into hint rows, adds the word's bit rows and a finiteness/normalisation decode (§1 of hash-relation's note), and absorbs
the words 16 bits per lane into two Poseidon2 sponges (x row / W column).  `fp4/relation.py` (`compile_fp4_unit`, 1583 rows/unit, 24 steps/VU,
`ligero-system/v2`) has a different public interface — 141 pins per unit that are the VERIFIER'S arithmetic on the operand bytes, not the bytes:

* `a[i].n`, `b[i].n` (128): the E2M1 numerators in halves (`numerator(code)`: sign nibble bit 3, magnitude table (0,1,2,3,4,6,8,12) on bits 0..2);
* `g[g].sm` (4): the product of the two UE4M3 block-scale mantissas (`decode_scale`: `e == 0 -> (m, -9)` else `(8 + m, e - 10)`; domain bit 7 clear, not 0x7F);
* `g[g].X` (4): `-2 + ea + eb`; `g[g].part` (4): `[gd != 0 and ma != 0 and mb != 0]`; `anc.G`: `max over participating g of X_g - 27` (-174 if none).

Making the operands private therefore needs a NEW in-circuit decode layer before any sponge: per unit 128 nibble decodes (4 bit rows + a degree-3
magnitude polynomial in 3 booleans -> ~2 product rows each), 8 scale-byte decodes (8 bit rows, an `e == 0` test (inverse row), mantissa/exponent
selection), 4 `sm` products, 4 `part` flags (three non-zero tests each, incl. one on the group dot `gd` which is quadratic in the numerators), and the
4-way participating max `G` (4 comparisons = range checks on 9-bit differences + selector rows).  Estimate ~900 rows/unit (128 x 6 + 8 x 12 + ~70)
— on a 1583-row unit that alone is +57 %.  It replaces `witness.public_vectors_fp4` (the verifier's table) by hints, and the Rust side then only
sees digests, as for bf16/fp8.

Sponge shape.  Per operand per step the private data is 64 x 4 bits + 4 x 8 bits = 288 bits; at the current `LANE_BITS = 16` that is 18 lanes >
RATE = 16, so a naive port costs TWO permutations per operand per step (4 per unit: +3440 rows, mostly absorbing zeros).  The right shape is a
24-bit-lane packing for this relation only — the row as 1728 nibbles (a scale byte = 2 nibbles, so ONE word width; `pack_words` injectivity argument
unchanged: positional sums < 2^24 < p), 6 nibbles per lane, 12 lanes per step -> one permutation per operand per step, i.e. the same +1720 hash
rows/unit as bf16/fp8, with `IV(role, word_bits = 4, n_words = 1728)` giving the domain separation (a new `lane_bits` attribute on the relation,
carried in the IV's word_bits/n_words tags; `sponge_states` / `row_sponges` (torch) and `hash_row` (reference) take the lane width as a parameter).
Hashed fp4 unit ~= 1583 + ~900 + 1720 + 17 ~= 4200 rows (2.7x the bare unit; bf16-ampere is 1.67x) — the relative price is high because the FP4 unit
is small while a rate block is a rate block.

Chain end / statement.  The end is three components of an FP32 word (`sys.chain["y_end"] = [(ys,31,1),(yt,23,8),(yf,0,23)]`; the word itself is
>= 2^31 > p, which is why it is in components).  The y tree (public y words under the y root, multiproofs in the statement) is built OUTSIDE the
circuit, so 4-byte y leaves are what fp8's v5 already writes (`y_bytes = 4`) — no new statement version for the y side; but `_statement_of`,
`Statement.parse_v5` and Rust `format.rs` must accept a v5 statement whose SYSTEM has a component end (today v5 pairs with y16 systems; the Rust reader's
`K = steps x operands per unit` check needs the FP4 operand count 68 -> K = 1632 words per row of mixed width, i.e. K must be read as nibbles = 1728
or the header must carry the lane width).  `relation.rs` then gets `FP4_NVF4.hashed_sys_id / hashed_table_digest` from a CPU dump exactly as §3.

Work plan (for whoever picks it up; ~6-8 h + a 5090 hour): (1) `hashchain.compose` gains a per-relation *operand interface* hook (`rel.private_decode(ctx,
sys)` returning the packed lanes + the census) so the bf16/fp8 decode becomes one implementation and FP4 another — additive, the three existing hashed
systems' digests must stay byte-identical (assert in `hashchain_test.py`); (2) the FP4 decode gadgets + a CPU differential test against
`witness.public_vectors_fp4` on the 5090 tc-probe fixtures; (3) `witness`: nibble hints + `hash_hints` for 24-bit lanes; (4) `serialize` / `format.rs`
v5 with a component end + lane width; (5) `relation.rs` pin + fixture + tests; (6) gate on a 5090 (`--relation fp4-nvf4 gate-vu --auth included-hash`),
one `bench-vu --zk --mode interactive --batch <l> --total-vus 4096 --reps 3 --auth included-hash`.  The 5090 was not rented by this lane (nothing to gate).

## 7. Commands for the device lanes

A100 lane — bare column (unchanged Table 2 cell) and committed column over the SAME frozen 4096 VUs (`bench-instances/v1`, `vu-k1536`).  Operating
point: on the 24 GB 4090 l=16384 (§5); on the A100 try **l=32768 first** (13 sub-batches of 341 VUs, ~27 GB peak for the committed column — the 4090
OOMed there; ms/VU still improving with l), fall back to 16384.  The pod's tree must contain this branch (or main after the coordinator's merge):

~~~
# bare (vu.py; existing Table 2 cell) -- store tool bench_vu
python -m backends.direct.ligero.run --relation bf16 bench-vu --zk --mode interactive --batch 32768 --total-vus 4096 --reps 3 \
    --root <bench-instances/v1> --target -128 --device cuda --out result.json --dump-dir proofs --dump-reps 1
# committed (this lane) -- store tool bench_vu_fp8, labels authentication=included-hash hash=poseidon2-babybear-w24 sharing=none
python -m backends.direct.ligero.run --relation bf16-ampere bench-vu --zk --mode interactive --batch 32768 --total-vus 4096 --reps 3 \
    --auth included-hash --root <bench-instances/v1> --target -128 --device cuda --out result.json --dump-dir proofs --dump-reps 1
# gate (once per pod / tree) and Rust
python -m backends.direct.ligero.run --relation bf16-ampere gate-vu --vus 2048 --batch 16384 --auth included-hash --root <bench-instances/v1> --device cuda --target -128
ligero-verify batch --dir proofs/rep1 --system proofs/system.bin --target-bits 128      # expects "system pinned (bf16-ampere+hash)"
~~~

`--pipeline` is irrelevant for both (vu.py has none; the hashed runner forces depth 0 until hash-relation adds its stage generator), so the A100 numbers
are the sequential schedule on both columns, like §5.  The pod needs the frozen set once: `PYTHONPATH=packages/verity/src:backends/numerical/python:.
python -m verity_numerical.bench.instances build --out <dir> --seeds fixtures/bench-instances/v1/seeds --procs 16` (minutes on 16 vCPU), then install the repo's frozen
`fixtures/bench-instances/v1/manifest.json` over the built one so `manifest_sha256` is the pinned `059103cf…eeea` (the built arrays hash identically —
evidence/frozen_set_check.txt; only the manifest's `generated` block differs).  Exactly this lane's recipe: evidence/scripts/{bootstrap.sh, launch.sh}.

5090 / fp4-nvf4 committed column: **no command — not composed** (§6).  The bare fp4-nvf4 cell is unaffected by this branch (no file under `fp4/` touched;
`relation.rs` FP4_NVF4 pins unchanged).

## 8. Pod cost

vy-hash-compose RTX 4090 $0.74/h, 09:40Z → deleted at the final note (§9); ~1.0 h ≈ **$0.75**.  No 5090 was rented (nothing to gate).  Total well
under the $3.50 budget.

## 9. Store / snapshot / pod

Store tool `bench_vu_fp8@1` (committed column) / `bench_vu@1` (bare vu.py), campaign `r23-hash-compose`, source tree bdcd412 (`--source .`).  All six
attempts pulled (`research data pull <run> --from vy-hash-compose --project verity`, evidence/data_pull.txt), labelled (evidence/labels.txt: `authentication=`,
`hash=`, `sharing=`, `note=`; `--by hash-compose --ref <run>`; no `verified=`), `research data push --pending` 48/48 + 31/32 + 19/19, every result and
run_files artifact `research data verify` → PRESERVED (evidence/data_verify.txt).  Snapshot **`hash-compose-v1` =
`art:b632c0f92c08afe6bd5c2cee3d8e0c832523814a28abb8fc25f0dde2182c9ebf`** (24 members: result + run_files + events + resources of the six runs; pushed;
evidence/snapshot.json).  Each `run_files` is the run directory with `proofs/{system.bin, manifest.json, rep1/sub_NN.{stmt,proof,coins}}`.

| run | what | result | run_files (dumps) |
|---|---|---|---|
| r20260923-095623-ecdf | bf16-ampere committed, int-ZK, l=16384 | `art:b7f84dedc191f12e9fd25cb149587d4bf9f696b9a9fcc54840833bc0fa54780e` | `art:0765b1edc365ff2e1c38af5dcaf29ce9572ed56fee9a03d202be8de89fa19cc2` |
| r20260923-100248-4034 | bf16 vu.py bare, int-ZK, l=16384 | `art:e08ca9b4a39293774d9f34d69b2ca82b5df555c831fde544817258c5ecf9ed1d` | `art:310d32ce53660c156634d1bed1e9970fd9dd80770214682a9f52860f9e2d08cf` |
| r20260923-100319-3e25 | bf16-ampere committed, int-ZK, l=8192 | `art:be70d2c3a7ed8969236057f35959d7c673505127eb8c393f603615facb5aad58` | `art:2d17165f331e56c65f60e0e3a0caeb3db5e912d7508314a83623a4296b9f5c52` |
| r20260923-101935-ab9f | bf16-ampere committed, non-ZK int, l=16384 | `art:a24b28cd28f064343783d84a8b6835557574805ccbee196bacfa5a926203c0bd` | `art:34facf96957a5cf1d86613f0194bcd3253ad89cda1b5a378109dc5680a6a6b0f` |
| r20260923-102029-f7a8 | bf16-ampere committed, FS-ZK, l=16384 | `art:da049ed5a3bd4039d950f3dc9778824d736bb8f052e87886f31babecce03e5b4` | `art:7e2b844c4b90d07c2bad70e2efdaf89e776ed9ceed17c4ef1d478204a6954813` |
| r20260923-102124-5062 | bf16 vu.py bare, int-ZK, l=8192 | `art:9571564044ba4232752689becadaeb4dee07b97918fbf06ad842a3e4ee152ec6` | `art:a005a52fbeb5f8c3103e020821ef66a0d7b058e46b71b1370dbcd74b51e9b5e4` |

(r20260923-100414-301a, the l=32768 OOM, was not pulled — it has no result.)  Pod `vy-hash-compose` (vyz9u60733egnm) terminated 10:38Z (`research pods
terminate`; `pods list` no longer shows it; `machines.toml` entry annotated TERMINATED).  Laptop `cargo test --release` at bdcd412: 22 + 7 + 15 green.

## 10. Evidence index (`~/.research/notes/lanes/hash-compose/evidence/`)

gate_bf16ampere_hashed_2048.log / .json (the 2048-VU hashed gate), gate_bf16ampere_smoke.log, gate_bare_bf16_2048.log, bitexact_bare_bf16.log (main vs lane
CPU dumps IDENTICAL + Rust), fixture_bf16ampere_hash.log (the fixture dump + torch-free digests), frozen_set_check.txt, run_amp-hash-int-zk-l16k.log,
driver1.log / driver2.log, runs.txt, rust_batch_gpu_dump_l16k.txt, rust_batch_gpu_dumps_modes.txt, pod_pytest_1010Z.log / pod_pytest_1020Z.log,
data_pull.txt, labels.txt, data_push2.txt, data_verify.txt, snapshot.json, scripts/{bootstrap.sh, sync.sh, ssh.sh, launch.sh, driver1.sh, driver2.sh, bitexact.sh}.
