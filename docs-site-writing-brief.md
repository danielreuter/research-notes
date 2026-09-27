---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Brief for writing the Verity docs pages

**Written:** Fri Sep 25, 2026, 6:40 PM PT, by the docs-site worker. This is the shared brief for the subagents filling in the stub pages of the Verity docs site. Each subagent's prompt names its pages; everything else is here.

## Where the site lives

- **The worktree:** `/Users/danielreuter/projects/website-verity-docs`, branch `cursor/verity-docs`. The app is `apps/docs`, a self-contained Next.js site.
- **The dev server:** already running at `http://localhost:3001`. Don't start another one.
- **Page bodies:** markdown files under `apps/docs/content/`, named after the page's href. `/docs/core/ir` is `content/core/ir.md`, and `/docs` is `content/index.md`.
- **Titles and descriptions:** these come from `apps/docs/lib/tree.ts`, and the page renders the title and the one-line description above the body.
  - The body must not repeat the title as an H1.
  - Start the body with the summary paragraph.
- **An example of a finished page:** `apps/docs/content/backends.md`.

## Your scope

- **Files:** write only the content files your prompt assigns.
  - Don't edit `lib/tree.ts`, components or data files, or anyone else's pages.
  - The content loader throws on a file the tree doesn't list, so don't create extra files.
  - If a description in `lib/tree.ts` should change, say so in your report.
- **Git:** don't run git commands that change anything. No commit, checkout, switch, stash, reset, fetch or push, in any repository.
  - The parent agent commits.
  - Other agents share the verity checkout, so leave its branch and working tree alone.
- **Checking the render:** `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3001/docs/<page>` should print 200.
  - If it prints 500, load the page body and look for the error. A markdown or KaTeX mistake in your file is the usual cause.
  - If the error isn't yours, report it rather than working around it.

## Style

Follow the Vercel docs guidelines, condensed at `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/internal/vercel-docs-writing-guidelines.md`. Read it in full before writing. In short:

- **Choose one content type per page.** Most module pages (IR, Silicon, Commitments, Proofs, Randomness, Interaction) are Reference: exact names, types, invariants and interfaces. Overview, protocol and backend pages are Conceptual: the mental model, boundaries and tradeoffs. Census pages are Reference data.
- **Structure:**
  - Open with a one-paragraph summary.
  - Open each major section with a summary sentence.
  - Use `##` and `###` headings in sentence case.
  - Order sections by the reader's workflow.
  - Keep sections self-contained: repeat the full noun rather than an ambiguous pronoun.
- **Voice:** active voice, present tense, and "you" when the reader acts. Aim for sentences under 20 words.
  - Avoid these words: easy, simple, quick, just, really, very, simply, obviously, leverage, utilize, facilitate, robust, seamless.
  - Don't write rhetorical questions, filler introductions or promotional claims.
- **Mechanics:**
  - Introduce every list with a colon.
  - End list items without a period unless they're full sentences.
  - Use bold only for interface elements or critical facts.
  - Use inline code for identifiers, paths and literals.
  - Put numerals and a space before units (`64 KB`, `1 ms`).
  - Write one paragraph per line, with no hard wrapping.
  - Don't put `---` rules between sections.
- **The Project's own rules on top:**
  - No em dashes as punctuation: use colons, commas or periods.
  - Write "datacenters" as one word, "Datacenters" in title case.
  - No internal material in public docs:
    - no PR, issue or decision numbers;
    - no lane, pod, machine or agent names;
    - no artifact ids (`art:…`);
    - no regression row numbers;
    - no people's names or dated rulings.

## Terminology (the Project's ontology)

Use these terms exactly, and define each one on first use with a link to the page that owns it:

- **Subcircuit template:** a named template with typed parameters, such as the GEMM coordinate (`gemm-coordinate`, with parameters K, datatype and tensor-core semantics).
- **Subcircuit:** a template with every parameter bound. It's what a backend proves. Never call a subcircuit a "unit", and never say "family" or "kind" for computations.
- **Input:** one concrete input to a subcircuit, with the chip's output recorded alongside it.
- **Input set:** a batch of inputs with provenance, either captured from a model or synthetic. Don't write "instance" or "instance set". The Census file `census/instance_sets.json` still has its old name, and you may cite that path verbatim.
- **Commitment scheme:** how serving committed the values being proven. The schemes are frame-v3 (row leaves hashed with SHA-256, keyed BLAKE3 or Poseidon2) and vllm-v1 (SHA-256 position leaves, laid out the way the vLLM integration commits).
- **Statement:** what a backend proves: a subcircuit plus the commitment scheme that binds its inputs and outputs (the full committed relation). A different scheme is a different statement, not a different backend.
- **Circuit:** a backend's lowering of a statement.
- **Backend family:** A-GKR, B-Ligero, C-Flock and D-SP1.
- **Backend:** a concrete implementation of the `Backend` interface. The backends are:
  - A-route-a: A-GKR composed with C-Flock and a link, interactive;
  - A-fs;
  - B-interactive and B-fs;
  - C-interactive;
  - D-fs.

  "fs" means Fiat–Shamir. Properties and assumptions are stated per backend.
- **Cell:** one result, keyed by backend, statement, input set and prover hardware.
- **Replay unit and verification unit:** roles that sampled proofs assigns, not table concepts.

Don't say "configuration" for a backend with a scheme.

## Markdown the site supports

- GFM tables, footnotes and task lists.
- **Math:** `$…$` inline and `$$…$$` display, both KaTeX. Use `\mathsf`, `\mathrm` and similar freely. Escape nothing special: the file is plain markdown.
- **Code blocks must be fenced with `~~~`, not three backticks,** with a language tag: `~~~python`, `~~~text` and so on. The site's renderer and the author's tools expect tildes.
- **Diagrams:** a `~~~mermaid` fence renders a Mermaid diagram. Daniel likes diagrams: give every Conceptual page at least one where a flow, a composition or a structure helps, and give Reference pages one where it clarifies. Reuse and adapt the diagrams from the earlier port, collected in `docs-site-existing-diagrams.md` next to this brief. Keep them accurate, and label nodes with the ontology's terms.
- **Registry tokens:** `[CR · SHA-256](/assumptions/cr/sha-256)` renders a clickable token that opens the entry's definition. The ids that exist:
  - **Assumptions:** `cr/sha-256`, `cr/sha-512`, `cr/blake3`, `cr/blake2b`, `cr/poseidon2-babybear`, `cr/poseidon2-koalabear`, `xof/shake-256`, `random-oracle`, `honest-verifier`.
  - **Properties:** `sound-statistical`, `zk-malicious`, `zk-honest-verifier`, `no-zk`, `interactive`, `non-interactive`, `transparent-setup`, `binding`.
  - **Commitment schemes:** `scheme/frame-v3-sha256`, `scheme/frame-v3-blake3`, `scheme/frame-v3-poseidon2`, `scheme/vllm-v1`.
  - **Subcircuit templates:** `gemm-coordinate`, plus these, which are not in the tables yet: `attention-head`, `rope`, `rmsnorm`, `silu-mul`, `top-p-sampling`.
  - **Subcircuits:** `gemm-coordinate/k1536/sm80-mma-bf16`, `gemm-coordinate/k1536/sm90-mma-bf16`, `gemm-coordinate/k1536/sm90-wgmma-e4m3`, `gemm-coordinate/k1536/sm89-mma-e4m3`, `gemm-coordinate/k1536/sm120-mma-e2m1-nvf4`.

  An unknown id fails the build, so use only these. If you need an entry that doesn't exist, name it in your report.
- **Embedded tables:** `![Backends](/tables/backends)` renders the backend list. `![Table 1](/tables/table-1)`, `![Table 2](/tables/table-2)` and `![Table 3](/tables/table-3)` render the published benchmark tables.
- **Internal links:** plain markdown links to `/docs/...`. Every page should link to its related pages, and should be linked from at least one other page. The wide pages already exist:
  - `/docs/backends/comparison`: security and performance;
  - `/docs/assumptions`: every assumption with its trust rating;
  - `/docs/census/workloads`: every template and subcircuit.

## Accuracy

- **Order of evidence:**
  1. Current source, tests and CLI help on verity `origin/main` (commit `35560c88` when this brief was written).
  2. Merged PRs.
  3. Design documents in the Project store. These count as proposed, not shipped.
- **Reading the verity repo:** read it without touching the checkout at `/Users/danielreuter/projects/verity`:
  - `git -C /Users/danielreuter/projects/verity show origin/main:<path>`
  - `git -C /Users/danielreuter/projects/verity grep -n '<pattern>' origin/main -- <paths>`
  - `git -C /Users/danielreuter/projects/verity ls-tree -r --name-only origin/main`

  Useful starting points are `README.md`, `AGENTS.md`, the package layout under `packages/verity/src/verity/`, the `PROTOCOL.md` and `README.md` files under `backends/` and `packages/verity/src/verity/commitments/`, `integrations/vllm/README.md`, `protocols/` and `census/`.
- **Project store design docs:** in `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/`. Read `ontology.md`, `project-context.md` and `architecture/*.md` first, then the topic docs your prompt names. They explain intent. Check anything you state as current behavior against the repo.
- **Stay consistent with the site's existing data:**
  - `apps/docs/content/backends.md`;
  - `apps/docs/data/assumptions.ts`: registry entries, with the trust ratings the site uses;
  - `apps/docs/data/security-profiles.ts`: each backend's properties and assumptions;
  - `apps/docs/data/subcircuits.ts`.

  If the repo contradicts them, say so in your report rather than silently diverging.
- **Don't copy benchmark numbers into prose.** Link to `/docs/backends/comparison`, or embed a table. Census reference pages may tabulate Census data from `census/*.json` on `origin/main`, with its sources.
- **Leave out anything you can't verify.** Don't leave `[VERIFY]` markers, and don't invent examples, flags, measurements or guarantees.

## What to report back

Keep the report under 300 words. For each page, give:
- its content type and goal;
- the main sources, as repo paths and store docs;
- claims you left out because you couldn't verify them;
- any suggested change to its description in `lib/tree.ts`;
- missing registry entries;
- open questions for the author.

End with the HTTP status of each of your pages.
