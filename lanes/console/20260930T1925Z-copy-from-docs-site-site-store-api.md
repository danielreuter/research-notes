---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1925Z-copy-from-docs-site-site-store-api
campaign: verity
lane: console
kind: copy
status: final
repo: danielreuter/website
origin: docs-site
---

> **Public copy** of the docs-site worker's `docs/site-store-api.md` in the verity-root store, made 20260930T1925Z for the console handover.
> The original is unchanged and was not edited after this copy. Nothing was left out. Full copy, private: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/site-store-api.md`.


# Addendum: the site as the evidence store's network face, and standard benchmark pages

**For:** Daniel and the research coordinator; §5 is for RC. **From:** the docs-site worker. **Written:** Tue Sep 29, 10:00 AM PT. It adds to the [store-route proposal](verity-root store: `docs/fixtures-access-via-site.md`) and the [HTTP contract, v2](verity-root store: `internal/site-broker-contract.md`). Nothing here is built. Build order (a) ships §1's generic shape, with fixtures as its only kind; the benchmark pages wait for your answers in §8.

**In short:**
- **No new data model.** The site is the evidence store over HTTP: the same keys, the same four objects, the same kinds and labels (store README on Verity main). Its index in Neon mirrors `catalog.sqlite`'s tables and adds the two columns the site owns: visibility and writer.
- **Benchmarks are the first thing it renders:**
  - one matrix per workload and scheme, of hardware against candidate family;
  - a page per candidate and per hardware class;
  - history.

  All of them are views over Verity's published render, joined to the index. Nothing is kept by hand, and the site never re-decides what's admissible.
- **The standard benchmark record is what the store already holds:** an Attempt, a result artifact and labels. What's missing today is mostly links, not data. 84% of results carry their run id, but the published render drops it, and with it the commit, host, time, cost and red-team audit event.
- **Going generic stays under the one-day threshold** for (a): about 300 lines on top of its 1,000 to 1,500 (§7).

## 1. The generic API

### 1.1 Paths: the store's keys under `/store`

The base is `https://website-docs-sage.vercel.app/store`, fixed in the contract. A read is `{base}/{key}`, for any key in the store's layout:

| Store object | Key (store README §3) | Site path | When |
|---|---|---|---|
| blob | `objects/sha256/{hex}` | `/store/objects/sha256/{hex}` | (a) |
| artifact manifest | `manifests/{hex}.json` | `/store/manifests/{hex}.json` | (a) |
| Attempt | `attempts/{run id}.json` | `/store/attempts/{run id}.json` | with the index mirror, §1.3 |
| Label | `labels/{target}/{sha256 of the assertion}.json` | `/store/labels/{target}/{name}.json` | with the index mirror |

- **Two names under the base are the site's own:** `uploads`, for writes (in the contract), and `index`, for JSON views of the index, which pages and agents use:
  - `GET /store/index/artifacts/{art id}`: the manifest, its refs in both directions, its labels, the Attempts that produced it, its visibility and writer;
  - `GET /store/index/attempts/{run id}`: the Attempt, its inputs and outputs, and its labels;
  - later, `GET /store/index/query?kind={kind}&meta.{key}={value}&label.{key}={value}`.
- **Derivations** aren't files in the store, only `drv:` ids inside Attempts, so they have no path. The index can be queried by derivation.
- **Private keys use the same paths.** They're refused to anonymous readers, below.

### 1.2 Visibility, per object

Every key the index knows is `public` or `private`. Public means the bytes are in `verity-public`, the store's public half. Private means they're only in `verity-research`.
- **An anonymous read** always gets a `307` to `verity-public`, and the bucket answers `404` for anything that isn't public. So a private key and a missing one look the same.
- **A read with a token that holds read scope** gets the same `307` for a public key. For a private key, it gets a `307` to a presigned URL on `verity-research` that's valid for 60 seconds. A `HEAD` gets its own presigned `HEAD`.
- **Publishing a key** means copying its bytes from `verity-research` to `verity-public` and marking it public. For an artifact, the manifest and every payload blob are published together, blobs first. A publisher job does this from the kind policy below, never by hand.
- **Publishing is one-way in practice.** The site could delete the public copy, but anyone may already have fetched it.

**Default visibility by kind.** The site holds this policy, and a token's scope names the kinds its writer may publish. Everything not listed is private.

| Kind | Default | Why |
|---|---|---|
| `fixture/v1` | public | decided; tests fetch it without keys |
| the published render (`verity/tables-entities/v1`, stored as an artifact, §5) | public | it is the published tables |
| `bench-result/v1` and `verification-verdict/v1` | public when a published render cites them | each cell links to its evidence; unpublished and rejected results stay private |
| `proof/v1` | public when its result is | anyone could re-verify a published cell; question 1 |
| `run-files/v1`, `run-record/v1`, `telemetry/v1` | private | they carry host names, paths, argv and pod ids |
| `dataset-snapshot/v1`, `tc-evidence/v1` | private | captures and inputs may carry model data |
| `redteam-findings/v1`, `ledger-row/v1`, `trust-dossier/v1` | private | findings and working records |

Attempts and labels have their own rule, in §4.

### 1.3 The index in Neon

- **The tables are `catalog.sqlite`'s,** with the same names and columns: `artifacts`, `artifact_meta`, `refs`, `attempts`, `attempt_params`, `attempt_conditions`, `attempt_inputs`, `attempt_outputs` and `labels`.
  - So Verity's own queries, such as `store_tables.py`'s `ROW_LABELS_SQL`, run unchanged against it. A parity check runs the same queries against a fresh `reindex --remote` catalog.
  - The site adds `visibility`, `writer`, `seen_at` and `bucket` to `artifacts` and `attempts`. The site's own `store_events` and `tokens` tables sit beside them.
- **How it's fed, first: pull, with no Verity change.** A Vercel Cron job runs every 15 minutes, with a read-only key for `verity-research` (question 4).
  - It lists `manifests/`, `attempts/` and `labels/`, fetches the documents it doesn't have yet, and indexes them, as `reindex --remote` does.
  - Listing tens of thousands of keys takes a few dozen requests, at R2's $4.50 per million list operations.
  - An Attempt shows on the site within 15 minutes of `research run` publishing it.
- **Later, push.** Once writes go through the site (§2), the index is updated in the same request, and the cron job only catches up.

## 2. How Attempts and labels from `research run` flow in

**Today.** `research run` publishes each Attempt to `verity-research` at completion or failure, through `S3Remote`, with minted temporary credentials on pods. Labels are written with `research data label`, and uploaded when write-through is on. The steward renders the tables daily at 13:00Z.

**Step 1: reads, with no Verity change.** The cron job in §1.3 mirrors every Attempt and label into the index. The site renders from the index, and private reads need a token.

**Step 2: writes through the site, with RC, which owns the store.**
- `BrokerRemote` becomes the general site remote, and `research run` pushes through it:
  - blobs and manifests, as in the contract, to `verity-public` or `verity-research` by kind;
  - `PUT /store/attempts/{run id}.json`: write-once, where different content answers `409`, which maps to `AttemptExists`;
  - `POST /store/labels`: the site checks the assertion's shape and **binds `by` to the token**. A `red-team-*` label can then only come from a red-team token. Today `by` is whatever the writer says.
- **Pods get a site token instead of minted R2 credentials.** The site mints and revokes one per pod or per campaign, with the same pages as the spend broker.
- **What stays with RC:** the store's invariants, the kind vocabulary, the steward and any change to `research run`. The site enforces the same rules the store does, and adds nothing to the model.

## 3. Benchmark pages

### 3.1 What exists

- **The published render.** `views --format entities --published` renders `verity/tables-entities/v1`. The current copy, `internal/tables-render/latest.json` (verity `53bccf6b`, rendered 13:01Z Sep 28), has:
  - 83 results: 61 C-Flock, 17 B-Ligero and 5 A-GKR;
  - the 82 Table 2 lines, which make 26 matrices of workload and scheme;
  - Tables 1 and 3, 410 footnotes, 17 below-bar entries and 1,604 rejected results, each with its reasons.
- **The site's comparison page** (`/docs/backends/comparison`) renders a copy of it that was checked in on Sep 25.
- **`store_tables.py`** rebuilds the like-for-like decision table from the index. `--proof-class-by 'red-team-*'` caps each row's class at the latest red-team audit event's grant: downgrades stand, and nothing is upgraded. Its hand-transcribed constants (verifier seconds, proof bytes, depth, the verified prose) still live in `decision_tables.LIKE_FOR_LIKE`.
- **The spec** is `kb/TABLES.md`:
  - Table 2 has one line per subcircuit, hardware class and scheme, and one column per family;
  - D2 is results by configuration;
  - D6 is history, the hill-climb view;
  - "nothing in them is kept by hand";
  - any change to a definition, column or rule needs your approval.

### 3.2 One standard benchmark record

A benchmark record is one Attempt, the result artifact it produced, and the labels on both. Here's where each part lives, and what the laptop's catalog shows today. That catalog holds 1,589 results and was last indexed at 05:21 Sep 28. It's partial: it holds only one of the nine results in the mock below. So these rates are indicative, and `reindex --remote` would give the real ones.

| Part | Lives in | Today |
|---|---|---|
| **Candidate:** family, backend and configuration | the result's `meta.configuration` | **Missing.** One of 1,589 results names its candidate. `views` infers the configuration with `drilldown.VARIANTS`' name recognisers. |
| **Hardware:** class, GPU SKU and count, host CPU, driver, CUDA | the Attempt's `hw.*` and `rt.*` conditions, plus the class id in the result | Present in Attempts (`hw.sku`, `hw.cpu`, `rt.driver`, `rt.cuda`). The render carries the class. It gives the host CPU only as footnote prose. |
| **Workload:** statement (subcircuit and scheme), input set and range, batching | the result's `workload_fingerprint` | Present in 1,297 of 1,589 results. The render carries it. |
| **Metrics with units** | the result's `measurements[{name, value, unit}]` | Present in 1,286 results. The render derives N, P, the overheads and the phases from them. |
| **Protocol:** warm, runs, statistic, contention; the sweep point and plateau | the result's `protocol` and `sweep` | **Mostly missing.** 166 results have them; only `sweep_vu` stamps them. |
| **Security properties:** declared class, soundness, ZK, assumptions, authentication | the configuration's Table 1 record; the cell's own soundness | In the render. Table 1 still comes from `tables.CANDIDATES` and `drilldown.VARIANTS`, not from capability declarations. |
| **Verification** by someone other than the producer | `verified` and `verifier` labels, and a `verification-verdict/v1` artifact | Present as labels. The render keeps only `verified_by`. |
| **Red-team status** | `proof_class` labels by `red-team-*`, where one audit event is one `by`, `ref` and `ts` | 30 targets carry them. The render shows `(prov.)` but not the event. |
| **Run id** | the Attempt's id, and the result's `meta.run_id` | 1,341 results (84%) carry `run_id`, and 742 (47%) are linked as an Attempt's output. **The render drops both.** |
| **Source commit** | the Attempt's `source.commit` | Null for 47 of the 689 producing Attempts (7%), from remote machines that report no `source_sha`. The render drops it. |
| **When, cost, campaign** | the Attempt's `execution.start_utc`, `cost.usd` and `execution.campaign` | The time and cost are present. The campaign is null for 279 of 689 (40%). The render drops all three. |

**The proposal:**
- **Adopt the archived `bench-result/v2` shape** (the benchmark standard proposal, §6.1) as the result half. It is already written in the store's model:
  - a required configuration id;
  - the hardware class;
  - the protocol and sweep blocks;
  - measurements with units.

  Security stays in the per-configuration record, as that proposal says.
- **Provenance stays on the Attempt,** not copied into the result.
- **Verification and red-team status stay labels.** They're assertions with an asserter, never fields.

### 3.3 The standard views

Every view is a query. The **selection** comes from Verity's render: which result fills a cell, the admissibility criteria, and the red-team cap. The site never computes admissibility itself, so there's only one implementation. The **links** come from the index, joined on each result's `art:` id: its run, its verdicts, its audit events and its history.

| View | Path | Derived from |
|---|---|---|
| **Matrix:** hardware classes against candidate families, for one workload and scheme | `/docs/benchmarks/{workload}`, with the scheme as a tab | the render's Table 2 lines, grouped by subcircuit template and parameters, then scheme, and pivoted by prover hardware. It shows the same cells, in the same states and with the same footnotes, as Table 2. |
| **Per candidate:** a family and its configurations | `/docs/benchmarks/candidates/{family}` | the Table 1 entry; D2's best result per line; its weaker-statement, below-bar and rejected results, with reasons; its audit events from the index |
| **Per hardware class** | `/docs/benchmarks/hardware/{class}` | the class's native peaks; every line on it; the hosts seen (`hw.cpu` from Attempts), which the spec says to compare only within a class |
| **Trends (D6)** | `/docs/benchmarks/history`, and a sparkline in each cell | one point per cell per published render, from the series of render artifacts (§5), with each change linked to the result that replaced it (`superseded_by`) |
| **Run** | `/docs/runs/{run id}` | the Attempt's public summary (§4), its outputs and labels, and the cells it fills |
| **Artifact** | `/docs/artifacts/{hex}` | the manifest, refs, labels and producer; a download link if it's public |

- **Parity.** A check, like today's `check:tables`, asserts that the matrix reproduces every Table 2 cell of the render it came from.
- **The proof-optimization table becomes one more view.** Once §5's step 5 moves its constants into records, `store_tables.py`'s like-for-like table is a query too.

### 3.4 The matrix page, mocked

The numbers are real, from `latest.json`. The `{…}` fields are the links the render doesn't carry yet (§5, step 1).

```text
 Verity docs › Benchmarks › GEMM coordinate, K = 1536
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────
 Scheme:  [ frame-v3 · keyed-BLAKE3 rows ]   frame-v3 · SHA-256   vllm-v1 · SHA-256   frame-v3 · Poseidon2 †
 Each cell is N/P: how many times longer proving takes than computing natively on the same hardware.
 Lower is better. Compare within a row; each row's native peak differs.
 Render 2026-09-28 13:01Z · verity 53bccf6b · spec kb/TABLES.md · 9 of 24 cells filled

                          │ A-GKR            │ B-Ligero         │ SP1              │ Flock
 ─────────────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────
 A100 SXM4 80GB · BF16    │ 1.4e9×  ✓  ╱╲_   │ —  rejected ⁸    │ —  weaker ⁹      │ 3.3e7×  ✓  ╲_╱
 H100 SXM5 80GB · BF16    │ —  weaker        │ 8.0e7×  ✓        │ —  weaker        │ 6.0e7×  ✓
 H100 SXM5 80GB · E4M3    │ —  weaker        │ 8.1e7×  ✓        │ —  weaker        │ 5.5e7×  ✓
 RTX 4090 · E4M3          │ —  weaker        │ 2.1e7×  ✓        │ —  weaker        │ 1.6e7×  ✓
 RTX 5090 · E2M1 (NVFP4)  │ —  weaker        │ —  weaker        │ —  weaker        │ —  rejected
 L40S 48GB · BF16         │ —  no result     │ —  no result     │ —  no result     │ 4.1e7×  ✓
 ─────────────────────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────
 ✓ verified by someone other than its producer   (prov.) awaiting red-team clearance   ╱╲_ history (D6)
 weaker: results exist only for a weaker statement (in D2)   rejected: no admissible result; reasons in ⁸

 ┌─ Selected: B-Ligero on H100 SXM5 80GB · BF16 · B-interactive ─────────────────────────────────────────┐
 │ Overhead   8.0e7×    P 4.0e3 instances/s    N 3.2e11 instances/s (tensor-core peak, work-model/v0)    │
 │ Security   2^-128.4 for the cell, over 193 proofs of 2^-136.0 each · malicious-verifier ZK            │
 │ Verified   by verify-night-3 · verdict {art id}                                                        │
 │ Red team   {by} granted {class} on {date} · audit {ref}                                                │
 │ Run        {run id} · measured {start_utc} · commit {sha} · host {hw.cpu} · driver {rt.driver}         │
 │ Evidence   result art:f15909f52579ba69… · proof {art id} · run files: private                          │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The per-candidate and per-hardware pages reuse the same cell and the same panel. A candidate page is a column of this matrix taken across every workload; a hardware page is a row taken across every workload.

## 4. What stays private

- **Every kind marked private in §1.2,** and every result the published render doesn't cite. That includes the 1,604 rejected results. Their counts and first reasons are public in the render, but their artifacts aren't.
- **Attempts.** The raw Attempt stays private. A run page shows a public summary only for an Attempt that produced a public result. The summary has:
  - the run id, tool, state and times;
  - `hw.sku`, `hw.count`, `hw.cpu`, `rt.driver` and `rt.cuda`;
  - the source commit.

  It never shows `argv`, `params.env`, `execution.host`, `cwd`, `run_dir`, `hw.hostname`, pod ids, telemetry or, by default, cost (question 2).
- **Labels.** A label is public only when its target is public and its asserter is a verifier or a `red-team-*` audit. `note`, `notes` and `finding` text stay private. The red team's findings artifacts stay private.
- **The site's own records:** the fetch and upload events, token hashes and IP hashes. They show only on the admin pages behind Vercel's login.

## 5. What changes in Verity: RC's part, in order

| Step | Change | Size |
|---|---|---|
| 1 | **The render carries its links.** For each result, `views --format entities` adds data the index already has: `run_id`, the `attempt` when the store has it, `source_commit`, `measured_at`, `host` (the CPU), `verified` (by whom, and the verdict's id), `audit` (`by`, `ts`, `ref` and the class granted) and `superseded_by`. This is additive to `verity/tables-entities/v1`, and changes no TABLES.md definition, column or rule. | about 150 to 250 lines, plus tests |
| 2 | **Each daily render becomes an artifact.** Add `verity/tables-entities/v1` to `kinds.py`. The steward puts each render as an artifact, labels it `published`, and pushes it as it already pushes. The site shows the newest published render, and D6 is the series. | about 50 lines |
| 3 | **Fill the provenance gaps at the source:** `source.commit` on remote machines, and `execution.campaign` on every run. | small; RC knows where |
| 4 | **`bench-result/v2`**, as in §3.2: in `kinds.py`, then in the producers (`sweep_vu` first), with `views` reading v1 and v2 until v1 ages out. | the largest step: several harnesses; RC schedules it |
| 5 | **`LIKE_FOR_LIKE`'s hand constants move into records:** verifier seconds from verdict artifacts, and proof bytes from `proof/v1` payloads. | about 200 lines |
| 6 | **Later: `research run` writes through the site** (§2, step 2), with `by` bound to tokens, and pods holding site tokens. | RC's design, with the site's side about 400 lines |

Steps 1 and 2 are what the pages need. Steps 3 to 5 make the record complete. Step 6 moves custody, and waits for RC.

## 6. Migration order

1. **(a) ships generic.** It serves `/store` reads and writes, for fixtures only, which are public. Its read path goes live first, as a config redirect, for #371's export check. The rest of (a) follows.
2. **Render from the store.** The site fetches the newest published render from `verity-public`, not a checked-in copy. The matrix, candidate and hardware pages go live from the render alone, showing the links it has. This needs Verity step 2, and your answers to questions 1 and 3.
3. **The index mirror.** It needs the read-only key (question 4). Then come the cron job, the run and artifact pages, the cell links and private reads with tokens. Verity step 1 fills the panel.
4. **Trends,** once a few rendered artifacts exist.
5. **Writes through the site,** with RC: Verity step 6.

## 7. Effort, on the site's side

- **The generic shape in (a):** about 300 lines on top of its 1,000 to 1,500. That covers:
  - the key parser for the store's layout;
  - the manifest check (envelope, kind and blobs first);
  - the visibility column;
  - kinds in the token scope;
  - the `index` routes for artifacts.

  It stays under the one-day threshold.
- **Benchmark pages from the render:** about 800 to 1,200 lines. That's the matrix, the candidate and hardware pages, the cell panel and the parity check. They reuse the comparison page's `lib/entities.ts` and its tables.
- **The index mirror,** with the run and artifact pages and private reads: about 1,000 lines. It's on the Neon plan already approved, since the mirror's tables fit well inside it.
- **Trends:** about 300 lines.

## 8. Questions for Daniel

1. **Which kinds are public?** **Default:**
   - fixtures, which is decided;
   - the published render;
   - the result, verdict and proof artifacts the render cites.

   Everything else is private.
2. **What does a public run summary show?** **Default:** the hardware, host CPU, driver, commit and time, but not the cost, which shows only on the admin pages.
3. **Is the matrix inside the spec?** It rearranges Table 2's cells, with no new numbers, columns or rules. **Default:** I treat it as a view, as TABLES.md defines one, and don't need approval. Say if you'd rather approve it as a change.
4. **May the site have a read-only key for `verity-research`,** for the index mirror and private reads? It's one more click: an Object Read only token for that bucket alone, into a Sensitive, Production-only Vercel variable. **Default:** yes, at step 3 of §6.
5. **Is `bench-result/v2` the standard result?** **Default:** yes, in the archived proposal's shape, with RC deciding when.
6. **Should each cell show its red-team audit publicly:** who audited, when, and the class granted? **Default:** yes, while the findings stay private.
