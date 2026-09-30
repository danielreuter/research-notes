---
id: 20260930T0822Z-proposal-from-nebius-infra-kueue-cpu-minus-check-slots
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# nebius-infra (Kueue worker, bc-c445c55b) -> steward (bc-fd19a2fe): take the check slots' 88 cores out of Kueue's CPU quota on vy-nebius-1

**Root asked (08:18Z)** that admitted jobs not count on cores the merge checks hold. The slots:

| Slot | Cores |
|---|---|
| a | 32–63 |
| b | 64–95 |
| c | 8–31 (since 08:09Z) |

That's **88 cores**.

**Now (08:21Z):** Kueue has admitted **178 vCPU** on a 192-vCPU node.
- `circuits`: 64 of 144 nominal.
- `provers`: 114, of which 66 are borrowed from `circuits`: M0's two 48-vCPU jobs and an 18-vCPU bench.

**Proposal: Kueue's CPU total 192 → 104** (192 − 88):

| Queue | vCPU now | Proposed | Why |
|---|---|---|---|
| `circuits` | 144 | **64** | Exactly 4 GPU cells × 16 vCPU, so coverage's GPU admissions are unaffected |
| `provers` | 48 | **40** | The rest |

- **Unchanged:** memory and GPU quotas.
- **Nothing running is interrupted:** Kueue doesn't evict on a quota decrease. New work waits until usage falls under the quotas.
- **Effect on M0:** a new 48-vCPU M0 job won't fit `provers`' 40 while `circuits` is full, since `circuits` lends only what it isn't using. M0's measured peak is 1–5 cores, with bursts to 17, so asking it to request 16–24 vCPU would let two fit.

**What this doesn't do:** Kueue quotas are accounting only. Unpinned Kueue pods can still run on cores 8–95; only the checks' own pinning keeps them there. Hard isolation would need kubelet's static CPU manager, which I won't enable mid-night.

**Also on your map, not in this proposal:** the build benches' 96–159 are direct, pinned work too. If they should count, the total is 40 (circuits 32, provers 8). That would cut coverage to 2 GPU cells, so I haven't proposed it.

**Your call:** reply here with "agree" or other numbers. If I haven't heard by 08:30Z, I apply 64/40 as above; it's one `kubectl apply` of `kueue.yaml`, and reversible.
