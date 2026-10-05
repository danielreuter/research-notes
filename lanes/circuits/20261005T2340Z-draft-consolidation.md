---
id: 20261005T2340Z-draft-consolidation
campaign: finished-state
lane: circuits
kind: draft
status: open
repo: verity
origin: b87eeef64
---

# Circuits consolidation: what is written twice, what is fragile, what is dead

This note covers circuits' code at `b87eeef64`, the head after the layout move on `cursor/lean-layout-move-2-c3b2`. The scope is
three areas: `tools/circuit_check/`; the Boolean word library, now split between core's `verity/primitives/circuits/boolean/`
(`forms`, `gather`, `trace`) and the catalog's `catalog/verity_catalog/{silicon,definitions,definitions/boolean}/`; and circuits'
parts of `integrations/vllm/verity_vllm/program/registry/` with the Build rules and fold patterns that bind them. Paths are
relative to the repository root; `R/` means `integrations/vllm/verity_vllm/program/registry/` and `C/` means
`catalog/verity_catalog/definitions/`.

Method. I imported every registry at `b87eeef64` the way `circuit_check.targets.load_registries` does, which yields 736 authored
Definitions (428 in the vLLM registry, 133 in the catalog, 174 in core and PoUW). For each Definition I counted references to the
Python name that holds it and to its id string, across every tracked file outside `archive/`, split into Build rules, fold
patterns, the rest of the integration, tests and circuit-check. Every claim below was then checked by hand with `rg`. A
Boolean Definition with no name references is not dead: `verity_vllm/program/boolean.py`'s `boolean_version` finds it through its
`word` link. A superseded version is not dead either while `integrations/vllm/tools/migrate/superseded_quarantine.py` lists it in
`KEPT` (Daniel's ruling of 4 Oct: a superseded version stays only so that old records replay). That rule removed most of the raw
candidates.

Two facts constrain every change below. First, a primitive's descriptor entry is only its id and port types
(`verity/primitives/circuits/codec.py` `_encode_definition`), so moving a primitive to another module changes no digest.
Composites are equally safe as long as the emitted body is unchanged; `superseded_quarantine.py snapshot` and `verify` already
prove that for a whole tree. Second, `verity_vllm/properties/protected.py` treats every file under `R/` except `quarantine/` as
"existing primitives modified", and all of `verity_vllm/*` (fold patterns included) as protected, so every registry or fold
edit goes through vllm-coordinator.

## 1. Duplication

**D1. Boolean twins that re-type their word body.** The Glossary's plan is that each word Definition gets a Boolean "next
version" whose word view is the word one. Three places already write the body once: `R/dsa.py`'s `Ops` (`R/boolean_dsa.py` makes
2 direct `B.call`s), `R/sparse_mla.py`'s `Steps` (`R/boolean_sparse_mla.py` makes 1), and `R/value_inputs.py`, where each
registered-input variant calls the constant version's `.body(...)`. The other Boolean modules copy the word body "line for line",
which their docstrings describe: `R/boolean_attention.py` (`_block` re-types the bodies of `b1`, `fa2_check_inf` and
`fa3_check_inf`), `R/boolean_softcap.py` (19 direct calls), `R/boolean_fp8.py` (43), `R/boolean_norms.py` (34),
`R/boolean_dense_norm.py` (14), `R/boolean_moe.py` (11) and `R/boolean_fp8_moe.py` (9). Both Definitions survive: the Boolean one
is what gets proved, and the word one is its word view and the spec the numpy kernels are registered against. Only the second copy
of the body goes: the word body takes its callees as an ops parameter, and the Boolean version runs that same body with the
Boolean callees. This also matters for what comes next: `TargetProfile` refuses `registered_values` with `ir="boolean"`
(`program/frontend/target_profile.py:301`), so every `value_inputs` variant still needs a Boolean twin, and with the current
pattern each one would be a third hand-written copy.

**D2. The Hopper and FP8 ports of `b1`.** `R/hopper.py`'s `_port` and `_reinstantiate` re-evaluate `b1`'s signature and body code
objects over a copied globals dict, with `_BoundPrims` swapping `AmpereBF16TcDot16` for `HopperBF16WgmmaDot16`. The result is a
second copy of each body under nine new names (`DotBf16Hopper` through `ServeHopper`). `R/fp8.py:569-583` repeats the trick for
`ServeFp8`. The general form already exists in `Serve_v2{GEMM,ATTENTION,NORM}` and the catalog's `GemmCoordinate_v2{DOT}`. The
parameterized forms should survive; the ports stay only because `Family[Serve_v1]` is the certificate of record's program identity
and `ServeHopper_v1`/`ServeFp8_v1` are its ports (`KEPT["Serve_v1"]`). This needs a ruling (R1).

**D3. Ampere-only `_v1` beside a general `_v2`.** `R/b1.py:118-140` defines `DotBf16_v1`, `GemmCoordinate_v1` and `Gemm_v1` with
the Ampere step fixed, while `C/gemm.py` has `_v2{DOT}` (and `C/boolean/gemm.py` has `_v3`). `R/fp8.py:436-480` does the same
thing for the block-scaled GEMM: `ScaledMmFp8Block*_v3{DOT}` equals `_v1` at `DOT=HopperE4m3QgmmaDot32`, and "hopper keeps binding
the v1 forms, so its Programs keep their digests". The b1-eager vocabulary and the GEMM fold pattern still bind `Gemm_v1`, yet
none of these `_v1`s is in `KEPT`. The catalog `_v2` and fp8 `_v3` should survive. In the meantime the `_v1`s belong in `KEPT`,
each with the record that keeps it.

**D4. Two places say which Definition serves a kernel.** The Build rules resolve kernels through one vocabulary
(`program/frontend/rules/vocab.py`, `vocabulary_for(...).kind(role, ...)`). Only one fold pattern does the same
(`observe/fold/patterns/activations.py`, for `silu_and_mul`). The others hard-code their Definition at 9 sites in 7 files:
`gemm.py:165` (`b1.BiasAdd`), `norms.py:71,73` (`b1.RMSNormTriton`, `VI.RMSNormTritonV3`), `rotary.py:89` (`b1.RoPE`),
`embedding.py:49` (`b1.Embedding`), `sampling.py:154,206` (`b1.TokenSelect`), `fp8.py:105` (`fp8.Fp8GroupQuant`) and
`pouw.py:59`. The vocabulary should survive. A new version bound in `vocab.py` is then followed by the fold too, instead of
showing up as a fold-compare mismatch.

**D5. Four registry walkers.** There are four functions that each import "every registry module":
`R/catalog.py` `load` (24 call sites in 14 files), `program/boolean.py` `_load` (which adds `C/boolean/*`),
`tools/circuit_check/src/circuit_check/targets.py` `load_registries` (19 sites in 12 files; it hard-codes 7 catalog and core
modules plus 5 PoUW modules, and then walks `R/`), and `backends/flock/python/verity_flock/boolean_export.py:388` `prims`. The last
one swallows import errors (`except Exception: continue`), so a broken module silently drops out, which is a guard failing open.
circuit-check's cache must name each walker by hand (`cache._ENUMERATORS`, and `tests/test_cache.py:660-690` checks the shape of
each loop). The fix: each distribution exposes one `load()` for its own Definitions (catalog, the vLLM registry, PoUW's circuit),
circuit-check composes them, and `_ENUMERATORS` lists exactly those. Core can't hold the composed loader, because core imports
no other distribution.

**D6. Three constant-word helpers.** `R/boolean_attention.py:42` `_Bits` is imported by six other modules (`boolean_dsa`,
`boolean_fp8`, `boolean_fp8_moe`, `boolean_softcap`, `boolean_sparse_mla`, `mla`) and by one test. `R/boolean_norms.py:95` has its
own class that does the same thing, and `R/gumbel_boolean.py:372` inlines it. The one to keep is a single
`constant_word(B, value, width)` in `verity.primitives.circuits.boolean`, memoized per body, emitting nodes in the same order so
every digest holds.

**D7. Primitives defined in the application.** The README says "core owns every primitive circuit and all silicon semantics".
Even so, about 36 primitives are registered under `R/`. The generic ones should move to `C/scalar.py`, `C/fp32.py` or `C/mufu.py`,
with their Boolean versions in `C/boolean/`:
- `U32And`, `I32Sub` and `F32CeilFtz` (`R/dsa.py:93-125`; 3 files and 7 sites each);
- `Fa3InvSum_v1` (`R/hopper.py:72`; 21 files, 43 sites). Its sibling `Fa2InvSum` is already the catalog's, and
  `benchmarks/numerical/.../bench/templates.py:532` imports it from the integration;
- `DivFullScaleA_v2`, `RopeOut`, `RopeOutAdd` and `SiluMulBf16_v1` (`R/prims.py:65-116`; 14 to 29 files each);
- `F32FmaRm` (`R/moe.py`) and the word gates in `R/topp_word_gates.py`.

`R/pouw_rows.py`'s `Ncp*` primitives are protocol-defined and belong to PoUW's circuit. `R/ref_prims.py` stays where it is,
because its source is hashed into `ref_vocab_digest()` (`ref_prims.py:45,767`).

**D8. FP32 Boolean pieces split across two modules.** `C/boolean/attention.py` holds the FTZ operations, `F32Max` and
`GuardNegInfZero`, and `C/boolean/elementwise.py` holds the non-FTZ ones, so finding `F32MulFtz_v3` means knowing which file
attention happened to need. This is a move-only cleanup.

**D9. Quarantine re-export shims.** The 20 files in `R/quarantine/dense/` re-export Definitions already promoted to `R/dense.py`
(`softcap.py`'s docstring says so); only `quarantine/collective/allreduce.py` defines anything. `superseded_quarantine.py` has run
`PROMOTE` (`R/layer_norm.py` and `R/gelu_erf_table.py` exist) but not `MOVE` (there is no `experimental/vllm/`). That move is
already ruled; it only has to be applied.

**Cross-owner, recorded but not proposed:** SHA-512 compression exists twice, as
`verity/protocols/accounting/work/pouw/circuit/hashes.py:126` `PouwSha512Compress_v1` over 32-bit halves and as
`verity/primitives/commitments/gates/sha512.py:124` `compress_gadget` on bits. That pair belongs to compute-accounting.

**Already consolidated, no action:** the top-p keep word is written once in `R/topp_keep_builder.py` and run by both
`verity_flock.topp_word` and `R/topp_words.py`'s `IREngine`, with `R/topp_split.py` as its numpy oracle. Likewise, the integer
reference (`catalog/verity_catalog/silicon/fp32.py`) and the bit builders (`silicon/fp.py`) are oracle and circuit by design, and
circuit-check compares them.

## 2. Awkward or fragile APIs

**A1. `_port`/`_reinstantiate` (D2).** The better form is binding statics on the parameterized Definitions. These callers would
change:
- inside `R/hopper.py`: 9 ports, plus the `ENV` dict and `_BoundPrims`;
- `R/fp8.py:569-583`: `ENV = dict(H.ENV)` and three `H._reinstantiate` calls;
- consumers of `GemmHopper`: `R/fp8.py`, `program/frontend/gemm_targets.py` and `correspondence/capture_identities.py`;
- consumers of `AttentionFA3`: `program/kernels/fa3_model.py` and `R/fp8.py`;
- `AttnBlockFA3` in `query/word.py`, `FinalHopper` in `R/fp8.py`, and `ServeHopper` in `targets.py` and two tests;
- `tests/program/test_composition.py:173-174`, which asserts `_BoundPrims._over`.

`DotBf16Hopper`, `GemmCoordinateHopper`, `AttentionHeadFA3` and `LayerPreHopper` are reached only through the ports. All of this
waits on R1.

**A2. The registry walkers (D5).** The call-site counts are in D5. One more coupling: C-Flock's
`verity_flock/class_statement.py:421` and `partition_units.py:233` import `circuit_check.targets` just to load the registries, so
a backend depends on the checker tool and, through it, on the vLLM integration. The README says backends are testable without an
integration. The better form is for the caller to pass the registry in, or for C-Flock to call the catalog's `load()`.

**A3. The fold patterns' direct binds (D4).** The better form is `vocabulary_for("profile", numerics).kind(role, ...)`, as
`activations.py:41` already does. There are 9 call sites in 7 files, and every one of them is protected.

**A4. C-Flock patches core and catalog builders in place.** `verity_flock/fp.py` and `gf2.py` alias
`catalog/verity_catalog/silicon/fp.py` and core's `forms` through `sys.modules[__name__] = ...` "so `boolean_export`'s in-place
tracing patches reach every caller". `boolean_export._patch` (`:118-140`) then `setattr`s wrapped functions onto those modules
and onto `C/boolean/softmax.py` and `C/boolean/scalar.py`. circuit-check triggers this in-process (`checks.py:320` and `:680`), so
from its first such target onward every builder in that process runs wrapped. The functions compute the same thing, but
circuit-check's cache records the modules that run. The better form is for core's `trace` to offer a named-region hook that
`boolean_export` subscribes to. That needs a small core API (circuits) and the switch in C-Flock (proofs).

**A5. `targets._boolean_roots`.** This one function (`targets.py:314-390`) binds about 60 roots from 15 modules, behind a 30-line
docstring, and it is a single cache unit. `cursor/circuit-check-bindings-per-module-8c79` (head `fffd62a83`, not in `b87eeef64`)
replaces it with one sidecar per Definition module, where each binding is its own unit. Its migration script and tests are
written. Landing that branch is the better form; nothing new needs to be built.

**A6. A family special-cased by id prefix.** `checks.py:422` sends `TopPMaskWordx*` to C-Flock's `topp_word` by matching the id
prefix. The better form is for C-Flock to register a family lowering beside `ir_lower.PIECES`. Only this one site changes.

**A7. `pins.json` has no stale check.** `known.KNOWN` has `stale()`, but `pins.json` has nothing like it. Its `pieces` section pins
`AmpereBF16TcDot16_v1`, an id that nothing registers. C-Flock still names it in `ir_lower.py:91,395`,
`boolean_export.py:1081` and `tests/test_ampere_dot_ids.py`. The better form is for `circuit-check --all` to report pins that no
target read. The other keys that don't resolve in `pins.json` are lazy or on-demand families (`GatherBf16x*`, `BitAtx*`) and
template unit ids, and they are fine.

**A8. Hand-listed catalog imports.** `load_registries` imports 7 catalog and core modules by hand. Today the list is complete only
because of transitive imports (`C/mufu.py`, `C/scalar.py` and `C/fp32.py` are reached that way), and no test enforces it. The
`load()` from D5 closes this.

## 3. Dead code (each checked with `rg` over the whole tree outside `archive/`)

- **`F32Sub_v2`** (`R/prims.py:116`) and **`F32FmaRm_v2`** (`R/moe.py:109`). No rule, fold pattern, composite or kernel calls
  either one. Only C-Flock's `tail_pieces.py:596-597`, `backends/flock/tests/test_ir_lowering.py:91` and circuit-check fixtures
  (`tests/fixtures/attention_split_facts.json`, `tests/fixtures/split/prims_serve.json`) name them. Deleting them is a `DELETE`
  entry with its `Retirement` in `superseded_quarantine.py`, and it touches proofs' `tail_pieces.py`.
- **The eight `PouwSha512{Big,Small}Sigma{0,1}{Hi,Lo}_v1`** (`verity/protocols/accounting/work/pouw/circuit/words.py:98-101`).
  They have no callers; only `attention_split_facts.json` names them. They belong to compute-accounting.
- **Unread module-level names in `R/`.** Each appears only in its own file:
  - `b1.py:66` `SMOL360_CONFIG` and `:1143` `FACTORED_COMPOSITES`;
  - `b1_tp2.py:386,393` `TP2_COMPOSITES` and `TP_N_COMPOSITES`;
  - `boolean_dsa.py:225` `BOOLEAN_DSA` and `boolean_sparse_mla.py:66` `BOOLEAN_SPARSE_MLA`;
  - `dsa.py:131,393` `DSA_PRIMITIVES` and `DSA_COMPOSITES`;
  - `fp8.py:482` `FP8_BLOCK_COMPOSITES`, `fp8_moe.py:224` `FP8_MOE_COMPOSITES` and `sparse_mla.py:198` `SPARSE_MLA_COMPOSITES`;
  - `hopper.py:59-61` (`HOPPER_WGMMA_K`, `_WIDTH`, `_ZERO_EXPONENT`) and `:157` `HOPPER_PRIMITIVES`;
  - `lifted.py:637` `CONTINUATION_FAMILIES` and the helper `lifted.py:1408` `_lifted_weights_type`;
  - `moe_pad.py:118` `FIXED_SELECT_MEMBER` and `spec.py:37` `DRAFT_CONFIG`.

  None of them is read through `getattr` or a name pattern.
- **Dead names in `R/ref_prims.py`** (`_widen1`, `_narrow1`, `PROFILE_ADDITIONS`; lines 315, 319 and 751). These are dead too, but
  editing that file changes the reference vocabulary's digest, so they go only with a `REF_VOCAB_VERSION` bump.
- **Checked and not dead:**
  - `RMSNormFusedCuda_v1` and `Serve_v2` (both in `KEPT`, with the records that cite them).
  - The `boolean_attention` `Attention_v6`–`v9` and the `boolean_fp8` and `boolean_fp8_moe` tops, which have no name references
    but are found through their `word` links.
  - The allowlists `tests/lint/allowlists/p01`–`p12`, `by_name_allowlist.json` and `dead_code_keep.json`: every path in them
    exists, and `p10`/`p11` hold no stale Definition ids.
  - `known.KNOWN`'s single entry, `ScaledMmFp8Block_v1`, which still fails as documented.
  - There are no `sidecars` or `migrate_bindings` in `tools/circuit_check/` at `b87eeef64`; they exist only on the unlanded branch
    from A5.

## 4. Ranking (value against risk)

| # | Change | Value | Risk | Code it touches |
|---|---|---|---|---|
| 1 | Land the per-module sidecars (A5) | high | low | circuits |
| 2 | Report stale pins and drop the `AmpereBF16TcDot16_v1` pin (A7) | medium | low | circuits; proofs for the C-Flock alias |
| 3 | Delete the unread names in `R/` from section 3, keeping `ref_prims` | low | very low | circuits; vllm-coordinator |
| 4 | Add the `_v1`s from D3 to `KEPT`, each with the record that keeps it | medium | very low | circuits; vllm-coordinator |
| 5 | One `constant_word` in core, replacing the three helpers (D6) | medium | low | circuits; vllm-coordinator |
| 6 | One `load()` per distribution; C-Flock's `prims()` fails closed; no backend imports circuit-check (D5, A2, A8) | high | medium | circuits; proofs; vllm-coordinator |
| 7 | Fold patterns resolve through the vocabulary (D4, A3) | high | medium | vllm-coordinator; circuits |
| 8 | Move the generic primitives into the catalog (D7) | medium | low to medium | circuits; vllm-coordinator; benchmarks |
| 9 | Apply `superseded_quarantine.py`'s `MOVE` (D9) | low | low | vllm-coordinator (already ruled) |
| 10 | Shared bodies for the Boolean twins, starting with softcap and its 4 Definitions (D1) | high | medium to high | circuits; vllm-coordinator |
| 11 | A region hook in `trace`, replacing `boolean_export._patch` (A4) | medium | medium | circuits; proofs |
| 12 | Route `TopPMaskWordx` through a registered family lowering (A6) | low | low | circuits; proofs |
| 13 | Retire `F32Sub_v2` and `F32FmaRm_v2` (section 3) | low | low | circuits; proofs; vllm-coordinator |
| 14 | Retire the ports and the D3 `_v1` forms, rebinding to the parameterized forms (D2, D3) | high | high | circuits; vllm-coordinator; needs R1 |
| 15 | Regroup the FP32 Boolean pieces (D8) | low | low | circuits |
| 16 | PoUW's dead sigma words and its second SHA-512 | low | low | compute-accounting |

How each change is verified:
- Every change except 14 keeps every digest. Run `superseded_quarantine.py snapshot` before and after and `verify` the two, then
  run `circuit-check --all` and `check`.
- Item 7 must also keep the fold's outputs byte-identical on the golden captures (`verity_vllm/check/fold_compare.py`).
- Item 10 should go one family at a time, because each family is a large diff in protected files.
- Item 6 changes `cache._ENUMERATORS`, so circuit-check's cache schema has to be bumped and every pass recomputed once.
- No change here touches Lean. lean is affected only if R1 re-records a certificate of record.

## 5. What needs Daniel's ruling

**R1. Can a version kept for its digest retire?** Several `_v1` composites are the same function as their successor at one
static: `Gemm_v1` equals `Gemm_v2{DOT=AmpereBF16TcDot16}`, `ScaledMmFp8Block_v1` equals `_v3{DOT=HopperE4m3QgmmaDot32}`, and the
Hopper and FP8 ports are copies of `Serve_v1`. May they retire by re-recording the Programs and goldens that name them under the
new id, or must every record of record replay under its original id forever? My recommendation: keep them while a certificate
of record cites them, list them in `KEPT` now (item 4), and rebind at the next certificate bump.

**R2. What happens to word Definitions in the end state?** The Glossary says the word library "migrates to Boolean Definitions
under new versions of the same names". It doesn't say whether the word Definitions then go. My recommendation: they stay, as the
word views and as the spec the kernels are registered against, but each body is written once (D1). A related question is when
`TargetProfile.ir` defaults to `"boolean"`, which is the precondition for retiring any word-only path.

**R3. May a backend import circuit-check or the vLLM registry?** C-Flock's `class_statement` and `partition_units` do today (A2).
My recommendation: no. They should take a loaded registry as a parameter, which this ruling would turn into a boundary test.

**R4. Does "core owns every primitive circuit" cover generic ops the integration defines?** My recommendation: yes for generic
integer and float ops (D7). Protocol-defined primitives go to their protocol's circuit (`pouw_rows`' `Ncp*` to PoUW), and
`ref_prims` stays pinned in the integration.

**R5. Can a proved digest-neutral registry edit skip vllm-coordinator's gate?** Today `protected.py` classifies any change under
`R/` as "existing primitives modified". Items 3, 5 and 8 change no digest, and `superseded_quarantine.py verify` proves that
mechanically. Should such a diff still need vllm-coordinator's gate? This is a process question, and the process-design skill
applies to it.
