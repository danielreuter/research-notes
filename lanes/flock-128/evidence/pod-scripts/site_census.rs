//! flock-128: census of every challenge site in one Flock union proof (census unit + BLAKE3 row leaves, the
//! flock-bench-80gb `unit_shape` mixed statement). A logging wrapper around `FsChallenger` records each squeeze
//! (scalar, vector of n, F256, PoW bits) with the first flock-core / flock-prover frame of its call stack, so the
//! soundness ledger is built from what the prover actually samples, not from docs. The proof made through the
//! wrapper is verified with a plain `FsChallenger`: the wrapper must not change the transcript.
//!
//! env: US_NET=path.netlist  US_NS=4096  PROFILE=fast|fast100|secure
//! Output: `SITE\t<kind>\t<calls>\t<elements>\t<pow bits list>\t<frame>` lines, then `RESULT\t{json}`.

use std::{
    array::from_fn,
    backtrace::Backtrace,
    collections::BTreeMap,
    env::var,
    sync::{Arc, Mutex},
    time::Instant,
};

use flock_core::{
    challenger::Challenger,
    lincheck::LincheckCircuit,
    pcs::{PcsParams, ligerito::{LigeritoProfile, embedded_initial_k_or_default}},
    test_rng::Rng,
};
use flock_field::{F128, F256};
use flock_prover::{
    challenger::FsChallenger,
    init_perf_thread_pool,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    prover::{UnionSlotProverInput, prove_fast_ligerito_union},
    r1cs_hashes::{
        blake3::{Compression, build_block_r1cs as build_blake3_r1cs, generate_witness_batch_major_partial_into,
                 min_n_blocks_log},
        verity_unit::Netlist,
    },
    schedule::{Registry, TableType},
    union::UnionInstance,
    verifier::verify_ligerito_union,
};

type Log = Arc<Mutex<Vec<(String, usize, u32, String)>>>;

fn frame() -> String {
    let bt = Backtrace::force_capture().to_string();
    let lines: Vec<&str> = bt.lines().collect();
    let mut fn_name = String::new();
    let mut picked = Vec::new();
    for l in &lines {
        let t = l.trim();
        if t.starts_with("at ") {
            if (t.contains("flock-core/src") || t.contains("flock-prover/src"))
                && !t.contains("challenger.rs")
                && !t.contains("transcript_record.rs")
            {
                let loc = t.trim_start_matches("at ").rsplit("crates/").next().unwrap_or(t).to_string();
                picked.push(format!("{loc} {fn_name}"));
                if picked.len() == 2 {
                    break;
                }
            }
        } else if let Some((_, f)) = t.split_once(": ") {
            fn_name = f.rsplit("::").take(2).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("::");
        }
    }
    if picked.is_empty() { "?".into() } else { picked.join(" <- ") }
}

struct LogCh {
    inner: FsChallenger,
    log: Log,
}
impl LogCh {
    fn rec(&self, kind: &str, n: usize, bits: u32) {
        self.log.lock().unwrap().push((kind.into(), n, bits, frame()));
    }
}
impl Challenger for LogCh {
    fn supports_fused_pow_squeeze(&self) -> bool { self.inner.supports_fused_pow_squeeze() }
    fn observe_label(&mut self, l: &[u8]) { self.inner.observe_label(l) }
    fn observe_f128(&mut self, v: F128) { self.inner.observe_f128(v) }
    fn observe_f128_slice(&mut self, v: &[F128]) { self.inner.observe_f128_slice(v) }
    fn observe_f256(&mut self, v: F256) { self.inner.observe_f256(v) }
    fn observe_bytes(&mut self, b: &[u8]) { self.inner.observe_bytes(b) }
    fn sample_f128(&mut self) -> F128 { self.rec("f128", 1, 0); self.inner.sample_f128() }
    fn sample_f128_vec(&mut self, n: usize) -> Vec<F128> { self.rec("f128vec", n, 0); self.inner.sample_f128_vec(n) }
    fn sample_f256(&mut self) -> F256 { self.rec("f256", 1, 0); self.inner.sample_f256() }
    fn grind_pow(&mut self, bits: u32) -> u64 { self.rec("pow", 0, bits); self.inner.grind_pow(bits) }
    fn verify_pow(&mut self, nonce: u64, bits: u32) -> bool { self.inner.verify_pow(nonce, bits) }
    fn grind_pow_and_sample_f128(&mut self, bits: u32) -> (u64, F128) {
        self.rec("pow+f128", 1, bits); self.inner.grind_pow_and_sample_f128(bits)
    }
    fn verify_pow_and_sample_f128(&mut self, nonce: u64, bits: u32) -> Option<F128> {
        self.inner.verify_pow_and_sample_f128(nonce, bits)
    }
    fn grind_pow_and_sample_f128_vec(&mut self, bits: u32, n: usize) -> (u64, Vec<F128>) {
        self.rec("pow+f128vec", n, bits); self.inner.grind_pow_and_sample_f128_vec(bits, n)
    }
    fn verify_pow_and_sample_f128_vec(&mut self, nonce: u64, bits: u32, n: usize) -> Option<Vec<F128>> {
        self.inner.verify_pow_and_sample_f128_vec(nonce, bits, n)
    }
    fn fork_from_seed(&self, seed: [F128; 2], label: &'static [u8]) -> Self {
        self.rec("fork", 0, 0);
        LogCh { inner: self.inner.fork_from_seed(seed, label), log: self.log.clone() }
    }
    fn fork(&mut self, label: &'static [u8]) -> Self {
        let seed = [self.inner.sample_f128(), self.inner.sample_f128()];
        self.rec("fork-seed", 2, 0);
        LogCh { inner: self.inner.fork_from_seed(seed, label), log: self.log.clone() }
    }
    fn merge_child(&mut self, child: Self) { self.inner.merge_child(child.inner) }
    fn hash_kind(&self) -> HashKind { self.inner.hash_kind() }
}

fn main() {
    let _ = init_perf_thread_pool();
    let path = var("US_NET").expect("US_NET");
    let n: usize = var("US_NS").ok().and_then(|s| s.parse().ok()).unwrap_or(4096);
    let profile = match var("PROFILE").unwrap_or_else(|_| "fast".into()).as_str() {
        "fast100" => LigeritoProfile::Fast100,
        "secure" => LigeritoProfile::Secure,
        _ => LigeritoProfile::Fast,
    };
    let net = Netlist::load(&path);
    let upv = 1536 / net.terms;
    let comp_per_vu = 1536 * net.op_bits / 8 * 2 / 64;
    let n_units = n * upv;
    let n_comp = n * comp_per_vu;
    let nu = min_n_blocks_log(n_units.max(n_comp));
    let unit_r1cs = net.block_r1cs(nu);
    let b3_r1cs = build_blake3_r1cs(nu);
    let registry = Registry::new(vec![TableType::from_block_r1cs(&unit_r1cs), TableType::from_block_r1cs(&b3_r1cs)], nu);
    let order: Vec<&str> = registry.types().iter().map(|t| if t.k_log == net.k_log { "unit" } else { "blake3" }).collect();
    let counts: Vec<usize> = order.iter().map(|&o| if o == "unit" { n_units } else { n_comp }).collect();
    let unit_circ = unit_r1cs.csc_lincheck_circuit();
    let b3_circ: &dyn LincheckCircuit = b3_r1cs.csc_lincheck_circuit();
    let circs: Vec<&dyn LincheckCircuit> =
        order.iter().map(|&o| if o == "unit" { unit_circ as &dyn LincheckCircuit } else { b3_circ }).collect();
    let union = UnionInstance::new(&registry, counts.clone());
    let m = union.dense_m();
    let batch = embedded_initial_k_or_default(m, profile);
    let pcs = PcsParams {
        m,
        log_inv_rate: profile.log_inv_rate(),
        log_batch_size: batch,
        profile,
        num_lanes: union.commit_lanes(batch),
        merkle_hash: Default::default(),
    };
    let wit = net.gen_witness(n, upv, 7 ^ n as u64);
    let mut rng = Rng::new(0xB3 ^ n as u64);
    let blocks: Vec<Compression> = (0..n_comp)
        .map(|_| {
            let cv: [u32; 8] = from_fn(|_| rng.next_u32());
            let mm: [u32; 16] = from_fn(|_| rng.next_u32());
            (cv, mm, rng.next_u32() as u64, 64u32, 16u32 | (rng.next_u32() & 3))
        })
        .collect();
    let slots: Vec<UnionSlotProverInput<'_>> = order
        .iter()
        .map(|&o| {
            if o == "unit" {
                UnionSlotProverInput::in_place(|dst| net.witness_into(&wit, nu, dst), unit_circ)
            } else {
                UnionSlotProverInput::in_place(|dst| generate_witness_batch_major_partial_into(&blocks, nu, dst), b3_circ)
            }
        })
        .collect();
    let log: Log = Arc::new(Mutex::new(Vec::new()));
    let dom = b"flock-128-site-census-v0";
    let mut ch = LogCh { inner: FsChallenger::with_hash(dom, HashKind::default()), log: log.clone() };
    let t = Instant::now();
    let (proof, commitment, claim) = prove_fast_ligerito_union(&union, &pcs, slots, &mut ch);
    let prove_s = t.elapsed().as_secs_f64();
    let mut fs = FsChallenger::with_hash(dom, HashKind::default());
    let claim_v = verify_ligerito_union(&union, &circs, &commitment, &proof, &pcs, &mut fs).expect("verify failed");
    assert_eq!(claim_v, claim);
    let size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
    let log = log.lock().unwrap();
    let mut agg: BTreeMap<(String, String), (usize, usize, Vec<u32>)> = BTreeMap::new();
    let mut first: BTreeMap<(String, String), usize> = BTreeMap::new();
    for (i, (kind, k, bits, fr)) in log.iter().enumerate() {
        let key = (fr.clone(), kind.clone());
        first.entry(key.clone()).or_insert(i);
        let e = agg.entry(key).or_insert((0, 0, Vec::new()));
        e.0 += 1;
        e.1 += *k;
        if kind.starts_with("pow") { e.2.push(*bits); }
    }
    let mut rows: Vec<_> = agg.into_iter().collect();
    rows.sort_by_key(|(k, _)| first[k]);
    for ((fr, kind), (calls, elems, bits)) in rows {
        let mut b = bits.clone();
        b.sort();
        b.dedup();
        println!("SITE\t{kind}\t{calls}\t{elems}\t{b:?}\t{fr}");
    }
    println!(
        "RESULT\t{{\"pipeline\":\"{}\",\"n_vu\":{n},\"m\":{m},\"nu\":{nu},\"profile\":\"{}\",\"squeezes\":{},\"prove_s\":{prove_s:.3},\"proof_bytes\":{size}}}",
        net.name, profile.as_str(), log.len()
    );
}
