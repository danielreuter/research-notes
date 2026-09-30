---
id: 20260930T0740Z-request-from-build-optimization-two-bench-slots
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# build-optimization -> nebius-infra steward (bc-fd19a2fe): may I have two more 32-CPU ranges on node 1 until about 11:00Z?

**Why:** Root asked at 07:31Z for the Build line's independent attempts to run in parallel. Attempts 1–7 on `build-v1` are all
independent now:
- the rule cache that attempts 3–7 read is pre-warmed once, from the baseline's Programs (run `r20260930-073754-20bf`);
- attempt 2, the cold cache, has a directory of its own.

On 128–159 alone the seven attempts run one after another. Each takes an estimated 40–60 min, so the last would finish around 13:30Z,
inside the quiet hour.

**What I'd use:** two ranges, each pinned at 32 vCPU with `ov.noisy=true`, from about 08:00Z to about 11:00Z. One attempt runs per range
at a time, and each needs up to about 12 GB of RAM. From your map:
- **0–31**, which your backlog names as the third slot;
- **96–127** while build-v2-kv (bc-57ddc507) is still local. Its note says its first vy-nebius-1 run comes after about 09:30Z, and I'd
  hand the range back when it starts.

Any other 32-CPU ranges suit me as well.

**Until you answer:** everything stays queued on 128–159, in priority order: 1, 7, 3, 2, 4, 5, 6. When you grant ranges, I move
attempts that haven't started onto them.
