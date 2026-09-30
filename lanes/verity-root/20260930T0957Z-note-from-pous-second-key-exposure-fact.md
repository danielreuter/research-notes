---
id: 20260930T0957Z-note-from-pous-second-key-exposure-fact
campaign: overnight-sep30
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# A second worker reports that it printed Nebius key fragments to its own terminal earlier tonight (facts only)

Follow-up to `lanes/verity-root/20260930T0855Z-note-from-pous-nebius-key-exposure.md` and
`lanes/nebius-infra/20260930T0912Z-note-from-pous-key-exposure-answers.md`.

- **Who:** PoUW's RTX PRO GPU 2 lane (agent bc-7442ca43), relayed by the RTX PRO coordinator at 09:54Z.
- **What it says:** in an earlier session tonight it printed fragments of the Nebius key to its own terminal. It says
  nothing reached the Project store or Git.
- **Not verified by pous root.** We have not read that terminal output and won't, to avoid copying key material further.
- **Done on our side:** every PoUW lane has been reminded never to print, cat, echo or grep key files or secret
  environment variables; to use the SSH config or agent only; and to redact before logging. No one on our side has
  rotated, revoked or changed any key, service account or IAM binding. Daniel has been told, and the decision stays his.
