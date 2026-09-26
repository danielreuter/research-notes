---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-netlist · kind: handoff · from: coordinator · created: 2026-09-26T19:55Z

# Terminology: say "circuit", not "netlist" (Daniel, 2026-09-26; LANE-CONTRACT §5a)

In prose, reports, handoffs, table labels and any new identifier, write "circuit", or "expanded circuit" for the
gate-by-gate form.
- Your lane name, the campaign and existing ids stay as internal keys. That includes `verity/flock-netlist/v1`,
  `--netlist` flags and the existing statement ids.
- Rename them when you touch them.
- Name new statements, backend identities and labels without the word. Your cells publish under a new C-Flock backend
  identity, so pick its name now.
