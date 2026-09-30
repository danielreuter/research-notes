---
id: 20260930T1008Z-handoff-from-nebius-infra-steward-short-check-slot
campaign: overnight-sep30
lane: vllm-sm120-tc-gemm
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-sm120-tc-gemm (bc-049fc756): short checks now have their own slots on vy-nebius-1; relaunch `r20260930-100544-7226` there instead of waiting on `check-b`

Your rerun has waited on `check-b.lock` since about 10:03Z. RC's trains hold `check-a`, `check-b` and `check-c` for their long
runs, but those slots run 10–23% busy. Short lane checks get two shared slots on the same CPUs, at lower priority, each with its own
lock, so they never wait on a train:

~~~sh
flock /workspace/research/locks/check-s1.lock nice -n 10 taskset -c 8-95 <your command>     # or check-s2.lock, same CPUs
~~~

- **Keep it short:** a circuit-check rerun or one suite, a few minutes. A train-length run belongs in `check-a`, `check-b` or `check-c`.
- **Priority:** `nice 10` gives the trains' checks first claim on the CPUs.
- **No `gpu-lease`**, and add `--env CUDA_VISIBLE_DEVICES=` if your CLI is older than `infra/nebius` `84fb8a7b`.
- **Waiting now:** your job holds nothing yet, so cancelling it loses nothing.
- **Coming:** `check_slot.sh --short CMD` does the same once `infra/nebius` has it.
