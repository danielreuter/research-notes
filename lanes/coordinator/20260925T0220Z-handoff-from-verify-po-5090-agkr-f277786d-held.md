---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T02:20Z
---

# verified, label HELD: RTX 5090 NVFP4 A-GKR art:f277786d (agkr-nvf4's final record; verdict art:4513180d, no label)

agkr-nvf4's 02:10Z record (c97d2ad2, 0.1388 s) is its last. It supersedes art:53a64e8b (0.1462 s) and art:dfbc86c4
(0.1604 s), with the same statement (BOOL_QUADRATIC + PAIRED) and the same proof bytes. Under your 0050Z rule, I registered
PASS verdict art:4513180d and wrote no label.
- I ran the same checks as for art:53a64e8b, from c97d2ad2's source on my pod. The verifier is the 3c769c6d build
  (f271e422), and c97d2ad2's verifier sources are identical to it.
  - It accepts 5/5 (sha256 ebe7c545), taking 0.47-0.53 s each.
  - The statement is byte-identical to c97d2ad2's export, and public.bin has 0 rows mismatched.
  - Every file equals art:dfbc86c4's, and `27-nvf4-rewrite-check.py` passes.
  - Negatives, all rejected: mutate 148/148 and my 5 public-line negatives.
- Runs: verify r20260925-021500-3af9, verdict r20260925-021635-b48c.
- **For the release, the 5090 cell's best is now art:f277786d** (`31-release.sh`, RELEASE includes f277786d). Six labels
  are held in all:
  - 4090: art:45c5be4a
  - H100: art:3ae971dd and art:ad76c106
  - 5090: art:dfbc86c4, art:53a64e8b and art:f277786d
