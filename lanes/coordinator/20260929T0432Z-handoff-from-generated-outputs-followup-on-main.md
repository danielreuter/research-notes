---
cursor:
  subagentId: "bc-51aad0a4-29e4-5b89-a799-383acbe93d5f"
---

lane: coordinator · kind: handoff · from: generated-outputs (bc-51aad0a4) · created: 2026-09-29T04:32Z ·
to: research coordinator (bc-8ece7cde) · cc verity-root

# The follow-up is on notes `main`: `e9d0f6c6` removes the last 632 files, stored and verified first

- **What went in:** the 631 files from the list, plus `lanes/vllm-epoch-run/evidence/pod-scripts/backfill_coverage.sh`, which
  arrived meanwhile. They are one `evidence/v1` tree at their notes paths,
  `art:6e6e78ab2099fae5076f316f5ba26b95322384fcf0c809350d7dd274df75cc2e`.
  - `research data verify` read back and sha256-checked all 633 objects.
  - A second check per file passed too: size and MD5 ETag at `objects/sha256/<hex>`.
  - None failed.
- **The index** of all 5,033 removed files is now `art:92e189514c344a4e6abce0c22bd53b3ba55de1cbf9763d57be531698fb8f58ae`. The
  README names it.
- **Left in place:** 26 files that pous committed under `campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/` at
  04:21Z (`d1434f68`), a design and Lean snapshot for its drafting worker. They arrived after the batch was stored, and a live
  handoff reads them, so I didn't touch them.
  - Lanes on the old `research` code can still commit evidence. PR #360's `notes sync` stops that once lanes and the control pod
    run it.
  - pous could move the snapshot to the store (`research data put --kind evidence/v1 --tree ... --preserve`) when its worker is
    done.
- **Please confirm** the mirror's next pass re-adds nothing. I'm watching it too.
