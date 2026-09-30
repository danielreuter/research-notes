---
id: 20260930T1832Z-handoff-from-pous-coordinator-charters-for-new-project
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: pous coordinator (bc-b729c175)
---

# Charters for circuit, proof and console, for the new top-level

Daniel is about to create the new top-level Project. Its kickoff creates the infra coordinator first, from
`lanes/pous/20260930T1740Z-handoff-from-pous-charter-infra.md`. Pouw's charter is
`lanes/pous/20260930T1740Z-handoff-from-pous-charter-pouw.md`.

The circuit (vLLM coordinator), proof (research coordinator) and console (website worker) charters were due at 17:50Z
in your store's `docs/restructure/`, which other Projects can't read. Please push them to research-notes as
`lanes/verity-root/<ts>-handoff-from-verity-root-charter-{circuit,proof,console}.md`, so the new top-level can read
them. Each one needs: the owner agent id, its remit, its running workers, its open items, and what it hands to infra.
