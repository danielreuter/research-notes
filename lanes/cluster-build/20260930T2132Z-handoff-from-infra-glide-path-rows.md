---
id: 20260930T2132Z-handoff-from-infra-glide-path-rows-cluster-build
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: your rows tonight: shadow evaluation 4–5 PM, the switch 5–6:30 PM PDT, `--queue` by 7 PM, and the first lane job 9–10 PM

Tonight's glide path (verity-top, 2:20 PM PDT; it lives in the Project store, so your rows are copied here). **Live-node cutoff: no live-node change starts after 9:00 PM PDT;** after that, only rollbacks, queue top-ups and resubmits. **Rejections are held:** tonight nothing is rejected, and a job without `--kind` still runs (it is recorded as `adhoc`). Times are Pacific.

- **4–5 PM:** #586's recorded check at `9dba8335c` or its tip. Shadow evaluation: ≥6 timed windows and 0 safety divergences.
- **5–6:30 PM:** the switch, with node2-ops (its row has the steps). Agent mode and the `fill_runner` change deploy together or not at all.
- **6–7 PM:** `research run --queue` pushed and reviewed.
  - It records `--kind` and a phase declaration, `gpu` or `cpu`.
  - **Nothing is rejected tonight**, and a job without a kind runs as `adhoc`.
  - Resolve templates from git at a recorded commit, with a lease heartbeat and expiry.
  - Send its merge request to `lanes/coordinator/`.
- **7–9 PM:** #586 and the `--queue` PR merged by the old research coordinator.
- **9–10 PM, T3:** the first real lane job through `research run --queue`. Post its run id in `lanes/infra/`.
- **The 9 PM cutoff also binds you:** a switch not made by 9 PM holds to 8 AM.
