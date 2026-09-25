---
lane: vllm-rf-gc
kind: report
created: 2026-09-25T16:25Z
status: final
---

CHECKPOINT f2599a27 (18:41Z) [final] READY f2599a27 (base 38a8d35d): jdiff rc 0, 6 fixed, 0 new fail/skip, lints green; merge-ready handoff sent; vyv-rf-gb-cpu terminated; spend ~$3.1
CHECKPOINT f2599a27 (17:21Z) [open] waiting detached: base 38a8d35d r20260925-165445-d918 (~98%, ends ~17:40Z), then head f2599a27 r20260925-165502-2bc9 auto-starts after it (ends ~18:25Z), both on vyv-rf-gb-cpu. Check back 18:25Z; next: jdiff, READY.md, handoff, terminate gb-cpu
CHECKPOINT f2599a27 (17:18Z) [open] base 38a8d35d gate (b) still running; head queued
CHECKPOINT f2599a27 (17:08Z) [open] base 38a8d35d gate (b) running on gb-cpu; head queued
CHECKPOINT f2599a27 (16:56Z) [open] merged main (f2599a27); base 38a8d35d r20260925-165445-d918 then head r20260925-165502-2bc9 on gb-cpu, ~18:15Z
CHECKPOINT 301ce7dc (16:49Z) [open] base gate (b) at 8a3aa083 running r20260925-163811-0e25 (first launch r20260925-163221-f7ab rc127: script path); fixes wait for it
CHECKPOINT 301ce7dc (16:36Z) [open] 3 test-side commits pushed (tip 301ce7dc); gate (b) base at 8a3aa083 running on gb-cpu r20260925-163221-f7ab
CHECKPOINT 8a3aa083 (16:25Z) [open] succeeded gb at 8a3aa083+176d3bff; adopting vyv-rf-gb-cpu; triaging gb base XML
