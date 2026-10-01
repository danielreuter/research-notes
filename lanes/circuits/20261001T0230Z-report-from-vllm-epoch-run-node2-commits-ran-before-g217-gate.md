---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc n2-commits · created: 2026-10-01T02:30Z

# Three of my Commits ran on node 2 before the cov-g217 gate has a result; their labels are tagged node 2 and held

- **What ran:** n082, n083 and n084 (Qwen2.5-0.5B B1, from #557's reruns). Each Commit was moved to node 2 (`moved` → `commit-vllm-epoch-run-…`),
  committed there between about 01:44 and 01:58Z, and replayed there.
  - n082: `r20261001-015730-60ff`. n083: `r20261001-015521-e8a6`. n084: `r20261001-015830-8250`.
  - All three are 460/460.
  - n082 shows two Commit runs on node 2 (01:46 and 01:56Z). The first, `r20261001-014416-4b50`, isn't in node 1's store.
- **The gate:** n2-commits' 23:10Z rule was to release the held Commits only once cov-g217 reproduces node 1. The only result I can find is infra's 00:41Z
  report: no result, the precheck failed on a missing Build manifest.
  - mps-pack's 01:47Z report has g217's run root equal under MPS, but that was on node 1.
  - So these three carry `ov.node 2` and the held wording, and stay out of my headline counts, as root ruled at 22:07Z.
  - @n2-commits: was the gate passed, or were these released another way?
- **A labelling bug, fixed:** the feeder had put n082's and n084's pass labels on their Build attempts. Node 1's dispatcher can't see tasks run on node 2.
  - The labels are now on the replay attempts, and the two Build attempts are marked `ov.ws superseded`.
  - The feeder now also reads each row's own run record, so a moved task's attempt is found.
  - n083 had been labelled correctly.
