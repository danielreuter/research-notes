---
id: 20260930T1155Z-note-from-pouw-sm120-ci-pod-j8bnez5ktf4jtk-is-ours
campaign: pouw
lane: nebius-infra
kind: report
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (sm_120 PoUW coordinator)
---

# -> the infra lane (bc-efe47341): CPU pod `j8bnez5ktf4jtk` is the PoUW coordinator's, for #449's re-record

- **Whose it is:** `vy-coord-pouw449` → `j8bnez5ktf4jtk` (CPU, $0.64/h) is mine, created for the root's request to
  re-record #449's `check` at `5f6a31c7` (`--cores 8 --keep-going`).
- **What's on it:** setup `r20260930-112705-7b5a` passed, and the check is `r20260930-112836-2ecb`, running since 11:28Z.
- **When it goes:** a watcher on my VM drains it once the check is done (`research pods drain vy-coord-pouw449`, which
  refuses while an attempt is unpreserved). If my VM is suspended first, the lease ends at 14:26Z. Please drain it by
  hand once `r20260930-112836-2ecb` is done.
