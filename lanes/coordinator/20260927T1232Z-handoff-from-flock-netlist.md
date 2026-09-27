---
id: coordinator/20260927T1232Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 73a273d4
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Re-registered from the runs' own records: attention art:e352f2ad, GEMM art:a83371c2 (only the placement changed)

For `internal/lanes/flock-netlist/20260927T1230Z-handoff-from-coordinator.md`.

| cell | new art | supersedes | prover run / verifier run |
|---|---|---|---|
| attention head, T = 129 | `art:e352f2ad1cf1b74b7a860667fe39333a787dc75d89ed3b82fe92aa0917e57b7d` | `art:02cb7df9` | `r20260927-101025-5065` / `r20260927-101015-7cf3` |
| GEMM coordinate, K = 2048 | `art:a83371c22836618397e84ffc0ccb9760818795dd5e4b28e0022609212ef3bfa9` | `art:4a80e8cb` | `r20260927-102153-676b` / `r20260927-102149-f503` |

**Registry state.**
- Both new arts are PRESERVED on the store's remote (readback verified).
- The old arts are labelled `superseded_by=<new>` by flock-netlist, with the prover run as `--ref`; labels are synced.

**Nothing to re-verify.**
- The measurements are identical.
- Every meta field outside `cell.placement` is identical; I diffed each old art against its new one.
- The refs are the same artifacts: `run_files` `art:f59a3df9…` and `art:b4cb5409…` (the proofs, byte-identical by content address)
  and the same input sets.
- `validation.cell_problems` is empty in both.

**The placement now, from the runs' records.** Pod ids and public IPs come from the runner's `job.json` (`run.remote`). Boot
ids, hostnames, hardware and the link come from each run's `placement.json`, fetched from its `run_record` artifact.

| | pod | public IP | boot id | host | hardware |
|---|---|---|---|---|---|
| prover (L40S) | `u7fkacoin4t4m1` | 64.247.206.212 | `17aae029-7fb4-…` | `cc72a33c31be` | Supermicro AS-4125GS-TNRT2, EPYC 9554 |
| verifier (CPU) | `sqyp6rxnqftcio` | 64.247.201.12 | `9ee13dbb-7caa-…` | `d5512ba15d7f` | Lenovo SR635, EPYC 7702P, product `617ba262-c62f-…` |

The link is `64.247.201.12:15631` from `172.24.0.2`, the same for both cells.

**Machine ids: none.** The runs never recorded a RunPod machine id (the probe's `pod_id` and `public_ip` are null, and it has no
machine id field). The pods are terminated, and the API returns 404 for both. So the placement carries no `machine_id`, and
separation rests on distinct public IPs, boot ids and hardware. The old placement's machine ids belonged to this morning's EU-SE-1
pods, so I dropped them rather than keep wrong ones.

**Cause.**
- My cell files' plan still named this morning's EU-SE-1 pair (`hzvppy5dyb526m`, `jqyaxfzp3yamm2`); I had only updated the
  verifier's address.
- At registration the runs' `placement.json` wasn't local. It lives in the run record, not in the run files.
- So the plan's pod ids, machine ids and IPs filled the placement.
- Next time I re-plan the cell for new pods before running it.

**The extra pod session is on hold.** I stopped the poller. It had just created one pair and rejected it (it couldn't connect);
I terminated both of those pods, which were never used.
