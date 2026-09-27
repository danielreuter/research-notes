# `accumulation/` — training security from bounded accumulation

Training and inference algorithms are written as Verity IR circuits; every root parameter carries a *role*.
An exact operator graph is extracted from the circuit, the *accumulation-dependent work* (ADW) is computed,
and the minimum runtime-input volume `I*(P; F, X)` an evaluator must move when every replay unit may hold at
most `X` bytes of non-fixed input and `F` MAC-equivalents of upstream work is bracketed by a certified lower
bound `L` and a constructive upper bound `U`. The definitions every module follows are in [`SPEC.md`](SPEC.md).

## Roles

| role | meaning | charged as input? |
|---|---|---|
| `fixed` | prescribed independently of this evaluation (registered weights, the `ids` constant, hash counters) | no — free at every RU boundary |
| `accumulated` | the changing model state (weights produced by earlier training) | yes — its bytes are the state floor `P` |
| `carried` | non-fixed state that is *not declared* as weights (an activation-carried adapter, a "context" that is really a parameter) | yes — exactly like `accumulated` (the red-team case) |
| `token` | token ids / targets / advantages (4 bytes each) | yes, once |
| `seed` | small non-fixed inputs (ES seeds, learning rate, sigma) | yes, once |

## Layout

~~~
accumulation/
  SPEC.md                 definitions (RU, I*, ADW), bound family, module contracts, reporting units
  configs.py              ModelConfig (llama3-1b/8b/70b/405b, mixtral-8x7b, deepseek-v3, qwen3-235b-a22b, tiny*) and Workload
  ir/prims.py, blocks.py  abstract primitives (Mac16 = 16 MAC-eq) and the MatmulT / norm / softmax / ... composites
  algorithms/transformer.py   Block, BlockBwd, AttnSeq(Bwd), MoeMlp, LoraBlock(Bwd) as explicit dataflow
  algorithms/registry.py  the algorithms: inference-dense, forward-nonfixed, inference-moe, pretrain-dense, local-sgd,
                          pretrain-moe, lora, hidden-adapter, rl-policy-gradient, es  (each: factory + roles + simplifications)
  graph/opgraph.py        extract(bp) -> OpGraph (ops with kind/statics/copies/work, tensors with role/width)
  graph/validate.py       gate-for-gate check of the op graph against the flattened circuit (tiny configs)
  bounds/adw.py           adw(g): accumulation-dependent work (total, matmul, matmul MACs, per op)
  bounds/lower.py         lower_bound(g, F, X) -> L   (Loomis-Whitney import charges, SPEC §2)
  bounds/upper.py         upper_bound(g, F, X) -> U   (explicit rectangular-tile partition, SPEC §3)
  sweeps/characterize.py  Goal-1 table, matmul breakdown, analytic MAC model, MAC audit
  sweeps/run.py           sweeps over (alg, model, workload) x F x X -> results/sweep_<preset>.jsonl (resumable)
  sweeps/plots.py         PNGs under results/plots/
  sweeps/report.py        JSONL/JSON -> markdown tables in results/RESULTS.md (between marker comments)
  sweeps/guard.py         run_guarded (child process + wall clock + 3 GB RSS watchdog + one-at-a-time lock);
                          SAFE_LIMITS (coarse envelope) / LEGACY_LIMITS (the pre-fix envelope)
  sweeps/scaling.py       guarded build+extract probes -> results/extract_scaling.json (timeout / oom-guard
                          rows are the extractor regression set)
  results/                RESULTS.md, characterization.{json,md}, audit.{json,md}, breakdown_*.md, sweep_*.jsonl, plots/
  tests/test_sweeps.py    smoke tests on tiny2 / tiny-moe
~~~

## Usage

Always run from the repo root with `PYTHONPATH=.` and the project interpreter `.venv/bin/python`.

Build a program, extract its operator graph, compute ADW:

~~~python
from accumulation.algorithms.registry import ALGORITHMS, build
from accumulation.configs import MODELS, Workload
from accumulation.graph import extract
from accumulation.bounds.adw import adw

bp = build("pretrain-dense", MODELS["llama3-8b"], Workload(tokens=4096, seq=4096))   # ~0 s
bp.roles, bp.state_bytes(), bp.param_bytes("token"), bp.notes, ALGORITHMS["pretrain-dense"].simplifications
g = extract(bp)                      # ~2 s at 8B: 2283 ops
a = adw(g)                           # a.total, a.matmul, a.matmul_macs, a.all_work, a.fraction
g.summary()                          # ops, work by kind, MACs
~~~

Bound it (once `bounds/lower.py` and `bounds/upper.py` exist):

~~~python
from accumulation.bounds.lower import lower_bound
from accumulation.bounds.upper import upper_bound
L = lower_bound(g, F=10**12, X=5_000_000)      # .total, .source, .cap, .per_op
U = upper_bound(g, F=10**12, X=5_000_000)      # .total, .n_units, .per_op, .plan
kappa_upper = a.matmul_macs / L.total          # certified max MACs per byte of runtime input
~~~

Characterize, audit, sweep, plot, report:

~~~
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.characterize --audit           # MAC audit -> results/audit.{json,md}, results/breakdown_*.md
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.characterize --table [--quick]  # Goal-1 table -> results/characterization.{json,md}
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.run --preset smoke              # tiny2 / tiny-moe, all algorithms
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.run --preset p1 --resume        # Q-scaling, pretrain-dense 8B, X = 5 MB
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.run --preset p2 --resume        # all algorithms x real models
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.run --preset p3                 # eta = kappa_upper / kappa_native from p1+p2
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.plots                           # results/plots/*.png
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.report                          # tables into results/RESULTS.md
~~~

Sweeps write one JSONL line per `(case, F, X)` as they go; `--resume` skips rows that already have every bound
that is currently importable, so a sweep started before the bound modules landed is completed by re-running it.
Every build+extract and every bound call is wall-clock guarded (`--time-limit`, `--bound-time-limit`).

In Python, a breakdown of where the MACs of a graph go (forward / recompute / dgrad / wgrad / attention, per
weight, per enclosing composite):

~~~python
from accumulation.sweeps.characterize import breakdown, format_breakdown, analytic_macs
bd = breakdown(g, bp)                 # rows keyed by (label, scope, M, N, K, copies); by_class; by_kind
print(format_breakdown(bd, tokens=4096))
analytic_macs("pretrain-dense", MODELS["llama3-8b"], Workload(4096, 4096))   # {"ir_model", "naive", "components", "notes"}
~~~

## Tests

~~~
PYTHONPATH=. .venv/bin/python -m pytest accumulation/tests -q
~~~

`tests/test_sweeps.py` runs `characterize` on tiny2, the analytic-vs-IR MAC check for every algorithm, the matmul
breakdown classifier, the `smoke` sweep preset (bounds checked when importable: `L >= P`, `U >= L`), resume, the
report renderer and the plot module's skip-on-missing behaviour.
