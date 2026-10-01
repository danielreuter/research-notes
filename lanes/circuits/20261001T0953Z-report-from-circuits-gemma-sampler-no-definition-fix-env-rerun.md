---
id: 20261001T0953Z-report-from-circuits-gemma-sampler-no-definition-fix-env-rerun
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-gemma-sampler
cursor:
  subagentId: "bc-0918173f-aaba-5a55-a671-49c9887db9ee"
---

# circuits-gemma-sampler -> @circuits (2:53 AM PDT): no Definition fix and no PR. cg02/03/04 failed on the submitted env; cg04-2 resubmitted with the grid cell's env at 2:46 AM PDT

**Update, 3:26 AM PDT: cg04-2 PASSES, 460/460.**

- config PASS at 10:23:39Z: replay 460/460 equal, 0 mismatches, run root `c22469530fd2f335`.
- Runs: Build `r20261001-094742-4b9c` (761 s, word check all from cache in 39 s, peak RSS 16.7 GiB), Commit `r20261001-100125-c1fc`
  (754 s on a node-1 GPU, admitted at once, no offload), replay `r20261001-101957-173a`. Its slim keep is 40.8 MB, and the bundle is deleted.
- cg02-2 (`nd-vllm-epoch-run-75fa1400dd`) and cg03-2 (`nd-vllm-epoch-run-47432eedd5`) were submitted at 09:59Z and their Builds started at
  10:03Z and 10:05Z. Expected end is about 11:10Z.
- **My slip, fixed:** `--priority circuits` on submit pins every task of the item to 500, so the Commit and replay lose the template's
  `circuits-gpu` (600). I set cg04-2's queued replay to 600 and dropped `priority` from cg02-2's and cg03-2's item annotations, so their
  later tasks take the template default. Don't pass `--priority` to `dispatch.py submit config-run`.

**Outcome.**

- **No branch, no PR, no run-branch commit.** Drop the 6:00 AM PDT slot. circuits-replay-keep-leaves has nothing to sync.
- **cg04-2 is running:**
  - Key `vllm-epoch-run/cov-cg04-2`, Job `nd-vllm-epoch-run-80d7e042e6-build-0`, submitted 09:46Z through node 1's dispatcher.
  - Tree `cursor-coverage-v1-2622`, live template `config-run@87e09228d7e0`.
  - Env: cg04's own (m003-3's), plus `VERITY_QWORD_MAX_GATES` and `VERITY_QWORD_MAX_GATES_ALLOWED` set to `GumbelTopPTokenSelect_v2=225000000`, and
    `BUILD_TIMEOUT=14400`.
  - `SWEEP_DIR=/workspace/jobs/cov/cov-cg04-2`, so cg04's failed directory is left as it was. Resources are n031's (Build 4 CPU and 48G).

**Why no Definition can do it.**

- **The failure is the gate guard, not the width.**
  - `GumbelTopPTokenSelect_v2{V=256000,S=32}` is 204,337,818 gates. `word.MAX_GATES` is 24,000,000, a memory guard (about 0.6 KB per gate).
  - Its output is one 32-bit word, so W=32 is fine.
  - `_name` prints "too-large, 32 Call(s)" without the gate counts, which is why it read as a width problem.
- **A vocabulary-tile tree inside a Definition is still one unit.** Q_word v1 recurses into a body only when it's separable, and a top-p
  select is a chain (stats, merge, 5 rounds of step and combine, mask, Gumbel). So any tree of Calls inside the sampler is cut as one flat
  CallGraph of the same size.
- **Only root-level Program Calls get cut separately, and that is option 1.** Every tile boundary (per-tile partials, pivots, keep bits)
  then becomes a required value that serving must commit. The sampler runs in `StochasticRequest._step`, outside every served module, so
  that means new acquisition, plus the sampling events, Match/fold and replay changes.
  - This is option 1 in note:20260930T0931Z-finding-from-vllm-coverage-defs-topp-v3-not-cuttable-as-composite.
  - The 09-30 ruling (note:20260930T1020Z-decision-from-vllm-coordinator-topp-option3-and-queue) sends it to Daniel and says not to start it.
  - Your state.md has it under "Ideas / decisions to bring later".
- **"The B>1 shape" isn't a tile tree.** B>1 binds `GumbelTopPTokenSelectSharedGreedy_v1{V}`. Its keep word is the single primitive
  `TopPMaskWordx{V}_v1`: one word gate, about 10^11 ANDs, which no query can cut. That's why it fits in about 3.5M gates.
  - Binding it at B1 would undo v2, whose whole point is to restate that primitive as word gates (`topp_words.py` docstring).
  - It would also move every B1 stochastic Program digest.

**Why it's the env** (as in note:20261001T0530Z-report-from-vllm-epoch-run-cg04-is-env-not-definition):

- cg02, cg03 and cg04 went out with m003-3's env, which has no gate raise.
- n031, the same Call at the same V and S (top_p is an operand, not a parameter), passed 460/460 with the raise (`r20261001-024546-40ec`).
  Its `strict_word.log` reads `--build-max-gates GumbelTopPTokenSelect_v2=225000000 --allowed-max-gates …=225000000`, PASS.
- **cg04-2's word check is a cache hit, so its Build should take about 12 min rather than an hour.**
  - Node 1's rule cache holds n031's rule under that limit: `/workspace/jobs/cache/unit-rules/c4/c485513a….json`, written 02:26Z. It
    records 204,337,818 gates, 1 unit per Call and no violation.
  - Its cutter code (545c358c8d77) is the grid tree's today: `verity.ir`, `word.py`, `cross_call.py`, `call_scope.py` and the `topp_*`
    and `sampling.py` registries are byte-equal between n031's source and the current tree.
  - The same entry serves cg02 and cg03, which bind the same Definition. n031 spent about 51 min cutting it, uncached.

**Commit placement.**

- Gemma-2 is never packable (the dispatcher's `packable`).
- `n2_commit.sh`'s `kept()` encodes the top-level rule of 1:30 AM PDT: Gemma-2 is kept off node 1 only at B16 and up with 1024 input tokens.
  This B1 256/32 Commit therefore takes the normal path.
- That means the offload will likely move it to node 2. Node 2 has no 90-min slot before 9:30 AM PDT
  (note:20261001T0920Z-handoff-from-circuits-grid-models-node2-no-commit-slot), so it would come back by reclaim after 60 min and then run on node 1.
  n031's twin Commit took 533 s.
- **Expected:**
  - Build ends about 10:00Z.
  - The Commit runs at about 10:15Z if it starts at once, or about 11:15Z after a reclaim.
  - The replay takes about 3 min.
  - Either way it ends before the 12:10Z hold.
- **Ask, for infra if you agree:** skip the offload for `cov-cg04-2`, `cov-cg02-2` and `cov-cg03-2` (for example, their keys in the guest's
  `reclaimed.txt`, which `offload` skips). Tonight it only adds 60 min. That's infra's file, so I haven't touched it.

**Next (my call; say no if you disagree):**

- I'll submit `cov-cg02-2` (B1 1k top-p) and `cov-cg03-2` (B1 1k Gumbel), with the same env plus their own ROW, as soon as cg04-2's Build
  passes its word check. I won't wait for its 460/460.
  - The Build's word check is what failed. The Commit and replay of this Call already passed at n031.
  - cg01's B1 1k chain took 62 min. With a 60-min offload detour on top, cg02 and cg03 can still end by about 12:05Z only if they go out
    by about 10:05Z.
- If the offload detour would push either past 12:15Z, I'll stop that Commit before it starts and leave it for after 13:30Z.
- I'll report cg04-2's 460/460 (or not), cg02-2 and cg03-2 when they end, and tell vllm-epoch-run's labeller about the three keys.
