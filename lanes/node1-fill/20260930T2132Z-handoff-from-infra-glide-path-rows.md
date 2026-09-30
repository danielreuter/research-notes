---
id: 20260930T2132Z-handoff-from-infra-glide-path-rows-node1-fill
campaign: verity
lane: node1-fill
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node1-fill: your rows tonight: T1 at 3:30 PM PDT (node 1 ≥60% useful), then T2 at 6 PM

Tonight's glide path (verity-top, 2:20 PM PDT; it lives in the Project store, so your rows are copied here). **Live-node cutoff: no live-node change starts after 9:00 PM PDT;** after that, only rollbacks, queue top-ups and resubmits. **Rejections are held:** tonight nothing is rejected, and a job without `--kind` still runs (it is recorded as `adhoc`). Times are Pacific.

- **2–3 PM:** the Phi-3 B8 probe `cfgtp2-deferred-phi3b8g` running at the front of the queue.
- **3–4 PM, T1:** node 1 ≥60% useful:
  - Commits defer their replay (new template, 2:16 PM);
  - TP2 heads are admitted under StrictFIFO;
  - the sweep's shape chunks move from `provers` to `backfill`.
- **6 PM, T2:** node 1 ≥80% useful GPU and ≥60% CPU.
- **Automatic rollback:** if two dispatched Commits in a row fail at bootstrap under the new template, restore `*.bak-20260930T2115Z` in `/workspace/jobs/dispatch/infra/nebius/sky/`.
- **Overnight, node 1 stays on Kueue.** Keep its useful GPU busy high: the gap is conversion (holders at 0–10%), not supply (circuits has about 100 GPU-h queued).
