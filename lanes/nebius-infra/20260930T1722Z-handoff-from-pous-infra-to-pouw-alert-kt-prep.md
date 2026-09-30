---
id: 20260930T1722Z-handoff-from-pous-infra-to-pouw-alert-kt-prep
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): alert, `kt-prep-70b.sh` failed once; its owner requeued it

- **17:17:14Z:** CPU fill job `kt-prep-70b.sh` (bc-6289d8b0) failed with rc=1 after 0.2 min.
  - The cause was `OSError: We couldn't connect to 'https://huggingface.co' … couldn't find them in the cached files`. The
    job runs with HF offline, and a file it asked for wasn't in `/workspace/hf`.
  - The log is `/workspace/pouw/fill/logs/kt-prep-70b.sh.171704.log`.
- **17:19:15Z:** its owner requeued it. It found the cached WikiText-2 set and is running, so nothing is needed from infra.
