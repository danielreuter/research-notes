---
id: r21-silicon/ligero-verify-fp4/20260923T0357Z-report-ligero-verify-fp4
campaign: r21-silicon
lane: ligero-verify-fp4
kind: report
status: closed
repo: verity-main@lane/ligero-verify-fp4 7d79aac
---

# ligero-verify-fp4: the Rust verifier verifies the RTX 5090 NVFP4 (`fp4-nvf4`) B-Ligero proofs from bytes, pinned

Branch `lane/ligero-verify-fp4` (worktree `verity-main-wt/ligero-verify-fp4`, base main **24bd337**, head **7d79aac**, two
commits, clean tree, not merged). Diff vs main: 9 files, +681/-36 (`backends/ligero-verify/src/{format,relation,verify,main}.rs`,
`tests/relations.rs`, the fixture `fixtures/fp4-nvf4/`). No `.md` in the repo, no Python touched. Everything ran on the laptop:
Rust builds, the three local dump trees, a torch-free Python recompilation of the relation's tables (`uv run` in the worktree).
`cargo test`: **30 -> 36 green** (17 + 7 + 6 before; 19 + 7 + 10 after). `cargo build --release` works.

**Result for Table 2 (RTX 5090 cell):** all three `fp4-nvf4` dump trees verify from bytes with the independent verifier, system
pinned, 25/25 sub-batches each, batch ACCEPT with the union bound <= 2^-128, 25/25 agreement with the Python verdicts:

| tree | run | zk | mode | coins | accepted | batch | union bound (bits) | per-proof bits | python_agree | verify sum | wall (4 jobs x 1 thread) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| non-ZK | `r20260923-024035-f3cf` (result art:5b5e9f3c..., run-files art:d83225e7...) | false | interactive | 25/25 against their own `.coins` | **25/25** | **ACCEPT** | **128.231** (2^-128.23) | 132.874 | 25/25 (0 disagree) | 0.855 s | **0.248 s** |
| ZK interactive | `r20260923-024119-8da9` (art:8dd5c524..., run-files art:188ddc75...) | true | interactive | 25/25 against their own `.coins` | **25/25** | **ACCEPT** | **128.046** (2^-128.05) | 132.690 | 25/25 | 0.866 s | **0.255 s** |
| ZK Fiat-Shamir | `r20260923-024204-1f80` (art:249785b8..., run-files art:9c5f7eea...) | true | fiat-shamir | none (transferable, D7) | **25/25** | **ACCEPT** | **128.089** (2^-128.09) | 132.733 | 25/25 | 1.146 s | **0.331 s** |

Command per tree (release build, head 7d79aac): `ligero-verify batch --system dumps/system.bin --dir dumps/rep1 --jobs 4
--threads 1 --target-bits 128 --json out.json`; `system_pinned: true`, `pinned_relation: "fp4-nvf4"` in every JSON. Statement
parameters (all three): l = 4096, n = 16384, 170 VUs x 24 steps, K = 68, n_proofs = 25; non-ZK D = 6, t = 196; ZK D = 6, t = 196
(interactive) and D = 7, t = 300 (Fiat-Shamir). The two interactive trees are live-verifier-only evidence (the coins files are
the runner's own step-0 randomness, replayed with `--coins` per sub-batch); the Fiat-Shamir tree is the transferable one.
Per sub-batch verification is ~0.033 s (non-ZK) / ~0.045 s (ZK-FS) single-threaded on this laptop.

**Custody (done first):** every `rep1/sub_NN.stmt` and `.proof` of the three trees (50 files per tree) has the sha256 the tree's
`dumps/manifest.json` records, every `.proof` has the recorded byte count, `dumps/system.bin` has the manifest's
`system_file.sha256` = **6bb9d77fac27118f60e316333508bade1c13eb952c43722372c13b5410c195c8** (95,330 bytes, `sys_id`
a825ba0b...) in all three trees, no file on disk is missing from the manifest and none is listed and missing. The 25 `.coins`
files of each interactive tree are *not* hashed by the manifest (see Python-side notes, item 2); they were used as found.
The manifests record commit `3b0301717aad` (lane fp4-proof) and the instance set `bench-instances-nvfp4-sm120/v1`,
tier `vu-k1536-nvfp4-sm120`, range [0, 4096], seed 20260922.

## 1. The pin: sys_id, table digest, and how they were recomputed

| | value |
|---|---|
| relation | `fp4-nvf4` (tag `\|rel=fp4-nvf4\|v1`, 1-byte operand words, 4-byte accumulator words, `y_bits` 32) |
| `sys_id` (Python `protocol.system_id`, the last 32 bytes of `system.bin`) | **a825ba0b826a15366bfb8cdd720a5e9978603cbe589491abcbba7346ad35bf3c** |
| table digest (this verifier's BLAKE3 of the file bytes without the trailing sys_id) | **b597b003e55b8cf1025b517a04d442d9c6d8704f38fd06df13a21b3273b2d2f6** |
| `system.bin` sha256 (dumps == laptop recompilation) | 6bb9d77fac27118f60e316333508bade1c13eb952c43722372c13b5410c195c8 |
| tables | 1583 rows (hint 86, bit 972, prod 210, inv 2, pin 141, sel 172), 306 linear, 1389 quadratic, 141 pins, 86 hints |
| chain end (`ligero-system/v2` components of the FP32 accumulator word) | sign (lo 31, 1 bit), exponent field (23, 8), fraction (0, 23) |

How the digest was obtained **independently of the dumped file**: the relation's tables were recompiled on the laptop from the
Python definition and serialised with the Python writer, then hashed by the Rust verifier. `torch` is not installed here, and
`backends/direct/ligero/protocol.py` imports torch at module level, so:

* the tables: `backends.direct.ligero.fp4.relation.compile_fp4_unit()` -- pure Python (`compile.py` +
  `verity_numerical.checker.ctx/params`), imported directly;
* the bytes: the real `backends.direct.ligero.serialize.system_bytes` (torch-free: numpy, auth, compile), with the module
  `backends.direct.ligero.protocol` replaced in `sys.modules` by a stub carrying `system_id`;
* `system_id`: a verbatim transcription of `protocol.py::system_id` (lines 299-325 at main 24bd337; `hashlib.blake2b(digest_size
  = 32)` over `m`, `chain`, the rows, the linear and quadratic constraints, `repr(pins)`, `repr(hints)`, the chain `c` rows and,
  for component ends, `repr([Y.key() ...])` and `repr([("end", Y.key(), lo, bits) ...])`);
* `assert "torch" not in sys.modules` after the imports.

Two runs compiled byte-identical files (deterministic), `serialize.read_system` round-trips them (m 1583, L 306, Q 1389, 141 pins,
`y_end` [(31, 1), (23, 8), (0, 23)]), and the file is **BYTE-IDENTICAL** to `dumps/system.bin` (same 95,330 bytes, sha256
6bb9d77f..., sys_id a825ba0b...). `ligero-verify system-digest --system <recompiled>` and `--system <dump>` both print
`sys_id a825ba0b..., table_digest b597b003..., pinned_relation "fp4-nvf4", format ligero-system/v2, chain_end [31/1, 23/8, 0/23]`.
So the pin's two numbers were read off a file this laptop produced from the Python definition, and only then checked against the
dumps -- they matched. The script (kept out of the repo, `/tmp/lvfp4/recompute_fp4_system.py`; invoked as
`PYTHONPATH=$PWD uv run --no-sync python recompute_fp4_system.py out.bin dumps/system.bin 2` from the worktree):

~~~python
"""Recompute the fp4-nvf4 `system.bin` on the laptop without torch and compare it with the pod dump's."""
from __future__ import annotations
import hashlib, sys, types
from pathlib import Path

_SYS_ID: dict = {}

def system_id(sys_) -> bytes:                       # transcription of protocol.py::system_id (main 24bd337, lines 299-325)
    key = id(sys_)
    hit = _SYS_ID.get(key)
    if hit is not None and hit[0] is sys_:
        return hit[1]
    h = hashlib.blake2b(digest_size=32)
    h.update(f"m={sys_.m};chain={sys_.chain is not None}".encode())
    for r in sys_.rows:
        h.update(f"{r.idx}:{r.kind}:{r.name}:{r.lo}:{r.hi};".encode())
    for c in sys_.linear:
        h.update(f"L:{c.name}:{sorted(c.lin.items())}:{c.c}:{c.pub};".encode())
    for q in sys_.quadratic:
        h.update(f"Q:{q.name}:{q.a.key()}:{q.b.key()}:{q.c.key()};".encode())
    h.update(repr(sys_.pins).encode())
    h.update(repr(sys_.hints).encode())
    if sys_.chain is not None:
        h.update(repr(sys_.chain["c"]).encode())
        if sys_.chain.get("y16") is not None:
            h.update(repr([e.key() for e in sys_.chain["y"]] + [sys_.chain["y16"].key()]).encode())
        else:
            h.update(repr([e.key() for e in sys_.chain["y"]]).encode())
            h.update(repr([("end", Y.key(), int(lo), int(bits)) for Y, lo, bits in sys_.chain["y_end"]]).encode())
    d = h.digest()
    _SYS_ID[key] = (sys_, d)
    return d

stub = types.ModuleType("backends.direct.ligero.protocol")
stub.system_id = system_id
sys.modules["backends.direct.ligero.protocol"] = stub
from backends.direct.ligero import serialize                      # torch-free
from backends.direct.ligero.fp4.relation import compile_fp4_unit  # pure Python
assert "torch" not in sys.modules

out, ref, runs = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
datas = []
for i in range(runs):
    s = compile_fp4_unit()
    data = serialize.system_bytes(s)
    datas.append(data)
    print(f"run {i}: rows {s.m} linear {len(s.linear)} quadratic {len(s.quadratic)} pins {len(s.pins)} hints {len(s.hints)}; "
          f"{len(data)} bytes; sha256 {hashlib.sha256(data).hexdigest()}; sys_id {data[-32:].hex()}; magic {data[:8]!r}")
    print("   y_end:", [(lo, bits) for _, lo, bits in s.chain["y_end"]], "c rows:", s.chain["c"])
assert all(d == datas[0] for d in datas), "compilation is not deterministic"
out.write_bytes(datas[0])
rd = serialize.read_system(datas[0])
print("read_system round trip: m", rd["m"], "L", len(rd["linear"]), "Q", len(rd["quadratic"]), "pins", len(rd["pins"]),
      "y_end", [(lo, bits) for _, lo, bits in rd["chain"]["y_end"]])
refb = ref.read_bytes()
print(f"dump system.bin: {len(refb)} bytes; sha256 {hashlib.sha256(refb).hexdigest()}; sys_id {refb[-32:].hex()}")
print("BYTE-IDENTICAL" if refb == datas[0] else "DIFFERENT")
~~~

Output (both runs): `rows 1583 linear 306 quadratic 1389 pins 141 hints 86; 95330 bytes; sha256 6bb9d77f...; sys_id a825ba0b...;
magic b'LIGSYS02'`, `y_end: [(31, 1), (23, 8), (0, 23)] c rows: [0, 1, 2]`, `BYTE-IDENTICAL`.

Caveat on independence: the transcription of `system_id` is a copy of Python code, and `system_bytes` is the Python writer -- what
is independent is the *table content* (recompiled here from `fp4/relation.py`, not copied from the pod) and the Rust digest over
it. The verifier does not trust the sys_id for anything but pinning: the tables it enforces are the ones it parsed, and the pin
`(sys_id, table digest)` says those tables are the ones the laptop compiled from the relation's definition.

Every other relation's system still prints its own pin (`system-digest` on the four fixtures: bf16-ampere 44cb05b9.../c147cc4c...,
fp8-ada 6b570eef.../443e4fc7..., bf16-hopper 9dcc7cdc.../74ce68a2..., fp8-hopper c7cbebe3.../d5b77463..., all `ligero-system/v1`,
`chain_end "word"`).

## 2. What changed in the verifier

**`format.rs` -- `ligero-system/v2`.** `System::parse` accepts `LIGSYS01` (v1, unchanged) and `LIGSYS02`, recording `version`.
The chain end is now `Chain.ends: Vec<EndTerm>` with `EndTerm { y: Expr, family, lo, bits }`; a v1 end is the single term
`(y16, family 6, lo 0, bits 0)` -- `bits = 0` meaning "the whole word as a residue" (`chain.end_terms` does the same), so both
formats run through one chain test. A v2 end is `u32 n_end | n_end x (expr Y, u32 lo, u32 bits)` with `1 <= n_end <= 3`
(`chain.END_FAMILIES = (6, 0, 1)`: component x draws its challenge coefficient from family 6, 0, 1), and every component must be a
bit field of a 32-bit word that is an integer below p: `1 <= bits <= 30`, `lo <= 31`, `lo + bits <= 32`, else the file is
refused at parse ("chain end component x: bit field lo = .., bits = .. is not a field of a 32-bit word below p"). `has_chain`
must be 0/1; a v2 file must carry a chain. `EndTerm::value(y) = (y >> lo) & (2^bits - 1)` (or `y mod p` for bits = 0).
`Chain::components()` reports the `(lo, bits)` list (None for a word end); `system-digest` prints `format` and `chain_end`.

**`relation.rs` -- `fp4-nvf4`.** `Relation.operand: Operand` became `decode: Decode::{Word(Operand), Nvf4}` and gained
`end_components: Option<&[(u32, u32)]>` (None for the four v1 relations; `[(31, 1), (23, 8), (0, 23)]` for fp4). The `nvf4`
module is the public decode of `fp4/relation.py` + `fp4/witness.py::public_vectors_fp4`: `numerator(code)` (E2M1 nibble as a
signed number of halves, 0/1/2/3/4/6/8/12, bit 3 the sign; a byte >= 16 is off the domain), `scale(byte)` (UE4M3 -> `(mantissa,
exponent)`: `(m, -9)` at exponent field 0 else `(8 + m, e - 10)`; bit 7 set = the PTX ISA padding bit and the NaN code 0x7F are
off the domain), `unit_pins(a, b)` (per unit: 128 numerators, per group `g[g].sm = ma*mb`, `g[g].X = -2 + ea + eb`,
`g[g].part = any nonzero product && ma != 0 && mb != 0`, `anc.G = max over participating groups of X - 27, else -174`) and
`pin_index(name)` (the 141 pin names `a[i].n`, `b[i].n`, `g[g].sm/.X/.part`, `anc.G`). `FP4_NVF4` is pinned by the two numbers
above; `RELATIONS` has five entries, so an unknown name is refused with "this build pins bf16-ampere, fp8-ada, bf16-hopper,
fp8-hopper, fp4-nvf4".

**`verify.rs`.** `public_pins` dispatches on the decode (`public_pins_words` unchanged for BF16/FP8; `public_pins_nvf4` requires
K = 68, maps the system's pin names through `pin_index`, decodes every unit -- pad columns included, whose all-zero operands are
on the domain -- and reduces the signed values mod p). `check_end_components(chain, rel)` refuses a system FILE whose chain end
is not the relation's, after the digest pin and **whatever `--allow-any-system` says** (the components are read from the file
and feed the chain test's right-hand side, so a lifted pin must not let a file with other fields through). The chain test runs
one end constraint per end term with the term's family and `term.value(y_pub[j])`; the `y16 < 2^y_bits` check is done in u64 and
is vacuous at 32 bits (every FP32 pattern is a word; the components are compared by the chain test). The system/relation pin
messages are unchanged ("system file is the pinned X system, the statement is a Y statement"; "system file is not the pinned X
system ... pass --allow-any-system").

Why the honest accept is strong evidence for the decode: the pins enter the linear test as `beta = sum rho_q (pub_q - c_q)` at
every unit; a wrong value at any of the 4096 x 141 pins of a sub-batch would fail the linear test with overwhelming probability.
All 75 sub-batches accept, and the unit tests pin the decode against `relation.py` by hand-computed vectors.

## 3. Fixture and negatives

Fixture `backends/ligero-verify/fixtures/fp4-nvf4/`: sub-batch 0 of rep 1 of the **non-ZK interactive** tree (the smallest real
one: proof 1,723,100 bytes, statement 573,513, coins 128, system 95,330; I cannot make fp4 proofs on the laptop -- no torch, no
GPU -- so the smallest carve is the smallest real sub-batch). sha256s: stmt 8625d1bf224cc9635b89922ee93d666f3fcb390724ef5ce32633
e6e743436acd, proof f57e90deaf2991730f118901588349e0419c0264098fe1919e0bdd64ee4fc5cc (the manifest's), coins 7cead39cbf60a08d0bf9
803405866adc926569d76b2b19c63ef2c9c4a150b4d2 (not in the manifest), system 6bb9d77f.... The FS tree was verified from the dumps
directly (table above); adding its sub_00 as a second fixture would cost 2.7 MB more.

Tests added to `tests/relations.rs` (4) and `src/relation.rs` (2), every corruption rejected with the reason its check gives:

| # | negative | reason (substring asserted) |
|---|---|---|
| 1 | a public E2M1 nibble flipped to another code (unit 0, `a[0]` 0x0b -> 0x0a) | `column challenge mismatch`, and the reported statement digest differs from the honest one |
| 1b | an E2M1 code byte with its high nibble set (0x1b) | `public inputs: E2M1 code outside 4 bits (unit 0)` |
| 2 | a UE4M3 scale byte flipped to another finite scale (`a[0]` group 0: 0x31 -> 0x39) | `column challenge mismatch`, digest differs |
| 3 | UE4M3 `0x7F` (in `a`, unit 0; in `b`, unit 1) | `public inputs: UE4M3 NaN scale (unit 0)` / `(unit 1)` |
| 3b | UE4M3 padding bit set (0xB1 in `a`; 0xFF in `b`) | `public inputs: UE4M3 scale byte with the padding bit set (unit 0)` / `(unit 1)` |
| 4 | a changed accumulator component: sign bit, exponent-field bits (two), a fraction bit of `y[0]` | `column challenge mismatch`, digest differs (each) |
| 5 | flipped proof bytes: `w` / `h` / `q` / a column index / an opened value / the root / the last path node / coin commitment c1 | `proximity test failed` / `quadratic constraints failed` / `chain constraints failed (opened columns)` / `column challenge mismatch` / `merkle path 0 invalid` / `merkle path 0 invalid` / `merkle path 195 invalid` / `coin slot 1: opening does not match its commitment` |
| 6 | the wrong system, pinned: bf16-ampere and fp8-ada systems with the fp4 statement; the fp4 system with the bf16-ampere (v2 `b1.stmt`) and fp8-ada statements | `system file is the pinned bf16-ampere system, the statement is a fp4-nvf4 statement` (and the three other pairs, each named), `system_pinned: true` |
| 6b | the same two ways under `--allow-any-system` | `system file: system chain ends on one public word (ligero-system/v1); the fp4-nvf4 relation ends on 3 components (lo/bits 31/1, 23/8, 0/23)` / `system file: system chain ends on 3 components (lo/bits 31/1, 23/8, 0/23; ligero-system/v2); the bf16-ampere relation ends on one 16-bit public word` |
| 7 | a v2 system with a wrong component width (fraction `bits` 23 -> 22; also `lo` 0 -> 1) | pinned: `system file is not the pinned fp4-nvf4 system` (the table digest changed; `system-digest` prints `pinned_relation: null`, `chain_end ... 0/22`); `--allow-any-system`: `system file: system chain end components (lo/bits 31/1, 23/8, 0/22) are not the fp4-nvf4 relation's (31/1, 23/8, 0/23)` |
| 7b | component fields that are not bit fields below p: `bits` 31, `bits` 0, `lo` 10 (with bits 23) | `system file: chain end component 2: bit field lo = 0, bits = 31 is not a field of a 32-bit word below p` (etc.), pinned or not; `system-digest` exits 2 |
| 8 | truncated files: statement (-1 byte), proof (-1 byte), system (-40 bytes) | `statement file: truncated file` / `proof file: truncated file` / `system file: truncated file` |
| 9 | other widths under the name (2/4, 1/2); an unknown name `fp4-blackwell`; the FP8 Ada words (K = 32) re-encoded as `fp4-nvf4` with t and n_proofs patched so the proof header and the soundness gate pass | `word widths 2/4 bytes are not the fp4-nvf4 relation's 1/4`; `statement names relation "fp4-blackwell"; this build pins ..., fp4-nvf4`; `public inputs: statement has K = 32 words per operand per unit, the fp4-nvf4 unit takes 68` |
| 10 | the fp8-ada proof with the fp4 statement; foreign coins | `malformed proof: header M = 3769, the statement fixes 1583`; `coins are not this verifier's step-0 coins` |
| 11 | the v1 magic on the v2 body and the v2 magic on a v1 body | rejected as `system file: ...` (a parse error) |

Positives: the honest fixture accepted pinned with `--coins` ("coins are this verifier's step-0 coins"), without (`coins replayed
from the transcript`), and unpinned (`system_pinned: false`); digest 500bfdb2b69bce82e730a2387188a120c08ce4217ada8c7522180b810a998fad,
per-proof 2^-132.874, union over 25 = 2^-128.231. `system_digest_names_every_pinned_relation` now covers five systems and checks
`format` / `chain_end`. Unit tests: `e2m1_and_ue4m3_decodes_match_fp4_relation_py`, `nvf4_unit_pins_match_public_vectors_fp4`
(hand-computed pins for all-ones, a non-participating group, a zero scale mantissa, a subnormal x top scale group, the -174 anchor,
the pin-name map), and the components' disjoint cover of the 32-bit word in `names_are_distinct_and_digests_unique`.

On "every one rejected with a distinct reason": the corruptions that leave every byte on the domain (a nibble to another code, a
scale to another finite scale, any accumulator component) all fail as `column challenge mismatch` -- the statement digest binds
every public byte, and that IS the check that catches them (the same as the existing fp8-ada negatives 2 and 3). The tests
therefore also assert that the reported statement digest changed. The off-domain corruptions each have their own decode reason
with the unit index; the proof, system and format corruptions each have their own.

## 4. Python-side notes (nothing changed; for the coordinator)

1. **`backends/direct/ligero/chain.py:18`** says "Each component is < 2^31 < p" -- the inequality is wrong: 2^31 = 2147483648 >
   p = 15 * 2^27 + 1 = 2013265921. A 31-bit component in [p, 2^31) would be reduced mod p by the chain test and the integer
   equality the sentence promises would not follow. `chain.end_terms` (chain.py:38-46) validates only the component *count*
   (1..3), and `serialize.read_system` (serialize.py:211) reads `lo`, `bits` unchecked, so Python accepts any widths.
   Consequence today: none -- the pinned fp4 components are 1/8/23 bits. The Rust parser caps `bits` at 30 and requires
   `lo + bits <= 32`; if a future relation wants a 31-bit component the two sides will disagree (Rust refuses the file).
   Suggested: Python should state "at most 30 bits" and validate `1 <= bits <= 30`, `lo + bits <= 32` in `end_terms` or
   `read_system`.
2. **Dump manifests do not hash the `.coins` files.** `relchain.py:400-406` records `proof_sha256` (and the manifests carry
   `stmt_sha256`) but writes `entry["coins"] = "repN/sub_NN.coins"` with no `coins_sha256`. For the interactive trees the coins
   are the verifier's step-0 randomness -- the D7 live-verifier evidence -- so their custody is not attested. Suggested: add
   `coins_sha256` (and `coins_bytes` = 128) beside `proof_sha256`.
3. Nothing in the fp4 statement is un-checkable by the verifier: every operand byte is decoded (codes < 16, scales < 128 and !=
   0x7F, matching `fp4/witness.py:59-63`), every accumulator word's three components enter the chain test, and the K = 68
   layout is fixed by the relation. The component-end widths are fully specified by the file plus the pin.
4. The `--allow-any-system` diagnostic is now slightly stricter for every relation: a file whose chain end kind/fields are not the
   relation's is refused even unpinned (before, only the digest pin stood between a v1 system and a statement; there was no v2).
   The existing behaviour for the honest unpinned pairs is unchanged (they still accept, flagged).

## 5. Commits

* **aec1f89** `ligero-verify: ligero-system/v2 (LIGSYS02, the chain end in components) and the fp4-nvf4 relation, pinned.` --
  `src/format.rs`, `src/relation.rs`, `src/verify.rs`, `src/main.rs`.
* **7d79aac** `ligero-verify tests: the fp4-nvf4 fixture ... and 4 tests ... 30 -> 36 tests.` -- `fixtures/fp4-nvf4/{system.bin,
  sub_00.stmt, sub_00.proof, sub_00.coins}`, `tests/relations.rs`.

`git status --short` empty, no conflict markers, `cargo test` 36/36, `cargo build --release` clean (two pre-existing warnings in
`auth.rs`: an unused `sha256` import and the unused `pad`, untouched). Batch JSON outputs of the three trees: `/tmp/lvfp4/out/
r20260923-02{4035-f3cf,4119-8da9,4204-1f80}.json` (not published; rerunnable in ~1 s from the local dumps).
