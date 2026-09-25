//! red-team-flock: does the flock-128-r2 "two sequential runs" verifier tie its two reps to ONE committed witness?
//! Drop into flock b684b12 as crates/flock-prover/examples/rtf_unlinked_reps.rs and run
//! `cargo run --release -p flock-prover --example rtf_unlinked_reps`.
//!
//! Same prove/verify calls as flock-128's unit_shape128.rs (prove_fast_ligerito_union / verify_ligerito_union,
//! FsChallenger per-rep domain "flock-128/fast100x2/rep{r}", PcsParams fixed by the verifier), BLAKE3 table only.
//! Output: one `RTF\t{json}` line per case.

use std::array::from_fn;

use flock_core::{
    pcs::{PcsParams, ligerito::{LigeritoProfile, embedded_initial_k_or_default}},
    test_rng::Rng,
};
use flock_prover::{
    challenger::FsChallenger,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    prover::{UnionSlotProverInput, prove_fast_ligerito_union},
    r1cs_hashes::blake3::{Compression, build_block_r1cs, generate_witness_batch_major_partial_into, min_n_blocks_log},
    schedule::{Registry, TableType},
    union::UnionInstance,
    verifier::verify_ligerito_union,
};

fn blocks(seed: u64, n: usize) -> Vec<Compression> {
    let mut rng = Rng::new(seed);
    (0..n)
        .map(|_| {
            let cv: [u32; 8] = from_fn(|_| rng.next_u32());
            let m: [u32; 16] = from_fn(|_| rng.next_u32());
            (cv, m, rng.next_u32() as u64, 64u32, 16u32 | (rng.next_u32() & 3))
        })
        .collect()
}

fn main() {
    let n: usize = std::env::var("RTF_N").ok().and_then(|s| s.parse().ok()).unwrap_or(4096);
    let nu = min_n_blocks_log(n);
    let r1cs = build_block_r1cs(nu);
    let registry = Registry::new(vec![TableType::from_block_r1cs(&r1cs)], nu);
    let union = UnionInstance::new(&registry, vec![n]);
    let circ = r1cs.csc_lincheck_circuit();
    let circs: Vec<&dyn flock_core::lincheck::LincheckCircuit> = vec![circ];
    let params = |lig: LigeritoProfile| {
        let m = union.dense_m();
        let batch = embedded_initial_k_or_default(m, lig);
        PcsParams {
            m,
            log_inv_rate: lig.log_inv_rate(),
            log_batch_size: batch,
            profile: lig,
            num_lanes: union.commit_lanes(batch),
            merkle_hash: Default::default(),
        }
    };
    let p100 = params(LigeritoProfile::Fast100);
    let pfast = params(LigeritoProfile::Fast);
    let dom = |r: usize| format!("flock-128/fast100x2/rep{r}").into_bytes();
    let prove = |bl: &[Compression], pcs: &PcsParams, d: &[u8]| -> R1csProofBundleLigerito {
        let slots = vec![UnionSlotProverInput::in_place(|dst| generate_witness_batch_major_partial_into(bl, nu, dst), circ)];
        let (proof, commitment, _) =
            prove_fast_ligerito_union(&union, pcs, slots, &mut FsChallenger::with_hash(d, HashKind::default()));
        R1csProofBundleLigerito { commitment, proof }
    };
    let verify = |b: &R1csProofBundleLigerito, pcs: &PcsParams, d: &[u8]| -> Result<(), String> {
        let b = R1csProofBundleLigerito::from_bytes(&b.to_bytes()).map_err(|e| format!("decode {e:?}"))?;
        std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            verify_ligerito_union(&union, &circs, &b.commitment, &b.proof, pcs, &mut FsChallenger::with_hash(d, HashKind::default()))
        }))
        .map_err(|_| "panic".to_string())?
        .map(|_| ())
        .map_err(|e| format!("{e:?}").chars().take(120).collect())
    };
    // flock-128-r2 acceptance as implemented: every rep verifies under its own domain, nothing across reps.
    let r2_accepts = |r0: &R1csProofBundleLigerito, r1: &R1csProofBundleLigerito| {
        verify(r0, &p100, &dom(0)).is_ok() && verify(r1, &p100, &dom(1)).is_ok()
    };
    let same_root = |r0: &R1csProofBundleLigerito, r1: &R1csProofBundleLigerito| r0.commitment.cap == r1.commitment.cap;
    let out = |case: &str, v: String| println!("RTF\t{{\"case\":\"{case}\",\"n\":{n},\"dense_m\":{},{v}}}", union.dense_m());

    let wa = blocks(0xA, n);
    let wb = blocks(0xB, n);
    let a0 = prove(&wa, &p100, &dom(0));
    let a1 = prove(&wa, &p100, &dom(1));
    let b1 = prove(&wb, &p100, &dom(1));

    out("honest_pair_same_witness", format!(
        "\"r2_accepts\":{},\"same_root\":{}", r2_accepts(&a0, &a1), same_root(&a0, &a1)));
    out("unlinked_pair_rep1_other_witness", format!(
        "\"r2_accepts\":{},\"same_root\":{}", r2_accepts(&a0, &b1), same_root(&a0, &b1)));
    let f0 = prove(&wa, &pfast, &dom(0));
    out("fast_proof_under_fast100_verifier", format!(
        "\"accepted\":{},\"why\":\"{}\"", verify(&f0, &p100, &dom(0)).is_ok(),
        verify(&f0, &p100, &dom(0)).err().unwrap_or_default().replace('"', "'")));
    let mut forged = a0.clone();
    forged.commitment.params = p100.clone();
    forged.commitment.params.profile = LigeritoProfile::Fast;
    out("fast100_proof_relabelled_fast_params", format!(
        "\"accepted\":{}", verify(&forged, &p100, &dom(0)).is_ok()));
    out("fast100_proof_under_fast_verifier", format!(
        "\"accepted\":{}", verify(&a0, &pfast, &dom(0)).is_ok()));
    out("rep0_replayed_as_rep1", format!("\"accepted\":{}", verify(&a0, &p100, &dom(1)).is_ok()));
}
