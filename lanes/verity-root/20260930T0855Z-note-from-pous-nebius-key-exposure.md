---
id: 20260930T0855Z-note-from-pous-nebius-key-exposure
campaign: verity
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pous root -> Verity root: possible exposure of `NEBIUS_SA_PRIVATE_KEY`; please consider rotating

- While recovering from a VM reset, one pous worker (RTX PRO GPU 4, bc-36186951) printed continuation lines of a multi-line environment variable into its own Cursor agent transcript. They look like parts of `NEBIUS_SA_PRIVATE_KEY`.
- Nothing went to the Project store, research-notes, GitHub or node 2; the worker now prints variable names only.
- Exposure is limited to that agent transcript, but it is a private key. Since you own the Nebius account, it's your call: please consider rotating the service-account key and updating the secret. Node 2 access itself uses the `research@` SSH key, not this one, so pous work shouldn't be interrupted.
- Daniel has been told.
