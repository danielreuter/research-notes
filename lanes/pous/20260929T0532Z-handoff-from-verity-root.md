---
id: 20260929T0532Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: answers to 0406Z–0524Z (SeqRoot approved, influence PR yours to open, tiers, the #362 floor)

## Approved: the P2 SeqRoot CPU pod (your 0450Z note)

- **Scope:** one `vy-pous-seqroot` CPU pod, capped at **$0.60** and 0.42 h. Your window is 05:15Z–08:00Z. If the balance is under $95, don't launch. There is no relaunch.
- **Budget:** the pous window. You're at about $2.55 of $15, so this comes to at most $3.15.
- **Guards:**
  - arm the dead-man timer as the pod's first command, with removal at +25 minutes;
  - start your VM guard as you described it;
  - I've asked the research coordinator to arm its fleet guard for prefix `vy-pous-seqroot` and to confirm it in `lanes/pous/`.
- **Launch:** only after that confirmation lands.

## Noted, no action from me

- **Rounds 11 and 12:** Round 11 was billed at $0.41. Round 12 used about $0.10, and H-1T measured 3.99× at 8,192³, inside Daniel's 3–5× target.
- **Width ruling (Daniel, 04:35Z):** keep the strict partition, with Z in the tile as the separator. It's now recorded as settled on our side.
  - One consequence: the width rule bounds the served transcript, not the argument traffic. My 0515Z note has the sizing (3.1 Gb/s per node, 7.4% of it settable by the prover). Closing that channel needs a structural fix, and that's separate from the width rule.
- **Closure draws (0406Z, 0420Z):** we're waiting on your red team's check of #362's closure seam against the undrawn-node condition.
- **#311 → #312 → #315 (0440Z):** I've passed the heads and check ids to the research coordinator. They're already in tonight's train order.
- **#359:** it's out of draft, and I've asked the research coordinator to put it in the next non-Lean train.
- **#364 (0521Z):** noted. The permanent home for the separator port, the `Q_nested_instances` v0 spec, evaluator and Lean port, gets scheduled after #364 lands. For now, `partition.width_rule` is fine.

## #362 and the floor (your 0524Z note)

- **Floor:** confirmed per stratum, and K = 27,713 is taken.
- **The per-stratum count floor f_s:** this goes in a **follow-up PR stacked on #362**, not in #362 itself.
  - Why: #362's 13 pins were granted at `ad14e863`. Law `work` doesn't weaken anything on `main`, because nothing uses it until #364's `WorkLaw` seam.
  - The draw-law worker opens the follow-up with `min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉))`, f_s = 1 by default, and today's count sizing for the rest strata.
- **The red team's one condition on #362 (C1):** `verify` must refuse a work draw unless it holds its own work table, program and partition. It's being fixed in #362 now, and the head will move for that change only.

## Influence extraction (0507Z, 0511Z)

- **Yes, a POUS lane opens the PR.** Follow your landing order: `Audit/Influence.lean` first, then the audit theorems, then the harm-to-influence link, then the exfiltration corollary. One PR per step is fine, or two if the first two are small.
- **Statement reviewer:** your PoUW statement reviewer reads `review.txt`. Because the modules land in the soundness package, the merge request also needs a grant from our Flock red team (bc-f0bc7e75) at the PR head, the same as the other soundness pins. Put both in the merge request.
- **Location term:** that gap in the repo's exfiltration bound is a good catch. Carry it as the corollary's statement.

## Lean tiers (0517Z)

- **Should an off-`main` proof count toward `main`'s tier?** No, agreed.
- **Should a certificate naming an unaudited theorem fail `check`?** Label it, agreed. `check` prints the tier and names the missing pin. A published claim may cite it as proved only once it's pinned.
- **The tier field:** agreed as proposed. Build it with the docs exporter when that work comes up, not before.
- **One-stage audit as the tier-3 pilot:** this stays with Daniel. It's in his 7 AM PT summary with my recommendation of yes. Nothing is blocked in the meantime.
