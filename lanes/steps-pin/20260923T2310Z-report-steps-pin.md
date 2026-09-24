---
lane: steps-pin
kind: report
created: 2026-09-23T23:10Z
status: final
---

CHECKPOINT f2a74128 (23:53Z) [final] FINAL tip f2a74128: H1/H2 closed in Rust + Python (Relation.steps/k_ops for 25 relations, Ajtai steps<=n every mode, v5 K=1536 every mode, Python RelationHooks.steps/max_steps + layout_error + v5 K). All must-rejects refused; honest fixtures + R2 art:2c8d5089/527e99be accepted; no digest changed. Integration entries for blake3/share-logup/fp4-decode in the report. Pod terminated (~$0.51).
CHECKPOINT f2a74128 (23:46Z) [open] tip f2a74128: v5 K bound revised to K=1536 (fp4+poseidon2 from lane/fp4-decode-3 writes 24x64, verified its fixture accepts pinned with its pin, steps12 refused). R2 art:2c8d5089 / art:527e99be 13/13 pinned old+new Rust, Python accepts 4 subs on pod. Report body written (audit table, negatives, integration entries). Running Python regression (6 groups) on pod at tip.
CHECKPOINT b7453317 (23:36Z) [open] Rust+Python fix in (tip b7453317). Negatives: red-team collide n64/n128 + n64 steps32 refused both verifiers; forged real steps32 fp8-ada bare (old binary ACCEPTED pinned, now refused) and +poseidon2 (already refused by sys_id); header rewrites of steps/K per family. Python steps_pin_test 25/25 on pod, cargo 31+7+23. Next: R2 honest dumps re-accept, report.
CHECKPOINT c5cf7f6d (23:26Z) [open] Rust fix committed c5cf7f6d (Relation.steps/k_ops all 25, Ajtai steps<=n every mode, v5 K bound; red-team fixtures refused, cargo green). Python fix written (RelationHooks.steps/max_steps + protocol.layout_error, v5 K check in verify_files), bootstrapping 4090 pod i0q2rifehiltnd for torch tests + honest/negative dumps.
CHECKPOINT 47d191e2 (23:12Z) [open] H1 reproduced on base 47d191e (7 red-team fixtures accepted pinned); audit done in code (steps unbound everywhere, v5 K/k_ops unbound, rest bound); implementing Relation.steps/k_ops pins in relation.rs + leaf structural bound + Python RelationHooks.steps
CHECKPOINT 47d191e2 (23:08Z) [open] started; worktree lane/steps-pin @ 47d191e; auditing statement fields in verify.rs/relation.rs/leaf.rs + Python verifier
# steps-pin — bind statement.steps (and every other layout field) to the pinned relation (H1 BREAK / H2 BLOCKING)

Worktree `~/projects/verity-main-wt/steps-pin` on `lane/steps-pin`, base 47d191e (lane/ajtai-leaf-3 tip: leaf-iface + ajtai + G1 fix).
Pod: RTX 4090 `i0q2rifehiltnd` (torch prover / Python verifier only).

## Audit (Rust `backends/ligero-verify`, Python `backends/direct/ligero`)

"Proof" = absorbed in the statement digest (Fiat-Shamir / the column challenge), so it cannot change after proving, but
the prover picks it.  "Pin" = fixed by the relation the statement names plus its pinned system.  Before = 47d191e.

| statement field | what the verifiers derive from it | bound before (47d191e) | bound now |
|---|---|---|---|
| relation name (v4/v5 string; v2/v3 = bf16-ampere) | R `relation::for_statement` -> decode, widths, tag, pins; P `serialize._runner` picks the runner, `verify_files` compares it | pin (system gate on sys_id / table digest; `rel.tag` + sys_id in the digest) | same |
| leaf scheme (v5 `+<leaf>` suffix) | R `hash_auth.leaf` -> digest_elems, table width, `gate(rel, leaf)`, Ajtai key check; P `HashedRelationRunner(leaf=)` | pin per (rel, leaf) (`hashed_sys_id`, ajtai pins) | same |
| digest lanes (digest_elems, table cols 1 + 2d) | derived from the leaf scheme, never read from the statement; the table shape is checked at parse | leaf name | same |
| Ajtai n | from the leaf name (`ajtai-n64` / `n128`); the key rows re-derived from the tag (G1) | leaf name + pin | same, plus steps <= n (below) |
| **steps** (columns per VU) | R chain test + public table + auth ranks + `parse_v5` (k_ops = K / steps); P `Layout(l, n_vus, steps)` | **nothing** for bare and Ajtai: those systems are column-uniform (the bare fp8-ada system at steps 32 is byte-identical to the pinned one). Poseidon2: indirectly by the pin (its hashed system depends on steps: sys_id 2e3c6c39 at 32 vs pinned c4c4b403) | **pin**: `Relation.steps` (Rust, pinned verify) / `RelationHooks.steps` (Python, always); **leaf bound**: Ajtai steps <= n in every mode, both verifiers |
| **K** bare v2/v4 (operands per unit, `k_ops`) | R decodes read `k_ops` words per unit; in the digest as `k` | implicitly, by the decode functions' own K checks | explicit `k_ops == Relation.k_ops`, every mode |
| **K** v5 (words per committed row) | R `k_ops = K / steps`, reported only; **not in the statement digest** (the digest's `k` is the table width); P read and dropped | **nothing** (47d191e accepted an fp8-ada+hash statement claiming K = 768 pinned) | K == 1536 (`relations.K_VU`, what `serialize._K_of` writes for every relation) in every mode, both verifiers |
| n_vus | chain ends, public table, auth ranks; `n_vus x steps <= l` | proof + layout check (prover-chosen batch size) | same |
| l, n, D, t, t_pad, target, zk, mode, n_proofs | Ligero configuration; R `check_config` + soundness floor (`--soundness-bits`); P `config_for` | proof + the verifier's soundness floor (per-proof prover choices) | same |
| rows M / committed rows | from the system file (`sys.m`, zk pad), never from the statement | pin (sys_id) | same |
| word_bytes / y_bytes | R `widths_ok` vs the relation; P hooks dtypes (absorbed) | relation | same |
| y16 range, chain-end components | R `rel.y_bits`, `check_end_components` (every mode); P `y16_bits` | relation | same |
| a / b words, y16, auth block, v5 hash_auth (roots, ranks, multiproofs) | digest + Merkle / multiproof checks | proof | same |

The Python verifier has no unpinned mode: it compiles its own system from the relation, so its checks are always the
pinned ones.

## Fix (verifier-only; no system digest, statement digest or pin changed)

Rust (`check_vu_shape`, called in `verify_inner` right after the system gate):
1. a bare statement's `k_ops == Relation.k_ops` (every mode);
2. `steps <= leaf::max_steps(leaf)` (= n for `ajtai-n<N>`, None otherwise; every mode);
3. `steps == Relation.steps` (pinned);
4. a hashed statement's header K (`steps x k_ops`) `== HASHED_ROW_K = 1536` (every mode).

`Relation.steps` / `Relation.k_ops` for all 25 relations on the base (the unit test
`vu_shapes_are_the_python_registry_and_match_the_decodes` ties them to Python's registry and to each decode):
bf16-ampere / bf16-hopper and their v2 / v3: 96/16; fp8-ada / fp8-hopper and their v2 / v3: 48/32; fp4-nvf4: 24/68;
bf16-* x4 / v2x4 / v3x4: 24/64; fp8-* x4 / v2x4 / v3x4: 12/128.

Python: `RelationHooks.steps` / `.max_steps` (`Relation.hooks`: steps; `HashedRelationRunner`: steps + `AjtaiLeaf.max_steps`
= n; `FP4_HOOKS`: `STEPS`; `vu.ChainRunner.hooks`: 96), `protocol.layout_error` at the top of `protocol.verify` (chain
mode), and `verify_files` for v5: the same layout check, then K (`Statement.row_words`) `== K_VU`.  Same order as Rust.

## Must-reject (all refused now; before = the 47d191e binary / the red-team's recorded Python verdict)

| negative | before (Rust pinned) | Rust pinned now | Rust `--allow-any-system` now | Python now |
|---|---|---|---|---|
| fp8-ada+ajtai-n64 collide P / Q, steps 96 (red-team) | ACCEPT both (Python too) | steps exceeds leaf bound 64 | same | same |
| bf16-hopper+ajtai-n128 collide P / Q, steps 192 | ACCEPT both (Python too) | exceeds bound 128 | same | same |
| fp8-ada+ajtai-n64 steps 32 (red-team) | ACCEPT | steps 32, VU is 48 | K = 1024, row is 1536 | steps 32, VU is 48 |
| fp8-ada **bare** steps 32 (real proof, `steps_pin_forge.py`; system byte-identical to the pin) | **ACCEPT** | steps 32, VU is 48 | accept (no structural bound on a bare unit; verdict says NOT pinned) | steps 32, VU is 48 |
| fp8-ada **+poseidon2** steps 32 (real proof) | refused (column challenge mismatch: sys_id differs) | steps 32, VU is 48 | K = 1024 | steps 32, VU is 48 |
| header K = 768 on fp8-ada+hash | **ACCEPT** | K = 768, row is 1536 | same | same |
| header steps rewrites: fp8-ada 32, b1 32, fp4-nvf4 12, fp8-ada+hash 32, bf16-ampere+hash 32 | refused (digest) | the steps message | refused (digest) | the steps message |
| header steps 96 on fp8-ada+ajtai-n64 | refused (digest) | bound 64 | bound 64 | bound 64 |

Fixtures: `backends/ligero-verify/fixtures/steps-pin/` (the red-team collide pairs + n64 steps 32; `fp8-ada-bare-steps32`,
`fp8-ada-poseidon2-steps32`).  Tests: `tests/relations.rs` `steps_pin_red_team_fixtures_are_refused`,
`steps_pin_forged_steps32_proofs_are_refused_pinned`, `a_statement_whose_vu_shape_is_not_the_relations_is_refused_pinned`;
Python `steps_pin_test.py` (26 tests, 4090 pod, at f2a74128).  Python regressions at f2a74128 on the pod: hashchain_test
14, leaf/ajtai_key_test + ajtai_test 17, relations_test 21, fp4 + fp8 relation_test 22 passed.

## Honest re-accepts

* Rust `cargo test --release`: 31 + 7 + 23, every committed fixture (b1, fp8-ada, fp4-nvf4, fp8-ada-hash, bf16-ampere-hash,
  fp8-ada-ajtai-n64, bf16-hopper-ajtai-n128, the G1 decoy still refused).  The v1/v2/v3/x4 families have pinned systems
  but no proof fixtures; their (steps, K) is tied to Python's registry and to each decode by the unit test.
* R2 dumps, Rust `batch` pinned, 47d191e and f2a74128 binaries: art:2c8d5089 (fp8-ada bare, dev-4090, 13 sub-proofs x 341 VUs) 13/13;
  art:527e99be (fp8-ada+poseidon2) 13/13.
* Python on the pod (f2a74128, cuda): the 7 fixtures above, plus R2 bare sub_00 / sub_05 and hashed sub_03 / sub_06
  (341 VUs, steps 48, K 1536) accepted.
* `lane/fp4-decode-3` fixture `fp4-nvf4-hash` (v5, steps 24, K 1536): the new binary accepts it `--allow-any-system`, and
  pinned once that branch's hashed pin is applied (tried locally, then reverted); a steps = 12 rewrite is refused.  The
  first cut (a v5 K checked as `steps x k_ops`) would have refused it: fp4's hashed row is 24 x 64 codes, its bare unit 68.

## Entries for the other branches at integration

* `lane/blake3-leaf-3` 820aa6f (+blake3): nothing to add.  Its pins (`leaf::PINS` (rel, "blake3", ...)) key on the base
  `Relation`, so `steps` / `k_ops` apply unchanged; `leaf::max_steps(&BLAKE3)` is None (`ajtai::degree` parses only
  `ajtai-n<N>`); the Python BLAKE3 leaf has no `max_steps`.  The v5 writer is the same (`_K_of` = 1536).  Conflicts are
  textual only (leaf.rs: `SCHEMES` / `PINS` next to `max_steps`).  After merging, rerun cargo and the blake3 v5 fixture.
* `lane/share-logup-3` 453d7cf4 (+shared, v6): its `Relation` gains `shared_systems` on the same 25 literals (each literal
  takes both field sets; mechanical conflicts).  Its `verify_inner` is split into `verify_core_inner` (v5 and the G side
  of `verify_pair`): insert, right after its `if !opt.allow_any_system { gate }` block,
  `if !matches!(fpc, FpCtx::Public { .. }) { if let Err(e) = check_vu_shape(st, rel, leaf, !opt.allow_any_system) { return reject(&e, tm, None, Some(info)); } }`.
  The H side's layout is fixed by its pinned H system (the H digests are per steps / word width, per that branch's
  comment).  Python: `_read_v6` passes `row_words=K` and the `verify_files` check runs for `st.v5 or st.v6`;
  `SharedHashedRunner` inherits `HashedRelationRunner.hooks`, so the G side's `hooks_for(auth)` carries steps; give
  `hooks_h_for` `steps=rel.steps` too.  Verify with that branch's v6 fixtures + `shared_negatives` after the merge.
* `lane/fp4-decode-3` 6ffa0351 (fp4-nvf4+poseidon2): the entry is that branch's own `FP4_NVF4.hashed_sys_id =
  8c6d260c675cad40ae7263db08974f1842d04997f344cb4f9e52821e70bb25f5`, `hashed_table_digest =
  8dad2d286e92d9927464afb81846fcbdb16f09b2c01910e36fcf8aaac432fc3a`.  `steps: 24, k_ops: 68` are already on `FP4_NVF4` here.
  Python: `fp4_hashed_relation().steps = STEPS = 24`, so `HashedRelationRunner.hooks.steps = 24`; K = 1536.  Checked
  end to end above.

## Still unbound / notes

* `--allow-any-system` on a bare statement leaves steps free (a bare unit has no structural bound); this is the
  specified behaviour, and the verdict reports `system_pinned: false`.
* The Ligero configuration and n_vus remain prover choices, bounded by the digest and the soundness floor; they are
  not relation constants.
* Cosmetic: the Rust steps message for a hashed fp4 statement prints "K = 68" (the bare unit's word count).
* A pre-existing flake: `tests/relations.rs` tests write same-named files into one per-process tmp dir.
  `fp4_nvf4_proof_and_coins_negatives_are_rejected` failed once and passed in 3 reruns.

## FINAL

Branch `lane/steps-pin`, tip **f2a74128** (base 47d191e; 5 commits, verifier-only, not merged).  H1 (Ajtai steps > n
collisions) and H2 (no pin fixed steps) are closed in both verifiers.  Every pinned relation carries its canonical
steps / K; a pinned verify refuses a mismatch; `--allow-any-system` still enforces Ajtai steps <= n and the hashed K.
No system digest, statement digest or pin changed.  Rust: cargo 31 + 7 + 23.  Python on the 4090 pod: steps_pin_test 26,
plus the regressions (hashchain 14, ajtai key/leaf 17, relations 21, fp4/fp8 relation 22, leaf conformance + leaf + chain 29,
2 skipped).  R2 dumps art:2c8d5089 / art:527e99be accepted 13/13 pinned (Rust) and in the Python subsets.  Pod
`i0q2rifehiltnd` terminated 23:54Z (about 41 min at $0.74/h, about $0.51).

## Log
* 23:10Z start; brief, red-team-leaf-3 report + handoffs, coordinator H2 spec, ajtai-leaf-3 FINAL read. Worktree created.
* 23:12Z H1 reproduced on 47d191e (all 7 red-team fixtures accepted pinned).
* 23:22Z Rust fix c5cf7f6d.  23:30Z Python fix 3781590e.  23:34Z forged steps = 32 proofs on the pod; b7453317.
* 23:42Z v5 K check revised to K = 1536 (fp4+poseidon2 integration), f2a74128.
