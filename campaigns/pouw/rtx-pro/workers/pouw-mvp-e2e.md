---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

# PoUW MVP e2e on node 2: Pearl-C sm_120 inside vLLM

**6:38 PM PDT: window 7 is verified** (`r20260930-221231-3dd1`, `-h2`, both arms under CUDA graphs): decode 3.402× graphed FP8 and 1.263× eager; prefill 1.647× graphed and 1.617× eager. Accept, accept, reject, reject. Its rows go through compute-accounting's chain (bc-ccd30e80, then bc-2aa33ad8). My coordinator is compute-accounting (bc-e90634dd) from 5:52 PM PDT, and I report in research-notes `lanes/accounting/`. **7:16 PM PDT:** window 8 (#610 `e442d494`, `-h2`+`s` with the trims) is queued as `r20261001-020519-e39d`, lease 7:20 PM PDT; migration handoff written (`20261001T0215Z-handoff-from-bc-dd22acf8-migration`).

Worker bc-dd22acf8 (the PoUW MVP lane), for the RTX PRO coordinator bc-2aa33ad8. The plan, the run and the job spec are in [`docs/pouw/mvp-e2e.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/mvp-e2e.md), "RTX PRO 6000". The code is draft [#540](https://github.com/danielreuter/verity/pull/540) (`cursor/pouw-rtxpro-e2e-4f91`, head `8ca97148`). It is stacked on #435 and merges GPU 1's `cursor/pearl-c-sm120-h1-b44b` at `9f1e33b1` as its run tree. No GPU time used.

broker: source=broker 17:42Z

## Checkpoints

- 11:30Z: #540 pushed. `pouw_pearl_c_device` drives GPU 1's `run.py` `Pipeline` at each linear's `apply` (scheme `pearl-c-sm120-v1-h1`). `verify_run.py` is the reference verifier on a pass (`pearl_c_work`'s draws and exclusion tiles). `e2e.py` is the run. 8 new CPU tests pass, including the verifier agreeing with `pearl_c_work.audit` tile for tile.
- 11:42Z: `c7033d67`: after bc-b139c29c's 11:33Z finding, retained passes start from poisoned outputs (`0xA5`), and the gate has a negative control (tile leaves omitted, whose root must differ). 10 CPU tests.
- 11:34Z: node 2's environment is ready (setup run `r20260930-113242-c755`, CPU only, 82 s): `/workspace/pouw/mvp-e2e/venv312` with vLLM `d9105ea80` cu129 and torch 2.13.0+cu129, and Llama-3.1-8B-Instruct at `a2856192` in `/workspace/hf`. A CPU import check in that venv passes: the engine arguments, `apply`'s signature and the modules.

- 12:09Z: `285fe9c2`, for the coordinator's 11:50Z item 5:
  - the window adds the negative control the verifier must reject: one decode prompt, retained on poisoned buffers, writing none of the commitment;
  - `verify.sh` passes only on accept, accept, reject;
  - the verifier's lines name the window's run;
  - `panel_rows.py` writes the two rows (`pearl-c-sm120` v1-h1, `e2e-llama31-8b-vllm-m8192` and `-m32`). 11 CPU tests.
- 12:05Z: checked for the stray agents `bc-3076d4d9` and `bc-d808df26`: neither wrote to this file, #540's branch, research-notes, the store or node 2 (no run, fill job, lease or `passes/` under my owner id but my 11:32Z setup). Nothing to revert.

- 12:18Z: `c5ab7a1c`, for the root's ruling (12:11Z):
  - stock vLLM FP8 stays the baseline;
  - its engine and the Pearl-C engine stay resident in two processes on the leased GPU, the reps alternating (fp8, pearlc, fp8, pearlc-nohash, fp8, bf16), each engine idle while the other times;
  - the fallback is ABAB blocks, recorded and stated in the rows;
  - I append the rows after job 3. 13 CPU tests.

- 13:25Z: **`304436d3`, the tree ready for the window.**
  - `3a25cdcb` merges GPU 1's gated `-h1` head `9f1e33b1` (run `r20260930-124211-a304`). The merge was clean, and the lock is current.
  - `304436d3` resolves GPU 1's API question: `hash_msg` is optional in `_steps` when `pipe.fused`, and the test's stand-in device has `tmap`. The e2e therefore times the fused path GPU 1 gated at 128 × 128 tiles (every prefill call), and the unfused 64 × 64 path at decode.
  - CPU tests: 14 of `test_pearl_c_vllm.py`, including a fused-path call, plus GPU 1's `test_pearl_c_sm120.py`, the PoUW adapter suites and `protocols/pouw`: 302 passed, 9 skipped.
  - The wall-clock lint still fails only on `test_pearl_c_sm120.py`'s `timeout=` arguments, six now with `9f1e33b1`'s line 793.

- 13:37Z: **window `r20260930-133017-7242` failed before timing.** The stock-FP8 engine's first sampling call JIT-compiles FlashInfer's top-p/top-k module, which runs `ninja`, and `ninja` is only in the venv.
- 14:08Z: **`1cb80939`, the tree ready again.**
  - `e2b43ca3`: `window.sh` puts `$WORK/venv312/bin` first on PATH and pins `FLASHINFER_CUDA_ARCH_LIST=12.0f`, which is what the card's (12, 0) maps to. `setup.sh` builds FlashInfer's sampling module with the same settings and no GPU (setup run `r20260930-134243-b409`: `sampling.so` in `~/.cache/flashinfer/0.6.18/120f`, recorded in `ready.json`). The window's `jit-built.txt` lists any FlashInfer library built during a run. `verify.sh` spawns no venv tool and is unchanged.
  - `1cb80939`: NVML ignores `CUDA_VISIBLE_DEVICES`, so `window.sh`'s `nvidia-smi -i 0` read physical GPU 0. The first smoke (`r20260930-134459-8c03`, leased on index 1) therefore sent GPU 0's UUID to `run.py`, which refused it before any launch. Now the identity query, `PEARLC_EXPECT_UUID` and `e2e.py`'s per-rep clock and memory readings all use `GPU_LEASE_UUID`'s first UUID. The earlier window leased all 8 GPUs, so its first GPU happened to be 0.
  - **Smoke `r20260930-140351-6cf1`** (`gpu-lease 1`, untimed, GPU-fb680060, 2:27 in all; exit 0):
    - no FlashInfer JIT (`jit-built.txt` empty);
    - the FP8 engine started in 73 s (19.2 GB), with its first sampling calls in 1.5 s;
    - the Pearl-C engine started beside it in 35 s, including the install and the 16 gate rows, all of which passed: served y within 5.3% relative RMS with hashing and 4.6% without, every commitment repeated, every negative control rejected. The two engines together use 63.9 GB of 96;
    - first sampling calls: 1.2 s in BF16, and 12.4 s in `pearlc` for 16 chat prompts of 48 tokens, all committed;
    - all three modes answer coherently. Greedy-token agreement with BF16 is 0.79 for FP8 and 0.52 for Pearl-C.
  - The window's estimate is now about 6–8 min: 1:50 of engine starts, then the chats, the reps and the verify passes, under the same 19-min cap.
  - 15 CPU tests.

- 14:14Z: **window 2 (`r20260930-141053-b3c0`, at `1cb80939`) timed every mode; its verify pass failed at start.**
  - **Unverified timings, which don't count:**
    - prefill (m = 8,192): `pearlc` 0.786 s against stock FP8's 0.284 s, **2.77×**. The GEMM is 0.75× FP8, hashing and records 1.36×, the rest 0.66×.
    - decode (m = 32): 183 ms a step against FP8's 16.1 ms, **11.4×**. The GEMM is 0.60× FP8, hashing and records **9.34×** (150 ms a step), the rest 1.44×.
  - The engines stayed resident, the reps were interleaved, and the gates passed.
  - Why the verify pass failed: the timed passes make call buffers during vLLM's forward, so they are inference tensors, and `poison()`'s `fill_` ran outside inference mode.
- 14:22Z: **`9f31150f`, the tree ready again.** `poison()` fills under `torch.inference_mode()`, and so does `gemm`'s body (a no-op inside vLLM), so the gate and any caller outside a forward write the same buffers. The poisoning test now makes its buffers under inference mode, checks that they are inference tensors, and poisons and calls outside it. 17 CPU tests.
- 14:24Z: **the decode profile** (`r20260930-142010-8291`, untimed, `gpu-lease 1`, at `9f31150f`) is in [`pouw-mvp-decode-profile.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/rtx-pro/pouw-mvp-decode-profile.md), with the plan.
  - Decode is host-bound: a Pearl-C forward is about 223 ms of Python and driver calls against about 36 ms of GPU kernels (nsys). First use is negligible.
  - The 150 ms of "hashing" is mostly host work: the records' screen (75 ms a forward), the pure-Python BLAKE3 in `call_keys` (43), the hashing launches, and the key uploads. The GPU hashing is about 10 ms, 5.6 of it A's row tree.
  - The deferred side-stream schedule comes after the host fixes. Needs for GPU 1: the liveness count in `stats_s5`, and pre-bound launch arguments.

- 14:58Z: **window 3 (`r20260930-142122-83bd`, at `9f31150f`) verified.**
  - Both retained passes repeated their timed commitments.
  - The verify job (`r20260930-142832-c2ae`) ACCEPTed prefill (3 drawn tiles, 10 for excluded rows, of 2,752,512) and decode (3 drawn, 106, of 2,064,384 over 8,320 matmuls), and REJECTed the negative control (activation opening).
  - **Panel attempt 93** (`pearl-c-sm120` v1-h1, measured):
    - prefill `e2e-llama31-8b-vllm-m8192`: **2.759×** stock vLLM FP8, 1.838× BF16;
    - decode `e2e-llama31-8b-vllm-m32`: **10.603×** FP8, 11.219× BF16.

    The decode row went in as 94, and a renumber correction moved it to 93. `panel_rows.py` now does that itself.
- 15:05Z: **step 1 merged into #540** (#559; `8ca97148`).
  - **What it does:** native BLAKE3 for the per-call keys, byte for byte `call_keys`; a pinned upload ring; the records' screen as one fused Triton kernel, with the gate's check on the card; A's roots in a pass buffer; and cached stream objects for event records.
  - **Tests:** the same calls through the native and reference paths upload the same keys, launch the same steps, and retain the same manifest (records root, commitment, roots). The fused kernel gives the torch screen's flags under Triton's interpreter.
  - **Untimed profile of step 1** (`r20260930-143912-5cca`, at `2d40758a`): the gate passed, including the fused screen on the card. The steady decode forward is 108 ms, down from 260 (BF16 15.6); keys 2.9 ms a forward (was 43) and the screen 7.2 (was 75). What's left is mostly the kernels' launches through ctypes, GPU 1's launch-binding item.
- 15:19Z: **the re-timing window's request is posted in `server.md`** (the 15:19Z entry):
  - job 2 is `--timed` at `8ca97148`, with window 3's shapes and baseline, and ship3;
  - job 3 launches only on a passed validation: `result.json` ok, the gates true, both verify passes repeating their commitments, and `jit-built.txt` empty.
- 15:28Z: **step 2 is on draft #564** (`cursor/pouw-decode-deferred-4f91`, `f3739e52`), stacked on #540. It isn't merged until the re-timing window verifies.
  - **The deferred schedule** (`--schedule deferred`): the tile hashing goes on a least-priority side stream, with two rotating sets of C̃, U and the digests per shape. The gate's schedule check holds serial and deferred to the same commitments on the card.
  - **The hashing format is a switch:** the scheme names it, and `TREE_HASH` gives its tree hash. `-h1` is today's; `-h2` or `-h3` is one entry each once GPU 1's pipeline has it (bc-b139c29c, after its current step; the choice is Daniel's).
  - 96 CPU tests pass.
- 15:44Z: **the quality run is on #540 at `38f5a277`, and its queue command is in `server.md`** (the 15:44Z entry). It is separate from the re-timing window, which stays at `8ca97148`.
  - **What it measures, untimed:** WikiText-2's test split (141 windows of BOS and 2,047 tokens, 288,627 scored) through vLLM's prompt log-probs on Llama-3.1-8B-Instruct, for bf16, stock fp8, Pearl-C v1 (`pearl-c-sm120-v1-h1`) and v2 (`pearl-c-sm120-unpromoted-v1-h1`, the new scheme on GPU 1's `sm120-unpromoted` kernels). For each mode: perplexity, top-1 agreement with bf16 teacher-forced, and greedy agreement with bf16 on the chat prompts.
  - **How it runs:** `window.sh` with `MODE=perplexity`, one scheme group per chunk (fp8; bf16 and v1; v2), checkpointed as `quality-<group>.json` and exiting 99 while groups remain. The Pearl-C arms are gated first, and GPU 1's `run.py` check runs for both variants. Setup run `r20260930-154306-d71d` shipped the tree and installed `pyarrow`. All 24 tests in `test_pearl_c_vllm.py` pass, and the combined suites give 312 passed and 9 skipped.
  - **The fill job:** `/workspace/pouw/mvp-e2e/fill/mvp-quality-perplexity.sh` (`gpus=1 max_min=10`), queued with `cp /workspace/pouw/mvp-e2e/fill/mvp-quality-perplexity.sh /workspace/pouw/fill/queue/`. Its output is `/workspace/pouw/fill-out/mvp-quality/38f5a277/quality.json`, which I preserve through `research` when it finishes.
- 16:14Z: **the quality run finished** (16:08Z; preempted once by window 4, and resumed). It is preserved in `r20260930-161427-313f`.

  | Mode | Perplexity | Over BF16 | Top-1 agreement with BF16 | Greedy agreement |
  |---|---:|---:|---:|---:|
  | bf16 | 7.2317 | — | 1 | 1 |
  | fp8 | 7.2765 | +0.62% | 0.9574 | 0.794 |
  | Pearl-C v1 | 7.3351 | +1.43% | 0.9395 | 0.455 |
  | Pearl-C v2 | 7.3443 | +1.56% | 0.9390 | 0.440 |
- 16:22Z: **#564 synced with #540** at `9acf562b`, a mechanical merge of `38f5a277` (v2 and the quality mode). Tests: 26 in `test_pearl_c_vllm.py`, and 74 passed, 9 skipped in the protocol-option and kernel suites. The review's fixes for #564 are not in it: they go to bc-f4e8ae34's migration if it agrees.
- 16:37Z: **window 4 verified.** The window was `r20260930-155937-468e`, at `8ca97148`.
  - Verify `r20260930-160418-fbad` accepted prefill (3 drawn, 11 excluded, of 2,752,512) and decode (3 drawn, 104, of 2,064,384), and rejected the control (activation opening).
  - **Panel attempt 102**: prefill **1.712×** stock FP8 (1.144× BF16), decode **3.943×** (4.690× BF16). Attempt 93 had 2.759× and 10.603×.
  - `docs/pouw/mvp-e2e.md` has the window and the quality table.
- 16:40Z: **the migration handoff for bc-f4e8ae34** is at [`handoffs/pouw-mvp-migration.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/rtx-pro/handoffs/pouw-mvp-migration.md).
- 17:14Z: **the pre-fix profile of #564 at `9acf562b`**: three runs at once on three cards (`r20260930-165937-adc3` serial, `-165951-ec4f` deferred, `-165957-8a55` deferred with vLLM's stream at the greatest priority via a sent `prio.py`).
  - The three were equal within 2%: 130.3, 127.4 and 129.6 ms a steady decode forward.
  - All three are labelled PRE-FIX in the store (a `note` label), and nobody should cite them.
- 17:20Z: **the root wall-clock lint is fixed** on #540 (`120c26ed`) and merged into #564 (`a895ade7`). GPU 1's six `timeout=` arguments in `test_pearl_c_sm120.py` now wait on each process's exit. bc-f4e8ae34 merges it up the stack before any recorded `check`.
- 17:31Z: **the migration's card checks at #585's `bed66b08`:**
  - smoke `r20260930-171755-c52e` passed: both engines resident, 17 gate rows, served y at 5.3% and 4.6% relative RMS as before;
  - profile `r20260930-172231-591d`, one card, the schedules in turn: serial 87.5 ms, deferred-caller 105.1 ms, deferred 127.8 ms a steady decode forward. So `serial` is the default and the window times it.
- 17:27Z: **the per-linear error trace**, on the new branch `cursor/pouw-error-trace-4f91` (draft [#589](https://github.com/danielreuter/verity/pull/589), `294b113d`, on `38f5a277`).
  - Its smoke on layer 0 (`r20260930-172450-14b9`) closes the split. Pearl-C's error is 99% the cast of the noisy operands, and the scheme's noise law predicts that cast error within 4%.
  - The fill script is `/workspace/pouw/mvp-e2e/fill/mvp-error-trace.sh`.
- 20:00Z: **window 5 verified; the rows are panel attempt 103.**
  - The window was `r20260930-181144-19f9` and the verify `r20260930-182720-80d9`: ACCEPT, ACCEPT, REJECT.
  - Prefill 1.718× (485.5 ms against 282.6), decode 4.145× (60.8 ms against 14.7).
  - The Triton screen compile at 18:12:48 was outside the timed reps.
  - The panel was re-rendered with 4 store rows; the remote refresh timed out.
- 20:00Z: **the error trace is done** (fill, preserved in `r20260930-195640-ee96`).
  - Pearl-C's error is 1.43× stock FP8's at the median linear, and 99.4% of it is the cast of the noise-added operands.
  - The noise law predicts that cast error at 1.00×. Pearl-C's own quantizer with no noise matches stock FP8.
  - Verdict: the protocol's intended noise, at its expected size, and not a bug.
- 20:00Z: **the next run is planned** in `docs/pouw/mvp-e2e.md` and posted in `server.md` (20:00Z).
  - Window 6 is #593 (bc-ccd30e80's request).
  - Window 7 adds the `s,one` forms: GPU 1's gate, then my served-tree branch on #593 and a comparison at the MVP's shapes.
- 1:27 PM PDT: **window 7's prep, steps 1–3, is under way.**
  - **The branch:** `cursor/pouw-mvp-forms-4f91` at `d765b776`, which is #593's `b0fbc284` with GPU 1's `92285aab` (ship15) merged, taking `s,one`. 694 CPU tests pass.
  - **Step 1:** GPU 1's device check under `s,one` passed on the card, and the MVP's untimed retained window under `s,one` with graphs is `r20260930-202402-b130`, its verify to follow. GPU 1's arm gate is asked for in `server.md`.
  - **Step 3:** the forms comparison, graphs on both arms, is `r20260930-202418-deee`.
  - **Estimates against graphed FP8** are in `docs/pouw/mvp-e2e.md`: window 7 about 3.1×, and 1.7× against eager.
- 1:27 PM PDT: times people read are now in Pacific time (lane contract 2.7 §5a); UTC stays in ids, filenames and logs.
- 1:50 PM PDT: **`-h2` is folded into window 7.**
  - Daniel approved it at 1:36 PM PDT, so window 7 is #596: `-h2`, graphs with fix 8, the spread, and graphed FP8.
  - **Estimates:** prefill about 1.62× eager FP8 and 1.68× graphed; decode about 1.6× eager, 3.2× graphed, and 3.1× on kernel time.
  - **The forms comparison** (`r20260930-202418-deee`): `s,one` gives prefill −6.5% of Pearl-C's kernels, but decode is slower (65.6–65.9 against 47.9–50.8 ms a step under nsys). The node-traced attribution is `r20260930-204754-ffe0`.
  - **Graphed FP8, measured:** 7.4 ms a decode step, and 276.7 ms prefill.
- 3:14 PM PDT: **window 7 is queued.**
  - The smoke `r20260930-220851-c004` passed: 22 gate rows, both engines resident, no FlashInfer JIT.
  - The timed run is `r20260930-221231-3dd1`: it waits for 5:40 PM PDT, takes `gpu-lease 8 --wait --timed`, and then verifies on a passed validation.
  - The slot is confirmed in `server.md` (3:13 PM PDT).
- 3:30 PM PDT: **FP8 v2 at 0.371% is withdrawn** (compute-accounting; the assessor rated it D at 3:24 PM PDT).
  - None of my documents, PR texts (#389 among them) or branch files cites it.
  - The MVP serves v1 throughout (`v1-h1`, and `v1-h2` from window 7), so its γ claim is v1's 0.519% packed.
- 4:49 PM PDT: **window 8, `-h2` with the `s` form (#610, bc-b139c29c), is approved on conditions** (compute-accounting, 4:43 PM PDT).
  - **It waits on:** bc-b139c29c's untimed served-path verify with the switch on, the P10 split (bc-ccd30e80), #610's rows-form flag, and its own ship.
  - **The order:** it runs after window 7's row and the 6:30 PM PDT attempt-67 repeat.
  - **The slot** is asked of bc-2aa33ad8 in `server.md`: earliest about 7:00 PM PDT, latest useful start about 10:45 PM PDT.
  - **If its verified totals are in by 11:40 PM PDT,** they become the like-for-like row, with window 7's beside them.
- 4:44 PM PDT: **window 7's run carries `FP8_GRAPHS=1`** (its record and its live process), with the verify in the same run.
  - Its rows come from `panel_rows.py` at #596's `c43258ce`: decode's headline over graphed FP8, and the eager row beside it.
- 6:37 PM PDT: **window 7 verified and reported** in `lanes/accounting/`, in three replies: READY and the totals at 5:59 PM PDT, progress at 6:27, verified at 6:37.
  - The goal-critical job "window 7's verify and totals" (mark 7:40 PM PDT) is done.
  - The rows are bc-ccd30e80's to generate and bc-2aa33ad8's to append (the 6:04 PM PDT order). My dry run gives 1.6174, 3.4024 and 1.2629.
- 7:16 PM PDT: **window 8 is queued** as `r20261001-020519-e39d`, from #610 `e442d494`, with window 7's switches plus `ROWS_FORM=s`, the ship `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar`, and `--custody-r2 --custody-ttl 8h`. Its lease starts at 7:20 PM PDT.
  - READY line: `lanes/accounting/20261001T0208Z-reply-from-bc-dd22acf8-window8-queued.md`; also posted in `server.md` at 7:08 PM PDT.
  - **Migration handoff written:** `lanes/accounting/20261001T0215Z-handoff-from-bc-dd22acf8-migration.md`. Under the served-path exception I drive window 8 until it's preserved, and start nothing else.
  - VM-only scripts copied to `workers/pouw-mvp-e2e/` here and to node 2's `/workspace/pouw/mvp-e2e/`. The forms A/B `r20260930-202418-deee` is fetched and preserved.
  - MKL race: not exposed (no torch transcendental in `benchmarks/pouw/pearl_c_vllm/` or `protocols/pouw/` at `e442d494`).

## The run, in one line

Llama-3.1-8B-Instruct in BF16 at TP 1: prefill one 8,192-token prompt (every linear at m = 8,192) and decode 32 sequences (m = 32). The modes are `bf16`, `fp8` (the divisor), `pearlc-nohash` and `pearlc`, each gated before timing. Retained verify passes must repeat their timed commitments, and the reference verifier runs on them after the window.

## Needs

1. **bc-2aa33ad8:** item 5 is taken as written: you queue job 2 and job 3 when GPU 1's gate passes. The root ruled on the baseline at 12:11Z:
   - stock vLLM FP8 stays the baseline, interleaved rep by rep with both engines resident;
   - the fallback, if both can't stay resident, is ABAB blocks, said on the panel page;
   - I append the rows after job 3 accepts.

   The window's estimate drops to 8–10 min (12–15 on the fallback), with the same 19-min cap.
2. **GPU 1 (bc-18346d9c):** done. `9f1e33b1` is merged, and your API note is resolved on #540's side (the fused path, `tmap`).
   - #540 relies on `Pipeline(bufs=…, m_real=…)`, the step names, `keys_of` and `unit_block`. If any of them changes, say so; `test_pearl_c_vllm.py` fails loudly on it.
   - The window needs your `build.sh` ship, built from the tree #540 runs, since `window.sh` requires its `run.py` to be the tree's.
3. **bc-b139c29c and GPU 1:** `-h2` has to be in GPU 1's pipeline: A's rows and every tree as frame-b3s (`hash_rows_b3s`, `b3s_level_keys`) in the sm_120 cubin's steps.
   - #532 and GPU 1's device seam also conflict in `pearl_c.py` and `schemes/__init__.py`. The resolution is mechanical: the name is `pearl-c-{device}-v1` plus the hashing suffix, and the tree hash is `TREE_HASH[hashing]`.
   - After that, #540 adds `pearl-c-sm120-v1-h2` in one line. Until then the e2e runs `-h1`.
4. **The infra lane (bc-efe47341):** the window's verify passes write about 45 GB under `/workspace/pouw/mvp-e2e/passes/<run id>`. They can be deleted once job 3 has preserved its verdicts and the manifests.

## Panel rows

After job 3 accepts, I append them with `panel_rows.py --append`: two rows under `pearl-c-sm120` v1-h1: prefill at `e2e-llama31-8b-vllm-m8192` and decode at `e2e-llama31-8b-vllm-m32` (dependent chain). Both are measured, with slowdown over the window's interleaved stock `fp8`, the verifier's accept, transcript and negative-control lines, and every rep's clock. No rows yet.

## Lessons

- NVML (`nvidia-smi -i N`) ignores `CUDA_VISIBLE_DEVICES`, so a leased job names its GPU by `GPU_LEASE_UUID`, never by index.
- FlashInfer JIT-compiles on the first call, through `ninja` from PATH, into `~/.cache/flashinfer/<version>/<arch>/`. Pre-build it at setup with the window's `FLASHINFER_CUDA_ARCH_LIST`, so the flags and the cache path agree and nothing rebuilds.

- `research run --on vy-nebius-2` needs a tree whose `research` has the `ssh` provider, and `RESEARCH_MACHINES_D` pointing at research-notes' `machines.d`; `vy-nebius-2.toml` is registered there.
- A tool call that edits a file and a shell call that commits it must not run in parallel: a merge commit captured conflict markers that way, and the resolution is a separate follow-up commit (`82aaaf5f`).

## From bc-b139c29c (16:55Z): `-h2` in GPU 1's pipeline is ready ([#572](https://github.com/danielreuter/verity/pull/572), stacked on #540)

- **What:** `run.Pipeline(hashing="h2")` commits A's and B's rows and the tile tree as frame-b3s (`hash_rows_b3s`, `b3s_level_keys`, `hash_leaves_b3s`), and `pearl-c-sm120-v1-h2` is in `pouw_pearl_c_device.SCHEMES`. `-h1` stays the default. The scheme-name conflict is resolved as your need 3 says.
- **The format is read from the scheme, not from a table** (the API review's finding 3): `audit.commitment_hash(scheme)`, `scheme.digest_keys` and `scheme.hashing`. `weight_roots(kernel, weights, scheme)` now takes the scheme's name.
- **Against #564:** drop its `TREE_HASH` and `tree_hash`, and pass the scheme's name to `weight_roots`. Its `--scheme` then selects `-h2` with nothing else. Take #572's `_Keys`, which keeps native keys under frame-b3s.
- **Verified on the card:** run `r20260930-164205-838d`, one preemptible chunk on GPU 2. GPU 1's check passed. Under both `-h1` and `-h2`, the gate passed, each commitment repeated from poisoned outputs, the honest pass was ACCEPTed and the negative control REJECTed.
- **Details:** [`internal/pouw/rtx-pro/sm120-h2-switch.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/rtx-pro/sm120-h2-switch.md).
