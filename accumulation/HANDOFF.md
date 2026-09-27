# `accumulation/`: what it is, and which algorithms run over the Verity IR

State as of 2026-09-24. Written for someone benchmarking algorithms that run over the Verity IR.

**Heads-up:** nothing under `accumulation/` is committed to git yet. Another worktree or clone won't see any of it
until it is committed or copied over.

## 1. Use case

The question is whether an auditor can throttle frontier training without affecting inference, by checking only the
*structure* of the circuit a datacenter declares. The circuit must split into units of bounded size (called replay
units in the older models, isolation units or IUs in the current draft), and each unit may read only a little *novel*
information. Novel information is anything that isn't committed weights, code or data.

To get numbers, we write training and inference algorithms as **Verity IR circuits**, with a role on every root
parameter, and compute the minimum novel input that any legal partition of the circuit must read:

- **lower bounds** are certificates that hold for every legal partition;
- **upper bounds** are explicit partitions, i.e. concrete attacks;
- an **exact solver** on tiny circuits checks that both bounds bracket the true optimum.

The policy model has changed three times. Code for all three is still in the tree:

| Model | A unit is legal if | Main code | Status |
|---|---|---|---|
| v1 `(F, X)` | input bytes ≤ `X`, upstream work ≤ `F` | `bounds/lower.py::lower_bound`, `bounds/upper.py::upper_bound`, `sweeps/run.py` | Dead end: `THEORY_xcap_deadend.md`, `results/xcap_deadend/` |
| v4 `(F, G)`, acyclic | total work ≤ `G`, upstream work ≤ `F`, and the graph of units is acyclic | `bounds/coarse.py::upper_coarse`, `bounds/lower_coarse.py`, `bounds/lower_wp.py`, `sweeps/coarse_run.py` | Finished: `results/REPORT.md`, `results/TABLE1.md`, `results/TABLE2.md` |
| NCI `(Γ, α)`, the current draft | size ≤ `Γ` gates, novel input / size ≤ `α`, cycles allowed | `redteam/mlt.py` (closed form plus CP-SAT) | Current: `results/EXISTING_RESULTS_NCI.md` §12 |

Under NCI, the headline lower bound depends only on the circuit's *shape*, so the heavy extraction pipeline is no
longer needed for headline numbers. It is still the most IR-heavy code here, though, and it produced all of the
performance data in §4.

## 2. How this code uses the Verity IR

**Its own primitive vocabulary.** `ir/prims.py` registers 26 abstract primitives: `Mac16` (a chunk of 16
multiply-accumulates), `Mac1` (a scalar MAC), `Add16`, `Round16`, `Zero32`, `Rsqrt32`, `SiluMul16`, and so on. They
have the same shapes and widths as the B1 serving vocabulary (`verity_ir.registry.prims`), but simple integer
semantics (arithmetic mod `2^w`), and each carries a `work` attribute in MAC-equivalents. The circuits are faithful
to real models in shape but not in numerics. The analysis never looks at computed values, only at gates, wires,
widths and work.

**Composites.**

- `ir/blocks.py` defines `MatmulT`, the single matrix-product node: a batch over `m` of a batch over `n` of a `Dot`,
  which scans over `K/CH` chunks. Transposes and head-major slices are reference rearrangements, not gates. `CH=16`
  by default; `CH=1` gives scalar MAC chains at exact-solver scale.
- `algorithms/transformer.py` builds on it: `Block`, `BlockBwd`, `AttnSeq`, `MoeMlp`, `LoraBlock`, and so on.
- `algorithms/registry.py` holds the algorithm factories and assigns roles. The algorithms are `inference-dense`,
  `inference-session`, `inference-moe`, `forward-nonfixed` (rollout with updated weights), `forward-nonfixed-moe`,
  `pretrain-dense`, `local-sgd` (multi-step), `pretrain-moe`, `lora`, `hidden-adapter`, `rl-policy-gradient` and
  `es`.
- `configs.py` defines the models: llama3-1b/8b/70b/405b, mixtral-8x7b, deepseek-v3, qwen3-235b-a22b, the `tiny*`
  models, and the `syn-*` synthetic family (via `sweeps/synthetic.py`).

**IR API surface in use:**

~~~
verity_ir           Array, Value, Tuple, Program, bind, composite, primitive
verity_ir.defs      CompositeDefinition, PrimitiveDefinition, SpecializedDefinition, Node
verity_ir.refs      Affine, Concat, Explicit, Refs, Strided, Coll, compose_view, concat, strided_view, array_of, tuple_of
verity_ir.layout    Scope, resolve
verity_ir.program   Program
~~~

**Roles** on root parameters:

| Role | Meaning | Charged as input? |
|---|---|---|
| `fixed` | Committed: registered weights, constant ids, hash counters | No |
| `accumulated` | Weights produced by earlier training | Yes |
| `carried` | Non-fixed state that isn't declared as weights, e.g. an adapter carried in activations | Yes |
| `token` | Token ids, targets, advantages (4 bytes each) | Yes, once |
| `seed` | Small non-fixed inputs: ES seeds, learning rate | Yes, once |

**Two views of one circuit.**

- *Operator graph* (`graph/opgraph.py::extract`). This walks the composite hierarchy and stops at the terminal
  `Acc*` composites, recording one `Op` per terminal. Batches stay symbolic (`copies > 1`), and operands are resolved
  through bindings, batch slices and composite returns. It gives exact dataflow at operator granularity and scales to
  405B.
- *Flat gate list* (`exact/solve.py::flatten` / `make_flat`, via `verity_ir.layout.resolve`). This is the full
  expansion, only feasible for tiny circuits (up to a few hundred thousand gates).
- `graph/validate.py::check_against_flat` checks that the operator graph is a faithful quotient of the gate graph:
  every gate maps to exactly one op, work sums match, and the source tensors match.

## 3. The algorithms (benchmarkable inventory)

All paths are relative to `accumulation/`. Timings are wall clock on the laptop or on RunPod CPU pods, taken from the
data files in §4.

| # | Algorithm | Entry point | Input → output | Method | Observed scale and cost |
|---|---|---|---|---|---|
| 1 | Build circuit | `algorithms/registry.py::build(alg, model, Workload)` | factory → `BuiltProgram` | Symbolic composite construction | ~0.01 s at any size |
| 2 | Extract operator graph | `graph/opgraph.py::extract(bp)` | `Program` → `OpGraph` | Hierarchy walk; batches symbolic | 0.03 s (1B inference, 243 ops) to 155 s (8B pretraining, 4M tokens) to 615 s (405B pretraining, 4M tokens, 8,957 ops). Superlinear in sequences per forward. Peak RSS up to 1.5 GB (ES 8B, 32k ops). One probe was killed (ES 8B at 4M tokens). |
| 3 | Flatten to gates | `exact/solve.py::flatten`, `make_flat` | `Program` → `FlatCircuit` | `verity_ir.layout.resolve` | Tiny configs only |
| 4 | Validate operator graph | `graph/validate.py::check_against_flat` | `OpGraph` + `FlatCircuit` → pass/fail | Gate-to-op quotient check | Tiny configs only |
| 5 | Accumulation-dependent work (ADW) | `bounds/adw.py::adw(g)` | `OpGraph` → work totals | Role propagation through transitive closure | Sub-second |
| 6 | Constructive upper bound (v4) | `bounds/coarse.py::upper_coarse(g, F, G)` | `OpGraph` → checked plan and `U` | Rectangular-tile search and fused groups; `check_coarse_plan` checks it; `plan_gate_assignment` expands it to gates | 0.001 s (inference) to 8,900 s (405B, 3 training steps of 131k tokens, 27k ops) |
| 7 | Coarse lower bound (v4) | `bounds/lower.py::lower_coarse` (implemented in `bounds/lower_coarse.py`) | `OpGraph` → `L` and a certificate | Linear-program price certificate (HiGHS via scipy) | 0.0003 s to 14,000 s (8B, 8 training steps of 8k tokens, 18k ops) |
| 8 | Weight-presence certificate | `bounds/lower_wp.py::weight_presence_bound` | `OpGraph` → `L_wp` | Combinatorial (uses acyclicity) | 0.03–9 s |
| 9 | v1 bounds (superseded) | `bounds/lower.py::lower_bound`, `bounds/upper.py::upper_bound` | `OpGraph` → `L`, `U` | Loomis–Whitney charges; rectangular tiles | Superseded |
| 10 | Exact optimum | `exact/solve.py::exact_min_input(flat, F, X, G, acyclic=)` | `FlatCircuit` → `I*` and an optimal partition | Brute force up to 11 gates; HiGHS MILP (pairwise and assignment formulations) | Proven optimal on up to ~40 gates (median 18–42); cells from ~30 gates up can time out. Larger "optimal" cells, up to 18,816 gates, are single-unit cells settled by argument, not by search. |
| 11 | Exact optimum, NCI | `redteam/mlt.py::cpsat_min_input` | `FlatCircuit` → `I*` | OR-Tools CP-SAT, cycles allowed, work cap only; symmetry breaking; warm start from the best rectangle tiling | `M_{L,T}` instances of 16–32 gates: 31 of 35 proven optimal within the 120 s limit |
| 12 | Ground-truth checks | `exact/solve.py::partition_cost`, `is_legal`, `quotient_cycle`, `up_set` | Assignment → cost / legality | Literal definitions from SPEC §1 | Every bound is held to these |
| 13 | Red-team drivers | `redteam/`: `fuzz`, `torture`, `wedge`, `block_term`, `rollout_scale`, `coarse_validation`, `validation`, `wp_gatecheck`, `harness.evaluate` | Circuits → verdicts and tables | Random micro DAGs, hand-derived cases, whole-pipeline checks | Seconds to hours |

Performance notes for benchmarking:

- Extraction (#2) and flattening (#3) are the only algorithms that traverse the IR directly. Everything else
  consumes their outputs.
- Extraction was once superlinear badly enough to build multi-GB explicit reference tuples and take the machine down.
  That is why `sweeps/guard.py` exists. `results/extract_scaling.json` is the extractor's regression set.
- At scale, runtime is dominated by `upper_coarse` and `lower_coarse` (hours for multi-step training at 8B–405B),
  not by extraction.
- The HiGHS MILP stalls beyond ~40 gates. CP-SAT does much better on `M_{L,T}` but has only been run on that family.

## 4. Performance data already on disk (`accumulation/results/`)

| File | Rows | What it has |
|---|---|---|
| `extract_scaling.json` | 37 probes | Build and extract of `(alg, model, tokens, seq)`: `t_build`, `t_extract`, `ops`, `tensors`, `peak_rss_mb`, `rss_trace`, `status` (36 ok, 1 killed) |
| `coarse.jsonl` | 387 | Sweep cells (model × circuit × policy point): `extract_s`, `lower_s`, `upper_s`, `wp_s`, `n_ops`, `peak_rss_mb`, `tokens`, bound values, and source hashes of every bound module in `versions` |
| `pod/*.jsonl`, `pod/logs/` | shards | RunPod shard outputs, already merged into `coarse.jsonl` |
| `validation.json` | 1,772 | Exact solver vs bounds on micro circuits: `gates`, `seconds`, `optimal`, `L`, `U`, `I*` |
| `coarse_validation.json`, `wedge_exact.json` | 336 each | The same under the v4 policy, with `Istar_seconds` / `seconds` |
| `block_term.json` | 51 | Registry transformer circuits at tiny scale (662–7,272 gates) |
| `mlt_check.json` | 35 | `M_{L,T}` instances: `gates`, `Gamma`, closed-form lower bound, rectangle upper bound, CP-SAT `I*`, `seconds`, `optimal` |

## 5. Running it

~~~
# always from the repo root
PYTHONPATH=. .venv/bin/python -m pytest accumulation/tests -q            # 2,397 tests
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.scaling              # extraction probes -> results/extract_scaling.json
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.coarse_run --help    # v4 sweep driver (resumable, guarded)
PYTHONPATH=. .venv/bin/python -m accumulation.redteam.mlt                 # M_{L,T} closed form vs CP-SAT
~~~

~~~python
from accumulation.algorithms.registry import build
from accumulation.configs import MODELS, Workload
from accumulation.graph import extract
from accumulation.bounds.adw import adw

bp = build("pretrain-dense", MODELS["llama3-8b"], Workload(tokens=4096, seq=4096))
g = extract(bp)          # ~2 s at 8B, 2,283 ops
a = adw(g)
~~~

Operational constraints:

- The laptop's memory guardian caps any veritor Python process at 2.5 GB. `sweeps/guard.py::run_guarded` runs every
  build+extract in a child process under an RSS watchdog (3 GB default, 8 GB in the sweeps), with a wall-clock limit
  and a one-at-a-time lock file (`results/.probe.lock`). `SAFE_LIMITS` refuses absurd workloads.
- Heavy cells run on RunPod via `sweeps/pod.py`: 70B, 405B and MoE training, 8B training above ~140k tokens, and
  128k-context training.
- `ortools` (9.15) and `scipy` (1.18) are installed in `.venv` but not declared in `pyproject.toml`.

## 6. Where the docs are

- `SPEC.md`: definitions, the bound family, module contracts. Its §0 is the v4 policy.
- `THEORY.md`: v4 theory. `THEORY_xcap_deadend.md`: why v1 failed.
- `DELIVERABLES.md`, `REWRITE_OUTLINE.md`, `ROLLOUT_PLAN.md`: the v4 deliverables and report plan.
- `results/REPORT.md`: v4 results, including the validation panel.
- `results/EXISTING_RESULTS_NCI.md`: every result mapped onto the NCI draft, with caveats. §12 has the `M_{L,T}`
  closed form, its proof, the solver check and the Kimi-K3 read-off.
- `results/REDTEAM_STATUS.md`: red-team status.

## 7. Open threads

- The NCI draft's peak-variant bound needs to be redone with a separate `λ` per layer and separate weight/activation
  widths over Kimi-K3's actual matrices, which are not square 7168×7168 and have MXFP4 experts. This is analytic;
  nothing needs to run.
- The average-variant lower bound is proved in `EXISTING_RESULTS_NCI.md` §12, but only for pure linear chains.
  Nonlinearities, norms and attention between matmuls haven't been handled formally.
