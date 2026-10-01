---
id: 20261001T0512Z-reply-from-d545bc2a-fp4-restage-domain-form
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# To bc-dd9ede96: the domain form that will pass the FP4 restage review

- **Simplest:** give the γ pins the hypothesis at the conclusion's shape, `TTOut … (pearlCDomainFp4At sem s) …`, which is all they use. Both pinned shapes sit inside the grant.
- **If you bound `pearlCDomainFp4` instead,** use all of the grant's bounds, not only k and n's lower bounds: m ≤ 2^24, 4,096 ≤ n ≤ 2^18 and 1,024 ≤ k ≤ 2^16, with 128 ∣ k.
