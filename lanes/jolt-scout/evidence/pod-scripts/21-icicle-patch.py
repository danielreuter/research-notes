#!/usr/bin/env python3
"""jolt-scout: local build fix for a16z/jolt 4c259be477 `--features icicle` (upstream does not compile: the KZG SRS derives
ark CanonicalSerialize/Deserialize over `gpu_g1: Option<Vec<icicle Affine>>`, which has no ark impls). Replace the derive
with hand-written impls that serialize the three ark vectors and deserialize `gpu_g1 = None` (the MSM path rebuilds GPU
bases on demand: msm/mod.rs `gpu_bases.unwrap_or_else(|| get_gpu_bases(bases))`). Prover-side only; no proof-format change."""
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "jolt-core/src/poly/commitment/kzg.rs"
s = p.read_text()
old = "#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]\npub struct SRS<P: Pairing>"
assert old in s, "derive not found"
s = s.replace(old, "#[derive(Clone, Debug)]\npub struct SRS<P: Pairing>")
s = s.replace("use ark_serialize::{CanonicalDeserialize, CanonicalSerialize};",
              "use ark_serialize::{CanonicalDeserialize, CanonicalSerialize, Compress, SerializationError, Valid, Validate};")
s += '''
impl<P: Pairing> CanonicalSerialize for SRS<P>
where
    P::G1: Icicle,
{
    fn serialize_with_mode<W: std::io::Write>(&self, mut w: W, c: Compress) -> Result<(), SerializationError> {
        self.g1_powers.serialize_with_mode(&mut w, c)?;
        self.g2_powers.serialize_with_mode(&mut w, c)?;
        self.g_products.serialize_with_mode(&mut w, c)
    }
    fn serialized_size(&self, c: Compress) -> usize {
        self.g1_powers.serialized_size(c) + self.g2_powers.serialized_size(c) + self.g_products.serialized_size(c)
    }
}
impl<P: Pairing> Valid for SRS<P>
where
    P::G1: Icicle,
{
    fn check(&self) -> Result<(), SerializationError> {
        self.g1_powers.check()?;
        self.g2_powers.check()?;
        self.g_products.check()
    }
}
impl<P: Pairing> CanonicalDeserialize for SRS<P>
where
    P::G1: Icicle,
{
    fn deserialize_with_mode<R: std::io::Read>(mut r: R, c: Compress, v: Validate) -> Result<Self, SerializationError> {
        Ok(Self {
            g1_powers: Vec::deserialize_with_mode(&mut r, c, v)?,
            g2_powers: Vec::deserialize_with_mode(&mut r, c, v)?,
            g_products: Vec::deserialize_with_mode(&mut r, c, v)?,
            gpu_g1: None,
        })
    }
}
'''
p.write_text(s)
print("patched", p)
