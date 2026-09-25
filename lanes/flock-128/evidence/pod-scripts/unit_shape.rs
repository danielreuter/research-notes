//! flock-bench-80gb (verity): Flock prove/verify of the census transition-unit table (verity_unit.rs), alone
//! (`US_MODE=unit`) or in ONE union proof with the BLAKE3 row-leaf table at the same VU count (`US_MODE=mixed`:
//! relation + standard-hash leaves, what a binary backend would prove; glue not modelled).
//!
//! env: US_NET=path.netlist  US_MODE=unit|mixed  US_NS="64 1024 4096"  US_RUNS=3  US_SEED
//! Output: one `RESULT\t{json}` line per point. Timings: eval_s = bit-sliced unit witness evaluation + transpose
//! (outside the prove call); prove_s = Flock union prove (in-place slot assembly + BLAKE3 witness gen + PIOP + PCS).

use std::{
    alloc::{GlobalAlloc, Layout, System},
    array::from_fn,
    env::var,
    hint::black_box,
    sync::atomic::{AtomicUsize, Ordering},
    time::Instant,
};

use flock_core::{
    lincheck::LincheckCircuit,
    pcs::{PcsParams, ligerito::{LigeritoProfile, embedded_initial_k_or_default}},
    test_rng::Rng,
};
use flock_prover::{
    challenger::FsChallenger,
    init_perf_thread_pool,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    prover::{UnionSlotProverInput, prove_fast_ligerito_union},
    r1cs_hashes::{
        blake3::{Compression, build_block_r1cs as build_blake3_r1cs, generate_witness_batch_major_partial_into,
                 min_n_blocks_log},
        verity_unit::{Netlist, transpose64_selftest},
    },
    schedule::{Registry, TableType},
    union::UnionInstance,
    verifier::verify_ligerito_union,
};

struct PeakAlloc;
static CUR: AtomicUsize = AtomicUsize::new(0);
static PEAK: AtomicUsize = AtomicUsize::new(0);
unsafe impl GlobalAlloc for PeakAlloc {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 {
        let p = unsafe { System.alloc(l) };
        if !p.is_null() {
            let c = CUR.fetch_add(l.size(), Ordering::Relaxed) + l.size();
            PEAK.fetch_max(c, Ordering::Relaxed);
        }
        p
    }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
        unsafe { System.dealloc(p, l) };
        CUR.fetch_sub(l.size(), Ordering::Relaxed);
    }
    unsafe fn realloc(&self, p: *mut u8, l: Layout, new: usize) -> *mut u8 {
        let q = unsafe { System.realloc(p, l, new) };
        if !q.is_null() {
            if new >= l.size() {
                let c = CUR.fetch_add(new - l.size(), Ordering::Relaxed) + (new - l.size());
                PEAK.fetch_max(c, Ordering::Relaxed);
            } else {
                CUR.fetch_sub(l.size() - new, Ordering::Relaxed);
            }
        }
        q
    }
}
#[global_allocator]
static ALLOC: PeakAlloc = PeakAlloc;
fn mib(x: usize) -> f64 {
    x as f64 / 1048576.0
}

fn pcs_params(union: &UnionInstance<'_>) -> PcsParams {
    let m = union.dense_m();
    let batch = embedded_initial_k_or_default(m, LigeritoProfile::Fast);
    PcsParams {
        m,
        log_inv_rate: 1,
        log_batch_size: batch,
        profile: LigeritoProfile::Fast,
        num_lanes: union.commit_lanes(batch),
        merkle_hash: Default::default(),
    }
}

fn main() {
    let _ = init_perf_thread_pool();
    transpose64_selftest();
    let path = var("US_NET").expect("US_NET");
    let mode = var("US_MODE").unwrap_or_else(|_| "unit".into());
    let runs: usize = var("US_RUNS").ok().and_then(|s| s.parse().ok()).unwrap_or(3);
    let seed: u64 = var("US_SEED").ok().and_then(|s| s.parse().ok()).unwrap_or(0x5EED_80);
    let ns: Vec<usize> = var("US_NS")
        .unwrap_or_else(|_| "64 1024 4096".into())
        .split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(|t| t.parse().unwrap())
        .collect();
    let threads = rayon::current_num_threads();
    let t = Instant::now();
    let net = Netlist::load(&path);
    let (vok, vt, nrej, nt) = net.check_tests();
    eprintln!(
        "netlist {} useful={} n_in={} n_and={} nnz={} load {:.2}s; tests valid {vok}/{vt} negatives rejected {nrej}/{nt}",
        net.name, net.useful, net.n_in, net.n_and, net.nnz(), t.elapsed().as_secs_f64()
    );
    assert!(vok == vt && nrej == nt, "bit-exact test vectors failed");
    let upv = 1536 / net.terms;
    let comp_per_vu = 1536 * net.op_bits / 8 * 2 / 64;
    for &n in &ns {
        let n_units = n * upv;
        let n_comp = if mode == "mixed" { n * comp_per_vu } else { 0 };
        let t_setup = Instant::now();
        let nu = min_n_blocks_log(n_units.max(n_comp));
        let unit_r1cs = net.block_r1cs(nu);
        let b3_r1cs = build_blake3_r1cs(if mode == "mixed" { nu } else { 3 });
        let mut types = vec![TableType::from_block_r1cs(&unit_r1cs)];
        if mode == "mixed" {
            types.push(TableType::from_block_r1cs(&b3_r1cs));
        }
        let registry = Registry::new(types, nu);
        let _ = registry.digest();
        // slot order = registry order (capacity area descending): identify by k_log
        let order: Vec<&str> = registry.types().iter().map(|t| if t.k_log == net.k_log { "unit" } else { "blake3" }).collect();
        let counts: Vec<usize> = order.iter().map(|&o| if o == "unit" { n_units } else { n_comp }).collect();
        let unit_circ = unit_r1cs.csc_lincheck_circuit();
        let b3_circ: &dyn LincheckCircuit = if mode == "mixed" { b3_r1cs.csc_lincheck_circuit() } else { unit_circ };
        let circs: Vec<&dyn LincheckCircuit> = order.iter().map(|&o| if o == "unit" { unit_circ as &dyn LincheckCircuit } else { b3_circ as &dyn LincheckCircuit }).collect();
        let union = UnionInstance::new(&registry, counts.clone());
        let pcs = pcs_params(&union);
        flock_core::scratch::prewarm_prover(registry.m_total());
        let setup_s = t_setup.elapsed().as_secs_f64();

        let t_eval = Instant::now();
        let wit = net.gen_witness(n, upv, seed ^ n as u64);
        let eval_s = t_eval.elapsed().as_secs_f64();
        let mut rng = Rng::new(0xB3 ^ n as u64);
        let blocks: Vec<Compression> = (0..n_comp)
            .map(|_| {
                let cv: [u32; 8] = from_fn(|_| rng.next_u32());
                let m: [u32; 16] = from_fn(|_| rng.next_u32());
                (cv, m, rng.next_u32() as u64, 64u32, 16u32 | (rng.next_u32() & 3))
            })
            .collect();
        eprintln!("N={n} mode={mode} nu={nu} M={} dense_m={} order={order:?} counts={counts:?} setup {setup_s:.2}s eval {eval_s:.3}s", registry.m_total(), pcs.m);

        let fs = || FsChallenger::with_hash(b"flock-bench-80gb-v0", HashKind::default());
        let prove = || {
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
            prove_fast_ligerito_union(&union, &pcs, slots, &mut fs())
        };
        black_box(prove());
        let mut ts = Vec::new();
        for _ in 0..runs {
            let t0 = Instant::now();
            let p = prove();
            ts.push(t0.elapsed().as_secs_f64());
            black_box(&p);
        }
        PEAK.store(CUR.load(Ordering::Relaxed), Ordering::Relaxed);
        let base = CUR.load(Ordering::Relaxed);
        let (proof, commitment, claim) = prove();
        let peak = PEAK.load(Ordering::Relaxed) - base;
        let t = Instant::now();
        let claim_v = verify_ligerito_union(&union, &circs, &commitment, &proof, &pcs, &mut fs()).expect("verify failed");
        let verify_s = t.elapsed().as_secs_f64();
        assert_eq!(claim_v, claim);
        let size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
        let best = ts.iter().cloned().fold(f64::INFINITY, f64::min);
        let slot_bits = (n_units << net.k_log) + (n_comp << 14);
        let tss: Vec<String> = ts.iter().map(|t| format!("{t:.4}")).collect();
        println!(
            "RESULT\t{{\"pipeline\":\"{}\",\"mode\":\"{mode}\",\"n_vu\":{n},\"n_units\":{n_units},\"n_comp\":{n_comp},\"nu\":{nu},\
             \"m_total\":{},\"dense_m\":{},\"threads\":{threads},\"eval_s\":{eval_s:.4},\"prove_best_s\":{best:.4},\
             \"prove_runs_s\":[{}],\"verify_s\":{verify_s:.4},\"proof_bytes\":{size},\"peak_heap_mib\":{:.1},\
             \"peak_heap_abs_mib\":{:.1},\"witness_rows_mib\":{:.1},\"slot_bits\":{slot_bits},\"slot_bits_per_s\":{:.4e}}}",
            net.name,
            registry.m_total(),
            pcs.m,
            tss.join(","),
            mib(peak),
            mib(PEAK.load(Ordering::Relaxed)),
            mib(wit.z.len() * 8 * 3),
            slot_bits as f64 / best
        );
    }
}
