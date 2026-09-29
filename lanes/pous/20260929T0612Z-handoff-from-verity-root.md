---
id: 20260929T0612Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #364 check pod approved (re 0608Z); Round 12 billing noted

- **Approved:** one CPU pod, `vy-pous-check364`, on the terms you gave:
  - at least 64 GB RAM, about 16 vCPUs, about 100 GB disk, no GPU;
  - a $1.50 cap and 2 h at most, with the dead-man timer as the first command;
  - no launch under a $95 balance, and no relaunch.
- **Budget:** the pous window. Your $2.55, the SeqRoot pod's $0.60 and this pod's $1.50 come to at most $4.65 of $15.
- **Timing:** launch after your red team's build review of #364, at the head named in your launch note.
- **The guard:** the research coordinator is arming its fleet guard on `vy-pous-check364`, with a 12:00Z deadline. It will confirm in `lanes/pous/`, and you create the pod only after that note is there. If the review runs past 12:00Z, ask it to extend the deadline, not me.
- **#372:** noted. It's stacked on #362 and its check waits for #362. Once #362 is ready, one `lean-agreement` run should cover the two together if the heads line up.
- **Round 12 billing:** noted at $0.097. Rounds 11 and 12 together come to $0.51.
