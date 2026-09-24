CHECKPOINT 0b0768ed (06:26Z) [final] closed by coordinator 06:30Z: lane/integration fully merged into main (0b0768ed ancestry), worktree clean, pod vy-integration gone; the lane died before writing FINAL
CHECKPOINT 64c35b06 (01:11Z) [open] merges 1-9 done + red-team (order swap: shared-live before red-team, see report); LIGSTM06 collision tier0-trimmed vs shared-pair resolved by auth-string dispatch; 1cf9178 duplicate hashed pipeline dropped for shared-live's; now fp4-decode-3 conflicts (6 files)
CHECKPOINT 1703590a (01:06Z) [open] merges 1-7 done (research-qol, qol [cli/store conflicts: kept both], leaf-iface, ajtai-design, tier0-bytes, open-fixes, steps-pin [serialize.py trimmed+row_words, relations.rs both test blocks]); tools/research 293 pass; pod 97zxgf1oii4cga up; next red-team-leaf-3
# integration: merge 13 lanes onto main@22e10e0e + merge-val-3 on one 4090

Lane `integration`, branch `lane/integration`, worktree `~/projects/verity-main-wt/integration`, pod `vy-integration`
(97zxgf1oii4cga, RTX 4090, created 01:04Z). Budget $5, FINAL 03:00Z. Inbox at start: nothing new.

## Branch tips (confirmed with git log -1 at 01:03Z)
All 13 match the launch message: research-qol 32bd3478, qol a24f8ac5, leaf-iface 720820dc, ajtai-design 2a61a1fd,
tier0-bytes+leaf-iface 523981c0, open-fixes 5e6b3e3b, steps-pin f2a74128, red-team-leaf-3 89cd6cf7, shared-live e2a3b27e,
fp4-decode-3 6ffa0351, blake3-leaf-3 820aa6fe, hints-fused-2 4287a92b, bench-summary fd2971e8.

## Merge log
Order as briefed except two deviations (8 <-> 9 swapped; 10 deferred), each explained below. `git status` clean and no
`<<<<<<<` after every commit.

1. research-qol 32bd3478 -> 7924433d, clean.
2. qol a24f8ac5 -> 35e942c4. Conflicts only in usage text: `research/cli.py` docstring (kept both sides' command lines: pods
   unpreserved/drain/guard/env/mem + pods ssh/sync/notes), the helper block before `_prepare_store` (kept research-qol's
   `_resolve_cwd` / `_parse_env` / `_request_env` AND qol's `unredact_key_params`, research-qol's `_prepare_store(..., env_map)`
   signature, which qol's body already calls `unredact_key_params` inside), `store/cli.py` + `store/README.md` usage lines
   (`labels ... [--remote]` from research-qol + `label ... [--off-vocab]` refusing from qol; the code had auto-merged both).
   `tools/research` pytest: **293 passed, 1 skipped (88 s)**.
3. leaf-iface 720820dc -> 0cf3b11a, clean. 4. ajtai-design 2a61a1fd -> 9c87efdd, clean.
5. tier0-bytes+leaf-iface 523981c0 -> 5bd0cc99, clean; hashchain_test's magic assertion is its version (v6 = LIGSTM06 default,
   `LIGERO_STMT_TRIM=0` = v5).
6. open-fixes 5e6b3e3b -> e3b81438, clean.
7. steps-pin f2a74128 -> 1703590a. `serialize.py`: Statement keeps both new fields (tier0 `trimmed`, steps-pin `row_words`);
   `_read_v5` passes both. `tests/relations.rs`: both appended test blocks kept (tier0 v6 tests, then steps-pin's Ajtai/H1/H2).
9. **shared-live e2a3b27e merged BEFORE red-team-leaf-3** -> d71386a6. Why: red-team-leaf-3 carries share-logup's `1054caf3`
   (row sharing) + `cfdcf657` (pipelined pair), which are also ancestors of shared-live; its own 8 commits after cfdcf657 add only
   8 scripts under `redteam/`. Merging red-team first produced 5 core-file conflicts (steps-pin vs sharing) where "keep steps-pin"
   would have recorded the sharing commits as merged while dropping their code, and shared-live would then not re-add it. Resolved
   once against the newer sharing code instead. Decisions in this merge:
   - **LIGSTM06 magic collision.** tier0-bytes' trimmed hashed statement (v5 minus the l-vector) and shared-live's paired
     `included-hash-shared` statement BOTH use magic `LIGSTM06` / format name `ligero-statement/v6`. Both layouts read the same
     header, `u8 y_bytes`, `str relation`, `str authentication`, so the readers now dispatch on the authentication string:
     Python `read_statement` peeks it (`included-hash-shared` -> `_read_v6`, else `_read_v5(trimmed=True)`); Rust
     `Statement::parse` keeps tier0's `LIGSTM06 => 6` and `parse_hashed` returns shared-live's "is a PAIR: verify it with
     `pair` / `batch-pair`" for a shared file; `PairStatement::parse` already refuses a non-shared file. No bytes of either
     format changed, so existing +shared dumps / live sessions and tier0's fixture stay valid. **Coordinator decision needed
     before the wave:** give one of them a distinct magic/format name (it is a parse-dispatch wart, not a soundness issue: the
     authentication string is mandatory in both and the pinned systems differ).
   - `protocol._tests_compute` chain quotient: steps-pin (ajtai-leaf-3) chunked the encode by `CHAIN_ENC_CHUNK` (Ajtai n128 OOM);
     shared-live added the fused `tests_fused.chain_quotient`. Combined: chunk loop, fused kernel per chunk when available. One
     chunk (R <= 64: bare and Poseidon2) is exactly shared-live's path; sums are reduced mod P.
   - `verify.rs`: steps-pin's `check_vu_shape` + Ajtai key check kept BEFORE shared-live's fingerprint block, so the H2 shape pin
     also applies to both sides of a +shared pair (they carry the header's steps / K = 1536).
   - **Duplicate pipelined hashed prover.** `HashedRelationRunner` had two `prove_vus_many`: blake3-leaf-3's `1cf9178`
     (via steps-pin; `_marshal_hashed`, kw `vu_ids`) and shared-live's `cfdcf657` (`marshal_hashed` + `_pipelined`, kw
     `vu_ids_list`; Python kept whichever came last). Kept shared-live's (device-resident cached bundles, SharedHashedRunner
     builds on it; +hash measured 0.373 s vs 0.421 s), removed 1cf9178's, and ported 1cf9178's one extra feature: live-verifier
     coins for pipelined +hash (`live_statement` hook). `leaf/conformance_test.py` now passes `vu_ids_list=`.
   - relchain bench: red-team F5's per-scheme `ZK_HASHED_NOTE` + shared-live's `ZK_SHARED_NOTE`; statement_format names v6 for
     shared, `hashed_statement_format()` (v6/v5 per LIGERO_STMT_TRIM) for hashed; gate negatives = shared/hashed + Ajtai leaf battery.
8. red-team-leaf-3 89cd6cf7 -> 64c35b06, clean: adds only its 8 `redteam/leaf{2,3}_*.py` scripts; no overlap with steps-pin's
   copies (`fixtures/steps-pin/`, `redteam/steps_pin_forge.py`), so nothing to prefer.
10. **fp4-decode-3 6ffa0351: NOT merged (deferred).** It is based on e0cf2cdd, before leaf-iface; 32 conflict hunks in
   hashchain.py (13), relchain.py (9), hashauth.py, run.py, relation.rs, relations.rs. It generalises `compose` by an operand
   *format* object (NVFP4 nibbles + UE4M3 scales on 24-bit lanes, `native_digests`, its own sponge/permute_torch code) on the
   pre-registry code, while leaf-iface moved the sponge behind `leaf/poseidon2.py`'s gadget (`chain_witness(words, word_bits)`),
   which has no notion of pre-packed lanes. A correct merge is a port (a lane-format seam in the Poseidon2 leaf gadget) that must
   reproduce sys_id 8c6d260c (pinned `fp4-nvf4+hash`) byte for byte. Not attempted in this window. **Cherry-picked 6ffa035 alone**
   (fused witness kernel as compute_89 PTX + JIT on cc >= 12.0: the 5090 cold-compile fix) -> a281005d, clean; its differential
   test skips the `fp4-nvf4+poseidon2` case when `fp4/hashed.py` is absent (66293c45).
11. blake3-leaf-3 820aa6fe -> e918ac88. relchain/conformance_test: HEAD (it re-added its copy of 1cf9178's prover and the `vu_ids`
   keyword). `leaf.rs`: Ajtai schemes + BLAKE3 scheme, `SCHEMES = [POSEIDON2, BLAKE3, AJTAI_N64, AJTAI_N128]`, PINS = union.
12. hints-fused-2 4287a92b -> ba5c95e4, clean. 13. bench-summary fd2971e8 -> 1ba5e023, clean.
