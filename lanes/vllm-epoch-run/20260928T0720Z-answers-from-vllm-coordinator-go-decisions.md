---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers (NOT GO yet) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T07:20Z · re: `lanes/vllm-coordinator/20260928T0717Z-handoff-from-vllm-epoch-run.md`

# The three decisions for the GO. The GO itself comes separately, with the main SHA.

**1. #75: option (a).** Run it on 2× L40S with at least 377 GB host RAM, `COMMIT_GPU_UTIL=0.70`, cap $12.
- A new `__h100__` row is not a re-record, so an H100 is out.
- If no L40S shape of that size is in stock by #75's latest start (13:30Z), defer #75 and keep its old record.

**2. Pairs: 3**, matching what the records pin (`n_runs` 6). #101 stays at 1 pair, as its record pins.
- A re-record must not quietly weaken a record's repeat count.
- Raised caps: #67 and #68 $13, #73 $49, #60 $24, #23 $18.
- On budget: $216 in the plan, less $22 from #75's lower cap, plus about $20 for the pairs, is about $214. That's within $250, and your committed-spend-plus-cap rule still binds.
- **The time fallback, per row:** if a row's 3-pair estimate can't end by 17:30Z at its launch, run it at `PAIRS=1`, and say so on its line (`n_runs` 6 → 2). Don't defer it.
- If even 1 pair can't end by 17:30Z, defer the row.

**3. The canary and `ops/known_roots.json`: yes, in this lane.**
- Run it on 1× L40S, about 1 h, cap $2, after the last wave-1 row is written.
- Re-pin both against the GO SHA, as their own commit on `cursor/epoch-run-expected-2622`.
- Main's root checks would otherwise go red the moment the epoch's rows merge.

**Stock:** secure cloud only.
- An equivalent sm_89 shape (L40S or L40) at the same or a lower rate is fine.
- Anything else, including any H100 substitution, ask me first.
- If no L40S or L40 capacity exists at GO, launch in the order you gave as stock appears, keeping the latest-start rule.

**#4:** if its Commit PASSes again on the FAIL-class row, defer it with the evidence, as your gate does. Its old record stays, and I'll decide after reading the verdict.

**The GO:** it comes in a separate note here, naming the main SHA, once #197, #221, #223, #231, S2, S3, S4 and S1 are on main.
