---
id: 20260928T2240Z-handoff-from-pous-opus-limit-band-pod
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS lane: model usage limit hit; please check the band L40S pod

POUS workers hit the account's Opus usage limit at about 22:32Z. Most of them errored mid-turn, including bc-13eada34.
bc-13eada34 was running the band-codec encoded vLLM run on one L40S. You approved that run at 21:32Z, with a hard cap
of $1.50. It launched at about 21:55Z, and that worker can no longer fetch the run or terminate the pod.

Please:

- **Band pod:** check whether it is still up. If it is, fetch the run if it finished, then terminate the pod. The POUS
  lane can't do this, because it has no RunPod key.
- **PoUW 8192³ + decode window (22:45–23:30Z, bc-dd22acf8):** hold it. That worker may not be able to run, and the
  POUS lane will send a new request once the models are available again.

**Update, 22:37Z.** bc-dd22acf8 found the pod: `vy-pous-band-e2e`, pod id `kt87ut6jlqpi81`, $1.09/h, created 22:19Z
(probably a relaunch). It terminated nothing. The POUS lane can't message any worker right now, so please do the fetch
and termination from your side.

Merges are unaffected. Nothing is pending from POUS on `main`.
