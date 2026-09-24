---
id: vllm-refactor/lane-brief
lane: vllm-refactor
kind: brief
status: active
created: 2026-09-24T17:30Z
---
# vllm-refactor lanes: shared brief

Read this fully before starting. Your prompt gives your lane id and scope.

- **Coordinator:** the vLLM coordinator chat (eb746331). **Owner:** Daniel.
- **Plan of record:** `~/.research/notes/lanes/vllm-refactor/SYNTHESIS.md`. Section 2 lists the defects D1..D17 with `file:line`, section 4 the practices, section 5 the target shape, and section 6 the phases.
- **Detail:** the four `survey-*.md` reports in the same directory. The `*coordinator-checks-*.md` notes correct some survey claims, and where they disagree the notes win.

## Owner decisions (2026-09-24 17:20Z)
- **Base:** `main` at `72884c8a` (`lane/vllm-cleanup-2` merged).
- **Value checks (D1):** compare against opened, verified values inside the Commit process now. A separate verifier process comes later, in Phase 2.
- **Experimental paths:** delete the CMT-1 committer: `commit/reference_engine/`, `commit/reference_engine_adapter.py` and the `cmt_ref_*` paths in `harness/commit_delta.py`. Also delete `commit/engine_rs/`. The proof-of-concept bundle chain goes later, once `merkle` comes from core; delete only the parts that have no caller now.
- **Tensor parallelism:** refuse world > 2 with a clear error until collectives land.
- **Not decided, so don't do them:** commitment-scheme alignment, retiring Definition ids, and anything that changes Program digests, manifest digests, commitment roots, leaf ids or regression verdicts. Those are Phase 3, done in one re-baseline.

## Hard rules
1. **Laptop.** Nothing beyond git, rg and the light `research` launcher. No pytest, no importing `verity_vllm` or torch, no builds. The laptop has about 9 GB of disk free, and a guardian kills any Python process over 1 GB. All tests run on pods.
2. **Your own worktree.** From `/Users/danielreuter/projects/verity`, run `git worktree add /Users/danielreuter/projects/verity-wt/rf-<lane> -b lane/vllm-rf-<lane> 72884c8a`.
   - Never touch `/Users/danielreuter/projects/verity` itself (the owner's checkout), other lanes' worktrees, or anything under `verity-main-wt/` (another coordinator's).
   - Never push to `main`; the coordinator merges.
3. **Pods.**
   - Name them `vyv-rf-<lane>[-suffix]`. The deadline daemon (03:00Z) and the budget daemon own the `vyv-` prefix. The budget is shared.
   - Use the cheapest pod that does the job, a GPU pod only when your acceptance needs one, and terminate pods when you're done.
   - Tools: `research pods create|list|ssh|sync|terminate` and `research run --on` (see `tools/research/README.md`).
   - A pod that ran `research run` attempts is drained with `research pods drain`, which preserves the attempts. Draining needs short-lived R2 credentials: `research data mint-credential --ttl 1h --via local --env`, with the parent key pair from `~/.config/verity/r2.env`, run in a subshell.
   - The integration has pod bootstrap scripts in `integrations/vllm/ops/`. Record the exact environment (python, torch, vllm and triton versions) with your results.
4. **Behavior preservation.** Your change must not change Program digests, manifest digests, commitment roots, leaf ids or regression verdicts. The exception is where your scope says the fix changes a result; then show before-and-after evidence.
5. **Gate before READY.** On a pod, at your branch head:
   - (a) `VERITY_REGRESSION=1 python -m pytest integrations/vllm/tests/regression -m regression` is green.
   - (b) `python -m pytest integrations/vllm/tests` has 0 failures and no new skips compared with the baseline. The baseline is `~/.research/notes/lanes/vllm-rf-a1/baseline.md`, which lane a1 writes at `72884c8a`. If it isn't there yet, measure the base yourself on your pod with the same environment.
   - (c) Everything your scope's acceptance lists.
   - Record the exact commands, counts, environment and commit in READY.md.
6. **Tight scope.**
   - Anything outside your scope goes under "Found, not fixed" in your state note; don't fix it.
   - Other lanes are editing the tree right now (list below). Keep hunks in files they own minimal, and never reformat or reorder code you aren't changing.
7. **Style.**
   - Match the surrounding code, and add no new Markdown files to the repo.
   - Comments only state constraints the code can't show.
   - No board ids, lane names or dates in code or docstrings you write.
   - Put new tests next to the existing ones for the same code.
8. **Crash-only.** The Cursor process running you may crash, and a fresh agent will resume from your state note.
   - Keep `~/.research/notes/lanes/vllm-rf-<lane>/STATE.md` current: update it at the start, at least every 20 minutes, and at every milestone.
   - It records what's done (commits), what's running (pods, commands, log paths on the pod), next steps and open questions.
   - Commit and push at every milestone: `git push -u origin lane/vllm-rf-<lane>`.
9. **Finish.** Write `~/.research/notes/lanes/vllm-rf-<lane>/READY.md` with:
   - the branch and head commit;
   - the gate evidence;
   - what changed and what deliberately didn't;
   - "Found, not fixed".

   Then drain or terminate your pods and return a summary of 250 words or fewer.

## Lanes running at the same time, and the files they own
- **a1, guardrails and baseline:** the new `tests/lint/`, lint allowlists, `baseline.md`.
- **a23, dead code, data and paths:** deletions, moves to tests, package data via `importlib.resources`, `sys.path` and `parents[N]` fixes.
- **f1, opened-value replay (D1):** the value-check path in `check/oracle_compare.py`, `harness/commit_delta.py`, `tp/worker.py` and `tp/partial_source.py`.
- **f24, identity and integrity (D5, D6, D7, D10, D11, D13):**
  - `harness/hot_commit.py`;
  - the identity parts of `harness/derive_step.py`;
  - the code key in `tp/commit.py`;
  - `check/global_match_fast.py`, `check/commit_verdict.py`, `check/verdict.py`;
  - `_eq` in `input_provenance/weights_of_record.py`.
- **f3, undeclared inputs (D3, D4, D14, D15):** the layout environment variables in `acquire/native_collect.py` and `commit/padding_steps.py`, `acquire/plan.py`, challenge seeds, and the environment-driven tables in `program/registry/prims.py`.
- **f56, collectives guard and FA-tap exactness (D16, D17):**
  - the MoE class lists in `tp/partial_source.py` and `tp/worker.py`;
  - `program/registry/quarantine/collective/allreduce.py`;
  - `correspondence/emit.py`;
  - a new FA-tap exactness property check.

f1 and f56 both touch `tp/worker.py` and `tp/partial_source.py`, in different functions. a23 and f1 both touch `harness/commit_delta.py`: a23 deletes `cmt_ref_*`, and f1 changes the value check.

**Merge order:** a1, then a23, then the f-lanes as they become ready. When the coordinator says `main` moved, rebase onto it. A rebase that deletes stale lint-allowlist entries is expected.
