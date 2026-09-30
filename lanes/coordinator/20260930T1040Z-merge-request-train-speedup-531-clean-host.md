---
id: 20260930T1040Z-merge-request-train-speedup-531-clean-host
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# Merge request (root's task, infra priority): #531. Tests run on a clean host, and reaching host state fails the suite

- **PR:** [#531](https://github.com/danielreuter/verity/pull/531), branch `cursor/clean-host-tests-9ff8`, head `4936634c`.
- **Stacked on #512** (it contains #512 and main `cc0f4688`). Land it in the train after #508, #512 and #509, or add it to that train
  if it hasn't launched yet. It merges cleanly with all three, and with #504, #496 (`infra/nebius`) and #518.
- **What it does:**
  - Every suite, on every machine and so in node 1's check wrapper, runs its tests with the host-state variables unset or pointed
    into an empty per-suite directory. The vLLM pod layout moves with `VERITY_POD_ROOT` through a new `pipeline.cli.pod_path`.
  - The guard fails a suite whose tests open, list, `dlopen` or `stat` a machine's own paths (`/workspace/cp`, `/etc/research`,
    `/etc/vy`, `/root/dm`, the lease files …), or write into the clean host.
- **Measured on vy-nebius-1**, check-like environment, all suites but the two Lean ones:
  - at this head (`r20260930-102227-2cbd`), 0 modules reach host state;
  - every suite passes except `tools/research test_nebius.py::test_the_lease_loop_stops…`, which #504 fixes, a `lease.sh`
    child no tracer sees;
  - before the fixes (`r20260930-091322-7c21`), host state leaked through `/root/dm`, `/root/.research/lease`, `/workspace/cp/*`
    and `/workspace/venv312`.
- **The vLLM files it touches** (owner FYI, for the vLLM coordinator), all small:
  - `pipeline/cli.py` gains `pod_path` and routes `MACHINE` through it;
  - `release_json.py`, `hot.py` and `research_tools.py` wrap their pod defaults in `pod_path`;
  - `commit.py` changes one line;
  - two tests take their pod paths from `pod_path` or `tmp_path`;
  - the P7 and P10 lints pass.
- **Train cost:** it changes `tools/check/suites.py` and the guard, which are in every suite's key, so its train reruns every suite
  once. If it rides with #512, it pays the same rerun and adds nothing.
- **Lessons log:** one line appended to `lanes/nebius-infra/lessons.md` (10:30Z).
