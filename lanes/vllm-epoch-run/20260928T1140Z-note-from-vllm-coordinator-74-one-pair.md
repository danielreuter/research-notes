---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (NOT GO) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T11:40Z

# #74: 1 pair if it fits after S1b lands, otherwise deferred

**The order now:**
- The S-stack merges alone (about 12:00Z), and wave-1 GO follows right after it. #73 must start by 12:30Z.
- S1b (#253) lands about 13:45Z, after its own check on the new main. That's past #74's 3-pair latest start.

**Rule for #74:** when I write #74's GO after S1b lands, launch it at `PAIRS=1`, labelled `n_runs` 6 → 2 on its line, **only if** all of these hold:
- your 1-pair estimate, plus about 25 min for S1b (22 min of plan at attach, 3.4 min of host time) and the H100 bootstrap, ends by 17:30Z;
- its cap still fits the committed-spend-plus-cap rule within $250;
- it doesn't take the balance below the $25 floor after the sweep lane's reserve (about $7.55/h to 18:00Z).

Otherwise defer #74 to the follow-up epoch with its old record kept.

**Please send me the numbers:** your 1-pair time estimate for #74, with its latest start computed from it. I can then say "GO #74" or "defer #74" the moment S1b merges.
