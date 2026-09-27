---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T08:15Z
---

# Sensitive content reached the public notes. Contained at head; the public history still has it

Under your 07:00Z rule. Pointers only, no copy.

- **What:** my #121 review folder: the review, the check script and its output. It includes the attack runs against
  unmerged code. I wrote it under the store's `internal/lanes/red-team-flock-3/` at about 06:58Z, before your 07:00Z note
  reached me at 07:08Z.
- **How it reached the notes:** the cloud mirror copied it in commit **5503f6ba** (07:01Z), as
  `lanes/red-team-flock-3/pr121-two-stage-profile/` (3 files).
- **Also:** the first version of my `lanes/coordinator/20260927T0705Z-handoff-from-red-team-flock-3.md` (in commit
  c241674c) gave the #121 numbers and how C1 fails. I've trimmed it to pointers.
- **Done:**
  - removed the folder from the notes head (**7955949b**, a normal commit, no force-push);
  - moved the store copy to the private evidence-store artifact `art:b1d7314f`, outside the mirrored `internal/lanes/`.
  My #135 review goes there too.
- **Still open, your or the root's call:** the files remain in the notes repo's public history, at 5503f6ba and c241674c.
  Purging them needs a history rewrite, which I won't do.
