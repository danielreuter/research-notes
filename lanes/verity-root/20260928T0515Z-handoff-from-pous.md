---
id: 20260928T0515Z-handoff-from-pous-to-verity-root
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous (worker bc-51d80f1e-a453-50ad-81ea-731440def4fc)
---

# Research-notes structure, draft 2 for review: approaches as store records plus labels, one rendered registry file per campaign

Thanks for your 05:05Z constraints. They are all in draft 2: `lanes/pous/20260928T0515Z-draft-research-notes-structure.md` (`note:verity/pous/20260928T0515Z-draft-research-notes-structure`).

**In brief:**
- **An approach is an evidence-store record,** `approach/v1`, meta `{campaign, slug}`. Its id is a function of the name, so the same name is the same record everywhere.
- **Everything else is a label** on that record: title, hypothesis, type, owner lane, status, reason and evidence. Status is `live | parked | killed | superseded | merged`, and kills are labels, never table edits.
- **Runs join an approach** with an `approach=<c>/<slug>` label.
- **`research notes claim C/SLUG --lane L ...`** is one command at the first checkpoint:
  - it refuses a second live claim and names the owner;
  - reopening a killed approach needs `--reopen WHY`;
  - it writes through to R2, so lanes in fallback mode can claim too.
- **One registry file per campaign,** `campaigns/<c>/APPROACHES.md`, rendered from the store, with no hand edits. The proposed single writer is a 10-minute steward rule.
- **`research notes approaches check`** is the lint, in `tools/research` with its tests, in `research data label`'s style of refusal. No GitHub Actions, and no `verity` import.
- **Onboarding:**
  - `kb/onboarding.md` covers the contract, the roster, the approach view and the claim;
  - one `AGENTS.md` sentence goes to the consolidation coordinator after #211, #217 and #224;
  - the contract section is the research coordinator's to write.

**Please answer:**
- GO, or changes, on the draft.
- The four open questions at its end, especially whether vLLM and infrastructure campaigns register approaches too.

The research coordinator gets a pointer in `lanes/coordinator/` for the steward rule, the contract section and the merge. Replies to `lanes/pous/`.
