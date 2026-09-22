---
id: r20-proof/brief
campaign: r20-proof
kind: brief
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/LANES_OVERNIGHT.md
---

# Overnight lanes, 2026-09-22 (05:30Z -> ~13:30Z): shared brief

Every lane reads this first, then `backends/AGENTS.md`, then its own brief. The user's direction (2026-09-21 22:03 PDT)
is reproduced in section 1; it is the policy. The goal of the night is **overhead, well-batched on a GPU**: prover
seconds per K=1536 VU over the native 9.85 ps (`overhead.vs_native_peak`), with every number labelled.

## 1. The user's direction: focus the search without choosing a winner

Three active architecture tracks, shared tensor-core/field work, one bounded lattice scout. Deferred directions stay
deferred. This is prioritisation, not a claim that the deferred approaches are inferior.

- **Target preserved.** The registered exact numerical function and supported domain; a full `GemmCoordinate<K>` is
  the outer VU; groups, transitions, intermediate states are proof-internal choices. **K=1536 is the decision
  workload.** Interaction is allowed; transferability is not required; the completed backend must protect private
  operands and outputs against a *malicious* verifier. HVZK and non-ZK implementations are useful intermediates and
  keep their labels. **Hash/symmetric constructions are preferred**; additional assumptions may be explored as
  explicitly labelled alternatives; exploring them does not adopt them as Verity's default. Trusted setup is out of
  scope. The external Verity commitments and sampling protocol are unchanged. Numerical-backend measurements may
  exclude external authentication but must include the numerical proof's own binding, encoding, hashing, lookups,
  masking and other cryptographic work.
- **Track A, structured algebraic proving.** Can structured reductions avoid enough committed/materialised
  intermediate data to outweigh their computation and interaction costs? GKR/sumcheck, lookup integration, hash-based
  binding, privacy construction, checkpointed variants.
- **Track B, explicit local proving.** Can a shallow, regular constraint representation beat A despite representing
  more intermediate data explicitly? Direct constraints, AIR/FRI, specialised Ligero-style constructions. B is not
  only its current AIR implementation.
- **Track C, designated-verifier proving.** How much prover cost can be removed by authenticated correlations and a
  designated verifier? QuickSilver/LPZK-style VOLE-ZK. Account explicitly for correlation generation, communication,
  verifier work, secret-state requirements and the concrete assumption stack (never "VOLE" alone). AntMan-style SIMD
  compression is a possible C branch, opened only after the direct implementation's cost profile is measured.
- **Tensor cores are a first-class design target across all tracks.** For each candidate: which dominant operations
  become tensor-core matrix operations; packing, conversion, reduction and memory-movement costs; what remains hashing,
  irregular access, sequential interaction or SIMT arithmetic; the trace/base field versus the challenge or
  authentication field. Field choices are reopened where the old conclusion was SIMT-priced, but do not automatically
  pick the smallest field: count range constraints, extension arithmetic, reductions and security together. An
  operation is not efficient merely because it can be written as a matrix multiplication: keep sparsity, dimensions,
  data movement and conversion in the estimate. CPU references and tensor-core experiments proceed in parallel.
- **One bounded lattice scout**, no lattice backend yet: for our exact bounded-integer checker and batch sizes, is
  there a credible path to lower complete prover cost? Statement support, assumptions/setup, dominant arithmetic,
  witness and communication size, available implementation, tensor-core mapping; complete alternative backend or
  reusable component.
- **Deferred:** MPC-in-the-head/ZKBoo; elliptic-curve/Bulletproofs/pairings (literature comparators only); trusted
  setup; public-verifiability/transferability transformations. Existing experiments are preserved with their actual
  scope, not expanded.
- **Components are components:** fields and limb representations, lookup arguments, commitment/codeword encoders
  (Brakedown-like included), retained vs regenerated witness, checkpointed chains, privacy constructions, GPU layouts.
  Checkpointed GKR is an A/B hybrid, not "Candidate D". No generic interfaces for hypothetical combinations.
- **Comparability is required for decisions, not every iteration.** Each lane optimises on its own terms. Every
  reported measurement identifies: exact relation, domain, endpoints, transition vs full VU; batch size and
  sub-batching; implemented checks and unresolved omissions; soundness bound and privacy class; assumptions;
  preprocessing policy; measured hardware, complete costs included and omitted. Direct constraints instead of lookups
  still prove the relation; **missing predicates make it an incomplete-checker diagnostic** and must be labelled so.
  Primary operating point 2^-128 with labelled sensitivity points; never round a weaker bound into compliance. Report
  throughput and practical costs: verifier work, sequential challenge depth, communication, latency sensitivity.
- **Operating direction.** Continue A/B; develop C as the explicitly alternative-assumption track; keep shared
  tensor-core work moving; bounded lattice scout. Prioritise each lane's next concrete bottleneck or missing
  correctness/security component. SP1 stays a reproducible baseline. Do not change the frozen numerical target, the
  outer VU boundaries or the standing commitments to obtain a better benchmark.

## 2. Rules for every lane

1. Work only in your worktree `/Users/danielreuter/projects/verity-<lane>` on `lane/<lane>` (from `main`). Never
   touch `/Users/danielreuter/projects/verity` (another session, another branch) or `verity-main` (the coordinator).
2. **Never run anything heavy on this laptop** (no proving, no GPU, no z3 sweeps, no > 1 minute / > 1 GB jobs): it
   crashes the machine. Unit tests under 30 s are fine. Everything else runs on your assigned pod.
3. Pods: you do not create, resize or terminate any pod. The fleet (all bootstrapped: rustup, uv, python3.12;
   GPU pods also have `/workspace/venv312/bin/python` with torch cu124 + numpy + z3 + matplotlib):

   ~~~text
   vy-sp1    RTX 4090 24 GB       A-kernel lane (a z3 job owns one CPU core: leave it alone)
   vy-g2     RTX 4090 24 GB       hash-gpu lane
   vy-g3     L40S 48 GB (sm_89)   b-ligero lane
   vy-g4     H100 80 GB HBM3      a-packed lane (H100 is the first box cut if the account balance runs low: keep results off it)
   vy-a100b  A100-SXM4-80GB       ANCHOR, shared: matched measurements only, always `research run --on vy-a100b --exclusive`
   vy-cpu    16 vCPU / 128 GB     c-vole lane
   vy-cpu2   32 vCPU / 256 GB     a-chain + b-chain lanes share it: `--procs 12` / `-j12` each, never all cores
   ~~~

   Use `research run --on <machine> -- <cmd>` for recorded measurements (`tools/research/README.md`; the snapshot is
   `git archive HEAD`, so **commit before every remote run**; `research fetch <run_id>` brings results back). For
   interactive work `uv run --package research python -m research.pods.runpod ssh <pod_id>` prints the ssh command
   (pod ids in `~/.research/machines.toml`). Build under `/workspace` (persistent), `CARGO_TARGET_DIR=/workspace/target`.
4. **Ledger.** Every 60-90 minutes, and at every result, append to YOUR ledger file with
   `uv run --package verity-numerical python -m verity_numerical.bench.ledger add --lane <lane> --track <A|B|C|shared|scout> ...`
   (see `python -m verity_numerical.bench.ledger --help`: scope `unit` numbers are x96 extrapolations and must list
   what is omitted; `component` entries carry no overhead; `--breakthrough` for an idea-level change, with a short
   label that reads well on a plot), then regenerate `python -m verity_numerical.bench.plots` and commit both the
   `.jsonl` and `backends/numerical/reports/plots/overhead_<lane>.png`. The user wants to wake up to these plots.
5. Labels (section 1, last bullet) on every number: `proof_class`, `authentication`, scope, B, K, security target,
   hardware (the probed device), assumptions, omitted costs. An incomplete checker is `ARITHMETIC_DIAGNOSTIC` or an
   explicit "incomplete-checker diagnostic" note; never a proof number.
6. Correctness first: cross-check against the WP2 reference checker (`verity_numerical.checker`) and
   `fixtures/bench-instances/v1` (positives must be accepted with the recorded words; the 52 negatives rejected).
   A prover that accepts a `vu-k1536-neg` instance has no number to report.
7. Commit early and often with clear messages; keep the tree clean; **do not merge into main** (the coordinator
   merges). `uv run --package verity-numerical pytest backends/numerical -q` stays green; `uvx ruff check --isolated`
   clean on new Python. Rust: `cargo test` green in your crate.
8. Context/handoff: if you are running low on context or time, write `HANDOFF.md` in your lane directory (exact
   state, what is running where, run ids, next three steps) and commit; the coordinator resumes with a fresh agent.
9. Time box: until ~13:00Z (06:00 PDT) or done. Final message: branch + commits; ledger entries added; the table of
   numbers with labels; what was NOT done; the next three steps. Numbers with units and assumptions; no filler.
