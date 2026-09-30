---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: report (final) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T05:00Z · re: `lanes/vllm-epoch-run/20260929T1304Z-GO-from-vllm-coordinator-followup-epoch.md`

# Follow-up epoch: over. 4 rows written, 8 deferred, $209.87 of $260

Every row has ended, and no epoch pod is running. The per-row lines, with digests and art ids, are in `20260929T1641Z-epoch-digests.md` beside this file.

**Written** on `cursor/followup-epoch-expected-2622`, all pushed:

| row | commit | how |
|---|---|---|
| #101 | `dd8b6159` | record rebuilt off-pod (the store outran the job end); 2 checks sanctioned by you |
| #60 | `1abe1395` | record stage re-run on its pod; rule (a) |
| #4 | `45b9125c` | reclassified FAIL → GREEN (Daniel, 20:12Z); `class` label on `art:7b437ce1…`; regenerator PR #439 |
| #70 | `3485ad74` | FAIL reproduced; `program_digest` forced (your 21:24Z decision) |

**Deferred** with their old records:

| row | why |
|---|---|
| #39 | the Build's own 4 h cap on the request derive |
| #11 | the job end cut the Build's manifest step, after both derives passed |
| #67, #68, #75 | Commit cut at the job end; the stored-Build resumes then failed (your 22:26Z decision) |
| #74 | the 3-pair Commit was cut at the job end, with no pair done ($72.71) |
| #57 | the call-boundaries gate FAILed (244,648 of 251,400 uncovered); the manifest now builds, where v1 refused |
| #23 | the Commit's own admission check refused it (predicted host 562,640 MiB vs a 545,501 MiB limit, B64 on 2× L40) |

**Spend:** $208.94 on rows (#74 $72.71, #11 $24.30, #39 $18.75, #68 $17.51, #60 $14.64, #75 $13.48, #67 $12.63, #23 $10.87, #70 $10.10, #57 $6.43, #4 $5.45, #101 $2.07), plus about $0.93 of config-run smoke tests on the same line.

**What the epoch showed:** the job end is what bounds rows, not the cap. Six of the eight deferrals are time or host-RAM limits: a 3-pair OLMoE Commit is about 3 h, a B64 Commit's host peak is over 545 GB, and long-context Builds exceed 4 h. The config run (#470: one instrumented Commit under bounded staging) removes most of them. The canary and the `known_roots.json` re-pin were not run (my 02:50Z handoff).

**Open PRs from this lane:**
- [#422](https://github.com/danielreuter/verity/pull/422): the record stage is bounded by the run end.
- [#439](https://github.com/danielreuter/verity/pull/439): the class label regenerator, marked ready.
- [#467](https://github.com/danielreuter/verity/pull/467): JIT build dirs, marked ready.
- [#470](https://github.com/danielreuter/verity/pull/470): the config run, marked ready.

The last three wait for your grant in the queue.
