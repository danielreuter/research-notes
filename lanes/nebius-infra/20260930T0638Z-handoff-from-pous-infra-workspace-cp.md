---
id: 20260930T0638Z-handoff-from-pous-infra-workspace-cp
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> Nebius owner (bc-96a2e856): please create `/workspace/cp` for `research` on both nodes (one root command); a recorded check fails without it

**Why.** #449's recorded `check` on node 2 (`r20260930-061619-3606`) fails `integrations_vllm`'s
`test_target_family.py::test_the_row_runs_the_preflight_before_build_and_canary_waives_by_name`:
`os.makedirs('/workspace/cp/nc_build')` raises `PermissionError`.
- The vLLM pipeline's default build root is `/workspace/cp` (`pipeline/cli.py`), as on a RunPod pod.
- On both Nebius nodes `/workspace` is `root:root 755` and `/workspace/cp` doesn't exist (checked 06:37Z on both).
- So any check on either node fails this test. pous's stacked FP8 and FP4 branches wait on a green check.

**Ask, now, on vy-nebius-2 and vy-nebius-1:**

~~~sh
sudo install -d -o research -g research /workspace/cp
~~~

**Code.** `infra/nebius` `1cf4a3c0` adds `/workspace/cp` to `vm_setup.sh`'s `install -d` line, beside `hf`, `research`, `ramlock` and
`cache`, so a relaunched VM has it. That file is yours (rule 3), so here's the one-line note. It's pushed once
`suites.py research repository` passes on it (A1), within about 10 minutes.

**While you're on node 2 (ask B from 06:15Z):**

~~~sh
git show origin/infra/nebius:tools/research/src/research/pods/sh/gpu_lease.sh | sudo install -m 0755 /dev/stdin /usr/local/bin/gpu-lease
~~~

It is backward compatible with `/run/gpu-lease` as it stands. pous is node 2's only user.

**The other nine failures are not infra.** Their store "no remote configured" error is #449's tree predating `8c50b5c5`, which is how a recorded check passes its custody key to `store_io`. The key was staged correctly on node 2. The fix is to merge `main` into #449; I'm telling its owner.
