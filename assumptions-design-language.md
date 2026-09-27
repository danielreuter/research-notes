---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# A design language for assumptions, models and guarantees

> **Revised and built, Sep 25, about 4:10 PM PT.** After Daniel's review, the built version is simpler than this proposal:
> - **Two kinds of token, not three.** *Properties* (what a component has, neutral grey) and *assumptions* (what you have to trust).
> - **Opinionated trust ratings.** Each assumption is rated solid, accepted, caution or weak, coloured from soft blue through violet and amber to red, with a one-line reason.
> - **No proven bounds.** They're theorems, not trust, so they're dropped from the vocabulary.
> - **Fiat–Shamir** folds into the random oracle assumption, and a live verifier becomes the *Interactive* property.
> - **Math appears only in the dialog.** Every symbol is defined from one glossary (`data/notation.ts`).
> - **The catalog is Verity › Assumptions,** with no used-by column.
>
> The rest of this doc is the original proposal, kept for context.

**For:** Daniel. **Status:** the original proposal (see the revision note above). **Context:** the Verity docs app (`apps/docs`, branch `cursor/verity-docs`). Today, assumptions reach the site as free text in the frozen renderer's Table 1 and render as pills split at semicolons.

## The idea in one line

Every security claim on the site reads as one sentence:

> **⟨guarantee⟩**, assuming **⟨assumptions⟩**, in **⟨model⟩**.

- For a backend configuration: "statistically sound to $2^{-128}$ and zero-knowledge against a malicious verifier, assuming collision resistance of BLAKE3, in the live-verifier model."
- For a protocol: "at most $\varepsilon$ of units wrong except with probability $\delta$, assuming backend soundness, commitment binding and an unpredictable beacon, in the synchronous-audit model."

Each bold slot holds tokens drawn from one canonical registry. Nothing is free text. Clicking a token opens a small dialog that states it precisely, in KaTeX.

## Three kinds of token

The main confusion in today's Table 1 is that it mixes what a system *provides* with what it *rests on* and the *setting* in which that's proven. So the design separates three token kinds, each with its own look:

| Kind | Meaning | Look | Examples |
| --- | --- | --- | --- |
| **Guarantee** | what the component provides | filled, muted background | Statistical soundness $2^{-128}$ · Knowledge soundness · Malicious-verifier ZK · HVZK · No ZK · Binding · Hiding |
| **Assumption** | what the guarantee rests on and can't be proven here | solid outline | CR · SHA-512 · CR · Poseidon2-KoalaBear · XOF · SHAKE-256 · Unpredictable beacon · Transparent setup |
| **Model** | the idealized setting the proof lives in | dashed outline | Random oracle · Live verifier · Honest verifier · Fiat–Shamir (non-interactive) |

There are only two further visual states, both reusing marks that already exist:
- **Algebraic** (amber text): any token that involves an algebraic hash. This is the existing "algebraic hash, not for highest-stakes use" flag, and the `(alg.)` pill.
- **Conjectured** (a small "conj." suffix): a bound or assumption that isn't proven, such as proximity gaps beyond the Johnson bound. It never counts toward the $2^{-128}$ filter, per the benchmark standard.

There are no icons and no other colours. The shape carries the kind, and the text carries the rest.

## The token

- **Size and type:** 22px tall, Geist Medium at 12px, 8px horizontal padding, 6px radius, a 1px `--border` outline. It turns muted on hover and shows a focus ring when focused from the keyboard.
- **Label:** short and standard, generated from the entry:
  - an assumption over a primitive is **property · instance**: `CR · SHA-512`, `XOF · SHAKE-256`;
  - a model or guarantee is its short name: `Random oracle`, `HVZK`.
- **Hover:** a tooltip shows the full name. **Click:** a dialog opens.
- **Semantics:** it's a `<button aria-haspopup="dialog">` whose accessible name is the full name.

## The dialog (shadcn `Dialog`)

It's concise, with the same template for every token, and about 480px wide.

1. **Title:** the full name ("Collision resistance of SHA-512"), with the registry id in muted Geist Mono (`cr/sha-512`) and a kind chip.
2. **Statement:** the formal definition in KaTeX, in a muted panel. For collision resistance:

   $$\Pr\big[\,(x, x') \leftarrow \mathcal{A}(1^\lambda) : x \neq x' \wedge H(x) = H(x')\,\big] \le \mathrm{negl}(\lambda)$$

3. **In one sentence:** "No efficient adversary can find two different inputs with the same SHA-512 digest."
4. **Here** (optional, from the citing page): why this component needs it. For example: "It binds committed rows: a collision would let a prover open one row two ways."
5. **Standing:** standard or algebraic; proven, conjectured or heuristic; and the best known attack in one line, for example "generic birthday attack, about $2^{256}$ work".
6. **Used by:** backlinks computed from the registry, such as "A-GKR, the Flock plus link route". Each links to its page.
7. A **reference** link, and "Open in the registry".

Opening a dialog updates the URL (`?assumption=cr/sha-512`), so a dialog can be linked and Back closes it.

## The registry

One canonical catalog, in the same spirit as the Census: other pages cite entries by id and never restate them.

- **Where it lives:** Verity › Reference › Assumptions and models, as one catalog page. It's filterable by kind and standing, with an anchor per entry.
- **Where the data lives:** `data/assumptions.ts`, validated with zod at build time. The shape:

~~~ts
type Entry = {
  id: string                 // "cr/sha-512"
  kind: "guarantee" | "assumption" | "model"
  name: string               // "Collision resistance of SHA-512"
  label: string              // "CR · SHA-512"
  statement: string          // KaTeX
  summary: string            // one sentence
  standing: "standard" | "algebraic" | "heuristic" | "proven" | "conjectured"
  refs: { label: string; href: string }[]
}
~~~

- **Composition:** properties and instances compose, so there's no duplication. CR, preimage resistance, XOF/PRF security and the random-oracle property are defined once, with the hash as $H$. The instances each carry their class, standard or algebraic: SHA-256, SHA-512, keyed BLAKE3, BLAKE2b, SHAKE-256, Poseidon2 over BabyBear, and Poseidon2 over KoalaBear. `cr/sha-512` is generated from property `cr` and instance `sha-512`.

**Starting catalog** (about 25 entries), drawn from what Table 1 and the architecture notes already cite:
- **Guarantees:** statistical soundness at $2^{-k}$; computational soundness (argument); knowledge soundness; malicious-verifier ZK; honest-verifier ZK; no ZK; binding; hiding; transferable versus designated-verifier.
- **Computational assumptions:**
  - CR, or preimage resistance, of each hash above. Preimage resistance matters for unsalted row digests.
  - XOF security of SHAKE-256.
  - SIS, for Ajtai digests. It appears only in weaker results today.
- **Statistical bounds**, as proven theorems with parameters: Reed–Solomon proximity gaps (unique decoding and the Johnson bound proven, beyond Johnson conjectured); Schwartz–Zippel; sumcheck soundness; LogUp fractional-sum soundness; FRI soundness.
- **Models:** random oracle; Fiat–Shamir in the random-oracle model; live verifier; honest verifier; the reference network, which links to Census › Networks.
- **Trust and setup:** transparent setup; trusted setup (none today); unpredictable, unbiasable beacon; secrecy of the on-node challenger's key (PoUW and PoUS); an append-only auditor log with trusted registration times.

## Where it's consumed

| Place | What it shows |
| --- | --- |
| **Backends › Comparison › Security** | Per configuration: Guarantees, Assumptions, Model and Setup columns of tokens. This replaces today's six free-text columns. |
| **Each backend page** | A Security section with the same sentence for each of its configurations, plus the "Here" notes. |
| **Each protocol page** | Its security model as the sentence. Assumptions include other components' guarantees, such as "backend soundness", so claims chain. |
| **Core › Proofs** | Defines guarantee, assumption and model, and links the catalog. |
| **Core › Commitments** | Binding, assuming CR of the leaf hash. The algebraic flag comes from the registry. |
| **Core › Randomness** | Beacon, random oracle, Fiat–Shamir; live coins versus transferability. |
| **Core › Interaction** | The interaction models, and the reference network. |
| **Integrations › vLLM** | The union of the assumptions of the protocols and backends it composes, computed. |
| **Posts on the Foundation site** | "What this system rests on": the computed union for a concrete composition, frozen at publication. |
| **Prose anywhere** | A plain markdown link, `[CR · SHA-512](/assumptions/cr/sha-512)`, renders as a token. It degrades to an ordinary link outside the site. |

The computed unions are the payoff: a composed system's assumptions become a query over its components' registry ids, rather than a paragraph someone has to keep in sync.

## KaTeX, where feasible

- **Turn on inline math** (`$…$`) in the docs renderer. It's `singleDollarTextMath: false` today, so only display math renders.
- **Use it for site-authored text:** bounds ($2^{-128}$, $\mathrm{GF}(2^{128})$), the overhead $N \div P$, the cost model $t = t_{\text{compute}} + r \cdot \text{RTT} + b / \text{bandwidth}$, and every registry statement.
- **Don't use it for renderer display strings.** Those stay exact ("2^-128" prints as the renderer wrote it). To get typeset values there, ask the renderer to emit an optional `tex` beside each `display`.

## Dependencies and order

1. **Registry, token and dialog:** a data file, two components, the catalog page, and the `/assumptions/` link mapping. Small and self-contained.
2. **The Security tab:** needs Table 1 as ids. Two options:
   - the renderer emits, for each configuration, `guarantees`, `assumptions`, `models` and `setup` as registry ids (the better path, and worth adding to the JSON request already sent to the research coordinator);
   - in the interim, a site-side table maps each exact renderer string to ids. Unmapped strings render as plain pills with a visible "unmapped" state, so gaps show.
3. **Protocol and backend pages:** as their prose is written.
4. **Inline KaTeX:** a one-line renderer change, plus a pass over existing content.

## Open questions

- Should guarantees be tokens too, or only assumptions and models? I'd include them. The sentence reads well only if all three slots use the same grammar.
- Does the registry belong under Verity (Reference) or as its own top-level item beside the Census? I'd keep it in Verity, because it's Verity's vocabulary. The Census is about computing inventory.
- Should the "Here" note live at the citing site (in markdown or the tree) or in the registry? I'd put it at the citing site, since the same assumption does different jobs in different places.
