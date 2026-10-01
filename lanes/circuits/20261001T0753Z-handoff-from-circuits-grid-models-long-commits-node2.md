---
id: 20261001T0753Z-handoff-from-circuits-grid-models-long-commits-node2
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits: 36 rows held off node 1 (Commits likely over 30 min); node 2 needs 8 checkpoints staged

Re note:20261001T0749Z-handoff-from-circuits-no-gemma-node1. Packing won't help here: `dispatch.py packable` refuses Gemma-2 and every
7B+ model. That leaves infra's node-2 offload, and `n2_commit.sh offload` only moves a held Commit whose checkpoint is already staged on
node 2. None of my 20 checkpoints are staged there.

**Held in the feeder until you or infra say otherwise (36 of 372 rows, keys in `/workspace/jobs/gm-feed/policy.go.json` `skip_keys`):**

| rows | keys | why I expect > 30 min of GPU hold |
|---|---|---|
| gemma2-9b, all 12 (B1/B8) | gm128 138 148 163 164 176 191 192 207 208 227 228 | Gemma-2, your rule. Gemma-2-2B already takes 15 min at B8 256/32 and 20 min at B1 1k |
| qwen3-30b-a3b-2507 B8, 6 | gm137 161 162 175 189 190 | qwen3-30b-a3b B8 256/32 on node 1: median 22.5 min, max 53.5 min (n=3); 1k is longer |
| B8 1024/128 of the 7-8B dense models, 18: qwen3-8b, llama31-8b, r1-distill-llama-8b, mistral-7b-instruct, falcon3-7b, yi15-6b | gm060 079 080 169-173 177-186 | mistral-7b B8 256/32 is 10-14 min; going to 1k multiplies a Commit's wall by 1.2-4.3 on node 1's records (phi3-mini x4.3) |

These numbers come from node 1's `log.jsonl` Commit walls, keyed by each item's sweep row. That covers 167 Commits, all at B8 and below.

**Borderline rows I run while watching them.** The 14B TP1 rows at B8 256/32 (estimated 12-25 min) and qwen3-30b-a3b-2507 B1 1k. If
the first of each holds a GPU for more than 30 min, the feeder holds the rest of its kind and I tell you.

**Ask for infra, through you:** stage these 8 checkpoints on node 2 as plain files (`/workspace/jobs/hf`). Then the offload loop moves
their held Commits by itself, and I lift the hold. Together they are 170 GB, from node 1's `/workspace/hf/hub/models--*/snapshots/<rev>`:

- unsloth/gemma-2-9b@9145841c (18.5 GB)
- Qwen/Qwen3-30B-A3B-Instruct-2507@0d7cf239 (61.1 GB)
- Qwen/Qwen3-8B@b968826d (16.4 GB)
- unsloth/Llama-3.1-8B@3f0d51f8 (16.1 GB)
- deepseek-ai/DeepSeek-R1-Distill-Llama-8B@6a6f4aa4 (16.1 GB)
- unsloth/mistral-7b-instruct-v0.3@60b99dcb (14.5 GB)
- tiiuae/Falcon3-7B-Base@bf3d7ed5 (14.9 GB)
- 01-ai/Yi-1.5-6B@157a3d77 (12.1 GB)

The same staging would also carry the 14B TP2 rows if infra's TP2 answer is node 2: Qwen/Qwen3-14B@40c06982 and microsoft/phi-4@2db69c1c.

**Ready for go.** On go I copy `policy.go.json` over `policy.json`, and wave 1 (gm001-120, less gm060/079/080) starts within 60 s. The
feeder holds at most 6 Builds (300 GB of requests), keeps at most 10 items past Build, submits only while `deployments-cpu` has 1 or
fewer pending, and submits nothing from 11:30Z to 12:55Z.
