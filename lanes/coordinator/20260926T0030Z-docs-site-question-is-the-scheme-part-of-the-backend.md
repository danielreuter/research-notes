---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# From the docs site: is the commitment scheme part of a backend's identity?

**To:** coordinator. **From:** the docs-site worker. **Written:** Fri Sep 25, 5:30 PM PT. Daniel asked me to put this to you with context, and he'll likely continue the discussion with you directly.

## The question

Should a commitment scheme be part of what a backend *is*, or a parameter of a measurement?
- **Option 1:** B-fs proving SHA-256 rows and B-fs proving BLAKE3 rows are one backend.
- **Option 2:** they're two backends, or at least two first-class things with their own names.

## Daniel's point

A backend has its own circuit. `lower()` produces a pinned lowering of the full committed relation. For B-Ligero, that relation includes computing every row digest in-circuit with the scheme's hash. So SHA-256 rows, BLAKE3 rows and Poseidon2 rows are different circuits, with different cost, proof size and assumptions (the scheme's hashes join the backend's own).

For the Flock plus link route, the scheme also decides which prover handles the leaves. The scheme therefore shapes what the backend proves and how, not just a label on the result.

## What the ontology and PR #40 say today

- **The ontology** treats the commitment scheme as a parameter of a measurement, and defines a backend as family × mode: A-interactive, A-fs, B-interactive, B-fs, C-interactive, D-fs.
- **PR #40** lists, under each backend, its member *configurations*. A configuration is the backend plus a scheme plus variant parameters, for example `BLigero(scheme=FRAME_V3)`. Results are keyed by configuration × subcircuit.

## What the site does now

On branch `cursor/verity-docs`, commit `f874dee`:
- **Security tab:** one row per backend (A-interactive … D-fs), listing that backend's properties and assumptions. The scheme's hash assumptions aren't included; they live on the scheme's token.
- **Performance tab:**
  - rows are subcircuits, and bars are backend families;
  - each bar shows the family's best result, labelled with its backend and a scheme token;
  - "Commitment" is a single-select context, defaulting to the best standard hash, because different schemes are different statements.

My answer to Daniel was "same backend, different statement", with the scheme as that context. His objection above is the strongest argument against it.

## Options as I see them

1. **Keep the ontology.** A backend is family × mode, and a configuration is backend × scheme. Results and their assumptions are keyed by configuration, and the site keeps the scheme as a context selector.
2. **The scheme joins the backend's identity:** for example `B-fs · blake3-keyed`. Security rows multiply per scheme, each with its complete assumption set. The bars are these configurations.
3. **Hybrid.** "Backend" stays family × mode, because that's what implements the Backend interface. But the *configuration* (backend plus scheme) is named and first-class everywhere results and security appear. The site would show configurations as "B-fs · BLAKE3 rows" with complete assumption sets (backend's plus scheme's), and group them under their backend.

I lean towards option 3: it keeps the interface-level term clean and makes what's actually measured explicit. It's your and Daniel's call.

## What the site needs from the answer

- **The id the site keys on,** for results and for security rows.
- **Whether the entities JSON will give each configuration's complete assumption set** (backend plus scheme), or the site should take the union itself.
- **What Table 1 lists:** one entry per backend, or one per configuration.
