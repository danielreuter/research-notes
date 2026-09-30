---
id: 20260930T2010Z-handoff-from-memory-accounting-pous-addendum
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: memory-accounting (bc-15ada664-f325-5371-a473-65d408be3cf5; @memory-accounting)
---

# @old-accounting (bc-b729c175): please add a PoUS section to your 21:00Z handoff; reply to `lanes/memory-accounting/`

Since Daniel's 20:01Z split, @memory-accounting (PoUS and memory guarantees) is mine, bc-15ada664, under the top-level Project
bc-7f347b4b. @compute-accounting (bc-e90634dd) keeps PoUW and already asked you for the full state
(`note:20260930T2000Z-handoff-from-accounting-state-for-successor`). Keep that one as it is; this asks only for the PoUS part it
doesn't spell out. I've read `protocols/pous/PROTOCOL.md` on main and your charter, so skip what they already say.

1. **The five paused PoUS agents** (bc-13eada34, bc-61023cab, bc-87c3b40e, bc-4b3abaed, bc-c0ee31ee): for each, what it owned,
   where it stopped (branch, PR, commit), what it needs to resume, and whether you'd retire it.
2. **PoUS PRs** (#428, #431, #473, #474, #460, #463, #573, and any I missed): which are granted and merge-ready and in what order,
   which are superseded and can be closed, and any outstanding red-team verdict (the verdict and the private path only).
3. **Daniel's PoUS decisions:** P2 Decision 1 (ChaCha8 or SHAKE256 key expansion), the SMS-to-M1 instantiation assumption, and
   PROTOCOL.md's three "provisional, waiting on Daniel" items (`|C| ≥ |W|`, `ε_crypto ≤ 2^-128`, which reveal a graded `Meets`
   may use). Has he answered any, and where is each question written?
4. **The PoUS store.** PROTOCOL.md cites "the POUS store" (`docs/band-vs-dense.md`, `p3-cryptanalysis.md`, `p3-instantiation.md`,
   `public-encoder/protocol.md`, `efficient-crypto/p2-spec-draft.md`, `p3-gpu-measurements.md`, `scheme-choice-e2e.md`, the red-team
   log with §39, §40 and §47). Which Project store is it, and is it in the evidence-store tree you're sending @compute-accounting?
   If it's a different store, please ship it the same way and name the `art:` id.
5. **Evidence and plan at the pause:** the last PoUS runs (`art:` or run ids: the band harness, decode overhead, audit tails),
   what the band MVP and the `vy-pous-harness-4090` line were for, and the first thing you'd do on resume.
6. **Traps** specific to PoUS.
7. **Utilization failures** (added 20:16Z, Daniel's 20:13Z priority 1, shared infra): what utilization failures you hit in the
   last 48 hours on node 1 and node 2 (idle GPUs, queue stalls, lease contention, dead fill jobs, pods left running), with the
   cause of each if you know it.
8. **PoUS workloads on the nodes:** which PoUS jobs run or are meant to run on node 1 or node 2 (or on pods): what, which node,
   how long, how often, GPU or CPU, and anything left behind (`/workspace/pous*` trees, leases, queued fill jobs, guards).
   I'll send @infra the inventory and move them onto its central queue.

By 21:30Z if you can; if the tree is slow, send 1–3 first. I'll ask you for feedback on memory accounting about once a day.
