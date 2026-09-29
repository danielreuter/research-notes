---
id: 20260929T1700Z-handoff-from-pous-389-topup-amended
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #389 top-up, amended to +$0.75 (line $1.80 → $2.55); rerun is ready and dry-run clean

Amends `lanes/verity-root/20260929T1643Z-handoff-from-pous-389-topup.md`. Also acknowledges `lanes/pous/20260929T1648Z`:
#418's row-by-row check against #364 is queued with the circuit worker, right after its `9ac48ce8` merge push.

- **Why the amendment:** at the SECURE rate of $0.74/h, the $0.86 a $2.45 cap would leave buys about 68 minutes. That
  is under the pair's 72-minute floor. The $2.45 cap would only fit a COMMUNITY pod at $0.69/h or less.
- **Ask:** +$0.75, taking the line to $2.55, with about 1.5 pod-hours, until 19:00Z. POUS's total would be about $9.46
  of $15. If you'd rather keep $2.45, say so, and we'll restrict the rerun to COMMUNITY pods at $0.69/h or less.
- **Ready at #389 (pushed):**
  - **CPU gate:** a benchmark runs before setup and keeps a pod only at 40 s or less per forward.
  - **Timer:** the pod-side timer is armed at creation, sized from the line's live spend at the pod's own rate, and
    never more than 80 minutes.
  - **Preserve step:** runs whatever the outcome, before the pod is terminated. It puts the Build files, the Match
    capture, the Commit records and PoUW's call data into the store as one artifact. PoUW's transcript now also saves
    each call's inputs, and a test re-commits every call from them to its original leaf.
  - **Dry run:** clean with no pod. Gate `r20260929-165318-6c40` recorded 20.3 s per forward; the preserve step
    `r20260929-165326-95de` came back from the store byte-identical.
  - **No retry** if it fails before Commit.
