CHECKPOINT 24f252b1 (02:31Z) [open] 02:32Z tip 24f252b1 pushed. Clean-GPU bench done: fp8-ada bare p4 0.1860 s, bf16-hopper 0.2729, fp8-ada+shared 0.2837; bench.summary contract column ok x3 (phase-sum overshoot not reproduced), Rust ACCEPT pinned x3; art:3f18a292 (+bench-result art:8fa10d53 art:0ec87a43 art:cbe4d8c1). A/B timing rounds running on clean GPU (~2 min/run; will stop 02:44 with rounds done). Report sections a-f written; kb/pods-4090.md added (10.2-core quota). Pod terminate ~02:46, FINAL by 02:55.
CHECKPOINT none (02:23Z) [open] 02:25Z tip 24f252b1 (ajtai_test magic: LIGSTM06 default after tier0-bytes; passes on pod both STMT_TRIM modes). Gates 13/14 0F (fp8-ada-v3 2316 s); v3x4 --batch 4096 gate killed at 50 min (49 honest sub-batches vs CPU Python reference, 10.2-core quota): no verdict. Gates art:b833003b, tests art:455ad901 (cargo 64 pass; pytest partial 380/383 run pass, 2 F both fixed, 1 skip; ~122 not reached). Clean-GPU window running: bench (3 configs) then A/B timings; then steps_pin/reverify/live/leaf pytest files.
CHECKPOINT none (02:10Z) [open] 02:11Z Gates 12/14 0F (all 4 relations x bare/hash/shared); fp8-ada-v3 + v3x4 gates still running (every honest sub-batch checked vs CPU Python hint reference, 10.2-core quota). A/B digests all 4 pairs IDENTICAL (levels blake3 da424477, levels v3x4 b5af4f65, levels v1 6baf894a, fused v3x4 b5af4f65), art:9aca92d0. H1/H2 forges REJECT art:ca615053. Live: bare s..2ca7 + shared s..687e both ACCEPTED, Rust re-verify 13/13 each (shared first try OOM beside gates, rerun alone), art:c85b8b38. pytest 2 groups ~245/411 of the rest. Cutoff 02:27 for gates/pytest, then clean-GPU A/B timings + bench.
CHECKPOINT a6563c4b (01:53Z) [open] 01:54Z tip a6563c4b. Pod CPU quota is 10.2 cores (cfs 1020000/100000, 75% periods throttled) while torch sizes pools for 96 visible cores: concurrent jobs crawled. Killed stalled A/B v3x4 arm + 4-way pytest; pytest now 2 groups OMP_NUM_THREADS=2 (~35%); A/B rest restarted (digests only). Gates 7/14 0F (fp8-ada x3, fp8-hopper x3, bf16-ampere bare; bf16-hopper hash/shared also 0F => 9 incl those). A/B LEVELS blake3 pair IDENTICAL (27 files, combined da424477). Coordinator handoff ack: clean-GPU A/B timings (alternating, 3 rounds) + bench after gates/pytest.
CHECKPOINT a6563c4b (01:36Z) [open] 01:37Z tip a6563c4b fold_test: bf16-ampere-x4 rows/unit bound 4.1 -> 4.15 (pinned fixture gives 14576/3516 = 4.1456, as the comment documents) (fold_test bf16-ampere-x4 bound 4.1->4.15: pinned fixture ratio 14576/3516=4.1456 as its comment documents). Gates 4/14 pass 0F (fp8-ada bare/hash/shared, fp8-hopper bare); rest in 3 parallel runners (CPU-bound). H1/H2: cargo steps_pin_* ok (32+7+25 pass); fresh merged-prover steps32 forges bare/ajtai-n64 REJECT (steps 32 vs VU 48), poseidon2 REJECT (sys_id pin). A/B blake3 LEVELS pair done, v3x4/v1/fused running. pytest running (1 F so far).
CHECKPOINT 66293c45 (01:26Z) [open] 01:27Z merges 1-13 done (fp4-decode-3 deferred; 6ffa035 cherry-picked); tip 66293c45 witness_device_test: the PTX differential test skips fp4-nvf4+poseidon2 when fp4/hashed.py is absent (lane/fp4-decode-3 not merged; 6ffa035 cherry-picked alone). Pod: cargo test/check done, pytest running; gates 2/14 pass so far (fp8-ada bare 13h/92n 0F, +hash 13h/86n 0F). Reverify w/ merged pinned Rust: bare art:cc59294a PASS verdict art:615318d6; +hash art:4ab22886 PASS verdict art:ed6e78cf; +shared shared-live-2 cell art:fa2be398 manual batch --system-h 13/13 ACCEPT 128.66b, verdict art:e1b0fd7b (reverify.py lacks --system-h: gap to fix). A/B started concurrently with gates. Next: bench, live.
CHECKPOINT 66293c45 (01:19Z) [open] all merges done except fp4-decode-3 (deferred: pre-leaf-iface, needs port; 6ffa035 cherry-picked) tip 66293c45; pod bootstrapped; cargo test ligero-verify 64/64 (H1/H2 steps_pin refusals + v6 pass), cargo check backends/direct ok; pytest + gates running on pod
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
14. Post-merge fix a6563c4b: `fold_test[bf16-ampere-x4]` bound 4.1 -> 4.15. Stale threshold: the test pins the folded system
   byte-identical to its fixture two lines above, so rows/unit is a constant of the pinned system: 14576 / 3516 = 4.1456, the
   exact numbers the test's own comment documents ("3.6 % MORE rows per unit than four units"). Not a regression.

## merge-val-3 on the 4090 (pod vy-integration 97zxgf1oii4cga)

Pod tree = `research pods sync` of 66293c45 (+ a6563c4b's fold_test.py copied in; test-only). Bootstrap with qol's
`pod_bootstrap.sh`. Scripts: `evidence/pod-scripts/` (00 bootstrap, 01 tests, 01b pytest groups, 02/02c gates, 02b H1/H2,
03/03c A/B digests, 03b A/B timings, 04 bench, 05/05b live).

**Environment finding (affects every lane on these pods):** the container's CPU quota is **10.2 cores**
(`cpu.cfs_quota_us 1020000 / period 100000`, 75 % of periods throttled) while `nproc` / torch see 96 cores, so every Python
process sizes its thread pools for 96. Concurrent jobs crawled (a v3x4 A/B arm stalled 17 min; bf16-ampere-bare gate 1219 s vs
~70 s alone). Correctness runs were overlapped (restarted pytest with `OMP_NUM_THREADS=2`); timing runs got a clean GPU.

### a. Tests
* `cargo test` backends/ligero-verify: **64 passed** (32 unit + 7 + 25 relations, incl. `steps_pin_forged_steps32_proofs_are_refused_pinned`,
  `steps_pin_red_team_fixtures_are_refused`, v6 tests); `cargo check` backends/direct workspace OK.
* pytest `backends/direct/ligero` (449 collected) on the GPU: **not complete in the window** (CPU quota). Run as a sequential
  pass (killed at 92 results) + 2 parallel groups (`OMP_NUM_THREADS=2`; killed at 157 / 134 for the clean-GPU window).
  Distinct tests run ~327, all pass except two, both fixed:
  - `fold_test[bf16-ampere-x4]` (pre-existing, 4.1456 vs 4.1): stale bound, fixed a6563c4b (above); all 33 fold_test pass after.
  - `leaf/ajtai_test::test_statement_v5_round_trip_and_file_verifier`: a **merge interaction** (ajtai-leaf-3's test asserts
    magic LIGSTM05; tier0-bytes made the trimmed LIGSTM06 the default hashed statement). Fixed 24f252b1 the same way as
    tier0's hashchain_test (`STMT_MAGIC_V6 if HASHED_STATEMENT_TRIMMED else STMT_MAGIC_V5`); passes on the pod in both
    `LIGERO_STMT_TRIM` modes.
  - 1 skip (witness_device_test fp4-nvf4+poseidon2: fp4/hashed.py absent, fp4-decode-3 not merged).
  - Not reached: pubsel/relation_test (48 of 54), leaf/conformance_test (9 of 27; the blake3 negatives test ran > 30 min at
    2 threads), leaf_test, live_test, pipeline_race_test, reverify_test, steps_pin_test (see the tail run below).
  Logs: test-log art:455ad901.

### b. Gates (4096 VUs, zk interactive, local coins, --batch 16384) -- gate-report art:b833003b
| relation | bare | +hash | +shared (tile 64x64) |
|---|---|---|---|
| fp8-ada | 13 honest / 92 neg / 0 F | 13 / 86 / 0 | 13 / 98 / 0 |
| bf16-hopper | 25 / 87 / 0 | 25 / 86 / 0 | 25 / 98 / 0 |
| bf16-ampere | 25 / 87 / 0 | 25 / 86 / 0 | 25 / 98 / 0 |
| fp8-hopper | 13 / 92 / 0 | 13 / 86 / 0 | 13 / 98 / 0 |

fp8-ada-v3 bare: 13 / 92 / **0** (2316 s). **fp8-ada-v3x4 (fused, --batch 4096): no verdict** -- killed at 50 min for the
clean-GPU window; at --batch 4096 it has 49 honest sub-batches and the gate checks every one against the CPU Python hint
reference (hints-fused-2 gated it at 2 honest sub-batches: 2 / 99 / 0). Its correctness here is covered by the A/B below
(fused vs torch hints byte-identical at 4096 VUs) and by the hints_fused_test differential (in the g2 group, passed).
fp4-nvf4 skipped: needs a 5090 (device wave).

H1/H2 must-rejects: cargo `steps_pin_red_team_fixtures_are_refused` (red-team collide P/Q n64/n128 + n64 steps 32) and
`steps_pin_forged_steps32_proofs_are_refused_pinned` pass; plus fresh forges from the MERGED prover
(`redteam/steps_pin_forge.py --steps 32`, self-verify with the patched prover = accept) through the merged Rust CLI, pinned:
bare -> REJECT "steps = 32 columns per VU, the fp8-ada relation's VU is 48"; +ajtai-n64 -> same REJECT; +poseidon2 -> REJECT
(not the pinned hashed system: sys_id). execution-evidence art:ca615053.

### c. Byte-identity A/B (fiat-shamir, rep1 dumps; 27 files each = 13 proofs + 13 statements + system) -- art:9aca92d0
| env | relation / config | digest of the sha256 list | verdict |
|---|---|---|---|
| LIGERO_INTERP_LEVELS 1 vs 0 | fp8-ada+blake3 1024 VUs l=4096 p2 (the only config that takes the interpreter: 17534 ops > 16384) | da424477a8f3091f | IDENTICAL |
| LIGERO_INTERP_LEVELS 1 vs 0 | fp8-ada-v3x4 4096 VUs l=4096 p4 | b5af4f652669b9c1 | IDENTICAL |
| LIGERO_INTERP_LEVELS 1 vs 0 | fp8-ada 4096 VUs l=16384 p4 | 6baf894a384b104f | IDENTICAL |
| LIGERO_FUSED_HINTS 1 vs 0 | fp8-ada-v3x4 4096 VUs l=4096 p4 | b5af4f652669b9c1 | IDENTICAL |
(the v3x4 digest is the same in both rows: same config, both defaults on.) Probe: bare fp8-ada 967 ops, v3x4 6445, +poseidon2
1704, +ajtai-n64 2056, +blake3 17534 -> only +blake3 is on the interpreter path. `fp8-ada-v3x4 + poseidon2` does not compose
(ValueError: v3 packed operand pins vs expected decode triples) -- not a registered combination, noted only.

### d. Pipelined benches (clean GPU: nvidia-smi empty before; --pipeline 4, zk interactive, local coins, 4096 VUs, l=16384, --reps 3)
execution-evidence art:3f18a292 (tree with proofs + rust_batch.json + summary_table); bench-result/v1: fp8-ada bare
art:8fa10d53, bf16-hopper bare art:0ec87a43, fp8-ada +shared art:cbe4d8c1.
`python -m verity_numerical.bench.summary` over them:
| label | t.total | wit | enc | arith | ser | other | dev GiB | proof MB | contract | rust |
|---|---|---|---|---|---|---|---|---|---|---|
| fp8-ada bare | 0.1860 | 0.0184 | 0.0511 | 0.1024 | 0.0140 | -0.0000 | 6.12 | 66.1 | **ok** | ACCEPT 13/13 2^-128.32 |
| bf16-hopper bare | 0.2729 | 0.0177 | 0.0726 | 0.1567 | 0.0257 | 0.0001 | 5.15 | 118.0 | **ok** | ACCEPT 25/25 2^-128.05 |
| fp8-ada +shared | 0.2837 | 0.0180 | 0.0360 | 0.2132 | 0.0165 | -0.0001 | 8.46 | 94.4 | **ok** | ACCEPT 13/13 2^-128.66 |
**Phase-sum verdict: all three headline configs PASS the contract column** (buckets + joints = t.total within 0.1 ms). The
2.2 % overshoot bench-summary flagged (r20260923-223427-9bab p4/bench/bare) does not reproduce on the merged tree at these
configs, so no rule change is proposed; `tables.py` untouched.

### e. Live (verifier on the same pod, `live serve` 127.0.0.1:7000 from the merged tree, core ligero-verify a2a6cab8) -- art:c85b8b38
* fp8-ada bare, `--zk --mode interactive --pipeline 4`, session s20260924T020140Z-2ca7: **ACCEPTED** 13/13, 2^-128.32; merged
  Rust `batch` re-verify of the session dir: accepted 13/13 (own coins 13), pinned fp8-ada.
* fp8-ada +shared tile 64x64, session s20260924T020721Z-687e: **ACCEPTED** 13/13, 2^-128.66; Rust re-verify (`--system-h`):
  accepted 13/13, pinned fp8-ada+hash. (The first +shared attempt died with CUDA OOM while the v3/v3x4 gates held ~7 GB of
  the 24 GB; rerun alone -- environmental, not a merge defect.)
`vy-live2b-verifier-ro` not touched.

### f. Honest re-accepts with the merged Rust (steps-pin pins)
* bare fp8-ada: `reverify.py art:cc59294a` (dev-4090, run-files art:2c8d5089): **PASS** 13/13, 2^-128.32, pinned fp8-ada,
  custody 40/40; verdict art:615318d6.
* +hash: `reverify.py art:4ab22886` (dev-4090 fp8-ada+hash, v5 statement, run-files art:527e99be): **PASS** 13/13, 2^-128.32,
  pinned fp8-ada+hash; verdict art:ed6e78cf.
* +shared: no bench-result in the store carries a run_files ref for an included-hash-shared run (share-logup-3 dumped none;
  shared-live-2 stored proof/v1 cell trees), and **reverify.py never passes `--system-h`** (the verifier correctly refuses a
  v6 pair statement without it: "is a PAIR: verify it with `pair` / `batch-pair`"). So manually: shared-live-2's A-fp8-ada
  shared-local cell art:fa2be398 (rep1 dump), merged `ligero-verify batch --system system.bin --system-h system_h.bin
  --target-bits 128`: **ACCEPT** 13/13, 26 sub-batches, 2^-128.66, pinned fp8-ada+hash, Python agreement 13/13;
  verification-verdict art:e1b0fd7b.
