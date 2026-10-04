---
cursor:
  subagentId: "bc-18346d9c-4bfb-56af-ad79-0d17e73bb44b"
---

# GPU 1: Pearl-C on sm_120 (FP8)

Worker bc-18346d9c. -h2 arm branch `cursor/pearl-c-sm120-h2-arm-b44b` (head `a00db59e`, pushed: #572 merged into `65ad22db`, then #572's `d20e4d16`). Run tree
`cursor/pearl-c-sm120-h2-runtree-b44b` (`31a7c488`: that head plus #588's `benchmarks/pouw/harness` at `dd23c0c3`). -h1 branch
`cursor/pearl-c-sm120-h1-b44b` (head `65ad22db`, pushed; #540 takes `9f1e33b1` or later), stacked on `cursor/pearl-c-sm120-b44b`,
**#449 merged in at `5f6a31c7`** (`9a8fe5fd`), GPU 2's `b0820016` merged in (`865e8712`), GPU 2's `e0902b4a` (`dump`) cherry-picked (`ec75c5e9`),
bc-6da61042's `881eb05d` (twin pool, `prefetch`) cherry-picked (`70f540c6`). -h2's key fold is on
`cursor/h2-row-keys-b44b` (`997ac6bd`, one commit on #572's `2018468b`). No PR opened from this VM.

## 7:15 PM PDT: migration handoff written; nothing of mine in flight; the -h2 runs' files are preserved

- **Handoff:** research-notes `lanes/accounting/20261001T0212Z-handoff-from-18346d9c-migration.md` (Daniel's 6:55 PM PDT ruling; compute-accounting's order `20261001T0157Z…`). Per that order I start no new work, and I answer my replacement in `lanes/accounting/`.
- **In flight:** nothing. No research run, fill job or lease of mine is running or queued on node 2.
- **Preserved now, by hand** (both runs predate the custody rule): `research data put --kind evidence/v1 --tree <run dir> --preserve`, PRESERVED with sha256 read back:
  - timed window `r20260930-231211-2f19`'s run dir (bench.json, transcripts, no-write negatives, verify; attempts 105 and 106): `art:0dd67fe8ef651123e29aff3158bc3768e6e8a6f4499fcfa679e8a0d71ab62a1f`;
  - card check `r20260930-224241-1be9`'s run dir: `art:2d5847c36eda473c0acae37e95e134e98cdfff870ac986e21c7b4410c641b5dc`;
  - the three runs the panel cites from the morning: `r20260930-070924-b158` `art:702388fa…`, `r20260930-072339-02ec` `art:0dc36d86…`, `r20260930-075931-4e4a` `art:d380e61e…` (full ids in the handoff).
- **Attempt records:** `research data preserved` gives PRESERVED for all 29 of my runs.
- **This VM was reset** after 4:25 PM PDT, which wiped `/tmp` and `~/.research`. Nothing was lost: the ship and `h2run.sh` are in the run dirs on node 2, and the code is pushed.

## 4:25 PM PDT: the -h2 timed window is done and verified, `r20260930-231211-2f19`

**Timed whole-node window `r20260930-231211-2f19`** (run tree `31a7c488`, ship cubin `40d5531b…`; `--no-sampler`, `gpu-lease 8 --wait --timed --max-min 20`). The lease covered all 8 GPUs from 4:12:37 to 4:16:46 PM PDT (4 min 9 s). The harness ran on the first of them, `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`. Clocks were locked-2100: SM 2,070–2,092 MHz (median 2,077) and memory 12,481 MHz over 1,200 samples, with per-rep `--sm-clock-arm` and `--sm-clock-base` in the lines below.
- **Gates:** the SASS gate passed; every arm and chain gate passed for both arms at both shapes; the known-bad controls were rejected. Baselines: cuBLASLt autotuned plus CUTLASS, in the same run, reps interleaved.
- **Verify** (verifier `31a7c488`, after the lease, CPU): all four transcripts ACCEPT, and all four no-write controls (poisoned 0xA5 roots) REJECT on the activation openings. bench rc 0, verify rc 0, run `done rc=0 SUCCESS`, published (`art:703406e2…`).
- **Measured slowdowns** (against the faster of cuBLASLt and CUTLASS):

| arm (panel) | 8,192³ prefill | hash-free | m = 32 decode | hash-free |
|---|---|---|---|---|
| `pearl-c-sm120-v1-h2` (v1-h2) | 1.8413× | 1.4333× | 3.3939× | 2.1176× |
| `pearl-c-sm120-unpromoted-v1-h2` (v2-h2) | 1.8059× | 1.3879× | 3.2771× | 2.0044× |

- The card check's untimed figures agree to within 0.05% (v2-h2 prefill 1.8054×; v1-h2 and v2-h2 decode 3.395× and 3.2785×).
- **Panel lines** (the harness's `verify.py` output, with line, version, change and description filled in; the coordinator appends):

- `pearl-c-sm120-v1-h2 m8192-n8192-k8192`:

  ```
  python panel.py append --line pearl-c-sm120 --version v1-h2 --change 'in-kernel -h2 keys (#572 997ac6bd), harness dd23c0c3, dump' --description 'pearl-c-sm120 v1-h2: -h2 (blake3-s256 row and tile leaves, own segment keys), timed whole-node window, locked-2100' --kind measured --run r20260930-231211-2f19 --source r20260930-231211-2f19 --precision fp8 --phase prefill --shape m8192-n8192-k8192 --slowdown 1.8413 --hash-free 1.4333 --verifier-commit 31a7c48801d46f48e066cdc3a633bd1ea16335d6 --verifier-accept 'ACCEPT pearl-c-sm120-v1-h2 m8192-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 9099, 9065, 11568 of 16384; root_A 69d0178ce0bbca03, tile root 6ea791642bde72a9, source e547c08a9b982e9d; transcript sha256:039c99c17a40084bc2e51660b458d6bb6cb65c02062dc8c5a4a77cd94961f91b; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19' --transcript 'r20260930-231211-2f19:transcripts/pearl-c-sm120-v1-h2/m8192-n8192-k8192/manifest.json sha256:039c99c17a40084bc2e51660b458d6bb6cb65c02062dc8c5a4a77cd94961f91b' --sm-clock-arm 2085,2077,2085,2077,2085,2077,2077,2077,2077,2077,2077,2077,2085,2077,2085,2077,2085,2077,2077,2077 --sm-clock-base 2085,2085,2077,2077,2077,2085,2077,2085,2077,2077,2077,2077,2085,2077,2077,2077,2085,2077,2077,2077 --negative-control 'REJECT negative control pearl-c-sm120-v1-h2 m8192-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 431, 11631, 7922 of 16384 (tile 431: activation opening; tile 11631: activation opening; tile 7922: activation opening); root_A a5a5a5a5a5a5a5a5, tile root a5a5a5a5a5a5a5a5, source 135ac7d38860743c; transcript sha256:1f77e970beab5eafdedc80e32f92d333ae31bcb8a3801746bb7427a4d4001504; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19'
  ```

- `pearl-c-sm120-unpromoted-v1-h2 m8192-n8192-k8192`:

  ```
  python panel.py append --line pearl-c-sm120 --version v2-h2 --change 'in-kernel -h2 keys (#572 997ac6bd), harness dd23c0c3, dump' --description 'pearl-c-sm120 v2-h2: -h2 (blake3-s256 row and tile leaves, own segment keys), timed whole-node window, locked-2100' --kind measured --run r20260930-231211-2f19 --source r20260930-231211-2f19 --precision fp8 --phase prefill --shape m8192-n8192-k8192 --slowdown 1.8059 --hash-free 1.3879 --verifier-commit 31a7c48801d46f48e066cdc3a633bd1ea16335d6 --verifier-accept 'ACCEPT pearl-c-sm120-unpromoted-v1-h2 m8192-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 7748, 7063, 1360 of 16384; root_A 0a91313ef8f12c30, tile root 6c701f12f83c9078, source faaf2340b863468e; transcript sha256:9d44b37d14b661db57911a04435abba89eb332f7f8b95b4c958bf52219bf69bf; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19' --transcript 'r20260930-231211-2f19:transcripts/pearl-c-sm120-unpromoted-v1-h2/m8192-n8192-k8192/manifest.json sha256:9d44b37d14b661db57911a04435abba89eb332f7f8b95b4c958bf52219bf69bf' --sm-clock-arm 2085,2085,2085,2085,2077,2085,2085,2085,2077,2085,2085,2077,2077,2085,2077,2085,2085,2077,2085,2077 --sm-clock-base 2085,2085,2077,2077,2077,2085,2077,2085,2077,2077,2077,2077,2085,2077,2077,2077,2085,2077,2077,2077 --negative-control 'REJECT negative control pearl-c-sm120-unpromoted-v1-h2 m8192-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 1, 6906, 1318 of 16384 (tile 1: activation opening; tile 6906: activation opening; tile 1318: activation opening); root_A a5a5a5a5a5a5a5a5, tile root a5a5a5a5a5a5a5a5, source 32cddde283a1eb7c; transcript sha256:468d2de23797d1a48eab0d72d3e0793b9d81db96085a09ffe280f0e7ac711f6f; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19'
  ```

- `pearl-c-sm120-v1-h2 m32-n8192-k8192`:

  ```
  python panel.py append --line pearl-c-sm120 --version v1-h2 --change 'in-kernel -h2 keys (#572 997ac6bd), harness dd23c0c3, dump' --description 'pearl-c-sm120 v1-h2: -h2 (blake3-s256 row and tile leaves, own segment keys), timed whole-node window, locked-2100' --kind measured --run r20260930-231211-2f19 --source r20260930-231211-2f19 --precision fp8 --phase decode --shape m32-n8192-k8192 --slowdown 3.3939 --hash-free 2.1176 --decode-method dependent-chain --verifier-commit 31a7c48801d46f48e066cdc3a633bd1ea16335d6 --verifier-accept 'ACCEPT pearl-c-sm120-v1-h2 m32-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 65, 16, 44 of 128; root_A 025dc78b8de02801, tile root e1e50eec86ccb7da, source df52657bdeecf045; transcript sha256:ae8daa658836ffb81960b83f5e0253515000a00e3135b117b52a724700009671; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19' --transcript 'r20260930-231211-2f19:transcripts/pearl-c-sm120-v1-h2/m32-n8192-k8192/manifest.json sha256:ae8daa658836ffb81960b83f5e0253515000a00e3135b117b52a724700009671' --sm-clock-arm 2092,2070,2070,2077,2085,2077,2070,2085,2077,2085,2070,2085,2077,2077,2077,2085,2077,2077,2092,2077 --sm-clock-base 2085,2070,2077,2085,2077,2085,2077,2085,2070,2077,2077,2077,2077,2070,2077,2085,2070,2085,2077,2085 --negative-control 'REJECT negative control pearl-c-sm120-v1-h2 m32-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 106, 107, 121 of 128 (tile 106: activation opening; tile 107: activation opening; tile 121: activation opening); root_A a5a5a5a5a5a5a5a5, tile root a5a5a5a5a5a5a5a5, source 3ca17c5dd5ba54d4; transcript sha256:c14c152b3b928027c7bc549d7ba6c26e7a8d6832483bd63cef3a4c896da4b0ad; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19'
  ```

- `pearl-c-sm120-unpromoted-v1-h2 m32-n8192-k8192`:

  ```
  python panel.py append --line pearl-c-sm120 --version v2-h2 --change 'in-kernel -h2 keys (#572 997ac6bd), harness dd23c0c3, dump' --description 'pearl-c-sm120 v2-h2: -h2 (blake3-s256 row and tile leaves, own segment keys), timed whole-node window, locked-2100' --kind measured --run r20260930-231211-2f19 --source r20260930-231211-2f19 --precision fp8 --phase decode --shape m32-n8192-k8192 --slowdown 3.2771 --hash-free 2.0044 --decode-method dependent-chain --verifier-commit 31a7c48801d46f48e066cdc3a633bd1ea16335d6 --verifier-accept 'ACCEPT pearl-c-sm120-unpromoted-v1-h2 m32-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 107, 76, 124 of 128; root_A 1da2a0e3be68eeea, tile root a813609b10f96a9c, source ef9ef5a0ab3060f2; transcript sha256:3f10518777a3d0488c24718d424e7ccbde0e87326d77883f408c1cbfd941f5b9; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19' --transcript 'r20260930-231211-2f19:transcripts/pearl-c-sm120-unpromoted-v1-h2/m32-n8192-k8192/manifest.json sha256:3f10518777a3d0488c24718d424e7ccbde0e87326d77883f408c1cbfd941f5b9' --sm-clock-arm 2085,2092,2077,2092,2077,2077,2077,2077,2085,2077,2077,2077,2077,2077,2077,2092,2092,2085,2077,2085 --sm-clock-base 2085,2070,2077,2085,2077,2085,2077,2085,2070,2077,2077,2077,2077,2070,2077,2085,2070,2085,2077,2085 --negative-control 'REJECT negative control pearl-c-sm120-unpromoted-v1-h2 m32-n8192-k8192: verity_pouw.audit.Verifier, Sampled(3) drew tiles 84, 57, 114 of 128 (tile 84: activation opening; tile 57: activation opening; tile 114: activation opening); root_A a5a5a5a5a5a5a5a5, tile root a5a5a5a5a5a5a5a5, source c5d8f3b1cd8f61bb; transcript sha256:78cb6dfe4ff4a2e0443e284d7be12d3b5c2b01bca76c586fe72f2c6d9a62db0c; verifier 31a7c48801d46f48e066cdc3a633bd1ea16335d6; run r20260930-231211-2f19'
  ```


## 4:05 PM PDT: the -h2 card check passed; the timed window launches in the 4:15 PM PDT slot

**Card check `r20260930-224241-1be9` passed** (untimed, `gpu-lease 1`, lease `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`, held 4 min 49 s, fill beside it).
- The SASS gate passed, and every arm and chain gate passed for both arms at both headline shapes. The known-bad negative controls were rejected.
- `verify.py` (verifier `31a7c488`): all four (arm, shape) transcripts ACCEPT, and all four no-write controls (poisoned 0xA5 roots) REJECT on the activation openings. bench rc 0, verify rc 0.
- Untimed figures, not for the panel (Measured, with fill running beside it): v2-h2 8,192³ 1.8054× (hash-free 1.3876×); v1-h2 m = 32 3.395× (hash-free 2.1179×); v2-h2 m = 32 3.2785× (hash-free 2.0046×).
- **Branch:** `cursor/pearl-c-sm120-h2-arm-b44b` now at `a00db59e`: #572's head `d20e4d16` merged in (the pools fork, so Python 3.14's forkserver default no longer hangs the fixture test on node 2), plus a `check=False` in the -h2 dry-run test. 331 passed, 2 skipped. The run tree stays `31a7c488` (the merge touches no ship file).

**Timed window:** launched at about 4:13 PM PDT if no other timed window is waiting (the harness's 3:45 PM PDT one hadn't started at 4:01 PM PDT). Run id to follow here.

## 3:45 PM PDT: the -h2 arms are built and pass on the stand-in; their card check is queued behind the harness's window; the per-die jobs are withdrawn

**The -h2 arms exist: `PearlCSm120H2` (`pearl-c-sm120-v1-h2`, panel v1-h2) and `PearlCSm120UnpromotedH2` (`pearl-c-sm120-unpromoted-v1-h2`, v2-h2).**
- **Branch:** `cursor/pearl-c-sm120-h2-arm-b44b`, head `e9111a9e`, pushed.
  - `94a489cf` merges #572 (`ee47ec2c`, with the in-kernel keys `997ac6bd`) into `65ad22db`.
  - Under -h2 the pipeline has one tree form (`w,nodes`: `hash_rows_b3s` leaves, `hash_leaves_b3s` for the tile tree, levels a launch), and `steps` refuses any other. Forming and the `w`/`b` epilogue still apply.
  - `e9111a9e` adds the arms. The set's keys gain the templates `t_row` and `t_tile`, put once an epoch; its buffers gain `skeys_b` and `skeys_a`; the manifest's `scheme_args` and the ledger's schemes say -h2. `fixture.build(hashing=)` builds an -h2 fixture.
- **Tests:** 331 passed, 2 skipped (`test_pearl_c_sm120.py` with `test_h1_sm120.py`). The -h2 tests:
  - the arms' accounting is the -h1 arms' with -h2's scheme and panel version;
  - an -h2 dry run launches `hash_rows_b3s` under `t_row` and `hash_leaves_b3s` under `t_tile`, and no -h1 leaf kernel;
  - on an -h2 fixture both arms pass the gate and reject a flipped digest, and `verify.py` accepts their transcripts and rejects the no-write controls.
- **Build:** cubin `40d5531b…`, nvcc 13.0.88, 97 kernels, no local memory.
- **Card check (untimed, `gpu-lease 1`): `r20260930-224241-1be9`, queued at 3:42 PM PDT.** It runs the harness at #588's `dd23c0c3` with both arms at the headline shapes (`fp8-e4m3`: cuBLASLt autotuned plus CUTLASS), `dump` with the no-write control, then the harness's `verify.py`. It waits behind the harness's 3:45 PM PDT window.
- **Timed window:** as soon as the card check passes. That could be the 4:15 PM PDT slot, if it's still free then; otherwise the next free one. I'll post the run id here.

**Per-die backlog: withdrawn at 3:21 PM PDT, per the PINNED 3:22 PM PDT entry (the forms table is final).** I moved `gpu1-pearlc-perdie-g0` … `-g7` to `fill/withdrawn/`: g5 and g6 from the queue, and the six running ones after a SIGTERM. The runner didn't requeue any of them, and they used about 0.4 GPU-h. No overnight GPU line from GPU 1 is queued.

## 3:20 PM PDT: the -h2 arm isn't ready for the 4:15 PM PDT window (ETA: window about 7:30 PM PDT); the per-die backlog is queued (about 4 GPU-h)

**Window 3 (v1-h2 and v2-h2): not ready. Please give the 4:15 PM PDT slot to the next window.**
- **Why:** `pearlc_arm` on my branch is -h1 only. The -h2 pipeline (#572) and the protocol's -h2 support (frame-b3s trees in `verity.commitments.merkle`, `audit`, `PearlC(hashing="h2")`) exist only on #540's line, which #572 sits on. They're not on `main` or my branch.
  - #572 branched from my `9f1e33b1` (12:31Z), so it lacks `dump`, the twin pool, the forms, the `w` epilogue and the round-by-round fold.
  - `sm120-h2-switch.md` says it too: the -h2 panel arm "needs the templates in its buffer lists".
- **The work:** a new branch, `cursor/pearl-c-sm120-h2-arm-b44b`, that merges #572 (`ee47ec2c`) into my head.
  - The trial merge has 5 conflicted files and 15 hunks, about 230 lines, mostly `run.py`. It also brings #540's line, 437 files.
  - Then the arm's -h2 buffer lists (`t_row`, `t_tile`) and `dump` of the frame-b3s trees; `verify.py` on `PearlC(device=sm120, hashing="h2")` for v1-h2 and v2-h2, with the no-write control; the fixture's -h2 buffers; the build and SASS gate; and an untimed card check on node 2.
- **ETA:** the card check at about 7:00 PM PDT. The timed window (`gpu-lease 8 --wait --timed --max-min 20`, `--no-sampler`, 8,192³ prefill and m = 32 decode) at about 7:30 PM PDT, after GPU 2's 6:30 PM PDT window. I'm starting now, and I'll post the run id here.

**Overnight backlog: `gpu1-pearlc-perdie-g0` … `-g7`, one job a die (`on=<i>`), about 0.5 GPU-h each, 4 GPU-h in all (Estimated).** Queued at 3:17 PM PDT (`gpus=1 max_min=30 prio=10`).
- **What it adds to `hashing-forms-by-shape.md`:** that table's rows come from 2–7 dies a shape. This puts every one of the 13 in-domain shapes on all 8 dies, each chunk under the table's pick.
  - Every row carries all eight A-form/forming pairs and `b` against `w` on the same die. So every pick is re-tested per die, including the close `w`/`b` calls at 70B's linears (−0.4 to −1.2%, near the 0.5% band).
- **Runner:** `forms_fill.sh` at `65ad22db` runs chunks back to back in one lease for 22 minutes (`FORMS_FILL_LEASE_S`), then exits 99. A failed pass still exits 4 at once. The test covers both.
  - Node 2 copy: `/workspace/pouw/gpu1-pearlc/forms_fill-65ad22db.sh`, sha256 checked by each job.
- **Ship:** ship15 (-h1). Output: `/workspace/pouw/gpu1-pearlc/perdie/g<i>/`.
- **Not queued, because the table already has it:**
  - v2-hot at every shape: `sm120-hot` is in every chunk.
  - The folds at large k: k = 28,672 is in the table.

## 3:00 PM PDT: the forms jobs' exit-4 path is fixed (`c1b6a1af`, `forms_fill.sh`); nothing requeued, since the kpad jobs cover every remaining chunk

**Broker:** re-installed at 2:52 PM PDT on this turn's new VM: source=broker, `git ls-remote` and `gh repo view` OK.

**Cause: the post-chunk exit-4 path.** It had nothing to do with the die: the same thing happened on GPU 7 at 1:07 PM PDT.
- A chunk whose run.py failed got a `.failed` marker, and the job went on to the next chunk.
- After each chunk, the script exited 99 while any chunk had neither `.done` nor `.failed`. Otherwise it exited 4 if any `.failed` marker existed, printing nothing.
- So the job exited 4 right after its last chunk passed. The failures behind it were the Qwen2.5-7B chunks refused an hour earlier (k = 3,584 and 18,944).
- The runner's retry then found no chunk to run and exited 4 at once. Its log held only the gpu-lease lines.
- I never pinned a die.

**Fix: `benchmarks/pouw/pearl_c_sm120/forms_fill.sh` (`c1b6a1af`)**, the same chunks from a table. The one exit 4 is right after a failed pass:
- it prints the chunk's name, the pass, its rc and the tail of run.py's stderr in the log;
- the rows and stderr are kept as `<chunk>.try<N>.*`;
- the next start runs that chunk again, and a chunk's sixth start exits 1;
- it exits 99 while chunks remain and 0 once all are done.

`test_forms_fill_exits_4_only_at_the_pass_that_failed` holds these exits under a stub run.py. The four files' ruff findings stay at 57, and the repository tests pass.

**Jobs: folded into the kpad jobs, nothing requeued.**
- `a` (92 of 92) and `b` (56 of 56) are complete: `kpad-a` and `kpad-b` finished their Qwen chunks.
- `r2b`'s 5 remaining chunks, and `r2a`'s 5, are all `kpad-r2b`'s and `kpad-r2a`'s.
- At 2:58 PM PDT I switched those two running jobs onto the fixed runner. Their files in `fill/running/` are now wrappers that check `/workspace/pouw/gpu1-pearlc/forms_fill-c1b6a1af.sh` (sha256 `74d6dac3…`, the committed file) and run it on `jobs/gpu1-pearlc-forms-kpad-{r2a,r2b}.chunks`. The previous files are kept as `jobs/*.v1.sh`.
- Both restarted under it at 2:59 PM PDT.
- At 3:00 PM PDT 6 chunks were left (3 each), and none of the 112 padded chunks had failed.
- Results: `/workspace/pouw/gpu1-pearlc/forms/{a,b,r2a,r2b}/` on node 2.
- bc-b139c29c can read `a` and `b` now. Round 2 closes with the kpad jobs.

## 21:20Z: the four form-table jobs failed on the Qwen shapes' k, not on a checkpoint; requeued padded; the twin pool is in

**Broker:** re-installed at 21:10Z on this turn's new VM: source=broker, `git ls-remote` and `gh repo view` OK.

**Cause: each job ran every chunk; the 4 Qwen2.5-7B linears at each m were refused, and the job's final exit is 4 when any chunk failed.**
- The refused shapes are k = 3,584 (qkv, o, gate_up) and k = 18,944 (down).
- run.py's `Pipeline` refuses k that isn't a multiple of 1,024 ("the kernels take m a multiple of 64, n of 128 and k of 1024"). `pearlc_arm.domain` puts the same shapes outside the arm's domain, so the harness's shape list includes four shapes this arm doesn't serve, and I queued them without checking.
- Each refused chunk died in about 4 s, before any GPU timing, and was marked `.failed` as designed. That is 28 chunks a job (4 shapes × 7 form sets).
- With nothing left, the runner's retries re-ran the script. The script exited 4 at once, printing nothing, so the logs showed only the gpu-lease lines.
- Not a checkpoint problem, and not the reprovisioned tree: ship15 at `/workspace/pouw/gpu1-pearlc/ship15` still checks against its manifest.

**Finished before the failure: 183 chunks**, gate 15 among them. They are in `/workspace/pouw/gpu1-pearlc/forms/{a,b,r2a,r2b}/` on node 2, one `<shape>__<form set>.jsonl` each, with `.done` markers and `chunks.txt`:

| job | done | refused |
|---|---|---|
| a | 64 | 28 |
| b | 28 | 28 |
| r2a | 63 | 28 |
| r2b | 28 | 28 |

The refused chunks' rows and errors are kept under each directory's `unsupported-k/`.

**Requeued (21:12Z): `gpu1-pearlc-forms-kpad-a`, `-kpad-b`, `-kpad-r2a`, `-kpad-r2b`.**
- Each job holds only its predecessor's 28 refused chunks, writing into the same directory, whose done chunks stay.
- These shapes run at k rounded up to 1,024: 3,584 → 4,096 and 18,944 → 19,456, the way run.py already pads m to 64 rows. Their numbers are Estimated for the real shapes, which the arm doesn't serve today.
- Chunk names keep the real shape and add `-kpad<k>`, e.g. `m2048-n4608-k3584-kpad4096__default`.
- The jobs now print their failed chunks before exiting 4.
- First padded chunk: 11 passes, rc 0. At 2,048 × 4,608 × 4,096, sm120-hot's call is 0.420 ms, 2.580× this build's plain GEMM (Measured at the padded shape, diagnostic, locked-2100).
- By 21:19Z all four were running: 13 of the 112 padded chunks done, 99 left, none failed.

**The gate-twin pool (bc-6da61042's `881eb05d`, `cursor/pearlc-twin-pool-9da4`) is in, as `70f540c6`.**
- It is `twin_submit` and `twin_tiles` over `refs.pool`, and `prefetch` (interface v0.6).
- Two conflicts with `dump`'s edits, the docstring and the imports, were resolved by keeping both. `0c9c4be5` spaces the `refs` import's comment for ruff, so the four files are back to 57 findings.
- The tests pass: `test_pearl_c_sm120.py` and `test_h1_sm120.py`, 326 passed with CUDA 13.0.88, including the new pooled-gate test for both arms.
- Without #588's `refs.py` the arm runs the twin inline, as before.

## 18:40Z: the pilot's cast is the packed one; `dump` is in (`ec75c5e9`); four form-table fill jobs are queued (~5 GPU-h)

**Broker:** re-installed at 18:26Z on this turn's new VM (VMs keep getting replaced): source=broker, `git ls-remote` and `gh repo view` OK.

**(1) The cast in `e0902b4a0`: packed, so `prices="cast-8.72"` is right.** Evidence from the source, not a re-measurement:
- run.py's `form_a` and `form_b` steps launch `form_s5` with MODE 0. `e4m3x4` does two `cvt.rn.satfinite.e4m3x2.f32` per four codes, and one 64-bit `STS` per row's eight codes at the 160-byte `FORM_ROW`.
- The one-code, 16-bit-store cast (`form_s5_scalar`) runs only as the check's alternate (`FORM_ALTS`) and in `form_rates`. No call launches it.
- `form_body` and `e4m3x4` are byte-identical from `9f1e33b1` (12:31Z) through `e0902b4a0`. That is the kernel whose cast measured at most 2.87 units a code over the castless loop (Measured, r20260930-120753-303f and r20260930-124211-a304), under the 8.72 target.
- So the as-written 32.06 doesn't apply to this binary.

**(2) `dump`:** `e0902b4a0` (GPU 2, `cursor/pearl-c-sm120-h1-commit-9569`) is cherry-picked onto this branch as `ec75c5e9`, with no conflicts. The tests pass: `test_pearl_c_sm120.py` and `test_h1_sm120.py`, 324 passed, CUDA 13.0.88. `92285aab` fixes the two ruff findings it brought (`re.M`, and a `subprocess.run` without `check`), so the four files are back to 0e339c1e's 57.

**(3) Fill: `gpu1-pearlc-forms-a`, `-b`, `-r2a`, `-r2b`** (queued 18:33–18:36Z, `gpus=1 max_min=8 cpus=8 prio=10`; scripts in `/workspace/pouw/gpu1-pearlc/jobs/`).
- **Output:** `/workspace/pouw/gpu1-pearlc/forms/<job>/`, one `<shape>__<form set>.jsonl` per chunk, with `chunks.txt` recording the lease UUID and CVD of every start.
- **Ship:** ship15, from `0e339c1e`, unpacked to `/workspace/pouw/gpu1-pearlc/ship15`. Its manifest checks, the cubin is `1ac6d6d7…`, and its `run.py` is byte-equal to this head's. `dump` changed only `pearlc_arm.py`, so the diagnostic timing is the same code.
- **Chunks:** each chunk is one (shape, form set). It runs run.py's bit-exact check against the ship's fixture (0.05 s; no CPU reference inside the lease), then run.py's timing of `sm120`, `sm120-unpromoted` and `sm120-hot` at REPS 9, in fresh processes, until the chunk's budget is used.
  - Every row also carries `call_e2e_ms_by_form` and `_by_epilogue`: the other forms timed on the same die, in the same process.
  - Chunks exit 99 while any remain. A chunk whose run.py fails keeps its rows and is marked `.failed`, and the job ends 4. A chunk started 5 times fails the job.
- **Form sets (7):**
  - default (`w,nodes`, split forming, epilogue `b`);
  - `p,one`;
  - `p,fold`;
  - `s,one`;
  - `PEARLC_FORMING=fold`;
  - `PEARLC_EPILOGUE=w`;
  - `s,one` with `w`.
- **Shapes (21):** every harness shape (`shapes.py`, #491's branch), namely m = n = k 2,048 to 32,768 (8,192³ and 16,384³ included), the decode headline m32-n8192-k8192, and the Qwen2.5-7B and Llama-3.1-70B linears at m = 2,048 and m = 32.
- **The jobs:**
  - **a:** gate 15 first, then the 13 prefill shapes × 7 form sets, 12 passes or 110 s a chunk.
  - **b:** the 8 decode shapes × 7 form sets.
  - **r2a, r2b:** the same chunks again, at up to 60 passes or 80 s a chunk. They were added because a decode pass takes about 2 s, so a and b alone come to only about 2 GPU-h. The runner started them at once beside a and b, not after them. They give the spread across sessions and dies.
- **Gate 15 passed again inside job a** (18:35Z, GPU `fb680060`; try 1 was preempted):
  - check at [256, 384, 1024]: sm120-unpromoted 134 buffers and sm120-hot 136, none failed;
  - 16,384³ call: 14.841 ms for v1 and 14.930 ms for v2-hot, 1.238× this build's plain FP8 GEMM (Measured, diagnostic, locked-2100).
- 10 chunks were done and none failed by 18:39Z.
- A research run collects `forms/` into the store when the jobs end, and the table follows from it.

**Need 7, proposed to bc-dd22acf8 (the MVP) as its next step, not for the running window:** ship `PEARLC_A_FORMS=s,one` for the MVP's prefill, passed as `config` to `ledger.variant_record` per #590.
- The measured basis is item 6's first fold: 5.3–5.8% off the call at 8,192³ (17:30Z) and gate 15.
- Which form each shape ships waits on the fill's table, above.
- #540's API is unchanged: `Pipeline(bufs=…, m_real=…)`, the step names, `keys_of` and `unit_block`.

## 18:14Z: queue item 3 done (-h2's level keys inside `hash_rows_b3s`, −4.3 to −9.0 µs a decode call); item 7's large-k fold and the joint gate pass

- **Broker:** `source=broker` since 17:45Z (sha256 checked, `ls-remote` and `gh repo view` pass). This VM is new, cloned at
  16:41Z. The old VM's unpushed commit and its uncommitted kernel were lost with it. I rebuilt the commit and recovered the
  kernel from the run inputs of `r20260930-173941-fa97` (sha256 `cd71f2d6`), then pushed both.
- **Item 3, `997ac6bd` on `cursor/h2-row-keys-b44b` (for bc-b139c29c to merge into #572, a fast-forward from `2018468b`):**
  - The kernel: `hash_rows_b3s` derives its segment tree's level keys itself. Its first ⌈log2 segments⌉ threads compute
    them after their segments (`b3s_level_key`, into shared memory), and its first CTA stores them at p3 when p3 is set.
    Those are `b3s_level_keys`' bytes.
  - The pipeline drops step `seg_keys_<tree>` and its launch.
  - 61 registers (51), spill-free. 18 KB of shared memory a CTA (17), which is five CTAs an SM either way. Every other
    kernel's SASS is unchanged, and the harness's sass gate (`80bff34c`) passes.
  - CPU: 118 passed, 1 skipped (no triton here). A new twin test holds the stored keys to `b3s_level_keys`' and the leaves
    to a null p3's.
  - **#540's API is unchanged.** Every buffer (`skeys_a`, `skeys_b`) and every launch argument stays, with the same bytes.
    `b3s_level_keys` stays in the cubin (bc-b139c29c's `h1_bench.py` launches it).
  - What changes: under -h2 there is no `seg_keys_*` step, and `_steps` already tolerates that. `seg_keys_a` is now a dead
    name in `pouw_pearl_c_device.py`'s step lists, `e2e.CONTROL_OMITS` and `profile_decode.py`, which I didn't touch
    (vLLM and the MVP's files). The device path's launch-order test drops `b3s_level_keys`.
  - **Timed (Measured, diagnostic, `r20260930-181014-5180`, lease GPU-5f1149a4, 2,077–2,092 MHz; the leaves and stored
    keys equal the two launches' bytes at every shape):**

    | A's row leaves | #572: keys + rows | fused | change |
    |---|---|---|---|
    | decode 32 × 4,096, alone | 28.45 µs | **20.61 µs** | −7.8 µs |
    | decode 32 × 4,096, 32 back to back | 16.84 µs | **12.54 µs** | −4.3 µs |
    | decode 32 × 14,336, alone | 34.40 µs | **25.38 µs** | −9.0 µs |
    | decode 32 × 14,336, back to back | 20.95 µs | **16.68 µs** | −4.3 µs |
    | prefill 8,192 × 4,096, back to back | 175.1 µs | 183.2 µs | +8.1 µs |
    | prefill 8,192 × 14,336, back to back | 371.1 µs | 370.4 µs | even |

  - At decode the fused kernel costs what #572's rows kernel alone did (20.35 µs), so the keys ride free.
  - At prefill k = 4,096 the keys cost one warp-wide compression a CTA: about 6% of a 64-segment row's issue slots
    (Derived: 16 → 17 warp-compressions), close to the 8 µs measured.
  - Taking several rows a CTA would spread that cost (the kernel would stride its grid, and a grid of `count` stays valid).
    I haven't built it: at most ~6 µs a prefill call (Estimated).
- **Item 7, `0e339c1e`: `h1_rows_stats` round by round.** A warp hashes 32 chunks of its row, then takes `stats_s5`'s
  iterations over those words from L2, so each reread follows its first read by one 32 KB round.
  - 92 registers, spill-free. Every other kernel's SASS is unchanged, and the sass gate passes.
  - `3fb3a02c` fixes the check: under `s`, the `forming=fold` rerun now replays the commit phase too. That rerun is what
    failed gate 14 (`r20260930-172411-d518`), not a kernel.
  - **Timed (Measured, diagnostic, `r20260930-173941-fa97`, 2,085–2,092 MHz, throttle 0x0; bytes equal to `stats_s5` plus
    `h1_rows_p` at every shape; times in ms):**

    | 8,192 rows | apart | `h1_rows_p` alone | leaf first (`b6a91929`) | round by round |
    |---|---|---|---|---|
    | k = 4,096 | 0.2203 | 0.1879 | 0.1806 | **0.1804** |
    | k = 8,192 | 0.3988 | 0.2591 | 0.2612 | **0.2617** |
    | k = 16,384 | 0.8245 | 0.4602 | 0.7172 | **0.5089** |
    | k = 28,672 | 1.4517 | 0.7995 | 1.2849 | **0.8904** |
    | decode 64 (32 committed) × 8,192 | 0.0425 | 0.0340 | 0.0356 | **0.0348** |

- **Gate 15 (ship15 = `0e339c1e`), `r20260930-175714-aced`, lease GPU-fb680060, both opt-ins (`PEARLC_A_FORMS=s,one
  PEARLC_EPILOGUE=w`):**
  - The check passes on 134 and 136 buffers; every consistency count is 0.
  - Clocks were 2,062–2,092 MHz, with the SW power-cap flag (0x4) set from the first timing on. Ship15's cubin sha256 is
    `1ac6d6d7…`.
  - **The call end to end (Measured, diagnostic, REPS = 9):**

    | | 8,192³ v2 | 8,192³ v2-hot | 16,384³ v2 | 16,384³ v2-hot |
    |---|---|---|---|---|
    | `s,one/split` + `w` | **2.381 ms** | **2.392 ms** | **14.67 ms** | **14.74 ms** |
    | `p,one/split` + `w` | 2.521 ms | 2.535 ms | 15.05 ms | 15.10 ms |
    | `w,nodes/split` + `w` (the default forms) | 2.854 ms | 2.870 ms | 16.34 ms | 16.38 ms |
    | over this build's plain FP8 call | 1.568× | 1.576× | 1.249× | 1.240× |

  - At 16,384³ the fold saves 2.6% over `p,one`, and 10% over the default forms.
- **Timed rows:** none run yet. When they do, they pass `--no-sampler` (17:27Z).

## 17:30Z: item 6's first fold is gated: A's row leaves and stats_s5 in one pass, 5.3–5.8% off the call at 8,192³ (opt-in `PEARLC_A_FORMS=s,one`)

- **`b03b52e9`, `b6a91929`:** `h1_rows_stats` hashes A's -h1 row leaf of each row (`h1_rows_p`'s bytes), then takes the row's
  `stats_s5` words from the row that the leaf's loads left in L2. It runs a warp a row, 4 warps a CTA.
  - 96 registers, spill-free. Every other kernel's SASS is unchanged. The harness's `sass-gate/v4` passes the cubin: its `.FTZ`
    ops are `stats_s5`'s own, inside the pinned div, sqrt and rcp sequences.
  - **Rows form `s`** (`PEARLC_A_FORMS=s,one`): step `hash_rows_a` also writes `stats_a`'s words (alpha, beta, 1/alpha,
    (s, ρ) and the screen's verdicts). Forming drops `stats_a` and runs A's side split under either forming. B's leaves are
    `h1_rows_p`'s. The default stays `w,nodes`.
- **Gate (ship13):** `r20260930-172032-0a08`, lease GPU-fb680060 (index 1), 2,062–2,092/12,481 MHz. The SW power-cap flag
  (0x4) was set after the 8,192³ timings, at about 375 W.
  - Ship13 hashes: tar sha256 `c4e3e774…17938b9e`, cubin `6047f75a…f58c1fa6`.
  - The check passes: 136/142/145 buffers. The `s` rerun holds A's forming buffers to the fixture too. CPU: 320 passed.
- **The call end to end at 8,192³ (Measured, diagnostic, run.py REPS = 9, lockstep epilogue):**

  | | `p,one/split` | `s,one/split` | change | default `w,nodes/split` |
  |---|---|---|---|---|
  | v1 | 2.646 ms | **2.493 ms** | −5.8% | 2.962 ms |
  | v2 | 2.584 ms | **2.442 ms** | −5.5% | 2.908 ms |
  | v2-hot | 2.608 ms | **2.470 ms** | −5.3% | 2.929 ms |

  - `hash_rows_a@s,one` takes 0.262 ms, the same as `h1_rows_p` alone (0.259–0.262 ms), so `stats_a`'s 0.19 ms is gone.
  - At decode (32 × 8,192 × 8,192) `s,one` gains nothing yet: 0.139–0.145 ms, equal to `p,fold/fold`.
- **How it was chosen (Measured):**
  - Scratch variants (`r20260930-171217-9010`): every variant's bytes equal `stats_s5`'s plus `h1_rows_p`'s, reps interleaved.
  - At 8,192³, leaf first takes 0.261 ms against 0.311 ms stats first on 128-thread CTAs, and 0.305 against 0.351 ms on
    256-thread CTAs. The two kernels apart take 0.398 ms.
  - A grid-strided version lost to a CTA per row group at every CTA count: 0.34 against 0.29 ms (`r20260930-170417-10dd`).
  - ncu: 49.8% of the fused launch's L2 reads hit, so A comes from DRAM once.
- **Large k (Measured, the same scratch run):** at 8,192 × 28,672 the rows in flight (112 KB each) overflow L2.
  - Fused 1.289 ms, apart 1.452 ms, `h1_rows_p` alone 0.805 ms.
  - Taking the stats round by round, right after each round of 32 chunks the leaf hashes, would keep each reread within
    about 32 KB of its first read. That would bring the fused kernel to about `h1_rows_p`'s time: −0.48 ms at k = 28,672
    (Estimated), and likewise at 16,384³.
  - It needs `row_leaf_v`'s rounds exposed. `h1_sm120.cuh` is GPU 2's, so I'll write it in `pearl_c_sm120.cu`.
- **Correction:** `b03b52e9`'s message cites `r20260930-163611` for the 0.258/0.191 ms figures. The run is `r20260930-163336-42a6`.
- **For #540 (bc-dd22acf8):** the API is unchanged, and the new form is opt-in. Under `s` there is no `stats_a` step, and
  `hash_rows_a` writes A's stats as well as its leaves. A no-write control that omits `hash_rows_a` therefore leaves the
  stats unwritten too; the verifier still rejects it. `s,one` saves 0.47 ms a call over #540's default `w,nodes` at 8,192³
  (2.962 → 2.493 ms, v1). See Need 7.

## 16:45Z: hash warps now save 2.0–2.3% of the call at 8,192³ (`9011cf5c`, L1 loads); `b` stays the default because of #540's control

- **The profile** (ncu, `r20260930-162140-7285`, one launch each at 8,192³ v2-hot, `--clock-control none`):
  - the y-only and hash-warp GEMMs run at the same L2 sector rate (Measured): 281 M sectors in 1.563 ms, 338 M in 1.864 ms;
  - so every added sector costs time about one for one;
  - the hash warps' `__ldcg` loads used 16.1 of each 32-byte sector, 38 M load sectors for 19 M of data.
- **`9011cf5c`:** the hash warps read their slot through L1 (`__ldca`, `LDG.E.128.STRONG.SM`).
  - Only `gemm_pearlc_w_u` and `_w_hu` change in SASS. No spills (plain loads spilled 4/16 B, so it's `__ldca`).
  - L2 reads fall 311 → 291 M sectors, as predicted.
- **Gate (ship11):** `r20260930-163336-42a6`, lease GPU-5f1149a4 (index 0), 2,092/12,481 MHz, throttle 0x0.
  - Ship11 hashes: tar sha256 `95da329f…f9ab`, cubin `dd2dd9cd…175b`.
  - The check passes: 123/129/131 buffers. Every consistency count is 0, including y and leaves under hash warps against the
    unfused launches. CPU: 320 passed.
- **The end-to-end call at 8,192³ (Measured, run.py, REPS = 9, default A forms):**

  | | lockstep `b` | hash warps `w` | change |
  |---|---|---|---|
  | v2 | 2.900 ms | **2.841 ms** | −2.0% |
  | v2-hot | 2.923 ms | **2.856 ms** | −2.3% |

  - The GEMM with hash warps now costs about what the lockstep one does: 1.792 against 1.793 ms (v2), 1.800 against 1.797 ms
    (v2-hot). But it also builds the leaves, which removes `hash_leaf` (54 µs) and its reread of 64 MB of digests.
  - **What's left:** 245 µs over the y-only GEMM. About 190 µs of that is C̃ and U going through L2 (34 M sectors, Derived at the
    measured sector rate), which a scratch handoff can't avoid. The digests' round trip is about 6 M sectors, and staging them in
    the 3 KB of free shared memory would save most of it (about 35 µs, Estimated). That's the one lever left inside this design.
  - **The lever outside it** (bc-fb55a759's mainloop): the y-only GEMM itself runs at the L2's sector rate, reading 8.7 GB for
    8,192³ at 128 × 128 tiles. Operand sharing across a 2-CTA cluster would cut those reads by about 25%, and would give the
    scratch traffic room. That's for bc-fb55a759 to judge; I haven't checked that sm_120 has TMA multicast.
- **Why `b` stays the default (#540's API).** Under `w` the leaves are written by `gemm_pearlc` (step `gemm_pearlc`, phase
  cleanup), and there is no `hash_leaf` step. #540's timed-pass control omits `("hash_leaf",)`, and `CONTROL_OMITS` names
  `hash_leaf` and `hash_msg`. So under `w` those controls would still write valid leaves, and the verifier would accept them.
  For #540 to take `w` (`PEARLC_EPILOGUE=w`, or `Pipeline.epilogue = "w"` before the first call), its controls must first
  change: omit `gemm_pearlc`'s leaves, or run the control call under `b`. The verifier reads leaves and `tree_t`, never
  `digests`, so the missing digests change nothing for it.
- **Next (item 6, the hashing folds):** A is read in full three times at prefill: commit 0.258 ms (`h1_rows_p`), `stats_s5`
  0.191 ms, `form_s5` 0.235 ms. `stats_s5` uses no key, so A's -h1 row leaves can be hashed in the same pass. That saves about
  0.19 ms a call (Estimated), and the bytes are the same.

## 16:25Z: hash warps are built and gated (item 5, opt-in `PEARLC_EPILOGUE=w`); a 0.8% gain so far, next is finding their 290 µs

- **`282fd3d0`:** `gemm_pearlc_w_u` and `gemm_pearlc_w_hu` (v2 and v2-hot; G = 0 only). v1's hash-warp kernel spilled, so v1 stays lockstep.
  - The consumers store C̃ and U to a two-slot scratch per CTA in L2 (147,456 B a slot).
  - The producer WG's three idle warps compute hash_msg_v's digests, then §13's leaves at hash_leaf_p's layout.
  - The call then drops its `hash_leaf` launch. Default `b` is unchanged, byte for byte (SASS of every earlier kernel equals ship9's).
  - #540's API is unchanged: the new mode is `PEARLC_EPILOGUE=w`, `Pipeline.epilogue`, and a `wscratch` buffer that the Pipeline sizes.
  - 168 registers (consumers 224, producer and hash warps 56), no local memory. SASS gate clean: 320 QMMA, `_hu` +64 FADD, no `.FTZ`
    arithmetic.
- **Gate (ship10):** `r20260930-161348-4b53`, lease GPU-fb680060 (index 1), 2,092/12,481 MHz, throttle 0x0.
  - Ship10 hashes: tar sha256 `4f842126…3550`, cubin `8806dfc1…c514`.
  - The check passes: 123/129/131 buffers. Every consistency count is 0, including the two new ones: y and leaves from the hash-warp
    kernel against the unfused launches, at grid all, 1 and 3.
  - CPU: 403 passed, 1 skipped (`benchmarks/pouw/tests`); the wall-clock test passes.
- **Diagnostic timings (Measured, run.py, REPS = 9, 8,192³):**

  | | v2 | v2-hot |
  |---|---|---|
  | call, lockstep `b` | 2.903 ms | 2.926 ms |
  | call, hash warps `w` | **2.882 ms** | **2.903 ms** |
  | gemm_pearlc_s (y only) | 1.531 ms | 1.549 ms |
  | gemm_pearlc_b (+ digests) | 1.775 ms | 1.797 ms |
  | gemm_pearlc_w (+ digests + leaves) | 1.832 ms | 1.846 ms |
  | hash_leaf (dropped under `w`) | 53 µs | 54 µs |

- **Reading:** hash warps save 21–23 µs a call (0.7–0.8%). But their GEMM is still 293 µs over the unhashed GEMM (v2-hot; the lockstep
  kernel's digests cost 246 µs). So the hashing isn't hidden yet. My guess is L2 traffic: 1 GB of scratch stores and loads at 8,192³,
  beside the mainloop's ~8 GB of TMA reads. I'm profiling that next with ncu on my lease, before tuning.

## 15:45Z: the decode host items are done (words, form_rows, the screen, bound launches); the staggered epilogue can't stagger on this mainloop, so I propose hash warps

**Done, in order (15:16Z queue items 1–4; the v1-hot estimate is dropped per 15:02Z).** #540's API is unchanged by all of them: the
`Pipeline(...)` signature, the default step names and buffers, `keys_of` and `unit_block`.
- **`38152ead`, the decode words kernel (A′F_B):** one 8-byte load per row and operand; a permutation within each aligned 32 applied to
  both operands, so every product and group sum is unchanged. It launches one warp per block. Measured (`r20260930-142654-b509`,
  locked-2100):
  - A′F_B at m32 decode: 41 µs → **21.7 µs** (v1), 20.6 µs (v2), 20.0 µs (v2-hot);
  - the decode call: 0.199 → **0.177 ms** (v1).
- **`d7f31a4c`, `form_rows`:** forming's per-row steps of one side in one launch (stats_s5, the row's E line, E′, and v2-hot's H), one
  warp a row. Opt-in: `PEARLC_FORMING=fold`, under step `stats_<tag>`. The default kernels keep their bytes, and the check reruns
  forming's words and codes under the other forming.
- **`2f366e9d`, then `5cd287a6`, the liveness screen in stats_s5 and form_rows.** It writes `live_<tag>` where the caller has that
  buffer (`b.get`, opt-in). Verdicts are 0 pass, 1 fail, 2 left to `live_row`, sound for k ≤ 2²⁰. `fixture.screen_verdict` is its
  bit-exact twin, and a CPU test holds it to `pearl_c_work.row_passes`.
  - **Changed in `5cd287a6`:**
    - A row with a NaN or an infinity is now 2, in the kernel and the twin. It was 0 for a NaN off the stride, which the twin can't
      represent: s5_stats raises InvalidArtifact.
    - A row whose fl(max|x|²) is under the band's low end passes without the second read. That is exact: every fl(x²) is at most
      fl(max|x|²), so nothing is dead or in the band.
  - **Why:** at 8,192³ every row is in flight at once (256 MB against the 128 MB L2), so the second read went to DRAM. It doubled
    stats_s5, 0.19 → 0.37 ms a side (`r20260930-151753-d728`). With the shortcut it is back to **0.191 ms**, and 14.5 µs at decode.
  - Registers: stats_s5 44, form_rows 64, no local memory.
- **`7e6fe50b`, bound launches (15:16Z item 2):**
  - **How it works:** `Pipeline.steps()` records each step's launches at the first call, with every buffer a placeholder
    (`0xB5 << 56 | slot`). After that it launches from prepared argument blocks (`Launch`: the function, grid, block, shared memory
    and Args, built once).
  - **Repointing and streams:** a word that named a buffer follows it when the caller repoints it (`b["y"] = ptr` or `b.update(...)`,
    as #540 sets y and leaves each call). The stream is the device's at the time of the call.
  - **Fallback:** a device without `recording` (#540's RecordingDev) gets unbound steps; nothing changes for it.
  - **Test:** a CPU test holds bound launches to unbound ones word for word, under every form and forming, after repointing, at 64 × 32
    and 128 × 128.
  - Host time to enqueue one call, bound against unbound (Measured, `call_host_us`, `r20260930-153301-99a4`):

    | | bound | unbound |
    |---|---|---|
    | 8,192³ v1 | 111 µs | 167 µs |
    | m32 decode v1 | 86 µs | 120 µs |

**Gate at `5cd287a6` (ship9):** `r20260930-153301-99a4`.
- Ship9 hashes: tar sha256 `3472afa9…8eef`, cubin `58daf83e…d587`.
- GPU-1cd543c7 (index 2); 2,092/12,481 MHz, 2,077–2,092 after, throttle 0x0.
- The check passes: 123/123/125 buffers (sm120, sm120-unpromoted, sm120-hot); every consistency count 0; every screen verdict equals
  the twin's.
- The ship before it, ship8 at `7e6fe50b` (`r20260930-151753-d728`, tar `42cad76e…250c`), passed the same check.
- **Diagnostic end-to-end calls (Measured, run.py, REPS = 9):**

  | variant | 8,192³ default | 8,192³ `p,one` + `fold` | m32 decode default | m32 decode `p,fold` + `fold` |
  |---|---|---|---|---|
  | v1 | 2.952 ms | 2.635 ms | 0.177 ms | 0.144 ms |
  | v2 | 2.901 ms | 2.608 ms | 0.172 ms | 0.137 ms |
  | v2-hot | 2.925 ms | 2.628 ms | 0.175 ms | 0.138 ms |

**Item 5, the staggered epilogue with leaves inside it (15:04Z, §13): not buildable as a stagger on `mainloop_sm120.cuh`.**
- **Why:**
  - The two consumer WGs share each B stage, and the ring is 3 × 32 KB, so WG1 can lag WG0 by at most about 3 µs.
  - The fused epilogue costs about 10.5 µs a tile (Derived: gemm_pearlc_b − gemm_pearlc_s, ship8's v1 1.826 − 1.596 ms, over the
    ~22 tiles each of 188 CTAs runs at 8,192³). A tile's mainloop is about 68 µs.
  - K3's half-tile stagger needs B loaded twice: the ~25% loss the coordinator already dropped.
  - Adding §13's leaves (about 12 µs a tile, bc-b139c29c) to the lockstep epilogue costs about 0.26 ms a call. That is excluded
    (15:04Z).
- **Proposal: hash warps.** The producer WG's three idle warps (NCW+1..NCW+3, 96 threads) do the hashing a tile behind:
  - **The consumers** store C̃ and U to a per-CTA two-slot scratch in global memory (2 × 128 KB a CTA, about 47 MB at 188 CTAs), with
    full/empty mbarriers (+32 B of shared memory).
  - **The hash warps:**
    - read C̃ and U back from L2;
    - run `b3_msg_digest` over the tile's 512 messages (about 14 µs, Estimated), then `discard.global.L2` the slot;
    - stage the 512 digests in the tail stage, then run §13's 16 chunk chains and the parents (about 13 µs, Estimated);
    - write each leaf at hash_leaf_p's layout.

    All of it runs under the next tile's ~68 µs mainloop.
  - **The host:** drops hash_msg and hash_leaf from hashing under this mode. It is opt-in, and the default stays as is.
  - **The check:** the fused leaves must equal hash_leaf_p over an unfused launch's hash_msg_v digests (§13's rule), and y must match
    bit for bit.
- **Registers decide which variants can use it** (local compile, nvcc 13.0.88). The producer gives up RP = 56, which leaves the
  consumers 224:
  - `_u` and `_hu` (v2, v2-hot) are spill-free at RP = 56;
  - v1's gemm_pearlc_b spills 12 B already at RP = 40 and 56 B at RP = 56.

  So the hash warps are for v2 and v2-hot, and v1 stays lockstep.
- **Default: I'm prototyping `gemm_pearlc_w_u` / `_w_hu` now** (Need 5 below).

## 14:10Z: v2-hot built and gated; GPU 2's `b0820016` and #449 at `5f6a31c7` merged; v2 at ρ = 1/1,000; the lint fixed

**v2-hot (11:50Z §3 item 2), implemented at `0d786883`, H_i by the 13:08Z rule bit for bit.**
- **`hot_a`:** one thread a row, over all m rows, filler rows included.
  - It reads the first 4 bytes of the keyed line hash of E_A's seed at (side 0, factor 2, line i), using `lines`' own
    block.
  - It computes t_i = fl32(α_i·ρ_i) and e_i = E(t_i) + 10 + [M(t_i) ≥ 0x3504F4].
  - H_i = (h & 0x807FFFFF) | ((e_i + 127) mod 256) << 23. The mod only matters off the domain.
  - It is one launch in forming, between stats_s5 and eprime.
- **The chain:** the `_hu` GEMMs start each row's accumulator at H_i in place of +0: gemm_ct_hu, gemm_pearlc_hu,
  gemm_pearlc_s_hu, gemm_pearlc_b_hu, and decode's gemm_ct_d_hu and gemm_pearlc_d_hu.
  - The start goes through a new `INIT` flag on `mainloop_sm120.cuh`'s `tile<U, LATE, INIT>`. It defaults off and is
    static-asserted to G = 0.
  - All 65 earlier kernels are SASS-identical.
- **U's order (my default; bc-9914c188 to pin it):** C̃ is the hot chain's word, stored as is.
  U = peel(fl(C̃ − H_i)): one `__fsub_rn` (nearest even) per word, right before the peel's HMMA.
  - The fused `_b` kernel digests that (C̃, U).
  - The 32-column words (A′F_B, B̃F_A, G) stay on the `_u` kernels, from +0.
- **Honest cost (Measured, SASS):** the same QMMA and HMMA counts as `_u`, plus one FADD per word: +64 per thread on the
  128 × 128 peeled kernels, +16 on gemm_pearlc_d_hu, +0 on the ct kernels. The build test asserts it.
  - Registers: 168 on the 128 × 128 kernels, 116 on gemm_pearlc_d_hu, 29 on hot_a; no local memory.
- **The fixture's reference:** `fixture.hot_starts` implements the rule from the scheme's own keyed line hash.
  - The chain is `group_sum_total_batch` from H_i.
  - For 64 cells it checks against `atom.step` from H_i, then `fp32.add(C̃, −H_i)`, then the peel.
  - Hot C̃ differs from v2's on more than 99% of the fixture's words.

**Gate on the card:** `r20260930-134322-4b49`, run at `0d786883` from ship5.
- Tar sha256 `6d820ea1…a9b8`, cubin `3de9174a…0db9`.
- GPU-fb680060 (index 1), locked-2100.
- run.py's bit-exact check passes for all three variants: sm120 94/94 buffers, sm120-unpromoted 94/94, sm120-hot 95/95,
  and every consistency count 0.
- **Note:** gpu-lease handed me GPU-fb680060, which the pous root's 13:23Z keep-free holds, for 4 s (13:43:38–13:43:42Z).

**Diagnostic timing, v2 against v2-hot** (Measured, run.py, REPS = 9, per-step medians, same run):

| | 8,192³, fused | m32 decode (64 × 64) |
|---|---|---|
| hot_a | 11.6 µs | 11.4 µs |
| gemm_ct (the chain alone) | 1.5179 / 1.5132 ms | — |
| the call's GEMM | gemm_pearlc_b 1.7794 / 1.7946 ms (+0.85%) | gemm_pearlc 0.0428 / 0.0433 ms |
| call, end to end | 2.9138 / 2.9270 ms (+0.45%) | 0.1939 / 0.1980 ms |
| call without hashing | 2.0029 / 2.0252 ms | 0.1088 / 0.1180 ms |

- At decode, hot_a sits at the same ~11 µs launch floor as eprime.
- **Next lever:** fold hot_a into stats_s5, which already has α and ρ for the row, and save the launch.

**The merged head `e4f519c6`:**
- **GPU 2's `b0820016`:** h1_sm120.cuh and the per-epoch level-key table.
  - Its forms are opt-in under `PEARLC_A_FORMS=p,one|p,fold`, and the default stays `w,nodes`.
  - #540's API is unchanged: `Pipeline(dev, m, n, k, variant, keys, xa, xb, bufs=…, m_real=…, bm=…, fused=…)`, the default
    forms' step names and buffers, `keys_of` and `unit_block`.
  - The new `ctr_*` buffers are only read under `one` and `fold`.
  - `fake_cuda.c`: GPU 2 fixed the same 64-name overflow at 128. I kept mine: 256 names, and each abort says why.
- **#449 at `5f6a31c7`:** a clean merge.
- **The wall-clock lint (13:33Z, 13:49Z):** no `timeout=` on the six subprocess runs in `test_pearl_c_sm120.py`. Each waits
  on its process and checks `returncode`, as #449's tests do. There is no `ALLOWED` entry, and
  `tests/test_no_wall_clock.py` passes. #540 takes the fix from `f2c0caf8` on.
- **γ's basis (13:52Z):** `PearlCSm120Unpromoted.rho = 1/1,000`, v1's stays 1/400, and TT_OUT's γ₀ = 1/400 for both.
  - v2's cap at 8,192³ is **0.3616%** (Derived; it was 0.5112%). v1's is 0.5105%. The chain-only readings are 0.6879% for
    v2 and 0.9586% for v1.
  - The basis string names both, and the test pins 0.3616%.
  - Prices: the device record `pearl_c_device.SM120` (and `SM120_UNPROMOTED`) uses #449's `SM120_PRICES`: FADD 8, BF16 MAC 2,
    forming 40 + 1. Not 8.38.
- **Tests:** `benchmarks/pouw` 402 pass, with the nvcc 13.0 sm_120a build gate; `protocols/pouw` 214 pass.
- **The card gate:** `r20260930-140411-aeb6`, run at `e4f519c6` from ship6.
  - Tar sha256 `a7c282d8…9b2c`, cubin `61a02952…1e41504`.
  - GPU-af0bf9e0 (index 7), 2,092/12,481 MHz (locked-2100).
  - run.py's check passes: sm120 104/104 buffers, sm120-unpromoted 104/104, sm120-hot 105/105. Every tree, seed_A and
    E_A line key is rerun and passes under `p,one` and `p,fold`. Every consistency count is 0, at both shapes.
  - **Diagnostic end-to-end calls (Measured):**

    | variant | 8,192³ | m32 decode |
    |---|---|---|
    | v1 | 2.956 ms | 0.199 ms |
    | v2 | 2.912 ms | 0.202 ms |
    | v2-hot | 2.937 ms | 0.198 ms |

  - **Decode's `p,fold` forms (Measured, v1):** commit_a is one launch at 49.6 µs; tiles_t is 40.0 µs.
- **FTZ:** 16 arithmetic `.FTZ` ops on ship6, as before: stats_s5 12, lines 2, plainq 2, all inside the IEEE div, sqrt and
  rcp expansions. Neither `hot_a` nor GPU 2's kernels adds one.
  - The rest are the integer-division idiom (`F2I`/`UF2I.FTZ.U32.TRUNC.NTZ`) and `FSETP` inside those expansions.
  - toolchain.txt records nvcc 13.0.88 and `-O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -fmad=false -Xptxas -v
    -cubin`, with no FTZ or fast-math flag. Those are the flags the harness's v3 pins should match (13:52Z).

## 13:15Z: the epilogue measured before fusing (12:23Z): keep the fused digests at prefill

**Run `r20260930-131029-f041`** (`f0f9b1ab`, ship4, the same cubin as ship3):
- GPU-2b59d5fe (index 6), locked-2100, REPS = 9. run.py's check passed on all 94 buffers of both variants.
- Measured, diagnostic run.py timing.
- `deferral` times the unfused GEMM (gemm_pearlc_cu, which stores C̃, U and y) alone, and again beside the previous call's
  `-h1` hashing (hash_msg, the tile leaves and the tile tree) on a least-priority, non-blocking side stream.

| shape, variant | GEMM alone | hashing alone | pair (same / main at greatest priority) | pair − GEMM | fused digests (b − s) |
|---|---|---|---|---|---|
| 8,192³ v1 | 1.781 ms | 0.354 ms | 2.094 / 2.104 ms | 312 / 323 µs | 232 µs (1.833 − 1.602) |
| 8,192³ v2 | 1.718 ms | 0.350 ms | 2.031 / 2.031 ms | 313 / 313 µs | 241 µs (1.773 − 1.532) |
| m32 decode v1 | 0.046 ms | 0.050 ms | 0.068 / 0.071 ms | 22 / 25 µs | not fusable at 64 × 64 |
| m32 decode v2 | 0.042 ms | 0.050 ms | 0.068 / 0.071 ms | 26 / 29 µs | not fusable at 64 × 64 |

- **Prefill: fuse.** Overlap hides only about 12% of the 354 µs of hashing, because the GEMM holds every SM.
  - The pair's 312 µs is far above the 3 µs bar.
  - Fused costs 232 µs, and it also saves the C̃ and U stores: 179 µs, 1.781 against 1.602.
- **Decode: deferring hides about half of the hashing** (22 µs against 50 µs serial).
  - A digest-fused 64 × 64 epilogue, gemm_body's equivalent of gemm_pearlc_b, is the next decode step. -h3's tile fold
    goes in the same place.

## 12:56Z: the `-h1` gate passed at `9f1e33b1`; the head for #540 (11:50Z §3 item 1)

**Run `r20260930-124211-a304`:**
- **Setup:** GPU-fb680060 (index 1, the kept-free GPU, which I then released), locked-2100. The lease was
  `gpu-lease 1 --wait --max-min 20` for bc-18346d9c, 12:42:29–12:49:41Z.
- **Tree:** `f9b3338e` = `9f1e33b1` plus the harness at `f5e584af` (#491's `8d04bfe5` with the shared-memory gate fix).
- **Build:** ship3, tar sha256 `05bcb764…6d7`, cubin `62b01ad2…8e46`. nvcc 13.0.88,
  `-O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -fmad=false -Xptxas -v -cubin`, no FTZ or fast-math flag.
- **run.py's bit-exact check:** 0 words differ anywhere. That covers both variants, both headline shapes, the fused y and
  digests against the unfused call, and form_s5 against scalar and r144.
- **The harness:** both arms, with the fp8-e4m3 baselines (cuBLASLt autotuned and CUTLASS) in the same run.
  - The SASS gate passes: 16 `.FTZ`, all in the exempt IEEE slow paths.
  - Every arm, baseline, known-bad and dependent-chain gate passes.
- **The verifier (`verity_pouw.audit.Verifier`, Sampled(3), at `f9b3338e`):**
  - It ACCEPTs all 4 transcripts (2 arms × 2 shapes). Each dump starts from 0xA5 poison and reruns the weight side and the
    call.
  - It REJECTs all 4 negative controls, each on "activation opening" with `root_A a5a5…`.
  - Every line names the transcript's sha256 and `run r20260930-124211-a304`. The harness's verify.py exits 0, and
    `bench.json` carries the rows' `--verifier-accept` and `--transcript` fields.

**Numbers (Measured, graph medians over 20 reps, against the same run's best fp8-e4m3 baseline):** these are gate
diagnostics, not panel rows. At 8,192³, 32 to 34 of the arm items were flagged for throttling.

| shape | arm | total | hash-free | baseline |
|---|---|---|---|---|
| 8,192³ | v1-h1 | 2.009× (2.922 ms) | 1.397× | 1.455 ms, cuBLASLt algo 35 |
| 8,192³ | unpromoted-v1-h1 | 1.974× | 1.351× | same |
| m32 decode (dependent chain) | v1-h1 | 4.365× (0.218 ms) | 2.413× | 0.0500 ms |
| m32 decode (dependent chain) | unpromoted-v1-h1 | 4.313× | 2.358× | same |

- SM clock median 2,085 MHz (range 2,077–2,092).
- The weight side takes 1.05 ms per weight and epoch (0.72× the baseline at 8,192³).

**The E4M3 cast in form_s5: at most 2.87 units per code, under 8.72, on two dies (Measured, in-kernel).**
- The measure is form_rate − form_rate_nocast, over 3,080,192 codes, with every code equal to the scalar reference.

| die | run | 160-byte stride (kept) | 144-byte stride |
|---|---|---|---|
| GPU-5f1149a4 (index 0) | `r20260930-120753-303f` | 1.74–2.87 | 2.39–2.77 |
| GPU-fb680060 (index 1) | `r20260930-124211-a304` | 0.83–2.47 | 2.32–2.47 |

- **Bank conflicts** (ncu `l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_st` on the check's launches, `…-303f`):
  - 160 bytes: 0;
  - 144 bytes: 2-way (2,048 conflicts per 1,024 stores).
- form_s5 at 8,192³ is memory-bound: 0.238 ms with any of the cast variants. So γ at 8.72 can be published (10:29Z).

**For #540 (bc-dd22acf8): `9f1e33b1`, and what changed since the head #540 was written against:**
- **Unchanged:** `Pipeline(dev, m, n, k, variant, keys, xa, xb, bufs=…, m_real=…, bm=…)`, `keys_of`, `unit_block`, and every
  step name except the one below.
- **`fused`:** `fused=None` means fused where it applies, which is 128 × 128 tiles over m_real = m rows.
  - Fused, step `gemm_pearlc` is gemm_pearlc_b: it stores y and the digests, never C̃ or U, and **`hash_msg` is not a
    step**.
  - #540's `_steps` must treat `hash_msg` as optional when `pipe.fused`, or pass `fused=False`.
- **`tma`:** the 128 × 128 GEMMs read tensor maps, and the Pipeline allocates its own `tma` if `bufs` has none, freeing it
  with the Pipeline. #540's stand-in device needs `tmap(ptr, depth, rows, box_rows=128) -> bytes` (128 bytes).
- **Tested:** with those two #540-side lines, all 11 of `test_pearl_c_vllm.py` pass on #540 merged with `9f1e33b1`
  (a scratch merge, not pushed).
- **Other changes:**
  - `at`, `bt`, `faT32`, `fbT32` and `fbT128` are in K32 order: within each aligned 32 of k, byte 8q + 2b + s holds column
    8b + 2q + s. The products are unchanged.
  - `form_scalar` is now `form_alt`.
  - The peel buffers are read lazily, so a weight-side-only `bufs` works (`9f1e33b1`).
- **Ship:** `bash benchmarks/pouw/pearl_c_sm120/build.sh <dir>` from `9f1e33b1`. `benchmarks/pouw/pearl_c_sm120/` is
  byte-identical in #540 merged with it, so ship3 (above) is that build.

## Answers to the coordinator (10:57Z, 11:00Z, 11:06Z)

1. **#449 at `61d0298d`: merged** (`0b9da17f`). `pearl_c_device.SM120.prices` is `SM120_PRICES` (FADD 8, BF16 2, forming
   40 + 1), the `prices` stand-in dropped; `PearlC` takes its prices from the device unless given (an override is named
   `@sm_…`); `debit_units(atoms, elements, prices, device)`, `atom_units(SM120) = 34`. The sm_120 credit (`PearlC.credit_of`,
   `pearlc_arm.gamma`) reads them. `benchmarks/pouw/pearl_c/bench.py` is the H100 bench, pinned to `Gamma.lean`'s values,
   so it keeps `H100_PRICES`. protocols/pouw: 214 tests pass; the bench tests: 18 pass.
2. **FTZ.** None of my builds uses an FTZ flag: `nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a -fmad=false
   -Xptxas -v -cubin`. The `.FTZ` ops in `lines`, `plainq` and `stats_s5` come from ptxas's IEEE expansions of `/`,
   `sqrtf` and `__frcp_rn` under default flags. stats_s5 has one fsqrt, two fdiv and one frcp; lines one fdiv; plainq two
   fdiv. The harness's gate exempts exactly these (16 / 16, `6-harness.md`). My kernels have no rsqrt, so rsqrt_rn doesn't
   apply here. Builds are nvcc 13.0.88 only. From now on build.sh writes `nvcc --version` and the full flag line into
   `toolchain.txt`, which the arm's build record carries.
3. **The E4M3 cast, and the fused cast (A′ never stored): recommendation, to confirm with bc-fb55a759.** A fused cast
   doesn't pay on this mainloop. A′'s 128-row panel is re-read by N/128 = 64 column tiles at 8,192, so forming it inside the
   GEMM repeats the forming 64× per element: about 64 · 41 = 2,624 units against the chain's 8,192, or 32% (Derived).
   Moving FP32 x through TMA instead of the codes also quadruples the operand traffic. So A′ stays stored once, and form_s5
   gets 64-bit shared stores at the stride that measures conflict-free (144 vs 160 bytes, ncu
   `l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_st`). The column-pair transpose will be gated against the unpermuted
   reference at every pairing: A′ with B̃, A′ with F_B's lines, B̃ with F_A's, and the twin's reader. In the queue after the
   `-h1` arm.
4. **Mainloop: adopted.** `mainloop_sm120.cuh` at `356313e9` is unchanged (`1c2b9bfb`). Every 128 × 128 GEMM runs on it
   (`024eb834`: gemm_plain, fast, ct, pearlc, pearlc_s, and pearlc_b, the fused -h1 digests from GPU 2's `f2e5a32e`, each also
   with _u). K3 is dropped. GPU 2's digest scratch is 1 KB per warp, 8 KB per CTA, in the drained peel stage (within 32 KB).
   Notes:
   - Under nvcc 13.0, v1 runs `tile<1>`, because `tile<2>` spills.
   - A never-taken block boundary after the chain keeps gemm_plain spill-free.
   - The SASS gate passes: 62 kernels, 168 registers, no local memory; 192 QMMA per 3-stage tile; 64 HMMA in the peel, 16 in
     the fused `_b` (a loop of 4).
   - The 64 × 64 (decode) and 128 × 32 kernels stay on `gemm_body`.
5. **Timing the -h1 arm through the harness:** gated at `9f1e33b1` (see the top). The timed rows come from a whole-node
   window, with the verifier's accept, per-rep SM clocks and the negative control.
6. **Who writes the bytes forming reads, on my decode path.** Confirmed with one correction:
   - The harness's derive step writes A: FP32, m_real = 32 rows.
   - The next step is not a kernel: the arm copies those rows with `cuMemcpyDtoDAsync` into its zero-padded buffer of 64
     rows (`_Call.xa`, only when m isn't a multiple of 64).
   - Forming (`stats_s5`, `form_s5`) and A's frame-b3 row tree (`hash_rows_w`) both read that padded buffer. The copy
     changes no byte, so the rows forming reads are the harness's rows.
   - At prefill (64 | m) there is no copy: forming reads the harness's buffer directly.

   **For `-h2`** (bc-b139c29c's `b3s_segment_key` / `b3s_segment_regs`): the leaves need a kernel that reads every byte
   forming reads.
   - At decode, I replace the copy with a copy kernel that hashes the segments from the registers it stores.
   - At prefill, `stats_s5` (the first full read of A's FP32 rows) folds them in.

   Both hash the FP32 words forming reads, before its cast, and those are the bytes it reads. A′'s codes are its output.
   bc-b139c29c: tell me if the rule means the codes instead.
7. **`-h3` tile-hash fusion (11:06Z, 2):** `gemm_pearlc_b` already hashes the messages (C̃, U) from registers. The next
   step is to fold the tile leaf (hash_leaf_p over a 64 × 64 tile's 64 digests) into the same epilogue: one warp pair holds a
   tile's 32 digests. That goes after the -h1 arm's timed row.

## v2-hot: what's left (the kernels and the check are built; see the top)

- **The arm, `PearlCSm120Hot`, and the verifier's replay from H_i:** these wait on bc-9914c188 adding H_i and U's order to
  the scheme. After that the panel line is `v2-hot`.
- **The kernels:** fold hot_a into stats_s5.

## Results (locked-2100, gates first)

- Attempt 3b (Measured, `r20260930-075931-4e4a`, one GPU, harness `0d1d6615`): prefill 8,192³ v1 2.376×, v2 2.310×; decode m32
  on the dependent chain, v1 4.733×, v2 4.687×. The TurboSHAKE commitment, superseded by -h1.
- v1-h1 unfused on the old cp.async mainloop (Measured, `r20260930-094734-2e93`): 8,192³ call 3.868 ms against cuBLASLt's
  1.475 ms. Voided (11:50Z): no poisoned dump.
- The `-h1` gate at `9f1e33b1` on the mainloop, fused (Measured, `r20260930-124211-a304`, gate diagnostics, see the top):
  - 8,192³: 2.009× (1.397× hash-free);
  - m32 decode: 4.365× (2.413×);
  - 4 ACCEPTs and 4 negative-control REJECTs.
- v2-hot, gated (Measured, diagnostic, run.py): at 8,192³ the call costs +0.45% over v2 (`r20260930-134322-4b49`).
  At the merged head all three variants pass (`r20260930-140411-aeb6`).
- γ at 8,192³, cap / chain-only (Derived, the arm's reading, `SM120_PRICES`, TT_OUT γ₀ = 1/400):
  - v1 (ρ = 1/400): 0.5105% / 0.9586%;
  - v2 (ρ = 1/1,000): 0.3616% / 0.6879%.
  - The panel publishes from the Lean pins (13:49Z), not from these.

## Run lines

~~~sh
# ship: bash benchmarks/pouw/pearl_c_sm120/build.sh <dir>/ship (nvcc 13.0; toolchain.txt has the version and flags)
# run tree: this branch + benchmarks/pouw/harness at f5e584af (cursor/harness-shmem-gate-b44b), research from an origin/main worktree
# the kernel check at the merged head as run (r20260930-140411-aeb6): gpu-lease 1 --wait --max-min 14, then
#   VARIANTS="sm120 sm120-unpromoted sm120-hot" SHAPES="8192 32x8192x8192" REPS=9 python3 ship/run.py ship/check/check.json
# the -h1 gate as run (r20260930-124211-a304): run.py check, bench.py --shapes headline --families fp8-e4m3, then verify.py
R='research run --on vy-nebius-2 --project verity --campaign pouw --source <run tree> --cwd source --env GPU_LEASE_WHO=bc-18346d9c
   --send ship.tar --send libpouw_harness.so --send build.json --send server.md'
$R -- gpu-lease 1 --wait --max-min 8 -- bash -c '<gates: run.py check + harness untimed, then verify.py>'
$R -- gpu-lease 8 --wait --max-min 20 -- bash -c '<timed: the harness on the first leased GPU>'
~~~

## Needs

1. **bc-fb55a759:** confirm the fused-cast reading in answer 3, or show a mainloop order that forms A′ once per row panel.
   Also: v2-hot now uses an `INIT` flag in your `mainloop_sm120.cuh`, `tile<U, LATE, INIT>` and
   `stage_body<FIRST, LAST, LATE, INIT>`, in `0d786883`.
   - The first mma accumulates onto acc, which the caller set to H_i, instead of starting from +0.
   - It defaults off, and `static_assert(!INIT || G == 0)`.
   - Will you take it into your header, or name the hook you'd rather have?
2. ~~**bc-dd22acf8 (#540):** `hash_msg` optional in `_steps` when `pipe.fused`, and `tmap` on the test's `RecordingDev`.~~
   **Resolved:** #540 has it at `9f31150f` (`_steps`' `optional` set).
3. **bc-0de2d624 (the harness, #491):** will you take `f5e584af` (branch `cursor/harness-shmem-gate-b44b`)?
   - **The bug:** the SASS gate refused every arm with exit 7 on node 2, the example arm included, because it read the
     CUDA driver's four `/dev/zero (deleted)` shared mappings as deleted files (`r20260930-115405-c561`).
   - **Also:** #491 still neither poisons the dump nor asks for a negative control. My arm does both itself; other arms
     need the harness to.
   - For v3's FTZ pins, my build's toolchain is nvcc 13.0.88 with the flags above (the 14:10Z section).
4. **bc-9914c188:** will you pin U's order for v2-hot as built (U = peel(fl(C̃ − H_i)), nearest even, C̃ stored before
   the removal) and add H_i (the 13:08Z rule) to the scheme?
   - The kernels also compute H_i for filler rows, with the exponent field mod 256 off the domain. Say whether the scheme
     should state it that way.
   - With the scheme in place I'll build `PearlCSm120Hot` and its replay.
5. **The coordinator and bc-fb55a759: the staggered epilogue (15:16Z item 5).** On the shared-B-ring mainloop it can't stagger
   (see the 15:45Z section). Do you accept hash warps instead?
   - The three idle producer warps would hash a tile behind, for v2 and v2-hot only, with v1 kept lockstep.
   - It raises the producer's `setmaxnreg` to RP = 56 for those kernels, and adds a per-CTA global scratch (about 47 MB) and two
     mbarriers.
   - For bc-fb55a759: the hash warps need `roles()` to let warps NCW+1..NCW+3 run a loop rather than exit. I'd do that in `ml_body`
     with no change to your header. Say if you'd rather own that hook.
   - Default: I build it now as an opt-in mode and report the gate and its timing against gemm_pearlc_b_u and gemm_pearlc_s_u.
   - **Done (16:45Z):** built, gated, −2.0% (v2) and −2.3% (v2-hot) a call at 8,192³ (the 16:45Z section). What's still open:
     do you accept it as v2's and v2-hot's prefill epilogue? I did it all in `ml_body`, with no change to your header.
6. **bc-dd22acf8 (#540) and the coordinator: take hash warps for v2 and v2-hot at prefill?** It needs #540's negative controls
   to stop relying on a `hash_leaf` step (the 16:45Z section). Default: `b` stays the default until you say so; the switch is
   one environment variable.

7. **bc-dd22acf8 (#540) and the coordinator: take `PEARLC_A_FORMS=s,one` for the MVP's prefill?** At 8,192³ it saves 0.47 ms
   a call over #540's default `w,nodes` (2.962 → 2.493 ms, v1, the 17:30Z section), and 0.15 ms over `p,one`.
   - What changes: there is no `stats_a` step, and `hash_rows_a` writes A's stats as well as its leaves. The step names are
     otherwise unchanged, and `Pipeline(bufs=…, m_real=…)` is too.
   - Default: the call's forms stay `w,nodes` until you say so. The switch is one environment variable, or
     `pipe.rows_form, pipe.tree_form = "s", "one"` before the first call.

## Lessons

- A VM reset (10:51Z) wiped the checkout, /tmp, ~/.research, uv and CUDA along with all uncommitted work. The store
  survived. Commit and push work in progress often.
- `research run --source` ships only a clean commit. Run the research CLI from an origin/main worktree: branches stacked
  on #449 carry an older `tools/research`.
- The harness fills operands on its own non-blocking stream; an arm that warms up on the null stream synchronizes first.
- `fake_cuda.c`'s fixed name table silently dropped the 65th kernel name, so a dry run failed later as
  cuModuleGetFunction 500. GPU 2 and I both hit it. Now it aborts and names the limit.
