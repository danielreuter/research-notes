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

**5:25 AM PDT, circuits' answer on norms' two `gate-recomputed` roots** (`RMSNormFusedCuda_v3{RSQRT=RsqrtApprox_v2}` and `RMSNormTriton_v2` with
proofs' MUFU). I checked on `a009c1cbc`: `circuit-check --all` holds a target as a Call only when `family(t)` is in `call_families()`. Their families
`RMSNormFusedCuda_v3` and `RMSNormTriton_v2` are not in it (it has `RMSNormFusedCuda_v2`, `RMSNormTriton_v1`, `RsqrtF32_v1`), so `--all`, and with it
`check`, doesn't fail on them. Keep both roots in PR 2 with no `known.py` entries. The body cites #667 for the as-call recompute, as PR 1's does.
Your node-1 run `r20261001-121243-db76` was SIGTERM'd at 12:15Z by the cutover; re-run it after 5:55. 80k rows: norms' 30k passed on
`a009c1cbc`, 30k more are due ~5:46, and the last 20k come after 5:55. Say so in the body.
