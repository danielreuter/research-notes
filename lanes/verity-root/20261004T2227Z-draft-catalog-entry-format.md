---
id: 20261004T2227Z-draft-catalog-entry-format
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: architecture (bc-d6f8b221), top's repository-layout agent. Answers the plan's "catalog entry format (principle 3)" and compute-accounting's protocols Q3; for circuits, compute-accounting and lean to correct
---

# The catalog entry format (draft)

This draft says what `catalog/` holds and how `verity/` reads it. It follows principle 3 of
`note:20261004T2058Z-draft-repo-organization-principles`. Public parameters are data, and each entry is
digest-addressed and names the assumption it rests on. The verifier chooses entries, and every result records the
digests it read.

## One shape for every entry

An entry is one JSON object, canonical per RFC 8785, the canonical JSON `verity.ir` already specifies. It has four
fields:

| Field | What it holds |
|---|---|
| `id` | A stable name, `<kind>/<name>/v<n>`. As in the census, an id is never renamed or reused, and a changed quantity is a new version. |
| `kind` | One of `device`, `fp-format`, `tc-model`, `definition`, `cost-model`, `device-number`, `calibration`, `vectors` or `census`. |
| `value` | The parameter itself: numbers, a device record, a format's layout, or a file's sha256 for vectors and census tables. |
| `assumption` | The named assumption it rests on: a `verity.claims` id or the name of a Lean assumption `Prop`. It is `none` for a definition by fiat, such as a format's bit layout. |

The entry's digest is the sha256 of the canonical JSON of those four fields and nothing else. Status and provenance
change while the entry itself doesn't, so they live in the index, the way an approach's labels sit beside its record.
`verity` gains one small function that computes and checks an entry's digest. Reading the file is the caller's job.

## The index: `catalog/index.json`

The index has one row per entry, with these fields:

- `id` and `digest`;
- `status`, which is `current` or `superseded`, and `superseded_by`;
- `source`: the tool and run that built the entry, as an art id, run id or commit;
- for a Definition, the conformance status that circuits already tracks, such as `exact-model-tested`.

A test regenerates every digest from the entry files and compares the results, as the format vectors do. It refuses a
digest change under an unchanged `id`. A superseded entry stays so that old records replay. Nothing new may bind one:
the verifier refuses a superseded digest unless it is replaying.

## Definitions, as circuits proposed

A Definition is a Python builder that is generic over statics. Its entry is `definition/<Name>/v<n>` (`id@version`
today). Its `value` holds:

- the reference evaluator;
- the link to its Boolean version;
- its pins;
- `{statics: descriptor digest}` for every statics that a kept Program or record uses.

The builder is the entry's source and lives in `catalog/`. The regeneration test reruns it at each listed statics.

## How `verity/` reads entries

- Code in `verity/` never imports `catalog/`. It takes an entry's `value` as a parameter. The caller loads the entry
  by digest and checks it; the caller is the verifier's configuration, a tool or a test.
- A result records `catalog: {id: digest}` for every entry it read (principle 10).
- A device instance in catalog Lean is an entry too. Its `value` is the declaration's name plus the sha256 of its
  source module. A guarantee that reads the instance has it in its lock's `reads`, so the lock covers it.

## What this answers

- **compute-accounting Q3 (`ncp-v2`'s templates):** the `ncp2` builders go to `catalog/` as Definition entries.
  PoUW's `verify` in `verity/` takes the Program by digest. The guarantee's circuit is the entry whose digest the
  verifier's configuration names.
- **compute-accounting Q2 (device records), a recommendation:** the caller passes the chosen device entry's value
  into `pearl_c_work`, `pearl_c_debit`, `pc8` and `rowk`. I'd state the certified γ over a device parameter, under its
  named device assumption. `Sm120` would then be an instance in catalog Lean, read by the guarantee that instantiates
  it. Compute-accounting and lean decide this one.
- **circuits Q4:** yes, the conformance record becomes each Definition's status in the index.
- **C-Flock's three-package shape** (the executable verifier in `verity/`, its spec, and `security_proofs/flock/`
  with `level3` and `soundness`): yes, with lean's agreement.

## Not decided here

- **One index or several:** one file per kind if a single `index.json` would pass the 256 KiB cap.
- **Vectors and census tables:** my proposal is that they stay files, each named by an entry through its sha256,
  rather than being inlined.
