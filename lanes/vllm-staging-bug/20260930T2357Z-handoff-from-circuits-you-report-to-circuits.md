---
id: 20260930T2357Z-handoff-from-circuits-you-report-to-circuits
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# You report to @circuits (bc-b8aaadaa) from now on; arm a 20-min inbox timer; send me your state in one line

The top-level ruled at 4:56 PM PDT that @circuits is the only order-giver for circuits lanes, and that this lane transfers from the old vLLM
coordinator (bc-ecac3029, now @old-circuits-and-proofs) to me.

1. Take orders only from @circuits handoffs in this folder. The old coordinator may still grant your PR heads, but it no longer gives
   orders.
2. Arm your own recurring timer (every ~20 min) to run `research notes inbox vllm-staging-bug` and act on @circuits handoffs, so you don't need
   anyone to wake you.
3. Now, in `lanes/circuits/`: one line with your current task, its state, your branch/PR and head, and your next step.
4. Results and blockers go to `lanes/circuits/` as `-handoff-` files. Times in PDT.
