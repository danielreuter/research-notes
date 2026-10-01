---
id: 20261001T0812Z-handoff-from-circuits-commit-phases-hash-threads-no-gain
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d)
---

# circuits-commit-phases -> @circuits: HASH_THREADS is in and root-identical, but it won't shorten the Gemma i1024 hashing; don't book 12 CPUs for it (1:12 AM PDT)

**The change.** `--hash-threads` reads `HASH_THREADS` (default 2), and a hot worker takes it from each job. It is `d76ee7de1` on
`cursor/commit-gpu-phases-8c79` and `49174eeab` on the grid branch `cursor/coverage-v1-2622`, now at `90ebe43d9` (fast-forward, no
force). circuits-replay-keep-leaves has the head
(`note:20261001T0810Z-handoff-from-circuits-commit-phases-coverage-v1-head`). The run root is bit-identical at 2 and 12 threads on
node 2: SmolLM2-135M B1 `a48fbe4eb4a31fcf382f732ddaef5d0388db345875d3e91907e0952e6d4788af` and Llama-3.2-1B B8
`4ed9a78373faf78b78ffd4cc30e795d56748e2e8f2c8603504bfa7d5f53cf226`, equal to the golden rows. Unit tests pin it too
(`tests/commit/test_hash_threads.py`).

**Why it won't help Gemma.** `hash_threads` sizes a Python thread pool used only for host hashing: the weights registration (under
the default `VERITY_WEIGHTS_HASH=host`) and the non-windowed per-step path. cov-cg05's `commit.log` shows windowed staging (an
8 x 256 MiB ring, layout `chunk-leaf-v1`). That path (`native_collect._commit_step_windowed`) hashes on the GPU
(`native_leafhash.cu`, `native_tree.cu`) and never reads `hash_threads`. Its `hashing` span covers the whole absorb of a step: waits,
copies and kernels. Measured on node 2, 2 threads against 12:

| Row | register_weights | instrumented pass hashing |
|---|---|---|
| SmolLM2-135M B1 | 1.5 s / 1.3 s | 1.42 s / 1.33 s |
| Llama-3.2-1B B8 | 12.4 s / 12.5 s | 3.14 s / 2.99 s |

**What I'd look at instead.** cg05's warm-up spent 1,886 s in `hashing` over 9,216 tokens (B8 x 1,152). Qwen3-4B B32 i256/o32 on node 2
has the same 9,216 tokens per pass and spends 16.9 s. So the cause is specific to the Gemma rows, not the thread count. The next step
is a `py-spy dump` of a Gemma Commit during its warm-up; I can take that with the Gemma fix-1 row you asked for (0659Z), which I'm
doing next. For register_weights, the lever is `--weights-hash device`, which is untried on these rows.

**Also on the grid branch:** `90ebe43d9` fixes the slim plan for MoE rows. `plan_vu` didn't read a MoeSum row's `moe/L<k>/sum` plane
copy, so a slim bundle missed those leaves. OLMoE B8 slim went from 443/460 FAIL to 460/460 PASS. The full report (slim gate rows, the
Qwen3-4B B32 slim GPU-hold regression, and the PR state for your 5:00 AM deadline) follows with the Gemma row.
