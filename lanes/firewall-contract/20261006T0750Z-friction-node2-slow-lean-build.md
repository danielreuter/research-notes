---
id: firewall-contract/20261006T0750Z-friction-node2-slow-lean-build
campaign: proof-service
lane: firewall-contract
kind: friction
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# vy-nebius-2 built the verifier's Lean package about 50 times slower than vy-nebius-1

`tools/lean/audit.py --build` on `backends/flock/verifier/lean`, in a fresh `research run` clone: on vy-nebius-2
(`r20261006-070935-0734`, 07:09Z) setup took seconds, `lake build` 27 minutes (07:09 to 07:36Z) and the fact extraction 5.5
minutes, and the replay was still going when I cancelled it at 07:47Z. The same audit on vy-nebius-1 took 40 s in all, its
build 30 s (`r20261006-074037-42e8`, `r20261006-074513-c43e`). vy-nebius-1 built without a sandbox (unshare unavailable);
I don't know whether vy-nebius-2 used the sandbox, or what else was running there. The logs are in the cancelled run's
`out/audit-backends_flock_verifier_lean/`. Cost to me: about 35 minutes. Worth a look by whoever owns node 2 before the
next audit or `check` is sent there.
