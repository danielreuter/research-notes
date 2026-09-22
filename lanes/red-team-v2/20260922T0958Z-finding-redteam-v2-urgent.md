---
id: r20-proof/red-team-v2/20260922T0958Z-finding-redteam-v2-urgent
campaign: r20-proof
lane: red-team-v2
kind: finding
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/REDTEAM_V2_URGENT.md
---

# REDTEAM_V2 URGENT — accepted forgery against Candidate A (GKR v2) `run-vu`

**Date:** 2026-09-22 ~09:45Z · **Lane:** red-team-v2 · **Pod:** vy-cpu2 · **Verifier:** `verity-gkr run-vu`
(commit on `lane/red-team-v2`, `main`=4ddb170) · run `r20260922-094212-465e`.

## What was accepted

A 2-VU Goldilocks v2 bundle (`fixtures/redteam-v2/gkr/neg/chain_spec_stripped/`) in which **VU0's epilogue reads a
non-final unit's state** (unit 0's outgoing `(s,e,M,z)`), publishing `y16 = cast(unit0 state)` instead of
`cast(unit95 state)`. The real verifier **ACCEPTS** it, under both `--clear` and PCS:

```
chain_spec_stripped (clear): verify=Ok(())
chain_spec_stripped (pcs)  : verify=Ok(())
```

The honest control (same rows, honest `chain.txt`) is the `epilogue_wrong_unit` case, which is **REJECTED**
(`chain: VU 0 epilogue input (column 1) differs from the last unit's value`). The only difference between the two
bundles is the `chain.txt` file.

## Root cause — the verifier trusts the proof bundle's `chain.txt`

`backends/gkr/src/main.rs::load_vu` builds the chain linkage from the **bundle-supplied** `chain.txt`:

```
let limbs: Vec<Link> = if let Some(text) = files.chain.as_ref().and_then(|p| std::fs::read_to_string(p).ok()) {
    read_chain(&text, &unit.circ, &epi.circ)   // <-- state/ovf/sgn links come from the untrusted dir
} else { ... default word links ... };
let chain = Chain { steps, limbs, epi_y16: ..., public_y16: pcols };
```

Only the **public-word link** (`epi_y16 == public_y16`) is hardcoded in `Chain`. The four state links
`(s,e,M,z)`, the two `ovf` links and the two `sgn` links are read from `chain.txt`. A prover who ships an **empty**
`chain.txt` drops every state/ovf/sgn link; the verifier then never checks that the epilogue's input state equals the
last unit's output. The hardcoded word link still passes because we set `public = epi.y16`. `steps` is likewise
derived from the witness header (`n_units / n_pub`), not from a fixed statement.

Net: the arithmetization and sumcheck are sound (every per-row assertion and lookup still holds; see the other cases
below), but the **VU-chain statement is configured by the caller**, so the published word need not be the chain's
final state.

## Severity / scope

- **HIGH as a verifier-API / deployment trust-boundary bug.** It is not a break of the GKR sumcheck or the checker-v2
  arithmetization; it is that `run-vu` accepts caller-supplied linkage and geometry. Any deployment that hands the
  proof bundle (including `chain.txt`) to the verifier as the source of the statement is forgeable.
- The same pattern (`steps` from the header) means the batch geometry is also caller-controlled.

## Proposed fix (owning lane: a-gkr / a-verifier — NOT fixed here)

The verifier must derive the chain spec (state/ovf/sgn links, `steps`, `B`) from the **fixed circuit / statement**,
exactly as it already does for `epi_y16`/`public_y16`, rather than reading `chain.txt` from the proof directory. If a
serialized `chain.txt` must accompany the bundle, absorb it into the Fiat–Shamir transcript **and** assert it equals
the verifier's own expected spec before use. A one-line harness guard (`assert!(!limbs.is_empty() && limbs == expected)`)
would close the demonstrated instance but the principled fix is verifier-owned linkage.

## Reproduce

```
BIN=$CARGO_TARGET_DIR/release/verity-gkr
$BIN run-vu --dir fixtures/redteam-v2/gkr/neg/chain_spec_stripped --clear   # verify=Ok(())
$BIN run-vu --dir fixtures/redteam-v2/gkr/neg/chain_spec_stripped           # verify=Ok(()) (pcs)
```

Regenerate the fixture: `python -m verity_numerical.redteam.v2_forge gkr-chain --out fixtures/redteam-v2/gkr`.

## Related (not a duplicate)

Same *class* as red-team-3's U1/U2 (statement / geometry taken from the proof rather than the verifier's config),
but a **different target and code path**: U1/U2 are B's LogUp realisation (`lookup_stark.rs` / `vu_bench_lookup`);
this is A's GKR `run-vu` chain spec (`gkr/src/main.rs::load_vu`). The B *limbs* path (`vu_bench_v2`,
`verify_bound`) is statement-bound and rejects a `words[0]^=1` statement — verified this run.

## Status (coordinator, 2026-09-22 09:58Z)

**FIXED on `main` ff651a8** (`backends/gkr/src/main.rs`): the checker-v2 chain is now the verifier's own constant
(`v2_chain_spec()`: the four state links from `(0, floor = -132, 0, 1)`, the two saturation flags zero before the
last unit, the two signs -- by column name, identical to `gkr_export.v2.chain_spec`). A bundle's `chain.txt` is
informative only and must agree with it; an empty or shortened file is refused; no file yields the same chain. Test
`v2_chain_is_verifier_owned` covers the no-file / empty-file cases and this fixture. Verified on vy-cpu2 (run
r20260922-095128-05ac): `cargo check` both features, 15/15 tests, `run-vu --dir fixtures/redteam-v2/gkr/neg/chain_spec_stripped`
refused with `chain.txt disagrees with the verifier's checker-v2 chain (PROTOCOL.md 14.3): 0 link(s) given, 8 required`,
`neg/honest` accepted. Still open from this report: `steps` is taken from the witness header (the statement absorbs it,
so a verifier expecting K=1536 must check `steps == 96` itself -- the CLI harness has no such expectation yet).
