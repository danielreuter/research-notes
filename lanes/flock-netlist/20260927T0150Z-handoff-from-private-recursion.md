---
cursor:
  subagentId: "bc-be25385c-8dda-5970-9cf6-7c0ce338bad3"
---

lane: flock-netlist · kind: handoff · from: private-recursion · created: 2026-09-27T01:50Z

# Spec request: multi-table Flock statements with private values glued between tables (the private track's outer-proof prerequisite; plan now, build after the unit-shape census)

**Status.** Daniel adopted Project store `docs/circuit-privacy.md` §I.11 as the plan of record:
- c is a salted Ligerito commitment to Enc(C);
- V[B] checks one opening of c per run;
- V[B] is generated as structured tables;
- the outer proof is Flock over V[B].

The outer-proof milestone waits for the unit-shape census (`docs/unit-shape-census.md`), so there is no rush. This spec says what your prover must add so the outer proof can be built. It is the one piece both options needed.

## 1. Why a single-table statement is not enough

V[B] is a session of gadget tables, each one template repeated over blocks (`I_{2^{b_t}} ⊗ A_t`):
- SHA-512 compressions (57,947 ANDs each);
- the GF(2^128) multiplier (2,187 ANDs);
- switch columns;
- small AND/mux logic.

Values flow privately from one table's outputs into another table's inputs. Your `verity/flock-circuit` has one table, and its glue lives only inside a block (Δ). A 1.4–1.7 G-AND V[B] cannot fit in one block of at most 2^26 bits.

## 2. What the statement describes (all public, and bound by the statement digest)

**Tables** $t=1..T$. Each table has:
- a pinned template $(A_t,B_t)$ with $C=I$, in circuit form, with its own pin and in-block Δ as today;
- block size $2^{k_t}$ and block count $2^{b_t}$;
- an aligned offset in **one** witness of $2^m$ bits.

**Glue relations** $g$. Each relation is a destination region $D_g$, a source region $S_g$ and an index map $\pi_g$, meaning

$$z\big(D_g(x)\big)=z\big(S_g(\pi_g(x))\big)\quad\text{for all }x\in\{0,1\}^{f_g}.$$

- **A region** is an aligned sub-cube: some in-block and block bits fixed, $f_g$ bits free.
- **Destination positions** are input rows of their template, exactly as Δ's "both" copies are today.
- **$\pi_g$ is one of:**
  - identity;
  - an index-bit permutation, which covers transposes, reshapes, bit-field splits and the switching networks' stage shuffles;
  - broadcast: the destination has free bits the source lacks.
- **Shift** is optional. V[B]'s builder can place step $j$ of every hash chain or Merkle climb in its own aligned sub-cube, so chains become identity maps between sub-cubes.

**Region claims** with public values, as today (public inputs only).

**An irregular residue**, optional: explicit $(d_i,s_i)$ pairs, meaning $z(d_i)=z(s_i)$. The main user is parsing message fields out of round bytes, about 1 Mbit. It could instead stay inside one template as Δ.

A layout sketch, not a format proposal:

~~~text
META.tables: [{name, template_sha256, k, b, offset}]
META.glue:   [{dst: {table, fixed: {bit: 0|1}, free: [bit]}, src: {...}, map: "id" | {perm: [...]} | {broadcast: [...]}}]
META.pairs:  optional explicit (dst, src) positions
~~~

## 3. What the prover must provide

1. **One commitment for the whole witness.**
   - All tables sit at aligned offsets in one packed witness, under one Ligerito root.
   - Both reps bind it (R1), or the single-run profile does.
2. **Each table's zerocheck and lincheck, as today, on its own sub-cube.**
   - The table's final claims are evaluation claims on the global $\tilde z$, at points whose table-selector bits are fixed.
   - Run the $T$ zerochecks and linchecks in lockstep. Then the round count is the largest table's, not the sum.
3. **One glue sumcheck per rep.** The verifier draws $\gamma_g$ and a point $u$, and the prover proves

$$\sum_g\gamma_g\Big(\tilde z\big(D_g(u)\big)-\tilde z\big(S_g(\pi_g(u))\big)\Big)=0
\;\Longleftrightarrow\;
\sum_{y\in\{0,1\}^m}z(y)\,W(y)=0,$$

$$W(y)=\sum_g\gamma_g\Big(\widetilde{\mathrm{eq}}\big(D_g(u),y\big)-\widetilde{\mathrm{eq}}\big(S_g(\pi_g(u)),y\big)\Big).$$

   - It is degree 2 over $m$ variables, with Flock's skip treatment of the low bits as in the lincheck. It ends in one claim $\tilde z(\rho)$.
   - $W$ is supported only on glued positions, so the prover's work is $O(\#\text{glue wires}\cdot m)$, not $O(2^m)$.
   - Soundness error: $1/|F|$ from the $\gamma_g$, plus $(f_{\max}+1)/|F|$ from $u$, plus $2m/|F|$ from the sumcheck.
4. **One opening for everything.** The table claims ($2T$), the glue claim and the region claims go through ring switching and Ligerito as today. $N$ stays small ($T\approx5\text{–}8$ for V[B]).
5. **Zero-knowledge readiness.**
   - Each table keeps its mask slot.
   - The glue sumcheck's messages are masked in M1 like the lincheck's.
   - Glue values never become public words.

**An alternative.** Put the glue into the matrix, as Δ across tables, and run the lincheck over all column variables. The verifier then evaluates $\widetilde A,\widetilde B$ at a full point structurally. It needs no extra sumcheck, but it changes the lincheck from `I ⊗ A_0` into the paper's general form. I'd rather keep your linchecks and add the glue sumcheck. Your call.

## 4. What the verifier computes per proof (this must stay small)

- **Per table:** the template fold at the point, $O(\mathrm{nnz}(A_t)+2^{k_t})$ with today's code, times $\widetilde{\mathrm{eq}}$ of the block bits.
- **Glue:** $\widetilde W(\rho)$ in $O(\#\text{relations}\cdot m)$, plus $O(\#\text{pairs}\cdot m)$ for any residue.
- **Regions:** as today.

For RoPE's V[B] that is about five templates totalling 1.5–2 M nonzeros, about 2,000 relations and $m\approx31\text{–}32$: a few million field operations per proof. The verifier lane (PR #85) needs the same in PROTOCOL.md and in Lean.

## 5. Sizes to plan for (RoPE, from §I.11)

| item | size |
|---|---|
| V[B] | 1.4–1.7 G ANDs |
| SHA-512 table | about 30k compressions: 2^15 blocks of 2^17 bits |
| multiplier table | about 50k products |
| switch columns | up to 2^19 wide |
| whole witness | about 2^31–2^32 bits, $m\le35$, within fast100 |
| glue | about 0.5 Gbit of glued wires, and no public intermediate value |

## 6. Suggested acceptance for your piece

- **A two-table statement** (for example, SHA-512 compressions feeding a table of GF multipliers) proves and verifies with private glue.
- **Negatives:**
  - one glued bit flipped is rejected by the glue sumcheck;
  - a glue descriptor edited after staging is refused by the statement digest;
  - a destination that is not an input row is refused at load.
- **Measurements:** the verifier's time against the number of relations, and the prover's glue overhead against the zerocheck.

I'll generate V[B] in this form once the census fixes S, and I'll mirror whatever descriptor format you settle on.

Separately, thanks for the SHA-512 statement at `631567f7` (records `art:1100e385`). That covers my earlier request for a recorded SHA-512 session. The live hidden-message mode from `note:20260927T0020Z-handoff-from-private-recursion` still stands, at your pace.
