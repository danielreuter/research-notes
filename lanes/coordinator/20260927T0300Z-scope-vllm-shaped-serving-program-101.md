---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: draft · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:00Z · status: scope; no pod work started

# Scope: a whole-serving Program for row #101, arranged the way vLLM is (the derived "instrumented program" view)

**Daniel's ask (via the docs site).** One served row's whole Program, arranged as vLLM runs it: engine steps, then the
requests in each step, then the model runner (model, KV cache, sampler), then the TP ranks. Today's view is the folded
per-config Program. Row #101, the headline row.

**What it is.** A **view**, not a new Program: a regrouping of the Build's own request and workload Programs. Every node
points at Calls and gate ranges that already exist, so no digest changes. It is generated mechanically from the IR and
the Build's records; module names come only from the recorded correspondence, and no rule names a model or module.

## 1. What already exists

For #101, `llama32-1b…i256__o32…stoch-t0.8-p0.95`: TP1, B1, one request, 256 prompt tokens, 32 output tokens.

| Data | Where | Gives the view |
|---|---|---|
| **Workload Program** `Workload_v1` (the requests, `arrive_step`, `cap`) | `art:a4ea1a18…` `build_workload/workload_program.json` | the root: shared weights plus one call node per request |
| **Chronology** (`verity/workload-program/v1/chronology`) | same, `build_workload/chronology.json` | **engine steps**: per step e, its members (request id, request step s, phase prefill/decode, and a node range when recorded), co-scheduling, mixed prefill/decode |
| **Address map** | same, `build_workload/address_map.json` | a gate range and hierarchical path for every node (`root/node[k]/…`), and the shared-weights group |
| **Request Build** (instances: every Call's spec, its owning module and op index, and its reads as `p`/`n` runs) | `art:a9be8f7c…` `build_request/instances.json.gz` (Program `079ee0a8…`, 46,654 Calls) | the **model runner** subtree (torch module nesting), the **sampler** Calls (`gumbel_topp_token_select[_k]`), and the dataflow for steps and the KV cache |
| **Program graph** (modules, groups, edges, subtree hashes, Q_word rules) | `art:c74deac4…` (13 rows; #101 kept its previous graph) | folding identical siblings (`layers.0..15`), and the per-node committed words and gates |
| **Commit records** (`steps.jsonl`, `structure_p0.json`, the verdict) | `art:a4ea1a18…` `commit/` | per-step commit and verification facts to annotate step nodes |
| **TP2 rows' per-rank request Programs** (#70, #75) | the programs artifacts behind `art:c74deac4…` | the TP-rank level. #101 is TP1, so its rank level is a single node |

**What the stored #101 Build is.** It is the r19-reference Build (Program `079ee0a8…`, manifest `368283ad…`). The
headline record run `r20260926-035624-a133` has Program `ccc21347…` and manifest `90f81868…`, and **its Build is not in
the store**. The dataset index says the same: "`param_inputs` not recorded: the redraw run's Build is not in the store".

## 2. How the hierarchy is derived

1. **Serving (the root)** = the workload Program. Its children are the engine steps, from the chronology.
2. **Engine step e** → its members (request r, step s, phase).
   - Only step 0 carries a node range in the chronology. For the rest, a Call's step s comes from dataflow:
     - step 0 is the prompt's Calls;
     - step s ≥ 1 is the Calls downstream of sampler s−1's output token, up to and including sampler s;
     - the sampler of step s is the Call that reads `splits[s]`.
   - This is exact for B=1. For B>1 the same rule runs per request, and a step's co-scheduled members come from the
     chronology.
3. **Request r at step s** → the **model runner**:
   - **model:** the step's Calls grouped by the recorded owning module (torch nesting, as `program_graph` does), with
     identical siblings folded by subtree hash;
   - **KV cache:** derived as the attention Calls' reads of K/V values produced at earlier steps, per layer, with the
     edge counts and words. This is where the view shows cross-step state. No new Calls;
   - **sampler:** the step's sampler Call (temperature, top-p mask, Gumbel select), with its `splits[s]` / `seed` reads.
4. **TP ranks:** per rank, the rank's request Program under the same tree, with the all-reduce / gather Calls as edges
   between ranks. For #101 it's one rank.
5. **Every node carries:** Call count, gates (from the address map and the derive report), committed interior words
   (Q_word, the no-recompute rule), and its program-graph group ids.
   - The derivation passes only if the leaves partition all 46,654 Calls exactly once, and the per-step sums equal the
     request totals.

**Output.** `vllm-serving-view/v1` JSON, beside the program graph, and a site-ready tree (steps collapsed by default;
prefill and one decode step expanded). The generator is a new `pipeline/serving_view.py` that reads
`program_graph`'s accumulator and the Build's workload files. Its tests: a synthetic two-request, two-step workload
(co-scheduled members, a KV edge, TP2), and the partition-of-Calls invariant.

## 3. What's missing

- **#101's record Build** (`ccc21347…`) for the headline view. It needs a pod Build of #101: L40S, the Build stage only,
  no Commit. Its outputs go into the store as a programs artifact, and `program_graphs.py` runs on the pod, as
  `vux_row.sh` did.
- **The same run also fixes the export lane's gap:** #4 and #101 have no `param_inputs` because their redraw Builds
  aren't stored (item 3 of root's 02:44Z message). So I recommend one pod doing both rows' Builds.
- **Until then, a CPU dry run** on the stored #101 Build (`079ee0a8…`) exercises the whole generator. It is the same row
  configuration, but not the record Program, and the site must say so.
- **The TP level** gets a real test on #70 (TP2) from the stored per-rank Programs, on CPU.

## 4. Owner

**vllm-cross-call-check** (bc-f7aadce6). It owns `program_graph` and the regenerated graphs (`art:c74deac4…`), and its
`query.cross_call` already walks every request Program and Build, both TP ranks. Sequence it after #98 is re-merged
(the one blocker in its queue). If root wants it in parallel, a fresh lane seeded from this scope works too: the lane
count is well under 8.

## 5. Cost and sequencing (no pod starts before root approves)

| Step | Where | Cost |
|---|---|---|
| Generator plus tests; dry run on the stored #101 Build and on #70 (TP2) | CPU (lane VM) | $0 |
| Pod Build of #101 (record `ccc21347…`) and #4 (smollm2 b16), Build stage only, store put, `program_graphs.py` for both | 1× L40S secure ($1.09/h), about 2.5 h including bootstrap | **about $2.7, cap $4** |
| Final #101 view on the record Build, plus the #4 / #101 `param_inputs` for the export redraw | CPU | $0 |

- **Budget:** day spend at 02:40Z was $734.68, and nothing else is running. With the cap: at most about $739, under
  the $760 stop. The guard deadline is 04:15Z, so a 2.5 h run starting now needs one ≤4 h guard step.
- **Sequencing:** the CPU generator and dry run come first. The pod Build can run alongside, once approved: it depends
  only on the Build tooling, not on the generator. The final view follows the stored record Build.
- **Checks before the pod run:** the pod Build must reproduce #101's recorded Program digest `ccc21347…` (and #4's
  recorded digest). If it doesn't, stop and hand off: a different Build would not be the headline row.
