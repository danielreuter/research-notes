# Serving view (`vllm-serving-view/v1`)

A whole serving run of one row, laid out the way vLLM runs it: **engine steps → the requests in each step → the model runner
(model modules, sampler, KV-cache reads across steps) → TP ranks**. This is the "instrumented program" view for the docs-site
visualizer.

It is a view, not a new Program. Every node is a set of Calls that already exist in the Build's request Programs, and no digest
changes. It is derived mechanically from the Build's own files: the step chronology (`build_workload/chronology.json`), the address
map (`build_workload/address_map.json`) and the per-Call dataflow of the request Programs (`build_request*/instances.json.gz`, plus
`descriptor.json.gz` for the returned tokens). Module names come only from the recorded correspondence (`Correspondence.module_of`),
and no rule names a model or a module. The generator is `verity_vllm.pipeline.serving_view` (CLI `serving-view`).

## Files

| File | What |
|---|---|
| `index.json` | the rows, their files, provenance (Build artifact, runs, digests) and each row's checks |
| `<row>.serving-view.json` | the full view: every node, every edge, the checks, the rules |
| `<row>.site.json` | the site-ready tree: nested, steps collapsed except prefill (e=0) and the first decode step (e=1) |

Rows:

- **#101** `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`. This is the **record Build**: it
  reproduces the headline record run `r20260926-035624-a133`, with request Program `ccc21347…` and manifest `90f81868…`. Build
  artifact `art:9cb3a4df…`. One request, TP1: 32 engine steps (prefill plus 31 decode steps), 46,654 Calls.
- **#70** `olmoe-1b-7b__bf16__l40s__tp2__b8__…` (file suffix `.tp-exercise`). This is **not** a full row. It exercises the TP-rank
  level on 2 of the row's 8 request Programs, with both ranks, from the stored r19-reference programs artifact. That artifact has no
  chronology, address map or descriptor, so its "engine steps" are request steps (arrival not recorded) and its nodes have no gate
  ranges. Label it as an example of the rank level only.

## Hierarchy (`nodes`, flat list; `parent` / `children` are node ids)

~~~text
serving                      the workload Program (workload_digest, gates_total incl. inputs, shared weights group)
└ engine_step  e             co_scheduled, mixed_prefill_decode, collapsed (site default)
  └ member     request r at its step s   phase prefill|decode, program_digest, call_runs, gate_range, structure_hash
    └ runner   model runner
      ├ model                the step's model Calls
      │ └ module …           torch nesting by path (nearest enclosing module); body = the module issued Calls itself
      │   └ rank  k          LEAF: one rank's Calls of that module body at that step
      └ sampler              the step's token select and its constants
        └ rank  k            LEAF: spec, call id, inputs (e.g. seed [[0,1]], splits [[s,s+1]]), with_calls (the constants)
~~~

The leaves (`kind: "rank"`) partition every Call of every request Program exactly once. The generator refuses to write a view
that doesn't do this.

## Node fields

- **Every node:** `id` (`n<k>`), `kind`, `parent`, `children`, `label`.
- **Totals** (every node that has them; an inner node's totals are its subtree sum):
  - `calls`.
  - `gates`: exact, the sum of each Call's specialization gate count.
  - `units` and `committed_interior_words`: Q_word_v1{X=16,W=32,R=no-recompute} per Call, summed.
- **module:**
  - `path`, `body` (true when the module issued Calls itself), `body_calls`.
  - `groups`: program-graph group ids, the same ids as the row's `program.json`.
  - `subtree_hash`, and `fold_of`: the node id of the first sibling with the same structure. `layers.2`–`layers.15` fold onto
    `layers.1`; `layers.0` differs because its input norm is another Definition.
- **member:**
  - `request_id`, `s`, `phase`, `program_digest`.
  - `call_runs`: the member's Call ids in its request Program as `[lo, hi)` runs.
  - `gate_range`: its canonical gate range in the workload root, when it is one run.
  - `structure_hash`: equal for members with the same structure. On #101, all 31 decode steps are equal.
- **rank (leaf):** `rank`. A sampler leaf also has `spec`, `call`, `group`, `inputs` and `with_calls`.

## Edges (`edges`: leaf → leaf, `reads` = Values read, `words` = leaves the operand runs name)

| kind | meaning |
|---|---|
| `flow` | inside one member and rank: dataflow between module bodies |
| `token` | a sampler's token read at the next step (step s−1 sampler → step s embedding) |
| `state` | a read of a Value produced at an earlier step: **the KV cache**. On #101 they are exactly `rotary_emb → attn` (K) and `qkv_proj → attn` (V) per layer, 134,416 reads each |
| `collective` | TP: the Calls rank b feeds its collective with → rank a's Call reading them as its input `peers_<k>[lo:hi]` |
| `backward` | a read from a later step; must be 0 (checked) |

To draw KV-cache edges across steps, follow each `state` edge's endpoints up to their members; each member node has `s`.

## Site tree (`<row>.site.json`)

- `tree` is the serving node with nested `children`. Nested nodes keep the flat file's `id`, so you can lazy-load details from
  `<row>.serving-view.json`.
- **Expanded steps** (`expanded: [0, 1]`) are nested down to the rank leaves.
- **Collapsed steps** carry `collapsed: true`, their totals and their `members` (id, request, s, phase, calls, gates, gate_range).
  They also carry `same_structure_as: e` when their members have the same structure hashes as an expanded step. On #101, steps
  2–31 are `same_structure_as: 1`.
- **Folded siblings** appear once, with `repeat: [{label, id}, …]` listing the siblings they stand for.

## Checks (`checks` in each view; the generator fails unless `ok`)

- `partition`: each Call is in exactly one leaf.
- `members`: per request, the step sums equal the Program's Calls. This also records how the steps were found (`sampler_rule`
  `return` or `sampling-event`), agreement with the Build's body-order segmentation and with the forward dataflow rule, and, on a
  stochastic row, whether the `splits` readers are the samplers.
- `gates`: the Calls' gates equal the request's address-map span.
- `chronology_ranges`: every member equals the node and gate range the chronology records for it.
- `edges`: no backward reads; every collective's words match between the ranks.
- `graph` (#101): the group ids and the Q_word totals equal the row's program graph built from the same Build.

## How steps are found (rules, also in each view's `rules`)

- **The sampler of step s** produces element s of the request Program's return (its served tokens). With no descriptor, it is the
  s-th Call of the Build's sampling-event Definitions.
- **A Call's step** is the first step whose sampler needs it. A Call no sampler needs gets the forward rule: the maximum step of
  the Calls it reads, plus one past a sampler.
- **The sampler node** is the token select plus its constants: Calls that read no Call and are read by that sampler alone. On
  #101 these are top-p `0x3f733333` (0.95), temperature `0x3f4ccccd` (0.8) and a per-step integer `0xff + s`.
