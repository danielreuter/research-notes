---
id: 20260929T0507Z-handoff-from-pous-influence-extraction
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Draft 2's influence cap, extracted with Lean (as promised at 0442Z)

Daniel asked us to extract what his stale Notion "Draft 2: Computational integrity via zero-knowledge spot checks" still offers the sampled-proofs Lean. Done:

- **Extraction:** `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-influence-20260929T0506Z/sampled-proofs-notion-extraction.md`. Every definition, lemma and theorem is marked proved, stated only, missing, or superseded, with Lean statements for each recommendation.
- **Lean draft:** `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-influence-20260929T0506Z/sampled-proofs-influence/`. It holds 15 theorems with no `sorry` and standard axioms only, over `main`'s audit law (vendored byte for byte at b4fd93e9). They are unpinned and have not been reviewed, and the package has not been run through `tools/lean/audit.py`.
  - The influence cap is Lemma 4.7: for a downstream cut K of E, |𝒪_C(E)| ≤ 2^(w(K)). `compose_cone` is only its no-fault case.
  - The draft also proves Theorems 4.8 and 5.4 on the one-stage and two-stage audits, Corollary 3.3 (exfiltration), and a link from harm bounds to influence.
- **Recommended landing order:**
  1. `Audit/Influence.lean` (the separator module) in the soundness package;
  2. the audit influence theorems;
  3. the harm-to-influence link;
  4. the exfiltration corollary.

  Don't port the early exemptions, the acyclic-quotient requirement, the typing and normalization lemmas, or sampled input gates.
- **For you:** the repo's exfiltration bound counts value bits but leaves out which units are wrong (the draft's location term). PoUW's decision 4 (Z kept in the tile as the separator) applies the lemma correctly, provided the delivered set is the served tokens only and inputs stay anchored.

Landing and pinning are yours. Tell us if you want a POUS lane to open the PR.
