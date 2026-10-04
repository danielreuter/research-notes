---
id: lean/20261004T2112Z-draft-architecture
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Architecture: the protocol, its implementations, the harness

Draft by @lean, 3 Oct 2026, revised 20:45Z after Daniel's layering (subprotocols, accounting, workload classification,
with policy cutting across). It puts the concept and the repository tree side by side so each can be checked against the
other. Read from `origin/main` (`1074c52df`); nothing in the repository changed.

## The concept

**Verity is a protocol** between a developer and an auditor. The developer keeps records of the computations in its
datacenters and proves properties of them; the auditor checks the proofs and interprets what they show. In cryptography a
protocol calls subprotocols, and composition theorems (UC's among them) say when the whole's guarantee follows from the
parts'. The README already calls Verity "a composition of the following protocols".

It has three layers over a common core:

| Layer | What it does | Kind of work | Today |
|---|---|---|---|
| **Subprotocols** | collect and verify evidence by interacting with the developer | cryptography | sampled proofs, PoUW, PoUS, the network warden, and the proof systems that sampled proofs calls |
| **Accounting** | combine the subprotocols' outputs with physical facts into one account per resource | interpretation | compute, memory and network, each still embedded in a subprotocol's package |
| **Workload classification** | decide what kind of work the declared work is: inference, not training | interpretation | NCI, Lean only |

Each subprotocol's guarantee has, or is moving to, one form: `Sound`, meaning the auditor accepts while a stated claim is
false with probability at most δ. Accounting and classification are then deterministic consequences of those guarantees
together with their own assumptions.

**Accounting combines several subprotocols per resource.** Compute accounting, for example, needs sampled proofs (the
declared work was computed as declared), PoUW (the rest of the compute was occupied) and the chip's peak throughput. So
accounting is named by resource and subprotocols by mechanism.

**Physical facts are assumptions.** Examples are a chip's peak throughput, HBM capacity and link bandwidth. In the spec
they are named `Prop`s in accounting's `Assumptions`, measured by the probes and recorded in the census. PoUW's
`Pouw.Assumptions.Dimension.H100*` are the first of them, still inside PoUW.

**Does classification depend on accounting?** Its check doesn't. Whether each declared circuit's NCI is under the bound
reads only core (the circuit and its partition) and sampled proofs (the records are that circuit's). Its guarantee does:
"training is throttled across the datacenter" needs two things accounting supplies.
- Completeness: no training ran in undeclared compute, memory or network.
- The amounts that the throttling bound is per unit of.

So the layers form a chain, core ← subprotocols ← accounting ← classification, with the classification check reading only
core and the subprotocols.

**Policy cuts across the layers.** Each component has its own policy: the parameters the auditor fixes, its verdict rule,
and its report to the auditor. Two examples today:
- PoUS's `Pous.Protocol.Accounting.Params`: retention ρ = 18/19, δ = 1/100, space at most 1.05·|W|, λ = 128.
- The warden's `K_BITS` in `capacity.py`, which is "the inference-only policy's budget per isolation unit": a
  classification policy setting a subprotocol's parameter.

In the spec's terms, a guarantee holds at every parameter value; the policy picks the values, and a citation names them.

**Core** is the language all three layers are written in: circuits and their primitives' hardware semantics, evaluation,
commitments, randomness, statements and the integrity profile, and the shared Lean model (`Verity.Game`, `prob`, `Sound`).
It is not a layer, and it is part of every spec that reads it.

Outside the protocol:
- **Integrations** run the developer's side on a real runtime, today vLLM. They build the circuits, commit values while
  serving, and prove.
- **Measurements:** benchmarks measure what the implementations cost; probes measure the silicon against core's semantics
  and supply accounting's physical facts. For example, `native_peak` measures peak throughput.
- **The harness** builds all of the above: machines, runs, the database, integration (`check` and the merge gate),
  approvals and coordination. Infra's vision (its own document) gives its surfaces. It knows nothing about the protocol.

"System" retires as a technical term. Verity is the protocol plus its implementations, and the harness is what builds
them.

## The tree

~~~text
protocol/
  core/
    verity/                    the core library, with its Lean package         packages/verity
    circuit_check/                                                             tools/circuit_check
  subprotocols/
    sampled_proofs/                                                            protocols/sampled_proofs
    pouw/                                                                      protocols/pouw
    pous/                                                                      protocols/pous
    network_warden/                                                            protocols/network_warden
    proof_systems/             flock, the frozen gkr, direct, ligero-verify,   backends/
                               ligerito-verify, sp1, vole; redteam, shared
  accounting/                  appears with the first account split out
    compute/  memory/  network/
  workload_classification/
    lean/                      NCI's package, namespace Nci                    protocols/nci/lean
integrations/                  vllm                                            unchanged
benchmarks/                    plus numerical: references and table tooling    backends/numerical
probes/                        tc_probe, tc_probe_fp4, native_peak             tools/
harness/
  research/  check/  lean/  cluster/  agent-guard/                             tools/
  infra/                                                                       infra/
census/  fixtures/  tests/  .agents/                                           unchanged
~~~

Subprotocols are named by mechanism, and accounting and classification by the question they answer. NCI is the current
method inside `workload_classification/`, not a folder of its own.

## What the tree enforces

- `protocol/core` imports nothing else in the tree.
- A subprotocol imports only the standard library, core and itself. This is today's `tests/test_protocol_boundaries.py`,
  walking `subprotocols/`. The one crossing today is Flock's `stratified_agree.py`, an agreement check against sampled
  proofs, which belongs in tests.
- Accounting imports core and the subprotocols. Classification imports those and accounting.
- The protocol's code never imports the harness, but its tests may read the harness's store.
- The harness imports nothing from the protocol, the integrations or the measurements. This already holds for every tool
  that would move there.

## Where the tree doesn't track the concept, on purpose

1. **Policy has no folder.** It lives in each component, as its parameters, its verdict rule and its report.
2. **Specs live with what they specify.** Each component keeps its own `lean/`, and the validator that checks them is in
   `harness/lean`.
3. **The composed guarantee has no directory yet.** It would import every layer, so it gets a package at the `protocol/`
   level when the first composition theorem exists.
4. **Names in code don't move.** `import verity`, `verity_pouw`, the Lean namespaces (`Nci` among them) and the result
   kinds stay. Renaming a Lean namespace changes every record that reads it.
5. **Accounting starts inside the subprotocols.** Today the accounts live in PoUW, PoUS and the warden, and the tree
   catches up as each one is split out (see the next section).
6. **Repository-wide pieces stay at the root:** `tests/`, `fixtures/`, `.agents/`, and `census/` (data, which is leaving
   for its own repository).

## What the move costs: two steps

**Step 1, the directory move.** It's mechanical, and every approval carries.
- The moves:
  - the four subprotocol packages go under `subprotocols/`;
  - the proof systems go under `subprotocols/proof_systems/`;
  - NCI's package goes to `workload_classification/lean/`;
  - `numerical` goes to `benchmarks/`;
  - the tools are split between `harness/` and `probes/`.
- About 306 lines in 170 files outside JSON name a moved path, before counting `backends/`. The move also touches:
  - the uv member list;
  - the two Lake `path` requirements on core and their manifests;
  - `fixtures/artifacts.json`, research's `deploy.toml`, and the Tools whose commands name a path;
  - the frozen-results reader (`verity_numerical.bench.frozen`), which looks results up at their former `backends/` paths.
- No `lean-audit.json` changes, because the records hold module names and content digests, not paths.
- Every cache misses once, and every open branch rebases. `tests/test_repository.py` rejects the retired top-level
  directories so stragglers fail loudly.
- It's one scripted PR, landed in a train at a quiet hour, with the README, the Glossary and AGENTS.md in the same PR.

**Step 2, splitting accounting out, one resource at a time.** This is real work, and it is reviewed.
- Moving a Lean module to another package renames it, so every record that reads it changes. A pure move is certified by
  `audit.py --update --moved` (same statement under the old names) and needs no reviewer; anything whose statement
  changes on the way needs a statement review.
- Each account moves when it is written as a spec of its own. The candidates:
  - compute: PoUW's γ and its `Dimension` facts;
  - memory: PoUS's requirement at `Params`;
  - network: the warden's `capacity.py` and `calibration.py`.

**One name has to change.** "Accounting" already means soundness-error budgets in `verity_numerical.security.accounting`
and `FlockSoundness/Accounting/`. With accounting as a layer, those become "soundness budget" in the Glossary.

## Open questions

1. **Do proof systems move into `subprotocols/`?** They import the harness only through their `tool.py` declarations,
   plus two Ligero scripts. Either `tool.py`, which imports only `research.store.tool`, becomes the one allowed seam, or
   the declarations move to `benchmarks/`. The same choice decides whether the probes could sit in core. The frozen
   backends could also stay where they are, since nobody develops them.
2. **Where the joint policy lives.** Each component's policy is its own, but some must agree: the warden's `K_BITS` has to
   equal classification's budget. Something has to hold a deployment's parameter set and check that it is consistent. It
   isn't needed yet; the composed spec at the `protocol/` level is the natural home.
3. **When.** Step 1 changes no spec, so it can happen at any quiet hour. Step 2 rides each account's first spec.
