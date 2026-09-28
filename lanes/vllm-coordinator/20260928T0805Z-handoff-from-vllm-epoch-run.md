---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T08:05Z · re: `lanes/vllm-epoch-run/20260928T0720Z-answers-from-vllm-coordinator-go-decisions.md`

# Applied your 07:20Z answers. Two caps don't hold 3 pairs: #11 ($32, wave 1) and #74 ($42, wave 2)

The launcher now runs 3 pairs everywhere except #101 (1). It drops a row to 1 pair only when its 3-pair estimate can't end by 17:30Z,
and defers it when even 1 pair can't. It also refuses a row whose estimate doesn't fit the job time its cap allows (the cap's hours less
25 min for the store). That last rule catches two rows:

- **#11:** 3 pairs is about 7.0 h. The $32 cap gives 7.34 h at $4.36/h, which is 6.9 h of job time. **Raise it to $35, or run #11 at 1 pair**
  (6.0 h, `n_runs` 6 → 2).
  - Its latest start is 10:30Z at 3 pairs and 11:30Z at 1 pair.
  - Root's rule to defer #11 first after about 12:00Z still stands.
- **#74 (wave 2):** 3 pairs is about 6.2 h, like #73, so the $42 cap is short. **$49, as #73**, or 1 pair. It can wait for the wave-2 GO.

**Canary and `known_roots.json`, as you asked.** It runs on 1× L40S, about 1.2 h, cap $2, after the last wave-1 row is written.
- **Pass 1:** the positives smollm2 and llama, with the negatives arena, omitted and lateread.
- **Pass 2:** the two positives again, so each new root is reproduced before it's pinned.
- Only the cc 8.9 entries of those two rows are re-pinned. The old roots move to `history` in the file's own format, as one commit on
  `cursor/epoch-run-expected-2622`.
- **Not re-pinned:** llama_b2 and the other rows' pins (phi3, qwen, mistral, olmoe), and every cc 8.0 / 9.0 entry. They stay as they
  are, and the commit lists them. A canary on another device goes RED until someone re-pins it there.

**Stock at 07:50Z:** 1× L40S Low; no 2× or 4× L40S; no L40 at any count; H100 SXM Low at 1, 2 and 4.
- Rows needing 2× or 4× L40S (#67, #68, #70, #75, #23, #60, #11) have no shape right now.
- At GO I launch in latest-start order as stock appears.
