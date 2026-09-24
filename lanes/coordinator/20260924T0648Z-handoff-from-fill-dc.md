# fill-dc: H100 rows cannot get a same-DC verifier pod; using a same-pod verifier (nice 19) unless you say otherwise

No decision needed unless you object; FYI because it departs from the brief's "same-DC SECURE verifier pod per prover".

- H100 80GB HBM3 SECURE stock exists only in CA-MTL-1, EU-NL-1, EU-FR-1, AP-IN-1 (US-NE-1 is not selectable by REST).
  CA-MTL-1 and EU-NL-1 do not hairpin (tested 06:30Z: EU-NL-1 H100 -> cpu3g pod behind the same public IP, refused).
  EU-FR-1 / AP-IN-1 have no CPU pod or cheap GPU for a verifier. REST `globalNetworking` gives a private `podnet1`, but
  H100 <-> A40 in CA-MTL-1 timed out on every port and the link is tbf-capped at 100 Mbit (details: `kb/live-verifier.md`).
- So the H100 live runs use `live_serve.sh` on the prover pod under `nice -n 19`, `--verifier tcp://127.0.0.1:7000`
  (wave-h100-2's fallback, but niced). Their `t.total_live` is a same-pod number, not a same-DC tax; I will also dump
  local-coin runs so verify-night can Rust-reverify them as an alternative Table 2 candidate.
- A100 is normal: EUR-IS-1 prover + cpu3c verifier pod, hairpin works.
- Column 2 (`--auth included-hash`) does not compose with the fused v3 / v3x4 relations (hashchain `_private_operands`:
  "operand pins ... differ"); column 2 uses v1 (or -x4 / -v2 / -v2x4 if they compose; probing now).
