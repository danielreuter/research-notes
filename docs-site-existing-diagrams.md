---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Mermaid diagrams from the earlier docs port, for reuse

**Written:** Fri Sep 25, 2026, 6:45 PM PT, by the docs-site worker, for the subagents writing the Verity docs pages. The diagrams come from the first port of the architecture pages (website repo, commit `ee3a1b6`, later replaced by stubs). Daniel liked them and wants diagrams on the new pages.

## How to reuse them

- **Adapt before reusing.** Update the terms to the ontology in `docs-site-writing-brief.md`:
  - "instances" becomes inputs, or an input set;
  - "configured backend" becomes backend;
  - "Flock" becomes C-Flock, and "SP1" becomes D-SP1;
  - "units", when it means subcircuits, becomes subcircuits.
- **Remove internal roles:**
  - "Steward", "Research coordinator" and "GPU worker" become neutral roles: the benchmark render, the prover, a research run.
  - The site's public docs don't name internal services.
- **Check each arrow against verity `origin/main`.** Drop any step you can't confirm, rather than keeping it because it's in the diagram.
- **Fence diagrams with `~~~mermaid`.**
- **Suggested homes:**
  - The whole system: `/docs` (content/index.md), or `/docs/core` for the core part.
  - A Table 2 cell: `/docs/autoresearch`, or a "How results are produced" section.
  - A vLLM serving run spot-checked by sampled proofs: `/docs/integrations/vllm` and `/docs/protocols/sampled-proofs`.
  - Commitments across frame-v3 and vllm-v1: `/docs/core/commitments`, `/docs/backends/a-gkr` and `/docs/backends/c-flock`, for the Flock-plus-link route.
- **Draw new ones too.** Good candidates:
  - the core module import graph;
  - the Backend interface lifecycle (`supports`, `lower`, `prove`, `verify`);
  - A-route-a's composition;
  - how coins are derived;
  - the interaction cost model.

## The whole system (was the overview page)

~~~mermaid
flowchart TB
  subgraph VER["Verity: the code"]
    direction TB
    vl["vLLM application"]
    subgraph PROT["protocols"]
      sp["sampled proofs"]
      pw["PoUW, PoUS<br/>prototypes"]
    end
    subgraph BACK["backends"]
      bl["B-Ligero · A-GKR · SP1 · Flock"]
    end
    pol["policies"]
    bm["benchmarks<br/>harness, views"]
    core["core<br/>ir · query · evaluation · silicon · ops<br/>commitments · proofs · randomness<br/>resource accounting"]
  end
  subgraph HAR["Research harness"]
    rr["research runs,<br/>custody"]
    st["steward"]
  end
  subgraph STO["Store"]
    git[("git: notes,<br/>hardware records")]
    obj[("objects and catalog:<br/>proofs, results, labels")]
  end
  web["Website"]

  vl -->|"composes"| PROT
  vl -.->|"configured backends"| BACK
  PROT --> core
  BACK --> core
  pol --> core
  bm --> core
  bm -.->|"discovers"| BACK
  rr -->|"custody"| obj
  obj -->|"results, labels"| bm
  st -->|"runs the views"| bm
  st -->|"renders"| git
  git -->|"hardware snapshot"| core
  obj -->|"published bundles"| web
~~~

## A Table 2 cell (was the flows page)

~~~mermaid
sequenceDiagram
  participant C as Research coordinator
  participant P as GPU worker
  participant S as Store
  participant V as Independent verifier
  participant R as Red team
  participant W as Steward
  C->>P: research run, with a tool and campaign
  P->>P: seeded instances from the IR, committed with the scheme
  P->>P: supports(), then prove the full relation, sweep to the plateau
  P->>S: custody of the attempt, proofs and bench result
  V->>S: fetch the proofs by artifact id
  V->>V: re-lower with the pinned lowering and re-verify
  V->>S: label verified=accepted
  R->>S: audit the configured backend's statement, label its class
  W->>S: refresh, read results and labels
  W->>W: views, with N from work(spec) and silicon peaks
  W->>C: renders and twice-daily digests
~~~

## A vLLM serving run, spot-checked by sampled proofs (was the flows page)

~~~mermaid
sequenceDiagram
  participant A as vLLM application
  participant L as Auditor log
  participant B as Beacon
  participant SP as Sampled proofs
  participant BE as Configured backend
  participant VF as Verifier
  A->>A: serve, and commit values with the GPU committer
  A->>L: register the boundary root, one per scope
  B-->>SP: first round after the registration
  SP->>SP: derive() the replay-unit sample, each with probability p
  SP->>SP: replay the selected units, commit their interiors
  SP->>L: register the interiors root
  B-->>SP: next round
  SP->>SP: derive() exactly k verification units per selected unit
  SP->>BE: establish() each sampled unit's full committed relation
  VF->>L: read the registration times, re-derive both samples
  VF->>VF: check openings and proofs, recompute security
  VF->>VF: emit the integrity profile
~~~

Note: Daniel said earlier that the beacon, the auditor log and the challenger key are not assumptions Verity makes. If they appear, show them as parts of the protocol's setting, not as trusted parties. Include them only if the repo's sampled-proofs protocol really uses them.

## Commitments across frame-v3 and vllm-v1 (was the flows page)

~~~mermaid
sequenceDiagram
  participant G as GPU committer
  participant CS as verity.commitments
  participant PB as Prime-field backend
  participant FB as Flock, binary field
  participant VF as Verifier
  G->>CS: leaf layout for the selected scheme
  G->>G: row digests and trees, frame-v3 or vllm-v1
  Note over G,CS: byte-identical to the reference, checked by the vectors
  alt In-circuit hashing, B-Ligero today
    PB->>PB: prove the relation plus every row digest
  else Flock plus link, A-GKR
    PB->>VF: root B, committing the operand bits
    FB->>VF: root F, committing the leaf message bits
    VF-->>FB: two GF(2^128) points named in the statement, live coins
    FB->>VF: open the bits' evaluations at both points
    PB->>VF: prove matching parities, which is link L
  end
  VF->>VF: check the trees natively from the published digests
  VF->>VF: check the proofs, then the roots against the statement
~~~
