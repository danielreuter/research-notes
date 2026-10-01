---
id: 20261001T0101Z-alert-pouw-queue-h2s-verify-sigterm
campaign: pouw
lane: accounting
kind: alert
status: open
repo: danielreuter/verity
origin: pouw-queue (bc-829aa649), stall watch for compute-accounting
---

ALERT, 6:01 PM PDT: the `-h2`+`s` untimed verify `r20261001-000158-0c6d` (`h2s_verify.sh`, owner bc-b139c29c, deadline 9:30 PM PDT) ended at 5:51 PM PDT with rc=143 (SIGTERM, class UNKNOWN_SIGNAL, no `result.json`) after 49 min, still waiting for GPU 2's 6:30 PM PDT repeat, and nothing has relaunched it. The owner's `h2s_trims.sh` run `r20261001-005132-35d9` started 11 s later and is making progress, so the stop may be deliberate. bc-b139c29c should say so, or relaunch the verify.
