---
cursor:
  subagentId: "bc-7ff3de9e-dd31-5d7f-9e53-265bfba177d0"
id: 20261001T0705Z-merge-request-from-pr-captain-train-642-and-c6
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pr-captain (bc-7ff3de9e), for top-level (verity-top)
---

# For the lander (@old-circuits-and-proofs, bc-8ece7cde): the next free slot after C5B/T49 is one train of #642 plus the ready PRs, then C6 = #638 alone

The order is top-level's call, made at 11:59 PM PDT. Every head below is pinned. Each trial merge was done on `tr-T49` `fc8eac5a6`, in this order, and each one is clean.

## First: the Boolean IR (Daniel's first priority, added 12:25 AM PDT)

Once `cursor/proofs-ir-95d4` (`46c768b2c`, its PR opened by proofs) has a passing check, it takes **the next free slot, ahead of everything below**. It goes alone, with `lean-agreement`, since 7 of its files are under `backends/flock/`. It is clean on `main` and before or after every train here. It should land well before node 1's 5:10 AM PDT hold, so its train starts by about 3:30 AM, or records on node 2.

## Train 1 (no `lean-agreement`: nothing here touches `backends/flock/`)

| order | PR | owner | head |
|---|---|---|---|
| 1 | #642 Lean audit: the cache directory may be a symlink | proofs/lean | `34b483e78` |
| 2 | #612 using-slack: conflicting-actions norm | infra | `d046c615c` |
| 3 | #614 `research notes inbox --urgent` | infra | `34ff57b49` |
| 4 | #618 agent-guard: credentials out of remote URLs | infra | `0c22ce3ec` |
| 5 | #625 cluster: honor `gpu-lease --on` lists | infra | `b3b225e0f` |
| 6 | #626 `cluster status` | infra | `b74bbf74f` |
| 7 | #641 console: publish owners' overnight numbers as panels | console | `6f408854a` |
| 7b | #588 PoUW harness side chain (contains #491, #590 and #595) | compute accounting | `947f1de2c`: ready at 11:54 PM PDT, check `r20261001-063447-4b26` passed at this head; #491 lands first, in T49 |
| 8 | #639 vLLM Build: the manifest beside the workload compose | circuits | `1c2487ef8` (**only with circuits' grant at this head**) |
| 9 | #640 refuse a linear that carries a quantization parameter | compute accounting | `fbce5a2f4` (**only with circuits' grant**) |

- **The grant condition on #639 and #640.** I can't see the evidence store from here. #639's own note (`lanes/circuits/20261001T0618Z-handoff-from-circuits-build-speed-pr-639-grant`) says it waits for circuits' grant at `1c2487ef8` and a passing check. I found no grant for #640 either. Include each only if `grant=circuits` (or `vllm-coordinator`) is on its head. Without them, train items 1–7.
- **Why #642 goes first:** it puts the Lean audit cache fix on `main` before #638 runs. Any check on vy-nebius-1 that audits a Lean package without a cache hit fails until it lands, and #638's check failed that way.

## Train 2 = C6, stacked on train 1 (`lean-agreement`)

| PR | owner | head | notes |
|---|---|---|---|
| #638 C-Flock soundness restatement (SHA-512's two collision-resistance forms) | proofs | `22fe745f2` | red-team-flock-3 granted both roles at this head (`20261001T0550Z-reply-from-red-team-flock-3-638-granted`); Daniel's yes on the pin; touches `backends/flock/`, so record with `--on POD` and send the pinned build |

#638 stacks cleanly on train 1 with or without #639 and #640.

## Slot B, free now, in parallel (added 12:20 AM PDT)

| PR | owner | head | notes |
|---|---|---|---|
| #496 `infra/nebius`: shared Nebius server code | infra | `5314b8a34` (marked ready; `main` merged in) | clean on `main` and clean before or after slot A's train 1 and C6; nothing under `backends/flock/`, so no `lean-agreement`; 63 files |
| #473 PoUS band certificate up to 2^64 segments | memory accounting | `85edd4fb3` (marked ready about 12:25 AM PDT) | clean after #496; no `backends/flock/` |
| #643 census: RTX PRO 6000 Blackwell bf16 | memory accounting | `843363743` (marked ready) | clean after #473; no `backends/flock/` |

**Node 1's hold, 5:10–5:55 AM PDT:** a train whose check would start then should record on node 2, or be in flight by 5:10.

Queue: `internal/hygiene/train-queue.md` in the top-level Project store.
