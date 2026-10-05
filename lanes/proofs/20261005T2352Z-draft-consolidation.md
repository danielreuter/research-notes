---
id: proofs/20261005T2352Z-draft-consolidation
campaign: proofs
lane: proofs
kind: draft
status: draft
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-f0aa5078-b63e-575e-a74c-57a80534363c
---

# Consolidation: proofs' code (C-Flock, its Lean, one-stage and sampled proofs, the profile, frozen backends)

I read the code at `b87eeef64` (the Lean layout move, PR #1225, landing about 5:05 PM PDT) in a worktree, along with
@proofs' in-flight stack and the recursion branches. I changed no code. Every count below comes from `git grep`/`rg`, the
lock (`verity/Security/lean-audit.json`), `tools/check/ci.toml`, or the store's manifests. Times are PDT.

## The short version

- **The biggest consolidation is already built and waiting.** `cursor/verifier-fail-closed-95d4` →
  `cursor/flock-lock-reduction-95d4` implements your Oct 4 one-theorem ruling. It pins one
  `FailClosed.flock_verify_sound` and takes @proofs' lock from 831 pins to 41 (16 that Table 1 and the code rely on, 24
  Partitioning pins for compute-accounting, plus the theorem), deleting 46.7k lines of lock. It sits on the *first* layout
  move (`378453fb3`), not `b87eeef64`'s `verity/Security/Proofs/Flock/` layout, so it needs one more `tools/move/layout.py`
  restack before it can land.
- **Its sibling stack will undo the trim if it lands unchanged.** `cursor/canonical-v1-95d4` → `cursor/canon-pubin-95d4`
  was recorded before the trim and carries 796 and 797 pins. Whichever stack lands second must re-record under the
  41-pin policy.
- **Most of the Lean "duplication" is a variant ladder, not copies.** There are 78 pinned variants of the session, e2e and
  headline theorems, one per accepted statement form: unsalted vs `hm96-sha512/v1` leaves (`_L`), J tables, hidden outputs
  (H), registered (R), and custody vs records-live (`_json`). No two pinned guarantees share a statement hash.
  `flock_verify_sound` cites the unregistered session forms and the executable headlines directly, one case per accepted
  form. The ladder shrinks only when the verifier stops accepting old forms, which needs your ruling (R1).
- **Real copies are small** (§1). On the Python side, the cheapest real win is making the flock suite fail closed. The
  biggest deletable mass is the six pipelines that predate `flock-circuit` and have no verifier of record (§3).

## Ranked changes (value against risk)

| # | Change | Value | Risk | Owner | Needs |
|---|---|---|---|---|---|
| 1 | Flock suite fails closed: drop the 7 import-guard `skipif`s in `test_lean_verifier.py` and the 20 `importorskip`s on hard dependencies (§2a) | High: a broken install passes silently today | Low: tests only | proofs | nothing (tests are outside queue.toml's grant) |
| 2 | Restack fail-closed → lock-reduction onto `b87eeef64`'s layout, re-record, and land | Very high: your one-theorem ruling, lock 831 → 41 | Medium: restack and re-record; changes the verifier of record | proofs | red team on the restacked head; a statement reviewer for changed records; `lean-agreement` |
| 3 | After #2, re-record canonical-v1 / canon-pubin under the 41-pin policy (canonical headlines become cases of `flock_verify_sound`, not pins) | High: otherwise about 750 pins come back | Low | proofs | a statement reviewer |
| 4 | Close `rec-v0` and `rec-algebra`; have `rec-sound` reuse main's lemmas (§5) | Medium | Low | proofs (recursion) | nothing |
| 5 | Retire the pipelines that predate `flock-circuit`: pure, link, vllm-v1, ir-frame, ir-sampling and ir-block, plus `key_class_sets.py` and `arch_proto/` (§3) | Medium-high: 13 of 23 pod scripts, 8 of 10 Rust bins, three `verity_flock` modules, seven templates' `stage` functions | Low-medium: keep `20-gpu-link.sh MODE=build` and `bench.py`'s shared helpers | proofs; one line in `benchmarks/numerical` | a `circuit-check` report for the templates touched; tables read the store |
| 6 | Delete the true Lean copies (§1) | Low-medium | Low: no pinned statement changes after #2 | proofs | nothing (a statement reviewer only if a record changes) |
| 7 | Fix check's plumbing around the verifier (§2b): the `GB_PER_PROCESS` regex, `unit_cut_agree` run twice, 28 `lake build`s per suite, bare `python3` | Medium: faster and less fragile `check` | Low | proofs + `tools/check` (shared) | nothing |
| 8 | Replace `boolean_export`'s global monkeypatch and the `sys.modules` shims with an explicit tracing context (§2c) | Medium | Medium: touches lowering | proofs + circuits (`circuit_check.checks` calls `boolean_export`) | a `circuit-check` report |
| 9 | Stop private imports from `verity_vllm`, and move `ligero.timing_guard` out of `archive/direct`: the live circuit cell imports it through a `sys.path` hack (§2d) | Medium | Low-medium | proofs + vLLM lane | nothing |
| 10 | Retire historical statement forms with their replay sets, upstream binaries and vectors patches (§4) | High | High: verifier of record, wire format | proofs | **R1**, red team, `lean-agreement` re-pin |
| 11 | `suites.py` closure follows the root's `dev` group, so most suites' inputs include `backends/flock` and `archive/sp1` (§6) | Medium: cache misses across the tree | Medium | `tools/check` (shared) | nothing |
| 12 | Move or drop the `verity_sp1.proofs` helpers that active tests still import; then `archive/` is evidence only (§6) | Medium | Low | shared (core, catalog, vLLM, numerical tests) | coordinator |
| 13 | Fix stale docs: `archive/README.md` lists `flock/` and `numerical/` as if they were inside it; `backends/flock/README.md` says check runs no live Rust tests (`flock-rust-tests` does) | Low | None | proofs | nothing |

## 1. Duplication, and which copy survives

**The variant ladder (pinned).** Pinned variants by family:

- `zk_session_sound*`: 15 (base, J, H, HJ, R, HR, HJR, each with `_custody` and some with `_json`);
- `flock_e2e_count*` and `flock_e2e_drawn*`: 27, across Partition, Binding, CROnly, Prog, Registered and UProg, with
  `_exec`, `_hm96` and `_reads` forms;
- `flock_headline*`: 12;
- `zk_flock_count*`: 13.

Each is a different statement. For example, `Prog.flock_headline_L` is `Prog.flock_headline` "restated for the session
whose leaves are `hm96-sha512/v1`'s" (`HeadlineL.lean`), and `zk_session_soundJ_custody_json` replaces
`RecordCustodyZKJ` with `RecordsLiveZKJ` plus a draw-JSON hypothesis. `FailClosed/*.lean` cites 18 of these names
directly: the session forms base, J, H and HJ, each with a `_custody` form (J and HJ also with `_custody_json`);
`composed`, `composedHJ`, `view` and `viewHJ`; and the four `flock_headline_exec*` forms. The registered forms
(`zk_session_soundR`, `HR`, `HJR`) are not cited; registered reads appear only in its scope check.

The docs cite the oldest forms. `ASSUMPTIONS.md`, the Soundness README and `e2e-checklist.md` name `Prog.flock_headline`,
`CROnly.flock_headline` and `flock_e2e_count_hm96_reads`, while the newest (`zk_session_soundHJR_custody`) is cited
nowhere outside Lean. Fail-closed's doc commit (`8d4561fc3`) already rewrites "What is pinned".

Survivor: `flock_verify_sound` as the one guarantee (#2). The per-form theorems stay as unpinned lemmas until R1 retires
their forms (#10).

**True copies** (#6; after #2, so as not to conflict with the restack). Each is identical text:

| Copy | Survivor | Remove |
|---|---|---|
| `drawOkZKHJ_of_file`, about 95 lines; neither file imports the other | `Discharge/ZkHidden/CustodyJ.lean` (pinned today) | `Discharge/ZkReg/SoundHJCustody.lean`'s; import ZkHidden's |
| `avg_sqrt_le` | `Soundness/Compiled.lean:93` | `avg_sqrt_le'` in `Game/Lock.lean:388` (rec-sound would add a third, §5) |
| `dot_eq_foldl`, `lagrange_size` | `Refine/Arith.lean` | `Discharge/Composed/Inner/Zerocheck.lean`'s |
| `rank_inj`, `rank_div_lt` | `Discharge/Integrate/Sites.lean` | `Discharge/HiddenExec/Tables.lean`'s (it already imports Sites) |
| `setupHidden_{tags,hm96,wf,drawn}`, `parse_untyped` | `Discharge/Hidden/Facts.lean` | `Discharge/HiddenExec/Setup.lean`'s aliases (three cite Hidden's; two re-prove) |
| `tabAt`, `table`, `refused` | one definition over the setup | the four copies across DrawSetupZ, ZJ, ZH and ZHJ |

Smaller near-copies (`avg_sum` ×2, `avg_prod*` ×3, four `ite_throw_ok*`, `ebind_ok`/`except_bind_ok`,
`testBit_sumBits`/`sumBits_testBit`) are a sweep, not a plan item.

**Checked; not duplication:**

- Partitioning's `Witness.lean` restates each guarantee and proves it by citing `SecurityProofs/*/Witnesses.lean`. That is
  the facade pattern, and lock-reduction keeps those pins.
- Level3's `GF128.lean` proves facts about the executable's `Flock/Field.lean` (it imports it); it is not a second field.
- The one-stage `draw.py` (stratified and work draws over proof units) and experimental's `law.py` (the two-stage law)
  are different laws. Experimental's LEGACY `ru_key` and `vu_key` are still imported by vLLM's
  `commit/challenge.py`, so they stay until vLLM's re-baseline (decision 42).

## 2. Awkward or fragile APIs, the better form, and every caller

**a. Fail-open skips in the flock suite (#1).** In `backends/flock/tests/test_lean_verifier.py`, seven guards
(`_has_unit_cut`, `_template_vectors`, `_one_stage_draw`, `_has_check_cut`, `_qword_vector_file`, `_qword_vectors`,
`_format_vectors`) wrap core imports in `try/except ImportError` and skip on failure. Those functions have been in core
since PRs #111 and #131.

Twenty `pytest.importorskip` calls guard `verity_vllm.program.registry(.prims)`, `verity_numerical`,
`verity.primitives.circuits.units` and `verity_flock.class_statement`. Callers: `test_boolean_export`, `test_circuit`,
`test_class_statement`, `test_class_statement_redteam_1178`, `test_derive`, `test_flock_rows`, `test_ir_lowering`,
`test_ir_sampling`, `test_lean_registered_reads`, `test_lean_rope`, `test_lean_typed_statement`, `test_lean_verifier`
(×2), `test_partition_units`, `test_stage_typed`, `test_typed_statement`. `verity-vllm` and `verity-numerical` are in
`verity-flock`'s `dependencies`, so each of these skips can only hide a broken install.

Better form: import directly. Keep `shutil.which("lake")` as the only environmental skip; the check pod has `lake`
(`lean-build` runs there), so it never fires in `check`.

**b. Check's plumbing around the verifier (#7).**

- `check.py`'s `session_jobs` reads `GB_PER_PROCESS` by regex over `verifier/ci.py`'s source. Import it, or move it into
  `ci.toml`.
- `unit_cut_agree.py` runs twice per check: as the `lean-unit-cut` job, and again in pytest
  (`test_unit_cut_agrees_with_the_reference`). Drop the pytest copy.
- `test_lean_verifier.py` calls `lake build` 28 times. Use one session fixture, or rely on `lean-build`'s binary.
- `test_lean_verifier.py` runs the agree scripts with `"python3"` 10 times, not `sys.executable`. Elsewhere `agree.py` is
  loaded through `importlib.util.spec_from_file_location` (`check.py`'s `upstream_smoke`) and `sys.path` imports
  (`ci.py`: `import agree`). Make `verifier/` a module, or keep the scripts and call them uniformly.

**c. `boolean_export`'s tracing (#8).** `boolean_export._patch()` `setattr`s over `gf2`, `fp`, SM, SC, U, IL, TP and TW.
It is permanent, guarded by a `_PATCHED` global. Four shims (`fp.py`, `gf2.py`, `unit.py`, `unit_fp4.py`) do
`sys.modules[__name__] = <core or catalog module>` "so `boolean_export`'s in-place tracing patches reach every caller".
Import order therefore changes behaviour process-wide.

Better form: pass a tracing context (or a recorder argument) through the lowering, and delete the shims. Callers:

- The shims are imported by 13 `verity_flock` modules (`boolean_export`, `circuit_types`, `class_statement`, `ir_lower`,
  `ir_sampling`, `lowering`, `partition_units`, `sha512_circuit`, `tail`, `tail_pieces`, `topp_word`, `type_trace`,
  `typed_statement`), by `unit_fp4_check` and `arch_proto/step_template.py`, and by 12 flock test modules.
- `boolean_export` itself is called by `type_trace`, `test_boolean_export`, `test_ir_lowering`, and circuits' own
  `circuit_check.checks` (line 320). So #8 touches the circuits lane's tool as well.

**d. Cross-component reach-ins (#9).**

- **The live circuit benchmark depends on a frozen backend through a path hack.** `circuit_bench.py` (the
  `61-circuit-cell` sweep) calls `bench._guard()`. That calls `instances._ligero()`, which puts
  `_DIRECT = parents[4]/"archive"/"direct"` on `sys.path`, then imports `ligero.timing_guard`. Better form: move
  `timing_guard` (the CPU-quota and GPU-context guard) into `verity_flock` or the numerical bench. The rest of
  `instances.py`'s `ligero` use (B-Ligero's synthetic sets, `vllm_tree`) goes with #5.
- `verity_flock` imports `verity_vllm.program.pipeline.program_graph`'s private `_encoded` and `_word_values`, plus
  `verity_vllm.program.registry`, `.kernels` and `verity_vllm.query.word`.
- `tests/test_backend_boundaries.py`'s `KNOWN` set lists 30 backend → integration sites, and it may only shrink. Making
  the two private names public in `verity_vllm` (vLLM lane) removes the worst two.

## 3. Dead code to remove (#5)

The pipelines before `flock-circuit` are pure, link, vllm-v1, ir-frame, ir-sampling and ir-block. Their statements
(`verity/flock-pure-block`, `flock-vllm-block`, `flock-ir-frame/v3`) are not forms the Lean verifier accepts, so they have
no verifier of record. In the store, no `research run` has invoked their pod scripts since about Sep 27. Their table rows
are read from stored results (`verity_numerical.bench.frozen`, the drilldown), so the tables don't change.

What would go:

- **Rust:** 8 of `live/src/bin`'s 10 bins (`flock-gpu-link`, `flock-ir-block`, `flock-ir-frame`, `flock-ir-sampling`,
  `flock-link`, `flock-pure`, `flock-pure-gpu`, `flock-vllm-v1`; keep `flock-circuit` and `flock-live`), and
  `lib.rs`'s `ir_frame`, `ir_sampling`, `pure_block` and `vllm_block`. Only `flock-rust-tests` compiles them today.
  `check_build.sh`'s test mode already notes that `flock-pure-gpu` and `flock-gpu-link` "predate the SHA-512 patch".
- **Python:** `ir_frame.py`, `ir_sampling.py` and `ir_bench.py`; the `stage` functions of seven templates
  (`attention_head`, `gumbel_top_p_token_select`, `rmsnorm_fused_cuda`, `rmsnorm_triton`, `rope_head`, `silu_mul`,
  `gemm_coordinate`), which write frame-v3, ir-sampling or pure instance files, whereas the circuit cell stages through
  `circuit.stage`; `tool.py`'s `FLOCK_PURE`; and their tests. `bench.py` and `instances.py` shrink rather than go:
  `circuit_bench.py` imports `bench.py`'s guard, probe, quota and sampler helpers, and `register.py` imports its
  `PER_PROOF_LOG2`. `negatives.py` and `gemm_coordinate.stage` write pure instance files and go with the pure pipeline.
  The templates' lowerings stay; attach a `circuit-check` report showing the circuits are unchanged.
- **Pod scripts:** `10-link`, `20-pure`, `21-gpu-link-sweep`, `22-pure-gpu`, `23-ir-block`, `30-cell`, `31-replay`,
  `33-ir-cell`, `34-ir-{replay,sampling,selftest}`, `40-vllm-v1` and `50-preflight` (which builds `flock-pure-gpu` and
  `flock-vllm-v1`).
- **Numerical bench:** `c_interactive.py`'s `SCRIPT` and `IR_SCRIPT` entries. Keep `CIRCUIT_SCRIPT` (`61-circuit-cell`).
- **Unreferenced:** `key_class_sets.py` (no references anywhere), and `arch_proto/` (no job, test or pod script runs it).

Keep `20-gpu-link.sh MODE=build`, the patches and `cuda_*_patch.py`. `60-circuit.sh` builds through it, and
`70-class-sweep.sh`, `76-read-gadget.sh` and `benchmarks/private_circuit/pod.sh` hash it into their cache keys. Its build
line compiles `flock-gpu-link` and `flock-pure-gpu`, so first check whether `60-circuit.sh` needs either; if not, drop them
from the build.

## 4. The agreement check covers no current statement (#10, R1)

`vectors.json`'s 17 replayable sets and 6 live sets are all at historical tags (`@19c7269a`, `@fd02e847`, `@631567f7`,
`@eb90718f`, `@e51e2b86`, `@967b8d06`; plus `/types@210d32e1` in `Tags.lean`). Its own note says main's
`flock-circuit` "has no replay subcommand and the vectors patch no longer builds against it".

So `lean-agreement` cross-checks the Lean verifier against upstream only on forms that M0 no longer emits. Statements M0
emits today get Lean's own tests and nothing from upstream.

`Tags.all` lists 16 forms. M0 emits 4 (`verity/flock-circuit` and `verity/flock-circuit/types`, each with its
`+seed-injection` selftest form; `live/src/circuit.rs`'s `STATEMENT`). The other 12 (`netlistV1` and the `@`-tagged
forms) are historical, and `upstream.json` pins 8 binaries with 4 circuit-vectors patches plus `netlist-vectors.patch` to
replay them. The current forms are defined as `{ circuit967b8d06 with … }`, so retiring the old ones means inlining those
fields first.

Proposed order:

1. Record replay sets at the four current forms (and canonical v1 once it lands), with a replay patch against the
   pinned upstream build.
2. Then, under R1, refuse the historical forms. Fail-closed makes that a completeness limit, not a soundness gap.
3. Delete their `Tags.lean` entries, replay sets, binaries and patches, and the per-form lemmas only they use.

## 5. Recursion branches

- `rec-v0` (`cbad2989e`) and `rec-algebra` (`d4c745660`) are ancestors of `rec-reprice` (`454e3cd86`): no unique commits.
  Close both.
- `rec-reprice` is 39 commits ahead of `b87eeef64`; land it as the survivor. rec-v0's merkle and sha512 gates are already
  on main.
- `rec-sound` (`075e10e0b`) has 32 unique commits on pre-move paths, and touches 355 files from its merge base. On its
  restack, it should reuse main's `avg_sqrt_le` and the StrictCR / `Game/Lock` / Rewinding fork and plurality lemmas
  rather than add its own; its `/tmp` extracts show a third `avg_sqrt_le` variant. Its 5 `Recursion.Stage` pins should
  follow the 41-pin policy.

## 6. Archive and shared tooling

- **Frozen backends.** Everything in `archive/` feeds the tables only through stored evidence. The one live dependency is
  `verity_sp1.proofs` (the old core `verity.proofs`), still imported by core, catalog, vLLM and numerical tests. Move
  those helpers to their owners, or drop the tests (#12); then `archive/` is evidence only and can leave the workspace's
  `dev` group.
- **`suites.py` closure (#11).** `closure()` / `_requires()` follow dependency groups, and the root `dev` group lists
  verity-sp1, verity-flock, verity-numerical, verity-vllm and others. So most suites' inputs include `backends/flock` and
  `archive/sp1` (confirmed with `--list`). Per-test reuse softens it. The fix is to follow only `[project] dependencies`
  for a suite's inputs.

## Rulings for Daniel

- **R1. When canonical v1 lands, does the Lean verifier stop accepting the historical statement forms?** These are the
  12 of `Tags.all`'s 16 forms that M0 no longer emits, and the session forms behind the J, H, R and unsalted variants.
  - **Recommend yes, in the order in §4.** It is consistent with your Oct 4 ruling: refusing an unproved or retired form
    is a completeness limit.
  - Old recorded verdicts stay in the store as evidence, and re-verifying an old run would use the pinned old build.
  - This decides whether #10, the ladder's per-form lemmas, those 12 `Tags.lean` entries and the 8 upstream binaries can
    go.
- **R2. Must `lean-agreement` keep cross-checking against upstream once upstream can no longer replay current forms?**
  - Recommend yes. Record current-form replay sets with a replay patch (step 1 in §4) before retiring the old ones;
    otherwise the gate checks nothing current.
  - The alternative is to drop the gate and rely on the Lean verifier (the verifier of record) alone. That is cheaper,
    but it removes the only independent check on the executable.

Already ruled, so not asked again: trimming the lock to guarantees something relies on. This is your guarantee ruling,
which lock-reduction cites in `b2bc91cd0` and `913f3b052`; #2 and #3 only land it. Proofs will go ahead with #5
(retiring the pipelines with no verifier of record, keeping their table rows from the store) unless you object: it
touches only proofs' code and one numerical driver line.
