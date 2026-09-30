---
id: 20260930T2008Z-handoff-from-network-accounting-network-state
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: network-accounting subcoordinator (bc-ecea50f6-c509-5918-b17a-d2148d57728f; @network-accounting)
---

# @old-accounting (bc-b729c175): the network parts of your state, for @network-accounting

I'm bc-ecea50f6. Since Daniel's 20:01Z split I hold @network-accounting: the network warden (`protocols/network_warden`, its
Lean package) and network resource guarantees. I'm taking over the idle network-timing agent bc-6b78649f and its #326.
@compute-accounting's ask (`note:20260930T2000Z-handoff-from-accounting-state-for-successor`) covers PoUW; this one asks only
for the network parts. If your 21:00Z reply to `lanes/accounting/` already has a network section, point me at it and skip this.

Please answer in `lanes/network-accounting/<stamp>-handoff-from-pous-network.md`, by 21:30Z if you can:

1. **bc-6b78649f.** Its last brief from you, what you'd have it do next, and anything it owes or is owed.
2. **Direction.** What you think network accounting should deliver next (a live warden run on pods, integration with PoUW or
   vLLM, bandwidth or latency guarantees beyond the timing channel), and anything Daniel said about it.
3. **Daniel's decisions.** Any open or answered question about the network warden or network guarantees, and where it's
   written.
4. **Promises.** Anything on the network side you promised Daniel, @proofs (the train), infra or anyone else.
5. **Other work that touches it.** Agents, PRs or notes on network resource guarantees outside the warden (for example
   `census/networks.json`, the benches' RTT model, the resource-ontology agent bc-e79791ab).
6. **Reviews.** Red-team verdicts on #461 or #326 that are outstanding (the verdict only, with the private path).
7. **Traps.** Anything that bit you on this work.
