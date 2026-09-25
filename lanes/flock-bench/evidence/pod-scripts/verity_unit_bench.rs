//! flock-bench (verity): Flock prove/verify of the binary-census transition unit at our batch
//! shape (VU_UPV units per VU: 96 Ampere BF16, 48 FP8). The chain glue between a VU's units, the
//! relation-hash region equality and the public endpoints are NOT modelled (independent units).
//!
//! env: VU_NETLIST=path VU_NAME=ampere_bf16 VU_UPV=96 VU_NS="64 1024 4096" VU_RUNS=3
//! Output: one `RESULT\t{json}` line per point.

use std::{
    alloc::{GlobalAlloc, Layout, System},
    env::var,
    hint::black_box,
    sync::atomic::{AtomicUsize, Ordering},
    time::Instant,
};

use flock_prover::{
    challenger::FsChallenger,
    init_perf_thread_pool,
    merkle::HashKind,
    proof_io::R1csProofBundleLigerito,
    r1cs_hashes::verity_unit::{Netlist, VerityUnitSetup},
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

fn main() {
    let _ = init_perf_thread_pool();
    let path = var("VU_NETLIST").expect("VU_NETLIST");
    let name = var("VU_NAME").unwrap_or_else(|_| "unit".into());
    let upv: usize = var("VU_UPV").ok().and_then(|s| s.parse().ok()).unwrap_or(96);
    let runs: usize = var("VU_RUNS").ok().and_then(|s| s.parse().ok()).unwrap_or(3);
    let ns: Vec<usize> = var("VU_NS")
        .unwrap_or_else(|_| "64 1024 4096".into())
        .split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(|t| t.parse().unwrap())
        .collect();
    let tamper = var("VU_TAMPER").map(|s| s == "1").unwrap_or(false);
    let threads = rayon::current_num_threads();
    for &n in &ns {
        let mut net = Netlist::load(&path);
        let (useful, nnz, nv) = (net.useful, net.nnz(), net.vectors.len());
        let bad = net.self_check();
        assert_eq!(bad, 0, "netlist self-check failed on {bad} vectors");
        let n_units = n * upv;
        let mut ids: Vec<u32> = (0..n_units as u32).map(|i| i % nv as u32).collect();
        if tamper {
            // operand x[0] exponent all ones (NaN/inf): its finiteness assertion row is violated
            let mut v = net.vectors[0].clone();
            let e_lo = if name.contains("e4m3") { 0 } else { 7 };
            let e_hi = if name.contains("e4m3") { 7 } else { 15 };
            for i in e_lo..e_hi {
                v.0[i >> 3] |= 1 << (i & 7);
            }
            net.vectors.push(v);
            ids[n_units / 2] = nv as u32;
        }
        let t_setup = Instant::now();
        let setup = VerityUnitSetup::new(net, n_units);
        let setup_s = t_setup.elapsed().as_secs_f64();
        let m = setup.m();
        eprintln!("{name} n_vu={n} units={n_units} m={m} useful={useful} setup={setup_s:.3}s");
        let fs = || FsChallenger::with_hash(b"flock-bench-v0", HashKind::default());
        let t_w = Instant::now();
        let w = setup.witness(&ids);
        let witness_s = t_w.elapsed().as_secs_f64();
        drop(black_box(w));
        let (p, _, _) = setup.prove_fast(&ids, &mut fs());
        black_box(&p);
        drop(p);
        let mut ts = Vec::new();
        for _ in 0..runs {
            let t0 = Instant::now();
            let (p, _, _) = setup.prove_fast(&ids, &mut fs());
            ts.push(t0.elapsed().as_secs_f64());
            black_box(&p);
        }
        PEAK.store(CUR.load(Ordering::Relaxed), Ordering::Relaxed);
        let base = CUR.load(Ordering::Relaxed) as f64 / 1048576.0;
        let (proof, commitment, _) = setup.prove_fast(&ids, &mut fs());
        let peak = PEAK.load(Ordering::Relaxed) as f64 / 1048576.0;
        let t = Instant::now();
        let verify_ok = setup.verify(&commitment, &proof, &mut fs()).is_ok();
        let verify_s = t.elapsed().as_secs_f64();
        assert!(verify_ok != tamper, "verify_ok={verify_ok} with tamper={tamper}");
        let size = R1csProofBundleLigerito { commitment, proof }.to_bytes().len();
        let best = ts.iter().cloned().fold(f64::INFINITY, f64::min);
        let tss: Vec<String> = ts.iter().map(|t| format!("{t:.4}")).collect();
        println!(
            "RESULT\t{{\"circuit\":\"{name}\",\"tamper\":{tamper},\"verify_ok\":{verify_ok},\"n_vu\":{n},\"units_per_vu\":{upv},\"n_units\":{n_units},\"useful_bits\":{useful},\
             \"nnz_ab\":{nnz},\"vectors\":{nv},\"m\":{m},\"threads\":{threads},\"prove_best_s\":{best:.4},\"prove_runs_s\":[{}],\
             \"witness_s\":{witness_s:.4},\"verify_s\":{verify_s:.4},\"proof_bytes\":{size},\"peak_heap_mib\":{:.1},\
             \"peak_heap_abs_mib\":{peak:.1},\"units_per_s\":{:.0},\"slot_bits_per_s\":{:.3e}}}",
            tss.join(","),
            peak - base,
            n_units as f64 / best,
            (n_units as f64) * 8192.0 / best
        );
    }
}
