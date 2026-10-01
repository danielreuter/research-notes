---
id: 20261001T1217Z-handoff-from-circuits-pr2-plan
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (5:17 AM PDT): PR 2 plan; head and body to me by 5:50 AM PDT for node 1 after 5:55

1. **Merge PR 1's new head `80703ab0e`** (slot d's `c382dd846` merged in, re-granted) into `cursor/bool-gemma2-f91f`. PR 1 is no longer at `443538fed`.
2. **Softcap: yes, stack it on PR 2 if it's ready by 5:50.** circuits-bool-silu (bc-73f78a8e) is binding `MufuTanh_v2` (`abc153b55`) into
   `cursor/bool-softcap-attn-e311`, with circuit-check bindings and pins, and writes its head to this lane by 5:50. Take that head rather than
   reverting `eb8cb9169` yourself. If it isn't here by 5:50, PR 2 goes without softcap; say in the body that Gemma-2 isn't pure Boolean yet and
   name the one missing piece.
3. **SiLU v4 stays out** (it matters only after `SiluMul_v2` is promoted, which is on Daniel's morning list).
4. **The 80k-row chain comparison:** I'm asking circuits-bool-norms to re-run it on node CPUs in chunks after 5:55. Note in the body that it's re-running.
5. One line to me with the final head, the node-1 run `r20261001-121243-db76`'s results, and the body path. I open PR 2, grant it and send it to
   the captain. It must land by 7:50.
