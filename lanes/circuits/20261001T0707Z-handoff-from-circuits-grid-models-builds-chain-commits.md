---
id: 20261001T0707Z-handoff-from-circuits-grid-models-builds-chain-commits
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models (worker of @circuits)
---

# @circuits: 20 models (35 in the grid, 11+ families) staged; every Build path chains its Commit, so I hold all submissions until your go unless you say "builds now"

**State, 12:07 AM PDT:** the 20 ungated checkpoints are downloading to node 1 (run r20261001-064838-2a41, 275 GB, ETA ~12:45 AM PDT).
On `cursor/grid-models-8c79` (off `cursor/coverage-v1-2622`, not pushed yet), each role's HF config is shipped and its TP1 profile fixture is
written; every role derives at TP1, and QWEN3_14B and PHI4 also at TP2. The 480 workloads (24 per model) are generated, and the
weights.tsv group `grid-models` is in. The checkpoints.json entries follow from node 1's hashes once the downloads land.

**1. Hold (decision).** A config-run Build can't run without its Commit. `dispatch.py tick` submits task 1 when the Build succeeds,
`n2_build.sh` submits `--task 1` itself, and release.py releases by its own rule, not by your go. A Commit created while GPU quota is
free is admitted before any tick can hold it.
- **Default:** I submit nothing until your go, then the first wave within ~10 min. Builds take a median of 9 min (p90 50), so Commits
  flow by about go + 20 min.
- **My recommendation:** say "builds now" for the TP1 B1/B8 rows of the 10 models under 7B as soon as the checkpoints land (120 rows),
  so their Commits join release.py's queue from ~1:00 AM PDT.

**2. B16+ of 7B+ and MoE rows (FYI).** release.py's `kept()` holds B16+ for row ids starting with `mistral-7b`, `qwen3-30b`, `olmoe`,
`llama31-8b` or `gemma2-9b`, and that covers 5 of my models. I'll submit no B16/B32 row for any 7B+ or MoE model unless you lift the
hold. That also covers the 5 not in BIG_MODELS: qwen3-8b, r1-distill-llama-8b, falcon3-7b, qwen3-14b and phi4-14b. The plan is then
10 × 24 + 10 × 12 = **360 rows**.

**3. TP2 and node 2 (please ask @infra).** As of its 2:55 PM PDT report, `n2_commit.sh` refuses non-TP1 rows. How do TP2 Commits
(qwen3-14b and phi4-14b, 12 rows) and TP1 overflow go to node 2 now? Is `n2-commit-offload` (Commits held 2 min or more, `vllm-epoch-run/`)
the overflow path for TP1? Both 14B models also fit one GPU (29 GB). Given the known TP2 staging gap at B8, I can add TP1 B1/B8 rows for
them (12 more) if you want those counted on node 1.

**4. Families I count (proposal).** One id per publisher model series: base, instruct and coder variants together, and the R1 distills
under their base. New: `qwen25` (3b, 05b-instruct, coder-15b, r1-distill-qwen-15b), `qwen3` (06b, 17b, 8b, 14b, 30b-a3b-2507), `llama3`
(llama32-3b, llama31-8b, r1-distill-llama-8b), `smollm2` (17b), `mistral` (7b-instruct), `gemma2` (9b), `olmoe` (0125-instruct),
`phi` (phi4-14b), `yi` (yi15-6b), `falcon3` (1b, 7b). With the grid's `tinyllama` and `pythia` that makes 12, or 11 without
pythia. Counting qwen3-moe and deepseek-r1-distill as their own families makes 14.

Next: the checkpoints.json entries, the touched tests, then commit, push, and sync the tree to node 1. Keys will be `cov-gm01`…, with
SWEEP_DIR `/workspace/jobs/cov/cov-gmNN`, with env and resources as cov-cg10, and every item naming its research question.
